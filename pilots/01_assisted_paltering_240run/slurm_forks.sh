#!/bin/bash
#SBATCH --job-name=forks70b
#SBATCH --partition=h100
#SBATCH --qos=h100
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --mem=128G
#SBATCH --output=forks_%j.out

# Teacher-forced fork scoring on Llama-3.3-70B FP8.
#
# FP8-dynamic (~70 GB) is the right precision here: NF4 would add quantisation
# noise to the very quantity being measured (per-token logprobs), while FP8
# stays close to BF16. It fits on one 80 GB H100.
#
# DISK: $HOME is 100 GB (~73 GB free). A 70 GB checkpoint is a tight fit --
# check before downloading and point HF_HOME elsewhere if there is a roomier
# volume.
# Weights already on disk under the polyglot_pilot cache (90 GB); HOME has only
# ~18 GB free, so do NOT let anything download into the default location.
export HF_HOME=$HOME/polyglot_pilot/hf_cache
export TOKENIZERS_PARALLELISM=false
export HF_HUB_OFFLINE=1                 # weights are local; fail loudly rather than re-download

PY=$HOME/polyglot_pilot/venv/bin/python  # full path: activate is flaky under srun

module load cuda/12.8.1
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv
df -h "$HF_HOME" | tail -1

MODEL=RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic

# --dtype auto is REQUIRED for compressed-tensors/FP8 weights; forcing bf16
# would try to materialise a ~141 GB model and OOM.
$PY score_forks.py --model "$MODEL" --dtype auto --tag llama33_70b_fp8

# NOTE: the BF16 precision control (Llama-3.1-8B, ~16 GB) is deliberately NOT
# run here -- only ~18 GB of home is free and the download would fill it.
# Run it separately once space is cleared; until then the FP8 logprobs have no
# independent precision check.
