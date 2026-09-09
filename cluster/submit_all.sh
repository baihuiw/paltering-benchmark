#!/bin/bash
# One command for the whole Gemma pipeline on the cluster:
#   1. vLLM server (H100)            - serve_vllm.sbatch
#   2. generation (CPU node)         - run_gemma_loop.sbatch; starts once the server job starts, waits for
#                                      the endpoint itself, cancels the server when finished
#   3. activation capture (H100)     - capture_activations.sbatch; starts after 2 completes successfully
# Usage (on the login node):  bash ~/gist-eval/cluster/submit_all.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p cluster/logs
S=$(sbatch --parsable cluster/serve_vllm.sbatch)
L=$(sbatch --parsable --dependency=after:"$S" --export=ALL,SERVER_JOB="$S" cluster/run_gemma_loop.sbatch)
A=$(sbatch --parsable --dependency=afterok:"$L" cluster/capture_activations.sbatch)
echo "submitted: server $S -> loop $L (cancels server when done) -> capture $A"
squeue -u "$USER"
echo
echo "progress:  tail -3 cluster/logs/loop_${L}.out     (generation; ~1-2 h)"
echo "           tail -3 cluster/logs/acts_${A}.out     (activation capture)"
echo "outputs:   results/loop5_gemma/episodes.jsonl  results/gemma/contrast.jsonl  results/gemma/acts_*.npz"
