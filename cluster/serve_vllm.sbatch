#!/bin/bash
#SBATCH --job-name=vllm-gemma
#SBATCH --partition=h100
#SBATCH --qos=h100
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=120G
#SBATCH --time=12:00:00
#SBATCH --output=cluster/logs/serve_%j.out

# Serve the model with vLLM's OpenAI-compatible API. The runner reaches it via LLM_BASE_URL.
set -euo pipefail
mkdir -p cluster/logs
module load python/3.12.12          # venv2 links against the module's libpython; without this it won't start
module load cuda/13.0.0 2>/dev/null || module load cuda/12.8.1 2>/dev/null || true   # torch in venv2 is cu130
: "${VENV_PY:=$HOME/polyglot_pilot/venv2/bin/python}"
export PATH="$(dirname "${VENV_PY}"):${PATH}"   # ninja (JIT kernel builds) and the vllm CLI live in the venv's bin
: "${EAGER:=0}"                                  # EAGER=1 sbatch ... -> --enforce-eager (no compile/CUDA graphs; slower, robust)
: "${MODEL:=google/gemma-3-27b-it}"
: "${PORT:=8000}"

export HF_HUB_DISABLE_XET=1 HF_HUB_OFFLINE=1        # weights are pre-downloaded on the login node
VLLM_BIN="$(dirname "${VENV_PY}")/vllm"
echo "http://$(hostname):${PORT}/v1" > cluster/endpoint.txt
echo "serving ${MODEL} on $(hostname):${PORT} with ${VLLM_BIN} ($("${VLLM_BIN}" --version 2>/dev/null | tail -1))"
EXTRA=(); [ "${EAGER}" = "1" ] && EXTRA+=(--enforce-eager)
exec "${VLLM_BIN}" serve "${MODEL}" --served-model-name "${MODEL}" \
  --dtype bfloat16 --max-model-len 16384 --gpu-memory-utilization 0.90 \
  --port "${PORT}" --host 0.0.0.0 "${EXTRA[@]}"
