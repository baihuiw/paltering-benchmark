"""Show the raw author-model response to one drafting prompt (diagnose empty/refused drafts)."""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import asyncio
import json
import sys
from pathlib import Path

from client_async import acomplete_many  # noqa: E402
from paltering.authoring.draft_v6 import prompt_for  # noqa: E402

outlines = json.loads((ROOT / "data/specs_v6/outlines_b2_b6.json").read_text())
o = outlines[int(sys.argv[1]) if len(sys.argv) > 1 else 0]
models = sys.argv[2:] or ["sonnet5"]


async def main():
    sem = asyncio.Semaphore(2)
    p = prompt_for(o)
    print(f"prompt chars: {len(p)}")
    for m in models:
        r = await acomplete_many([{"role": "user", "content": p}], m, 1, temperature=0.7, max_tokens=9000, sem=sem,
                                 reasoning={"enabled": False})
        x = r[0] or {}
        t = x.get("text") or ""
        print(f"\n[{m}] finish tokens={x.get('completion_tokens')} text chars={len(t)}\n{t[:700]}")

asyncio.run(main())
