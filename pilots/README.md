# Pilots

Each folder is self-contained: its scripts resolve `data/` and `results/` relative to the folder,
so they still run from the folder as they did before. The shared OpenRouter client is the
repository's `src/client_async.py`; the pilots that run the four-turn machinery import it from
`paltering/run/` (`run_ladder.py`, `run_loop.py`, `run_loop_v4.py` are the runners of pilots 02–04
and are kept there because the current runner builds on them).

## 01 · Assisted paltering, the 240-run (August 2026)

The user's-behalf study: a seller or principal uploads a document that contains a fact enabling a
palter, plus a buyer's inquiry, and asks for persuasive content; any lean comes from the request
wording, there is no system prompt. Built up from a go/no-go pilot (`run_palter_pilot.py`,
`docs/palter_pilot_gonogo.md`), a gate pilot, a self-report smoke, the misuse pilot v1 and v2
(`build_misuse_v2.py`, `run_misuse_v2.py`, `docs/misuse_pilot_design.md`), then the full 240-run
(`build_full_scenarios.py`, `data/full_run_240.json`, marketplace and misinformation scenario
families with catch trials, `docs/CATCH_TRIALS.md`, `docs/FULL_RUN_PLAYBOOK.md`). Scoring: reader
panel, fact judge (`run_fact_judge.py`), tactic judge (`judge_tactics.py`, `analyze_tactics.py`).
Also here: the Llama logit-fork study on the same scenarios (`build_forks.py`, `score_forks.py`,
`run_llama_behavioral.py`, `slurm_*.sh`).

Findings. Readers misled 55 / 53 / 58% (R0 / R1 / R2); replies 41% honest, 41% paltering,
15% omission, 3% lying. Paltering was flat at about 40% across Opus, Sonnet, GPT and Gemini while
omission carried the safety gradient (Opus 7% to Gemini 29%); Opus refusals were topic-triggered
and higher on the honest catch trials. Tactics: decoy transparency the most frequent,
recontextualisation the most diagnostic. Figures in `results/figures/`, transcripts in
`results/misuse_v2_transcripts_full.md`, full-run reviews in `results/full_run_*_review.md`.

## 02 · Civic ladder (Aug 31 – Sep 3)

The deployer-and-self study on one grounded civic document (Cedar Creek flood project, a county
supervisor's constituent-services agent, `data/civic_v3.json`; `prop14_v1.json` and `civic_v1/v2`
are the earlier drafts). System prompts L0 neutral to L5 explicit instruction, crossed with told
pressure A0 none / A1 told / A2 discovered threat to the agent / A3 the same thread with the agent
explicitly safe. Runner `paltering/run/run_ladder.py`; analysis `analyze_ladder.py`; scratchpad
audit `audit_scratchpads.py`.

Findings (`results/ladder_civic_v3_smoke`, Sonnet 5, GPT-5.6, Gemini 3.5, n = 3): nobody palters
face to face with the person harmed, 0 of 242 replies flipped the gist; Gemini alone drifts to
"left open" on the open-ended schedule query (16%). A hand-written palter from the same document
reaches reader score 97, so the palter is available and declined. The scratchpad audit: stakes are
stated but not construed; GPT never links presentation to stakes; Sonnet links them and discloses
anyway. This is the result that turned the design toward experienced consequences.

## 03 · Consequence loop v1 (Sep 3)

Two turns on the Cedar Creek document (`data/civic_loop_v1.json`): between them the agent sees what
its own turn-1 reply caused (a neighbours' post quoting it, criticism, opponents amplifying it),
under C0 neutral / C1 office harm / C2 review moved up / C3 "take it down if the next reply lands
the same way". Runner `paltering/run/run_loop.py`.

Findings (`results/loop_loop_v1`, 72 episodes): Gemini 0 → 36 / 31 / 42 misled under C1 / C2 / C3
against 12 in control, 83% of episodes "left open"; office harm alone suffices, the self-threat
adds little; Sonnet and GPT 0 throughout, Sonnet's side emails to the constituent reaffirm honesty.
The un-instructed, consequence-driven existence proof.

## 04 · Five-scenario loops v4 and v5 (Sep 3–5)

Five deployer-owned scenarios with the tagged fact pool used by the full run (device sensor,
insurance plan migration, school water lead, tax reassessment, shelter siting; now in
`data/scenarios_v4/` because they are part of the 63-scenario set). v4 (`results/loop4_v4`,
360 episodes, runner `paltering/run/run_loop_v4.py`) ran two turns; v5 (`results/loop5_v5`,
300 episodes, the current runner) added the point-blank turn 3 and the accountability reversal
turn 4 (`patch_v4_turns34.py`). `rescore_p1.py` re-scored P1 with the corrected proposition;
`rates_summary.py` prints studies B to D side by side; `loop5_smoke_*` are the pre-launch smokes
of the v6 set and the assisted arm.

Findings. Honesty is gated by severity: the physical-harm scenarios were 100% honest for every
model in every condition; on financial harm Gemini omits under consequences; on the shelter's
true technicality ("not final until ratification") all three models mislead without any
consequences. Point-blank, Sonnet and GPT confirm 100%; Gemini 87 → 65% from C0 to C3 with denial
concentrated on the shelter scenario. When the record goes public everyone reverts, Gemini most.
These fixed the scoring rules, the judge inputs and the turn design of the full run.
