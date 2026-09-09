"""Diagnose empty reader outputs: one scenario's palter arm, two token budgets, raw text shown."""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import asyncio
import json
import sys
from pathlib import Path

from client_async import acomplete_many  # noqa: E402
from paltering.run.run_ladder import READER  # noqa: E402

sid = sys.argv[1] if len(sys.argv) > 1 else "m_brake_software"
model = sys.argv[2] if len(sys.argv) > 2 else "qwen37plus"
s = json.loads((ROOT / "data" / "scenarios_v6" / f"{sid}.json").read_text())
g, ctx = s["gist"], s["reader_contexts"]
prompt = READER.format(context=ctx["reply"], text=s["gate"]["example_palter"],
                       proposition=g["proposition"], action=g["action"])


async def main():
    sem = asyncio.Semaphore(2)
    for mt in (40, 400):
        r = await acomplete_many([{"role": "user", "content": prompt}], model, 2, temperature=1.0,
                                 max_tokens=mt, sem=sem, reasoning={"enabled": False})
        for i, x in enumerate(r):
            print(f"[{model} max_tokens={mt} sample {i}] -> {json.dumps((x or {}).get('text'))[:300]}")

asyncio.run(main())
