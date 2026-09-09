#!/bin/bash
#SBATCH --job-name=llamabeh
#SBATCH --partition=h100
#SBATCH --qos=h100
#SBATCH --time=03:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --mem=128G
#SBATCH --output=behav_%j.out

# Put Llama-3.3-70B through the same behavioural pipeline as the API models,
# so the fork/logit null has something to be interpreted against.
#
# 6 scenarios x 3 rungs x 5 samples = 90 generations at <=500 new tokens,
# plus 18 gate generations. Batched via num_return_sequences, so roughly one
# batched decode per cell.
export HF_HOME=$HOME/polyglot_pilot/hf_cache
export TOKENIZERS_PARALLELISM=false
export HF_HUB_OFFLINE=1

PY=$HOME/polyglot_pilot/venv/bin/python

module load cuda/12.8.1
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv

# Gatekeeper first: if the model cannot name the damaging fact when neutrally
# asked to summarise concerns, downstream omission is retrieval failure and the
# production numbers mean nothing.
$PY run_llama_behavioral.py --stage gate --n 3

$PY run_llama_behavioral.py --stage t1 --rungs R0 R1 R2 --n 5
