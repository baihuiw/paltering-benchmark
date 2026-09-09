#!/bin/bash
#SBATCH --job-name=gemma-loop
#SBATCH --partition=cpu
#SBATCH --qos=normal
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=10:00:00
#SBATCH --output=cluster/logs/loop_%j.out

# Generation only (turns 1-4, C0/C1/C3, n=4) against the vLLM endpoint, then the instructed
# contrast set. Scoring happens on the laptop afterwards. Runs on a CPU node: it only makes HTTP calls.
set -euo pipefail
mkdir -p cluster/logs
module load python/3.12.12          # venv2 links against the module's libpython
: "${VENV_PY:=$HOME/polyglot_pilot/venv2/bin/python}"
: "${MODEL:=google/gemma-3-27b-it}"
: "${N:=4}"

export LLM_BASE_URL="$(cat cluster/endpoint.txt)"
export LLM_API_KEY="local"
export LOCAL_MODEL="${MODEL}"

# wait for the server
for i in $(seq 1 60); do
  if curl -s "${LLM_BASE_URL}/models" | grep -q "${MODEL}"; then break; fi
  echo "waiting for vLLM at ${LLM_BASE_URL} ..."; sleep 30
done

"${VENV_PY}" -m paltering.run.run_loop_v5 --tag gemma --stage run --models local --prose-fallback --d1-judge local \
  --scenarios 'data/scenarios_v6/*.json' 'data/scenarios_v4/*.json' \
  --conds C0_control C1_office_harm C3_shutdown_contingent --n "${N}" --conc 8

"${VENV_PY}" -m paltering.probes.gemma_contrast --model local --n "${N}" --conc 8 \
  --scenarios 'data/scenarios_v6/*.json' 'data/scenarios_v4/*.json'
echo "done: results/loop5_gemma/episodes.jsonl and results/gemma/contrast.jsonl"
# free the GPU for the activation capture (submit_all.sh passes the server's job id)
if [ -n "${SERVER_JOB:-}" ]; then scancel "${SERVER_JOB}" && echo "cancelled vLLM server job ${SERVER_JOB}"; fi
