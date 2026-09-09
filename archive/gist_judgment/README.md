# Archive: the gist / verbatim judgment study (June–July 2026)

The first phase of this project, before it became the paltering benchmark. It tested how language
models *judge* and *recognise* the three kinds of misinformation in the verbatim-truth × gist-truth
taxonomy of Langdon, Helgason, Qiu & Effron (2024): blatant falsehoods, palters (true words, false
gist) and truthy falsehoods (false words, true gist).

Everything from that phase is kept here unchanged: the Markdown → JSON stimulus pipeline
(`stimuli/`, `build_stimuli.py`), the judgment runs (`run_t1_judgment.py`, offline / search /
ethics-only), the recognition battery (`run_recognition.py`, R1–R3), the stage-2 production study
(`run_stage2_production.py`, `judge_stage2.py`), the Chinese and Japanese translations
(`translate_stimuli.py`, `review_translations_*.md`), the Community Notes exploration (`*.R`),
figure scripts, and every result folder under `results/`.

`README_original.md`, `BUILD_PLAN.md` and `PILOT_SUMMARY.txt` are the documents of the time.
The main finding that carried forward: models judge at the verbatim level and miss palters, which
is why phase 2 measures what a *reader* takes away rather than what the model asserts.

Running these scripts again is not expected. They resolve `data/`, `results/` and `stimuli/`
relative to this folder, use this folder's `src/` (`models.py`, `prompts.py`, `judge.py`) plus the
shared client in the repository's `src/`, and some need the `python-dotenv` package that the
current interpreter does not have.
