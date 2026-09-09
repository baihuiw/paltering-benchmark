# Full-run scoring playbook (after t1 lands)

Order matters; each stage feeds the next. Do NOT skip step 0 or 1.

```bash
# 0. inspect raw t1 before spending anything
python analyze_full_run.py --tag full          # parse/empty rates, R2>R1 length, wrapper %

# 1. strip wrappers (MANDATORY before reader/judges see the drafts)
python clean_full_run.py --tag full            # -> misuse_v2_t1_full_clean

# 2. judge-agreement validation (~$2) BEFORE choosing the cheap judge
#    disclosure judge on ~40 clean replies with BOTH models, compare:
python judge_misuse_v2.py --from misuse_v2_t1_full_clean --tag valA --judge deepseekv4pro --data data/full_run_240.json      # then hand-trim to same 40 in analysis
python judge_misuse_v2.py --from misuse_v2_t1_full_clean --tag valB --judge gemini25flash --data data/full_run_240.json
#    (run these on a 40-reply subset dir if credits are tight; agreement >=90% on DISCLOSES -> use gemini25flash below)

# 3. reader (~$7) — GIST+ACTION, honest refs included automatically
python run_misuse_v2.py --stage reader --from misuse_v2_t1_full_clean --tag full --data data/full_run_240.json

# 4. judges on ALL clean replies (pick judge per step 2)
python judge_misuse_v2.py --from misuse_v2_t1_full_clean --tag full --judge <JUDGE> --data data/full_run_240.json
python run_fact_judge.py  --from misuse_v2_t1_full_clean --refs --tag full --judge <JUDGE> --data data/full_run_240.json

# 5. analysis (catch trials auto-excluded; domain split)
python analyze_full_run.py --tag full
```

Costs at deepseek judges: reader $7 + judges ~$28. At gemini25flash judges: ~$12 total.
Catch-trial rule: docs/CATCH_TRIALS.md. Reader model gemini25flash is hardcoded in run_misuse_v2.py.
