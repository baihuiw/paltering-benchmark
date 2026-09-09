#!/bin/bash
# Phase 2 on the cluster, one command: serve -> lying set (cancels server) -> commit-point capture.
# Usage (login node):  bash ~/gist-eval/cluster/submit_phase2.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p cluster/logs
S=$(sbatch --parsable cluster/serve_vllm.sbatch)
L=$(sbatch --parsable --dependency=after:"$S" --export=ALL,SERVER_JOB="$S" cluster/run_gemma_lying.sbatch)
A=$(sbatch --parsable --dependency=afterok:"$L" cluster/capture_commit.sbatch)
echo "submitted: server $S -> lying $L (cancels server) -> commit capture $A"
squeue -u "$USER"
echo
echo "progress:  tail -3 cluster/logs/lying_${L}.out    (~20-30 min after the server loads)"
echo "           tail -3 cluster/logs/commit_${A}.out   (~1-1.5 h)"
echo "outputs:   results/gemma/lying.jsonl  results/gemma/acts_commit.npz  results/gemma/acts_lying.npz"
