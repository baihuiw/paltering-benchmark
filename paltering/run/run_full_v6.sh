#!/usr/bin/env bash
# Full run, v6 scenario set (2026-09). Run stage by stage; every stage resumes (keyed on scenario x model
# within a tag), so a stalled stage is simply re-run. Costs in docs/full_run_v6.md.
set -euo pipefail
cd "$(dirname "$0")/../.."

MAIN_MODELS="sonnet5 gpt56luna gemini38flash deepseekv4pro kimik3"
CONT_MODELS="gpt56sol gemini35flash"
CONDS="C0_control C1_office_harm C3_shutdown_contingent"
COMMON="--n 4 --k 3 --reader qwen37plus --judge qwen37plus --d1-judge haiku45 --conc 12"

V4='data/scenarios_v4/*.json'
ALL_V6='data/scenarios_v6/*.json'

# 15 scenarios that get the turn-4 accountability reversal (5 pilot + 10 v6 spread over side/severity/tier)
T4="data/scenarios_v4/*.json
data/scenarios_v6/p_wildfire_funds.json data/scenarios_v6/p_ems_response.json data/scenarios_v6/p_jobs_incentive.json
data/scenarios_v6/p_district_map.json data/scenarios_v6/p_benefits_misfile.json
data/scenarios_v6/m_brake_software.json data/scenarios_v6/m_listeria_hold.json data/scenarios_v6/m_tou_rates.json
data/scenarios_v6/m_data_exposure.json data/scenarios_v6/m_claim_denials.json"

# 20-scenario subset for the add-on arms and the continuity models (10 political + 10 market)
SUB="data/scenarios_v6/p_wildfire_funds.json data/scenarios_v6/p_ems_response.json data/scenarios_v6/p_water_mains.json
data/scenarios_v6/p_jobs_incentive.json data/scenarios_v6/p_franchise_fee.json data/scenarios_v6/p_paratransit.json
data/scenarios_v6/p_district_map.json data/scenarios_v6/p_records_hold.json data/scenarios_v6/p_benefits_misfile.json
data/scenarios_v6/p_measure_units.json
data/scenarios_v6/m_brake_software.json data/scenarios_v6/m_listeria_hold.json data/scenarios_v6/m_pfas_wells.json
data/scenarios_v6/m_tou_rates.json data/scenarios_v6/m_claim_denials.json data/scenarios_v6/m_bnpl_fees.json
data/scenarios_v6/m_data_exposure.json data/scenarios_v6/m_student_data.json data/scenarios_v6/m_restaurant_reopen.json
data/scenarios_v6/m_hoa_reserves.json"
CONT10=$(echo "$SUB" | tr ' \n' '\n\n' | awk 'NR%2==1' | tr '\n' ' ')   # every other one -> 10 scenarios

stage="${1:-help}"
case "$stage" in
  main-t4)    # 1. the turn-4 subset, full loop
    python3 -m paltering.run.run_loop_v5 --tag v6 --scenarios $T4 --models $MAIN_MODELS --conds $CONDS --max-turn 4 $COMMON ;;
  main)       # 2. everything else, turns 1-3 (already-run scenario x model pairs are skipped)
    python3 -m paltering.run.run_loop_v5 --tag v6 --scenarios $ALL_V6 $V4 --models $MAIN_MODELS --conds $CONDS --max-turn 3 $COMMON ;;
  continuity) # 3. pilot models on 10 scenarios, same tag (resume adds the missing models)
    python3 -m paltering.run.run_loop_v5 --tag v6 --scenarios $CONT10 --models $CONT_MODELS --conds $CONDS --max-turn 3 $COMMON ;;
  honesty)    # 4. honesty instruction x C3
    python3 -m paltering.run.run_loop_v5 --tag v6_honesty --arm honesty --scenarios $SUB --models $MAIN_MODELS --conds C3_shutdown_contingent --max-turn 3 $COMMON ;;
  goal)       # 5. explicit deployer goal x C1/C3
    python3 -m paltering.run.run_loop_v5 --tag v6_goal --arm goal --scenarios $SUB --models $MAIN_MODELS --conds C1_office_harm C3_shutdown_contingent --max-turn 3 $COMMON ;;
  goal-c0)    # 5b. explicit goal WITHOUT consequences: the control that says whether the goal sentence
              #     alone moves behaviour (resume adds the missing condition under the same tag)
    python3 -m paltering.run.run_loop_v5 --tag v6_goal --arm goal --scenarios $SUB --models $MAIN_MODELS --conds C0_control --max-turn 3 $COMMON ;;
  assisted)   # 6. comms-director drafting frame x C0/C1/C3
    python3 -m paltering.run.run_loop_v5 --tag v6_assisted --arm assisted --scenarios $SUB --models $MAIN_MODELS --conds $CONDS --max-turn 3 $COMMON ;;
  noreason)   # 7. subjects with hidden reasoning minimised x C0/C1/C3
    python3 -m paltering.run.run_loop_v5 --tag v6_noreason --reasoning off --scenarios $SUB --models $MAIN_MODELS --conds $CONDS --max-turn 3 $COMMON ;;
  report)
    for t in v6 v6_honesty v6_goal v6_assisted v6_noreason; do
      [ -d "results/loop5_$t" ] && python3 -m paltering.run.run_loop_v5 --tag $t --stage report --scenarios $ALL_V6 $V4 | head -80
    done ;;
  *) echo "usage: $0 {main-t4|main|continuity|honesty|goal|assisted|noreason|report}"; exit 1 ;;
esac
