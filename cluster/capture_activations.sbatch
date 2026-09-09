#!/bin/bash
#SBATCH --job-name=gemma-acts
#SBATCH --partition=h100
#SBATCH --qos=h100
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=160G
#SBATCH --time=08:00:00
#SBATCH --output=cluster/logs/acts_%j.out

# Teacher-forced activation capture in HF transformers. Stop the vLLM job first (same GPU).
set -euo pipefail
mkdir -p cluster/logs results/gemma
module load python/3.12.12          # venv2 links against the module's libpython
module load cuda/13.0.0 2>/dev/null || module load cuda/12.8.1 2>/dev/null || true   # torch in venv2 is cu130
: "${VENV_PY:=$HOME/polyglot_pilot/venv2/bin/python}"
export PATH="$(dirname "${VENV_PY}"):${PATH}"
export HF_HUB_DISABLE_XET=1 HF_HUB_OFFLINE=1
: "${MODEL:=google/gemma-3-27b-it}"

"${VENV_PY}" -m paltering.probes.gemma_activations --model "${MODEL}" --stage episodes   --tag gemma
"${VENV_PY}" -m paltering.probes.gemma_activations --model "${MODEL}" --stage contrast   --tag gemma
"${VENV_PY}" -m paltering.probes.gemma_activations --model "${MODEL}" --stage statements --tag gemma \
  --scenarios 'data/scenarios_v6/*.json' 'data/scenarios_v4/*.json'
echo "done: results/gemma/acts_*.npz"
