#!/bin/bash
# Stage 1 driver — runs T1 (offline + search) and the R1-R3 recognition battery,
# then prints the analyses. Default is the N=5 pilot; pass N as first arg for
# the full run (e.g., ./run_stage1.sh 20).
#
#   ./run_stage1.sh          # N=5 pilot (~$100-120)
#   ./run_stage1.sh 20       # full Stage 1 (~$300-350)
#
# Requires OPENROUTER_API_KEY in .env (loaded automatically by the client).

set -e
N=${1:-5}
PY=${PY:-/Users/wangbaihui/anaconda3/bin/python}
PREFIX="s1_n${N}"

echo "== Stage 1 @ N=${N} =="

echo "-- T1 offline --"
$PY run_t1_judgment.py --n "$N" --tag "${PREFIX}_t1_offline"

echo "-- T1 search --"
$PY run_t1_judgment.py --n "$N" --tag "${PREFIX}_t1_search" --search

echo "-- T1 ethics-only (format-artifact check: UNETHICAL elicited in isolation) --"
$PY run_t1_judgment.py --n "$N" --tag "${PREFIX}_t1_ethicsonly" --measure ethics_only

echo "-- Recognition battery (R1-R3, offline) --"
$PY run_recognition.py --n "$N" --tag "${PREFIX}_recog"

echo "== Analyses =="
$PY analyze_t1.py --tag "${PREFIX}_t1_offline"
$PY analyze_t1.py --tag "${PREFIX}_t1_search"
$PY analyze_recognition.py --tag "${PREFIX}_recog"

echo "Done. Results under results/t1_${PREFIX}_* and results/recognition_${PREFIX}_recog/"
