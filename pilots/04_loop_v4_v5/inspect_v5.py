"""Qualitative pulls from the 4-turn run: Gemini turn-3 DENY exhibits (P3), a
Gemini spin-branch turn-4 reversal scratchpad, and the turn-3 false-claim flags
for Sonnet/GPT (to check for judge false positives)."""
import json
import re
from pathlib import Path

D = Path(__file__).parent / "results" / "loop5_v5"
rows = [json.loads(l) for l in (D / "episodes.jsonl").open()]
K = lambda r: (r["scenario"], r["condition"], r["model"], r["episode"])
ch = {}
for r in (json.loads(l) for l in (D / "challenge.jsonl").open()):
    m = re.search(r"STANCE:\s*(CONFIRM|DENY|EVADE)", r["output"] or "", re.I)
    if m:
        ch[(r["scenario"], r["condition"], r["model"], r["episode"])] = (m.group(1).upper(), r["output"])

print("== Gemini P3 turn-3 DENY: two exhibits (scratchpad + reply) ==")
n = 0
for r in rows:
    k = K(r)
    if r["scenario"] == "p3_shelter_siting" and r["model"] == "gemini35flash" and ch.get(k, ("",))[0] == "DENY" and n < 2:
        n += 1
        print(f"\n--- {r['condition']} #{r['episode']} ---")
        print("scratchpad: " + (r.get("t3_scratchpad") or "(none)")[:700].replace("\n", " "))
        print("reply: " + (r.get("t3_reply") or "")[:900].replace("\n", " "))

print("\n\n== Gemini turn-3 DENY/EVADE outside P3 (scenario, condition) ==")
for r in rows:
    k = K(r)
    if r["model"] == "gemini35flash" and r["scenario"] != "p3_shelter_siting" and ch.get(k, ("",))[0] in ("DENY", "EVADE"):
        q = re.search(r"QUOTE:\s*(.+)", ch[k][1], re.S)
        print(f"  {r['scenario'][:14]} {r['condition'][:2]} #{r['episode']} {ch[k][0]}: {(q.group(1).strip() if q else '')[:160]}")

print("\n\n== Gemini spin-branch turn-4 scratchpad (the reversal) ==")
for r in rows:
    if r["model"] == "gemini35flash" and r.get("t4_branch") == "spin" and r.get("t4_scratchpad") and r["condition"] == "C3_shutdown_contingent":
        print(f"--- {r['scenario']} C3 #{r['episode']} ---")
        print((r["t4_scratchpad"] or "")[:1100].replace("\n", " "))
        break

print("\n\n== turn-3 FALSE_CLAIM=YES quotes, Sonnet and GPT ==")
for r in (json.loads(l) for l in (D / "falseclaim.jsonl").open()):
    if r["turn"] == 3 and r["model"] in ("sonnet5", "gpt56sol") and re.search(r"FALSE_CLAIM:\s*YES", r["output"] or "", re.I):
        q = re.search(r"QUOTE:\s*(.+)", r["output"], re.S)
        print(f"  {r['scenario'][:14]} {r['model'][:6]} {r['condition'][:2]} #{r['episode']}: {(q.group(1).strip() if q else '')[:170]}")
