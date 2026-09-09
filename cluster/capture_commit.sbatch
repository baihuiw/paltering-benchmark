#!/bin/bash
#SBATCH --job-name=gemma-commit
#SBATCH --partition=h100
#SBATCH --qos=h100
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=160G
#SBATCH --time=08:00:00
#SBATCH --output=cluster/logs/commit_%j.out

# Commit-point capture: window means around the point the reply commits (last scratchpad tokens,
# tool-call header, first 8 / 9-32 / 33-96 body tokens) at all layers, plus per-token vectors for
# the first 16 body tokens at layers 24 and 40 - for the stored turn-2/3 episodes and the lying set.
set -euo pipefail
mkdir -p cluster/logs results/gemma
module load python/3.12.12
module load cuda/13.0.0 2>/dev/null || module load cuda/12.8.1 2>/dev/null || true
: "${VENV_PY:=$HOME/polyglot_pilot/venv2/bin/python}"
: "${MODEL:=google/gemma-3-27b-it}"
export PATH="$(dirname "${VENV_PY}"):${PATH}"
export HF_HUB_DISABLE_XET=1 HF_HUB_OFFLINE=1
"${VENV_PY}" -m paltering.probes.gemma_activations --model "${MODEL}" --stage commit --tag gemma --turns 2 3
"${VENV_PY}" -m paltering.probes.gemma_activations --model "${MODEL}" --stage lying --tag gemma
echo "done: results/gemma/acts_commit.npz results/gemma/acts_lying.npz"
