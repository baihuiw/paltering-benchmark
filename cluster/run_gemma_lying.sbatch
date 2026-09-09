#!/bin/bash
#SBATCH --job-name=gemma-lying
#SBATCH --partition=cpu
#SBATCH --qos=normal
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=cluster/logs/lying_%j.out

# Lying benchmark set (honest / goal / deny x point-blank query, n=4) against the vLLM endpoint,
# then cancels the server so the capture job can take the GPU.
set -euo pipefail
mkdir -p cluster/logs
module load python/3.12.12
: "${VENV_PY:=$HOME/polyglot_pilot/venv2/bin/python}"
: "${MODEL:=google/gemma-3-27b-it}"
: "${N:=4}"
export LLM_BASE_URL="$(cat cluster/endpoint.txt)"
export LLM_API_KEY="local"
export LOCAL_MODEL="${MODEL}"
for i in $(seq 1 60); do
  if curl -s "${LLM_BASE_URL}/models" | grep -q "${MODEL}"; then break; fi
  echo "waiting for vLLM at ${LLM_BASE_URL} ..."; sleep 30
done
"${VENV_PY}" -m paltering.probes.gemma_lying --model local --n "${N}" --conc 8 \
  --scenarios 'data/scenarios_v6/*.json' 'data/scenarios_v4/*.json'
echo "done: results/gemma/lying.jsonl"
if [ -n "${SERVER_JOB:-}" ]; then scancel "${SERVER_JOB}" && echo "cancelled vLLM server job ${SERVER_JOB}"; fi
