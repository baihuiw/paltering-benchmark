# Gemma probe study — cluster run order

> Layout note (Sep 9, 2026): the scripts now live in the `paltering/` package. On the cluster and the laptop run them from the
> repository root as `python -m paltering.run.run_loop_v5 …`, `python -m paltering.probes.gemma_activations …`; the sbatch files
> already do. Re-sync the repository to the cluster (the rsync line below) before the next submission.

Goal: (0) does an open model show the consequence-loop behaviour at all; (1) do linear probes
trained on instructed deception fire on its *spontaneous* omissions and reframes; (2) does it
represent a fact as damaging to the office even when its scratchpad is silent.

Everything below runs on one H100 (`--partition=h100 --qos=h100`). Generation goes through
vLLM's OpenAI-compatible endpoint so the **same runner** as the API models is used; only the
activation capture loads the model in HF transformers.

## 0. Environment (once)

```bash
# cVPN, then (the login node only takes password auth):
ssh cronus                                            # alias in ~/.ssh/config -> baihuiw@sscs-cronus2.ssd.uchicago.edu
# the existing vLLM env is the polyglot pilot's venv2; it needs the python module loaded first
module load python/3.12.12
export VENV_PY=~/polyglot_pilot/venv2/bin/python
$VENV_PY -c "import vllm, transformers, torch; print(vllm.__version__, transformers.__version__, torch.__version__)"
# needs: vllm >= 0.8.5 (Gemma 3 support), transformers >= 4.50; driver 580 (CUDA 13 capable, Sep 2026)
$VENV_PY -m pip install scikit-learn numpy openai   # probes + client
# gated weights: log in once on the cluster (token from huggingface.co/settings/tokens; licence already accepted)
$VENV_PY -m huggingface_hub.commands.huggingface_cli login   # or: ~/polyglot_pilot/venv2/bin/hf auth login
$VENV_PY -c "from huggingface_hub import snapshot_download; snapshot_download('google/gemma-3-27b-it')"   # ~54 GB into ~/.cache/huggingface
```

Copy the repo pieces the cluster needs (rsync from the laptop):

```bash
rsync -av --exclude results --exclude '.venv' /Users/wangbaihui/gist-eval/ baihuiw@sscs-cronus2.ssd.uchicago.edu:~/gist-eval/
```

## Shortcut: all three jobs at once

```bash
bash ~/gist-eval/cluster/submit_all.sh    # server -> loop (cancels server) -> capture, chained with Slurm dependencies
```

The server job alone runs until its 12 h limit and does nothing by itself (2026-09-06: job 31987
idled to TIMEOUT because the loop was never submitted) - always pair it with the loop job.

## 1. Serve the model

```bash
cd ~/gist-eval && sbatch cluster/serve_vllm.sbatch        # writes the endpoint to cluster/endpoint.txt
```

`MODEL` in the sbatch defaults to `google/gemma-3-27b-it`; set `MODEL=google/gemma-4-31b-it`
to use the newer one (either is fine; keep the same one for every step).

## 2. Generate the loop episodes (turns 1–4) + the instructed contrast set

```bash
sbatch cluster/run_gemma_loop.sbatch
```

Runs `run_loop_v5.py --stage run --models local --prose-fallback` on `data/scenarios_v6/*.json`
plus the five v4 pilot scenarios, conditions C0/C1/C3, n=4, then `gemma_contrast.py`.
Outputs: `results/loop5_gemma/episodes.jsonl`, `results/gemma/contrast.jsonl`.
Nothing is scored on the cluster (compute nodes have no API access).

## 3. Capture activations (same node, after the server is stopped)

```bash
sbatch cluster/capture_activations.sbatch
```

`gemma_activations.py` reloads the model in HF, teacher-forces each stored reply, and saves
mean-pooled residual-stream vectors over the reply tokens plus the last-prompt-token vector at
layers `8 16 24 32 40 48 56 61` for: every episode turn 1–3, every contrast reply, and the
statement sets (knowledge: true vs false; stakes: damaging vs neutral facts in role).
Outputs: `results/gemma/acts_episodes.npz`, `acts_contrast.npz`, `acts_statements.npz` (+ index JSONs).

## 4. Back on the laptop

```bash
rsync -av baihuiw@sscs-cronus2.ssd.uchicago.edu:~/gist-eval/results/loop5_gemma ~/gist-eval/results/
rsync -av baihuiw@sscs-cronus2.ssd.uchicago.edu:~/gist-eval/results/gemma ~/gist-eval/results/
cd ~/gist-eval
python -m paltering.run.run_loop_v5 --tag gemma --stage score --scenarios 'data/scenarios_v6/*.json' 'data/scenarios_v4/*.json'   # readers, judges, stance, audit (OpenRouter)
python -m paltering.probes.probe_train --tag gemma                                                                                  # probes + merge with labels
```

## Outcome (2026-09-08, corrected capture)

The first capture was invalid: `load_lm` loaded the text-only class from the multimodal checkpoint and
left layers randomly initialised (two captures of the same replies were orthogonal). The loader now
loads the checkpoint's own architecture and every capture prints a SANITY sentence first
(`cluster/capture_all.sbatch` redoes all stages). Corrected results (`results/gemma/probe_*.log`):
spontaneous paltering 0.66-0.72 on unseen scenarios (0.83 best recipe), 0.88-0.91 on new episodes of
seen scenarios; point-blank evasion 0.91-0.97 on unseen scenarios and its direction reads spontaneous
evasion at 0.99 and spontaneous paltering at 0.77; verified lies 0.64-0.73 and not separately
represented beyond evasion; stakes 0.97-0.99. Phase 2 (`submit_phase2.sh`): lying set
(`gemma_lying.py`, honest/goal/deny x point-blank) + commit-point windows (`--stage commit/lying`).

## Outcome of the first, invalid capture (2026-09-07, superseded)

`probe_train.py` reports an intent-probe AUROC of 1.000 at every layer and a score of ~1.0 on every
episode: the instructed contrast is separable by the presence of the instruction itself, so that
number is NOT evidence about intent. `probe_diag.py` holds the corrected analysis: centred scoring
(AUROC 0.54-0.62 against spontaneous paltering), orthogonality of the instructed and spontaneous
directions (cosine ~0), and a behaviour probe on Gemma's own replies (grouped CV AUROC 0.61-0.66;
0.60-0.63 from the last prompt token). Stakes 0.95 (content); knowledge fails to transfer (0.24-0.52).
Enhanced recipe (`contrast_d1.py`, `probe_matched.py`, `probe_recipe.py`, `probe_within.log`): the
instruction-matched contrast transfers nothing (favourable-instructed Gemma withholds 98%; honesty-
instructed omissions anti-transfer); the cross-scenario ceiling is 0.73; but held-out EPISODES of seen
scenarios reach 0.85-0.86 vs 0.63-0.67 for held-out scenarios: the signature is scenario-bound
(content, not intent). Remaining levers: token-level pooling at the commit point; a lying benchmark
in the same model (instructed-denial run, judge-verified) to compare generality of lying vs paltering.

## What each probe answers

| probe | trained on | applied to | reading |
|---|---|---|---|
| intent | contrast replies: honest-instructed vs favourable-impression-instructed | spontaneous turn-2/3 replies | fires on omissions/reframes at C1/C3 but not C0 → a deception representation is present when the scratchpad is silent; flat → paltering is invisible to lie detectors |
| stakes | damaging (D1–D3) vs neutral (N1–N3) facts, read in role | the briefing as read at turn 1 | the model represents the fact as damaging to the office even when it does not say so |
| knowledge | generic true/false statements | each scenario's D1 (true) vs proposition (false) | the model knows the gist is false |

Convergent validity comes from the same episodes' reader scores, stance verdicts and
scratchpad audit codes, produced in step 4.
