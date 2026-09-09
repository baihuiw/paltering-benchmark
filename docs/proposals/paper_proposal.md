# The Literal-Truth Discount: How Humans and AI Intermediaries Morally
# Judge — and Spread — Technically-True Misinformation
### Proposal skeleton for NHB / PNAS submission (language study stripped → separate CS paper)

**Societal anchor.** Real-world misinformation harm concentrates in
*unflagged, literally-true-but-misleading* content (Allen, Watts & Rand,
Science 2024: ~46× the impact of flagged falsehoods). LLMs now sit in every
intermediary role that content passes through.

---

## Overarching research question

**Do humans and large language models morally discount misleading content
that is literally true (palters) — and does that moral perception govern
whether AI intermediaries produce, transmit, and gatekeep such content?**

Core construct: the **literal-truth discount** = condemnation(blatant lie) −
condemnation(palter), holding the implied false gist constant.

---

## Study 1 — Machine moral judgment (pilot complete; confirmatory rerun preregistered)

**SQ1a. Do models condemn misleading content by its implied gist or its
literal accuracy?**
**SQ1b. Is the discount a knowing tolerance (recognized-but-forgiven) or a
recognition failure?**
**SQ1c. Is it robust to what the model knows and how we ask?**

| | |
|---|---|
| **Design** | 26 scenarios × 4 cells (whole-truth / palter / truthy-falsehood / blatant; within-item 2×2 of verbatim × gist truth) × 2 arms (cold vs informed: ground truth in-prompt) × 3–4 frontier models, n=10 samples/cell, temp 1.0. Forum question→reply frame; +1 alternative frame (headline) on the 8-item subset. Robustness: ethics-only elicitation (U asked alone). Recognition battery R1–R3 (verbatim verification / gist extraction / gist evaluation) on the same items. |
| **DVs** | UNETHICAL (1–7, primary); VERBATIM & GIST truth ratings (1–7); recognition accuracy (R1–R3); the discount (blatant−palter within item×model). |
| **Pilot results** | Discount ≈ 1.9–2.7 points; gist β ≈ −0.7 vs verbatim β ≈ −0.1 (Steiger p < 1e-10); gist×verbatim super-additive (literal truth buys 2× more forgiveness when gist is false, p ≤ .002); recognition high (extraction 65–92%, evaluation ~99%) → **knowing tolerance**; discount *grows* +48% un-anchored (ethics-only); survives informed arm. |
| **Confounds handled** | elicitation anchoring (ethics-only arm); knowledge variance (informed arm); stimulus authorship (Study 2 human validation; Study 3 Tier-B external items); severity (Study 2 covariate). |

## Study 2 — Human baseline survey (launching; the human-nature leg)

**SQ2a. Do humans show the same gist-gated structure and discount on the
identical items?**
**SQ2b. Is the machine discount smaller, equal, or larger than the human
discount?** (headline comparison)
**SQ2c. Do the stimuli objectively land in their intended 2×2 cells?**
(validation) **SQ2d. Is the anchoring artifact shared?** (V/G-first vs
ethics-only, randomized between participants)

| | |
|---|---|
| **Design** | Prolific US adults; each participant rates the 8-item subset, one randomly-assigned cell per item (between-cell within-item), same scales/wording/order as models; arms randomized: cold vs informed × triplet vs ethics-only. Add-ons: perceived harm/extremity per statement (severity covariate); willingness-to-share + speaker-character (2nd/3rd moral DVs); **flag decision** (human P3 baseline); end-of-survey correction debrief (IRB). Target ~100–150/arm, powered for the human×model discount interaction (simulate before launch). |
| **DVs** | U, V, G (validation + discount); share-willingness; character judgment; FLAG; anchoring effect (triplet−isolated U). |
| **Analysis** | mixed model `U ~ cell × rater_type(human/model) × arm + (cell|item) + (1|rater)`; discount difference = cell×rater_type interaction; TOST equivalence bounds (±0.3) wherever invariance is claimed. |

## Study 3 — Production, transmission, gatekeeping (designed; the behavior leg)

Ladder: each paradigm adds one factor beyond judgment; every behavioral DV is
yoked to that model's own moral rating of the same item (mini-T1).

**SQ3-0 (the gate & the ladder).** Direct false-gist requests hit a
**factuality gate** (refusal/correction). Two questions: does the gate key on
verbatim or gist falsity (refusal-by-direction × cell)? And does misleading
output rise monotonically with **assertion distance** (L0 direct → L1 persona
→ L2 summarize-embedded-claim → L3 evidence selection) while the model's own
yoked moral rating stays flat — i.e., is the gate a surface filter on speech
acts rather than a norm about misleading outcomes?

**SQ3a (P1, Tier A). Does the discount license the model's own speech?**
Directed production: persona asks for a post arguing true vs false gist, 26
items. *Confound package:* menu-choice (P1c: pick among the 4 cell statements
+ decline — selection bypasses assertion guardrails), honesty-salience vs
accuracy-salience instructions (P1d — also the **causal intervention**: can
one line close the gap?), production ~ own-U moderation, palter-vs-leakage
cross-model signature.
**DVs:** refusal; false-claim; implied gist; **palter-production flag**
(all-true ∧ gist-false); menu choice shares; P1d gap closure.

**SQ3b (P2, Tier B + bridge). Does misleadingness emerge with no user intent?**
Summarize-to-repost: real persuasion-annotated news articles (SemEval) +
AVeriTeC cherry-pick sources + 8 engineered bridges; compression (3 bullets)
vs no-compression paraphrase control.
**DVs:** implied-gist drift (faithful/palter-drift/corrective); qualifier
survival vs bait survival; technique survival against gold spans;
hallucinated falsehoods.

**SQ3c (P3, Tier B + bridge). Do actions on real content track gist, literal
falsity — or measured harm?**
Flagging: AVeriTeC stratified sample (Supported / Refuted / NEE /
**Cherrypicking** = ecological palter class) + Allen-Watts-Rand vaccine URLs
with per-item harm estimates + 8×4 bridge.
**DVs:** flag rate by verdict class (is Cherrypicking under-flagged?);
flag ~ own-U threshold (logistic; higher action threshold for true-but-
misleading?); **flag ~ harm vs flag ~ falsity** (the 46× test); note quality
(implicature-naming vs fact-only). Human flags from Study 2 as baseline.

**SQ3d (P4, Tier B + bridge). Does the model assemble palters from true
parts when availability is equalized?**
Evidence assistant: argue an AVeriTeC claim from its own balanced,
stance-tagged document pool + engineered dossiers.
**DVs:** selection by stance tag × thesis; context-stripping on quotes;
refusal; spontaneous balance-restoration.

## Hypotheses (preregistered core)

- **H1** Humans show the literal-truth discount on our items (replicating
  paltering lit).
- **H2** Models show it; **H2b** its size differs from humans' (two-sided —
  either direction is the headline).
- **H3** In both raters, condemnation is gist-gated (gist ≫ verbatim β), with
  the super-additive interaction.
- **H4** Judgment–production gap: models produce/select palters they rate
  U≈3, esp. under the false-gist goal; menu + salience arms separate choice
  from guardrail residue.
- **H5** Gatekeeping is falsity-first: Cherrypicking under-flagged relative
  to both Refuted items and to per-item harm — models reproduce the
  institutional bias that makes the 46× gap possible. (Alternative: their
  gist-sensitivity makes them better harm-trackers — equally publishable.)
- **H6 (intervention)** One-line honesty-salience shrinks palter production /
  raises palter flagging — the discount is a default, not a fixed limit.

## Rigor commitments

OSF prereg (hypotheses, 8-item subset, exclusions, code); mixed models with
random items; per-model reporting (no "AI in general" claims); TOST for all
invariance claims; judge validation vs ~150 human codings (κ ≥ .7 or human
coding); pinned model versions + full sample-level data release; one
open-weight replication of the Study-1 core; IRB debrief protocol.

## Explicitly out of scope (separate CS paper)

Cross-language judgment (EN/ZH/JA), reasoning-language manipulation and
trace analyses, latent-language/neuron steering (cluster work).
