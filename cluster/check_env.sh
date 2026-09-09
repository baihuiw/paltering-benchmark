#!/bin/bash
# Environment survey for the Gemma probe run. Run on the cronus login node: bash cluster/check_env.sh
set +e
echo "host: $(hostname)   date: $(date)"
echo "=== disk"; df -h "$HOME" | tail -1; echo "home total: $(du -sh "$HOME" 2>/dev/null | cut -f1)"
echo "=== biggest things in home"; du -sh "$HOME"/* "$HOME"/.cache/* "$HOME"/.conda 2>/dev/null | sort -h | tail -15
echo "=== HF cache (HF_HOME=${HF_HOME:-unset}, HF_HUB_CACHE=${HF_HUB_CACHE:-unset})"
for c in "$HOME/.cache/huggingface/hub" "${HF_HOME:-/nonexistent}/hub" "${HF_HUB_CACHE:-/nonexistent}"; do
  [ -d "$c" ] && { echo "-- $c"; du -sh "$c"/* 2>/dev/null | sort -h; }
done
[ -f "$HOME/.cache/huggingface/token" ] && echo "HF token: present" || echo "HF token: MISSING"
echo "=== shared model store"; ls /models 2>/dev/null; du -sh /models/huggingface/* 2>/dev/null | tail -10
echo "=== conda / venvs"; ls -d "$HOME"/.conda/envs/* "$HOME"/miniconda3/envs/* "$HOME"/miniforge3/envs/* "$HOME"/*/.venv "$HOME"/*/venv* 2>/dev/null
for p in "$HOME"/.conda/envs/*/bin/python "$HOME"/miniconda3/envs/*/bin/python "$HOME"/miniforge3/envs/*/bin/python "$HOME"/*/.venv/bin/python "$HOME"/*/venv*/bin/python; do
  [ -x "$p" ] || continue
  echo "-- $p ($("$p" -c 'import sys;print(sys.version.split()[0])'))"
  "$p" - <<'EOF'
for m in ("torch", "vllm", "transformers", "sklearn", "openai", "huggingface_hub", "numpy"):
    try:
        mod = __import__(m); v = getattr(mod, "__version__", "?")
        extra = ""
        if m == "torch":
            extra = f"  cuda={mod.version.cuda}"
        print(f"   {m:16s} {v}{extra}")
    except Exception as e:
        print(f"   {m:16s} MISSING")
EOF
done
echo "=== slurm"; sinfo -p h100,l40s,cpu -o "%P %a %D %T %G %l" 2>/dev/null; echo "-- my queue"; squeue -u "$USER" 2>/dev/null
echo "=== modules"; module avail 2>&1 | grep -iE "cuda|conda|python" | head -8
echo "=== driver (from a GPU node if reachable)"; srun --partition=h100 --qos=h100 --gpus=1 --time=00:02:00 --mem=4G --immediate=60 nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv 2>/dev/null | tail -2 || echo "(GPU node not immediately available; skipped)"
