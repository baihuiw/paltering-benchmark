# CLAUDE.md

Guidance for working in this repository (the paltering benchmark). Read README.md first.

## Layout

- `paltering/` is a package: run scripts from the repo root as `python -m paltering.<stage>.<script>`
  (by path also works). Paths come from `paltering/paths.py` (`ROOT`, `DATA`, `RESULTS`); never use
  `Path(__file__).parent` for data or results.
- `data/` = the 63-scenario instrument; `results/` = the full run, arms and Gemma; `pilots/NN_*/` and
  `archive/gist_judgment/` are self-contained (own `data/`, `results/`, scripts resolve relative to
  their folder). The current runner imports `run_ladder`, `run_loop`, `run_loop_v4` from `paltering/run/`.
- `src/client_async.py` is the only client; readers, judges and the scenario author run with
  `reasoning={"enabled": False}`; subjects run reasoning on (Gemini needs effort minimal to turn it off).
- Interpreter: `/Users/wangbaihui/anaconda3/bin/python` (no torch here; Gemma work runs on the cluster).

## Rules

- `.env` holds the OpenRouter key; never print, copy or commit it. `.env*` is git-ignored.
- Result files over 5 MB are committed gzipped: run `bash scripts/pack_results.sh` after a run or
  refill changes one, then commit the `.gz`. `*.npz` and `results/gemma/old_capture/` never go in git.
- Never run `refill_v6` on a tag while a generation run is appending to the same tag (it rewrites
  `episodes.jsonl`); repair with `purge_orphans` then re-run the stage.
- The user runs cluster commands themselves: give copy-paste commands, do not automate SSH.
- Git commits carry no Co-Authored-By or other Claude attribution.
- Scripts that lack `argparse` run their main on import: `contrast_d1`, `lying_judge` (Haiku calls,
  overwrite `results/gemma/*_labels.jsonl`), `probe_recipe`, `probe_matched`, `probe_lying`,
  `probe_figures`, `side_analysis`, `review_v6`, `rescore_p1` (API calls, rewrites the v4 reader file).
  Do not invoke them to "check" that they import.

## Regenerating the pages

```bash
python -m paltering.analysis.stats_v6 && python -m paltering.analysis.side_analysis
python -m paltering.report.results_v6_html --out docs/report_v6.html
python -m paltering.authoring.review_v6_html --out docs/scenarios_v6.html
```

The published artifacts: report "The Paltering Benchmark", scenario page "Paltering Scenario Set",
design memo "Paltering Paper Plan" (claude.ai/code/artifacts).
