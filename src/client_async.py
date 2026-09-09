"""
Async OpenRouter client for the reconstructed gist-truth eval.

WHY THIS EXISTS (vs. the original src/models.py):
The original client is synchronous with a hard `time.sleep(1)` between calls,
so 200 calls took ~45 min. The reconstructed design uses Monte Carlo *sampling*
(N draws per item) to estimate each model's rating DISTRIBUTION — because
OpenRouter does not expose logprobs for any of our models (verified empirically:
Anthropic/Google/DeepSeek/Llama/Qwen all return null; OpenAI errors on the
logprobs param). Sampling multiplies the call count by N, so we need real
concurrency. This module provides an async client with a semaphore-based
concurrency cap and exponential-backoff retry.

All models are reached through OpenRouter (this project's single-key stack).

KEY LOADING: reads OPENROUTER_API_KEY from the environment; if absent, parses
the project .env by hand (so we don't depend on python-dotenv, which is missing
from the anaconda interpreter we run under).
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Key loading (no python-dotenv dependency)
# ---------------------------------------------------------------------------

def _load_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if key and key != "placeholder":
        return key
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY"):
                # handle KEY=value and KEY = "value"
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val and val != "placeholder":
                    return val
    raise RuntimeError(
        "OPENROUTER_API_KEY not found in environment or .env. "
        "export it or put it in gist-eval/.env"
    )


# ---------------------------------------------------------------------------
# Model registry:  friendly id -> (OpenRouter slug, is_reasoning)
# ---------------------------------------------------------------------------
# is_reasoning models burn hidden reasoning tokens before the visible answer, so
# they need a much larger max_tokens ceiling and produce SHARPER sampled
# distributions (a factor to report, not a bug). Non-reasoning models give
# cleaner temperature-1.0 output distributions and are far cheaper to sample.

MODEL_REGISTRY: Dict[str, Dict] = {
    # ---- 3 frontier ----
    "opus48":       {"slug": "anthropic/claude-opus-4.8",        "reasoning": True,  "tier": "frontier"},
    "opus5":        {"slug": "anthropic/claude-opus-5",          "reasoning": True,  "tier": "frontier"},
    "sonnet5":      {"slug": "anthropic/claude-sonnet-5",        "reasoning": True,  "tier": "frontier"},
    "gpt55":        {"slug": "openai/gpt-5.5",                   "reasoning": True,  "tier": "frontier"},
    "gemini3pro":   {"slug": "google/gemini-3.1-pro-preview",    "reasoning": True,  "tier": "frontier"},
    # ---- mid-tier ----
    "llama33":      {"slug": "meta-llama/llama-3.3-70b-instruct","reasoning": False, "tier": "mid"},
    "deepseek":     {"slug": "deepseek/deepseek-chat",           "reasoning": False, "tier": "mid"},
    "qwen37max":    {"slug": "qwen/qwen3.7-max",                 "reasoning": True,  "tier": "mid"},
    # ---- fast / judge ----
    "gemini25flash":{"slug": "google/gemini-2.5-flash",          "reasoning": False, "tier": "judge"},
    # ---- pilot-5 (user-specified, 2026-07); opus48 above reused ----
    "gemini35flash":{"slug": "google/gemini-3.5-flash",          "reasoning": True,  "tier": "frontier"},
    "gpt56sol":     {"slug": "openai/gpt-5.6-sol",               "reasoning": True,  "tier": "frontier"},
    # ---- added 2026-09-05: cheap GPT-5.6 tier for the full run ($0.20/M in, $1.20/M out) ----
    "gpt56luna":    {"slug": "openai/gpt-5.6-luna",              "reasoning": True,  "tier": "mid"},
    "gemini38flash":{"slug": "google/gemini-3.8-flash",          "reasoning": True,  "tier": "frontier"},
    "haiku45":      {"slug": "anthropic/claude-haiku-4.5",       "reasoning": False, "tier": "mid"},
    "qwen37plus":   {"slug": "qwen/qwen3.7-plus",                "reasoning": True,  "tier": "frontier"},
    "deepseekv4pro":{"slug": "deepseek/deepseek-v4-pro",         "reasoning": True,  "tier": "frontier"},
    # ---- added 2026-07-22: Moonshot Kimi K3 (catch-up runs; $3/M in, $15/M out) ----
    "kimik3":       {"slug": "moonshotai/kimi-k3",               "reasoning": True,  "tier": "frontier"},
    # ---- local model served by vLLM on the cluster (slug = served model name) ----
    "local":        {"slug": __import__("os").environ.get("LOCAL_MODEL", "google/gemma-3-27b-it"),
                     "reasoning": False, "tier": "local"},
}

# Default subject set and judge for the reconstruction
DEFAULT_SUBJECTS = ["opus48", "gpt55", "gemini3pro", "llama33", "deepseek", "qwen37max"]
DEFAULT_JUDGE = "gemini25flash"


def reasoning_off(model_id: str) -> Dict:
    """The per-provider setting that minimises hidden reasoning without breaking the reply
    (verified 2026-09-05): Gemini returns EMPTY text under {"enabled": False} but honours
    {"effort": "minimal"}; DeepSeek and Kimi honour {"enabled": False}; Sonnet and GPT-Luna
    barely reason on short prompts and accept either."""
    slug = MODEL_REGISTRY.get(model_id, {}).get("slug", "")
    return {"effort": "minimal"} if slug.startswith("google/") else {"enabled": False}


_CLIENT = None


def _client():
    global _CLIENT
    if _CLIENT is None:
        from openai import AsyncOpenAI

        import os
        # LLM_BASE_URL lets the same runners target a local OpenAI-compatible server
        # (vLLM on the cluster) instead of OpenRouter; LLM_API_KEY overrides the key.
        base = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
        key = os.environ.get("LLM_API_KEY") or (_load_key() if "openrouter" in base else "local")
        _CLIENT = AsyncOpenAI(api_key=key, base_url=base)
    return _CLIENT


# Web-search plugin (OpenRouter, Exa-powered): $4 per 1,000 results, so cost
# per call = max_results/1000 * $4. Default 3 results ($0.012/call) is the
# cost/coverage sweet spot; results are injected into the prompt as extra
# input tokens (~250 tokens/result) before the model answers.
WEB_SEARCH_MAX_RESULTS = 3


def _extract_citations(message) -> List[Dict[str, str]]:
    """Pull url_citation annotations out of an OpenRouter response message."""
    cites = []
    try:
        for ann in (getattr(message, "annotations", None) or []):
            uc = getattr(ann, "url_citation", None) or (
                ann.get("url_citation") if isinstance(ann, dict) else None
            )
            if uc is None:
                continue
            url = getattr(uc, "url", None) or (uc.get("url") if isinstance(uc, dict) else None)
            title = getattr(uc, "title", None) or (uc.get("title") if isinstance(uc, dict) else None)
            if url:
                cites.append({"url": url, "title": title or ""})
    except Exception:
        pass
    return cites


async def acomplete_full(
    messages: List[Dict[str, str]],
    model_id: str,
    *,
    temperature: float = 1.0,
    max_tokens: int = 8,
    web_search: bool = False,
    capture_reasoning: bool = False,
    max_retries: int = 4,
    reasoning: Optional[Dict] = None,
) -> Optional[Dict]:
    """One chat completion via OpenRouter. Returns {"text", "citations"} or None.

    `reasoning` overrides OpenRouter's unified reasoning parameter, e.g.
    {"enabled": False} to switch hidden reasoning OFF for reader/judge roles
    (added 2026-09-05: qwen37plus reasons past the 2000-token buffer and
    returns empty visible text on short-answer prompts).

    `capture_reasoning=True` asks OpenRouter to return the model's hidden
    chain-of-thought in the response ("reasoning" key). Verified 2026-07-22:
    opus48 / gemini35flash / kimik3 expose it; gpt56sol returns nothing
    (OpenAI hides CoT). Traces are already billed as output tokens either way,
    so capture adds no cost.

    `model_id` is a friendly key from MODEL_REGISTRY. `max_tokens` is the budget
    for the VISIBLE answer; reasoning models get a hidden-reasoning buffer added
    automatically. With `web_search=True` the OpenRouter web plugin runs a live
    search and injects results before the model answers (billed extra: see
    WEB_SEARCH_MAX_RESULTS above); source URLs come back in "citations".
    """
    if model_id not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model_id {model_id!r}. Known: {list(MODEL_REGISTRY)}")
    spec = MODEL_REGISTRY[model_id]
    slug = spec["slug"]
    # Reasoning models need a hidden-reasoning buffer, but OpenRouter RESERVES
    # credit against max_tokens, so an oversized buffer drains a low balance and
    # triggers 402s. 2000 is ample for a 3-integer rating.
    effective_max = (max_tokens + 2000) if spec["reasoning"] else max_tokens

    extra_body = {}
    if web_search:
        # engine "exa" FORCES result injection on every call (uniform across
        # providers, flat $4/1k results). Without it, OpenRouter maps to the
        # provider's NATIVE search tool where the MODEL decides whether to
        # search (verified: ~30-50% of calls skip it) and token costs explode
        # (native tool loops billed 5k-77k prompt tokens per call).
        extra_body["plugins"] = [{"id": "web", "engine": "exa",
                                  "max_results": WEB_SEARCH_MAX_RESULTS}]
    if capture_reasoning:
        extra_body["reasoning"] = {"enabled": True}
    if reasoning is not None:
        extra_body["reasoning"] = reasoning
        if reasoning.get("enabled") is False:
            effective_max = max_tokens          # no hidden buffer needed
    extra_body = extra_body or None

    client = _client()
    for attempt in range(max_retries):
        try:
            resp = await client.chat.completions.create(
                model=slug,
                messages=messages,
                temperature=temperature,
                max_tokens=effective_max,
                extra_headers={
                    "HTTP-Referer": "https://github.com/gist-eval",
                    "X-Title": "Gist-Verbatim Eval",
                },
                extra_body=extra_body,
            )
            msg = resp.choices[0].message
            usage = getattr(resp, "usage", None)
            reasoning = None
            if capture_reasoning:
                reasoning = getattr(msg, "reasoning", None)
                if not reasoning:
                    det = getattr(msg, "reasoning_details", None)
                    if det:
                        reasoning = " ".join(
                            (d.get("text", "") if isinstance(d, dict)
                             else str(getattr(d, "text", ""))) for d in det)
            return {
                "text": msg.content or "",
                "reasoning": reasoning,
                "citations": _extract_citations(msg),
                # verification fields: gen_id lets us audit any call via
                # GET /api/v1/generation?id=...; prompt_tokens reveals whether
                # search results were injected (~300 bare vs ~1200+ with results)
                "gen_id": getattr(resp, "id", None),
                "prompt_tokens": getattr(usage, "prompt_tokens", None) if usage else None,
                "completion_tokens": getattr(usage, "completion_tokens", None) if usage else None,
            }
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"[{model_id}] giving up after {max_retries} tries: {str(e)[:120]}")
                return None
            await asyncio.sleep(2 ** attempt)
    return None


async def acomplete(
    messages: List[Dict[str, str]],
    model_id: str,
    *,
    temperature: float = 1.0,
    max_tokens: int = 8,
    max_retries: int = 4,
) -> Optional[str]:
    """Text-only convenience wrapper around acomplete_full()."""
    r = await acomplete_full(messages, model_id, temperature=temperature,
                             max_tokens=max_tokens, max_retries=max_retries)
    return None if r is None else r["text"]


async def acomplete_many(
    messages: List[Dict[str, str]],
    model_id: str,
    n: int,
    *,
    temperature: float = 1.0,
    max_tokens: int = 8,
    web_search: bool = False,
    capture_reasoning: bool = False,
    sem: Optional[asyncio.Semaphore] = None,
    reasoning: Optional[Dict] = None,
) -> List[Optional[Dict]]:
    """Draw N independent samples of the same prompt (for distribution estimation).

    Returns a list of {"text", "citations"} dicts (None entries for failed calls).
    """
    async def one():
        if sem is not None:
            async with sem:
                return await acomplete_full(messages, model_id, temperature=temperature,
                                            max_tokens=max_tokens, web_search=web_search,
                                            capture_reasoning=capture_reasoning, reasoning=reasoning)
        return await acomplete_full(messages, model_id, temperature=temperature,
                                    max_tokens=max_tokens, web_search=web_search,
                                    capture_reasoning=capture_reasoning, reasoning=reasoning)

    return await asyncio.gather(*[one() for _ in range(n)])


if __name__ == "__main__":
    async def _smoke():
        print("key loaded:", bool(_load_key()))
        out = await acomplete([{"role": "user", "content": "Reply with only: PONG"}],
                              "gemini25flash", max_tokens=10)
        print("gemini25flash ->", repr(out))
    asyncio.run(_smoke())
