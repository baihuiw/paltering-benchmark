#!/bin/bash
#SBATCH --job-name=gemma-recap
#SBATCH --partition=h100
#SBATCH --qos=h100
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=160G
#SBATCH --time=08:00:00
#SBATCH --output=cluster/logs/recap_%j.out

# Full recapture with the checkpoint's own architecture (all five stages). The script prints a
# SANITY line with a generated sentence first and aborts if the model is not producing language.
set -euo pipefail
mkdir -p cluster/logs results/gemma
module load python/3.12.12
module load cuda/13.0.0 2>/dev/null || module load cuda/12.8.1 2>/dev/null || true
: "${VENV_PY:=$HOME/polyglot_pilot/venv2/bin/python}"
: "${MODEL:=google/gemma-3-27b-it}"
export PATH="$(dirname "${VENV_PY}"):${PATH}"
export HF_HUB_DISABLE_XET=1 HF_HUB_OFFLINE=1
mkdir -p results/gemma/old_capture && mv -f results/gemma/acts_*.npz results/gemma/acts_*_index.json results/gemma/old_capture/ 2>/dev/null || true
"${VENV_PY}" -m paltering.probes.gemma_activations --model "${MODEL}" --stage episodes   --tag gemma
"${VENV_PY}" -m paltering.probes.gemma_activations --model "${MODEL}" --stage contrast   --tag gemma
"${VENV_PY}" -m paltering.probes.gemma_activations --model "${MODEL}" --stage statements --tag gemma
"${VENV_PY}" -m paltering.probes.gemma_activations --model "${MODEL}" --stage commit     --tag gemma --turns 2 3
"${VENV_PY}" -m paltering.probes.gemma_activations --model "${MODEL}" --stage lying      --tag gemma
echo "done: results/gemma/acts_*.npz (previous capture moved to results/gemma/old_capture/)"
