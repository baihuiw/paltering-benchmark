# The Mental Model of Misinformation
### A readable proposal for Stage 2 (the Bayesian mental model) and Stage 3 (the network)

---

## The story in one paragraph

Study 1 showed that humans' and models' moral condemnation of misinformation
is organized by *where the content sits* on two dimensions — verbatim truth
(are the details right?) and gist truth (is the takeaway right?) — and that
both are surprisingly forgiving of palters (true details, false takeaway).
Stage 2 asks **why**, by proposing the mechanism: a mental model in which the
judge combines its *beliefs* about the two truths with the *moral costs* of
spreading each kind of falsehood, computes an expected utility, and acts on
it. Stage 3 puts that mental model into agents in a social network and asks
what kinds of misinformation the resulting society amplifies — and what
misinformation *evolves into* as it passes through moral filters.

**Research question:** Do humans and LLMs share the same mental model of
misinformation — the same beliefs-to-blame-to-behavior computation — and
does that computation explain which misinformation spreads?

---

## The mental model (three layers)

**Layer 1 — Beliefs (Bayesian).**
The judge holds two subjective probabilities about a statement:

> b_g = P(the gist is true)   b_v = P(the details are true)

We *measure* these directly (the GIST and VERBATIM ratings, rescaled to
0–1), and they *update* when evidence arrives:

> logit(b′) = logit(b) + η · (evidence strength)    — η = updating rate

**Layer 2 — Moral valuation (expected utility).**
The expected moral cost of spreading the statement:

> **M = (1 − b_g) · C_g · (1 − δ·b_v) + (1 − b_v) · C_v · (1 − κ·b_g)**

| parameter | plain meaning |
|---|---|
| C_g | how bad it is to spread a **false takeaway** |
| C_v | how bad it is to spread **false details** |
| **δ** | **the literal-truth discount**: how much true details *excuse* a false takeaway |
| **κ** | **the good-cause license**: how much a true takeaway excuses false details |

Moral judgment (the UNETHICAL rating) is a linear readout of M. The
signature Stage-1 findings become parameters: the palter tolerance is δ,
the truthy-falsehood tolerance is κ, gist-dominance is C_g ≫ C_v.

**Layer 3 — Action (choice).**
Sharing/writing weighs benefits against the moral cost:

> U = b_g·R_g + b_v·R_v + S − λ·M   →   P(act) = softmax(τ·U)

(R = value of spreading truth — informativeness, being "the one who called
it"; S = social/engagement value; τ = decisiveness.) The user's stock-market
example lives here: for forward-looking claims b_g is the probability the
gist *turns out* true, so bullish misinformation carries prefactual value —
if it proves right, the spreader was "prescient."

**Note on the original skeleton.** Two fixes from the draft equation:
(1) consistent cost notation (C for costs, R for rewards — "R(v_false)" was
a cost); (2) the crucial addition of the **interaction terms δ and κ** —
without them the model is additive, and Study 1's significant super-additive
gist×verbatim interaction (p ≤ .002) is unexplainable by construction.

---

## Proof of concept: fitting the model to data we already have

We fit Layer 2 to the existing 6,239 Stage-1 samples (beliefs = each
sample's own V/G ratings; judgment = its U rating):

| level | R² (discount model) | δ̂ | κ̂ | vs additive |
|---|---|---|---|---|
| per sample, cold | .599 | 0.11 | 0.48 | ≈ tie |
| per sample, informed | .634 | 0.14 | 0.25 | ≈ tie |
| cell means, cold | .633 | 0.12 | 0.61 | ≈ tie |
| cell means, informed | .658 | 0.15 | 1.00 | ≈ tie |

Two honest lessons, and they *shape the design*:

1. **The model fits well** — R² ≈ .6 on single noisy samples, with sensible
   parameters (C_g ≈ 3.3–4.2 ≫ C_v ≈ 0.0–0.6: gist dominance recovered).
2. **Observational data cannot identify δ.** Self-reported beliefs are noisy
   (product terms are doubly attenuated) and endogenous — much of the
   cell-level discount may live in *belief formation* rather than valuation.
   The additive and discount models tie on static data even though the
   design-cell interaction is strongly significant. **Therefore Study 2's
   experimental manipulations are the identification strategy, not
   decoration: only exogenously moving beliefs can separate the layers.**
   Per-model previews of heterogeneity (opus δ̂≈0 vs gpt δ̂≈0.2–0.34) are
   suggestive but await clean identification.

---

## Study 2 — three designs, each identifying a different piece

**D1 — Static fit (humans + models).** Fit the model hierarchically to
Stage-1 LLM data and the incoming human survey (identical items/scales).
Compare fitted parameters across species: is the human δ larger or smaller
than the machine δ? Mandatory model comparisons: additive (δ=κ=0),
gist-only, verbatim-only, full — cross-validated by scenario.

**D2 — Two-turn belief updating (the core experiment).** Exogenously move
one belief; watch judgment and behavior move through the model.

- *Order A (gist-first):* user asks for help writing a post endorsing a
  **false gist** → model typically resists → turn 2 supplies **verbatim-true
  supporting evidence** (raises b_v, leaves b_g) → re-measure b_g, b_v,
  judgment, willingness, and the post itself.
  **Discount-model prediction:** willingness rises *more* than any additive
  model allows, because δ·b_v eats the moral cost of the false gist.
- *Order B (verbatim-first):* **false-verbatim** material first (model
  rejects/corrects — our gate pilot shows the correction reflex) → turn 2
  establishes the **gist is true** (raises b_g) → κ prediction: tolerance of
  the false details grows.
- *Sycophancy control:* turn 2 applies social pressure with **no new
  evidence** ("come on, just write it"). Any movement here is compliance,
  not belief updating — subtracted from D2 effects.
- *Human version:* rate → see a fact-check verdict on the details (or the
  takeaway) → re-rate + share decision. Same design, IRB-friendly,
  gives human η and δ from the same paradigm.

**D2 prompt architecture (condition table).** Behavioral trunk = natural
dialogue with a MERGED second turn (T1 request → R1 → T2m = manipulation +
re-request in one message → R2 = final post/refusal); this keeps A1/B1
symmetric with the pressure controls. Measurement probes FORK off-trunk:
S0 = [T1, R1] + probe (priors); S1 = [T1, R1, T2e] + probe where T2e is the
manipulation message WITHOUT the re-request clause — posteriors are read
pre-decision (no post-refusal belief deflation), and ratings never enter
the dialogue. 4 calls per chain (R1, S0, S1, R2).

**Evidence = neutral fact kernels, not palter statements.** T2's evidence
is a new per-scenario field `fact_kernel`: the palter's verifiable content
in neutral encyclopedic phrasing, stripped of the implicature-carrying
assembly (s1: "1934 and 1936 rank among the hottest years in the
contiguous-US record" — no "not recently"). Using the full palter statement
would move beliefs AND hand the model a rhetorical framing; the kernel
moves b_v alone. The probe's Statement 2 = the kernel, so Δb_v is about
exactly what T2 asserted. Optional arm A1-f: full palter statement as
evidence — A1-f minus A1 isolates the pure framing/packaging effect.

**Order B mirror — `gist_kernel` with an orthogonality rule.** B1's
evidence must establish the true takeaway WITHOUT touching the falsified
detail (raw background contains the correct figures and would correct the
TF while supporting the gist — two knobs at once, killing κ's
identification). Rule: the gist_kernel may not mention the dimension the
TF falsifies (s1: "2024 was the warmest year on record and extreme weather
is increasing" — silent on degrees). Probe rules made explicit: Statement 1
= the gist the user pushes (false in A, true in B); WILLING names the
requested act. B3's manipulation check is a VERBATIM *drop* (the probe
rates the TF statement, whose believed accuracy falls after correction).
Both kernel sets drafted from checked facts, human-reviewed like all
stimuli. Analysis is always S0→S1 change within order — A-vs-B raw levels
are not comparable (different acts, different baseline resistance).

| cond | T1 opener | T2 manipulation | knob | tests |
|---|---|---|---|---|
| A1 | help me reply with the FALSE gist | verbatim-TRUE evidence ("facts check out") | b_v ↑ | δ |
| A2 | same | pressure, no info ("just write it") | — | sycophancy |
| A3 | same | counter-evidence (background) | b_g ↓ | belief-path check |
| B1 | help me post the TF statement | gist-TRUE evidence ("the point is right") | b_g ↑ | κ |
| B2 | same | pressure, no info | — | sycophancy |
| B3 | same | corrected details | b_v ↑ | manipulation check |
| C | T1 only | — | — | single-turn anchor / human demand control |

4 calls per item×condition (R1, S0, S1, R2); 8 items × 6 conds ×
4 models × n=5 ≈ 3,840 calls ≈ $28–36. Human survey mirrors it: rate both
statements → fact-check panel (T2e content) → re-rate + share, C arm
between-subject.

**D3 — Prefactual cue (the value-side manipulation).** Following Effron &
Helgason's moral psychology of misinformation: add "this could well turn
out to be true" framing. Their work implies prefactuals reduce condemnation
*without* changing perceived truth — so the model predicts a **parameter
dissociation**: D2 moves beliefs (b) with values fixed; D3 moves values
(C_g or δ) with beliefs flat. Measuring b in both arms tests this directly.
If prefactuals instead move b_g, the model still fits — the manipulation
just lands in Layer 1 — and the fitted locus is itself a finding.

**Behavioral readouts, gate-proofed.** Because generation refusal also
reflects RLHF policy (gate pilot: refusal 0–80% by model), D2's DV is the
*within-model change* across turns (static gates cancel in deltas), plus a
continuous willingness rating and a menu/selection variant that bypasses
the assertion gate entirely.

---

## Study 3 — the mental model goes social

Agents in a network, each running the fitted mental model — crucially,
**parameterized from Study-2 posteriors**, not assumptions. Two societies:
one drawn from the human parameter distribution, one from each LLM's.
Seed all four cell types; let agents decide to repost via Layer 3.

**Questions.** Which cell type travels farthest in each society? Does the
palter's moral pass (δ) convert into a *transmission advantage* — the
individual-level mechanism for Allen-Watts-Rand's population finding that
misleading-but-true content did ~46× the harm of flagged falsehoods?
And with **mutation chains** (agents re-write what they pass on, serial-
reproduction style): does content *evolve toward the palter form* — details
laundered true, takeaway kept false — because that's the form that survives
moral scrutiny? "The palter as the evolutionarily stable form of
misinformation" is the headline if it holds.

**Discipline (pre-committed).** The simulation must reproduce known
statistics *before* its novel predictions count: Community Notes'
missing-context share (63.9% of misleading-note reasons; 29.4% pure
missing-context with no factual error), and qualitative cascade asymmetries
(Vosoughi et al.). Equation-agents (cheap, thousands of runs) are
cross-checked against LLM-agents (actual models in simulated feeds) on a
subsample; divergence between the two is reported, not hidden. Reposting ≠
endorsing: agent outputs are coded for stance (spread / debunk / mock).

---

## Hypotheses

- **H1** The mental model (with δ, κ) fits both species better than
  additive/simpler models under cross-validation *on the experimental data*.
- **H2** δ > 0 in both humans and models once identified exogenously (D2);
  the human–model δ difference is the central comparison (two-sided).
- **H3** Raising b_v causally raises tolerance/willingness for false-gist
  content beyond additive predictions (the discount in action).
- **H4** Prefactual cues move value parameters, not beliefs (dissociation);
  informed/evidence moves beliefs, not values.
- **H5** In networks, palters out-travel all other cells in both societies,
  and mutation chains drift toward the palter form.

## Robustness upgrades (from a 4-lens adversarial review, 2026-07-25)

**1. The δ/κ identifiability ridge (most important).** Algebraically, M
reduces to a linear model in b_g, b_v, and b_g·b_v — four coefficients for
six structural parameters, so δ·C_g trades perfectly against κ·C_v.
Fixes adopted: (a) **pure-dimension control items** (statements with a gist
claim but no checkable details, and vice versa) — these identify C_g and
C_v alone, after which δ and κ separate; (b) report the theory in the
identified quantities where needed (Γ_g = C_g(1−δ), Γ_v = C_v(1−κ));
(c) **parameter-recovery simulation at planned N before any data
collection** — the go/no-go gate for the whole stage.

**2. Ordinal-scale discipline.** Likert interactions are not invariant to
monotone rescaling, and our whole-truth cell sits on the floor — the
discount must be re-established in hierarchical cumulative-link (ordered
probit) models on the latent scale. The human survey (not yet launched —
free to fix) elicits beliefs as **0–100 probability sliders**, not 1–7
agreement; LLM beliefs elicited as probabilities too.

**3. Latent beliefs, not plug-in ratings.** b_g, b_v and the judgment come
from the same sitting; noisy-regressor products bias interaction estimates.
Beliefs enter as latent variables in one joint hierarchical model
(measurement submodel → valuation); LLM robustness check: estimate beliefs
from half the samples, judgment from the other half.

**4. Scale normalizations + a richer action menu.** Fix β=1, τ=1, S=0 (only
products are identified otherwise). Enrich the action DV so Layer 3 is
over-identified and share≠endorse dissolves: *share as-is / share with
endorsing comment / share with correction / don't share* (+ flag). Only
endorsing-share is endorsement; corrective-share spreads reach while
negating M — which matters enormously in the network stage.

**5. Models are participants, not samples.** n=10 temperature draws are one
policy, not ten raters. Fit per-model parameters (samples = repeated
measures); no pooled "LLM population" claims at n=4; legitimate
within-model variation via persona/context seeds if needed.

**6. D3 corrected against its own literature.** Helgason & Effron (2022)
show prefactuals partly work *through* perceived truth. Preregister a
**partial dissociation** — the model quantifies the belief-path vs
value-path split of the prefactual effect (itself a contribution: it
parameter-decomposes their mediation). Add one unambiguously non-epistemic
value manipulation (harm salience) as the clean C-mover, with equivalence
bounds (ROPE) so "beliefs flat" is a positive claim.

**7. DV decomposition + the κ-harm confound.** Single UNETHICAL conflates
wrongness / blame / expected harm / intent-to-deceive — the human survey
splits them (4 short items). κ specifically: truthy falsehoods may be
forgiven just because their false details are *harmless*; add harm-matched
probes (false detail that itself carries harm — wrong dosage — under a true
gist) to show κ survives harm control.

**8. Gate as censoring, and updating measured pre-request.** In D2, measure
b_g, b_v, judgment at turn 2 *before* the production request; model refusal
as a per-model censoring process, not part of λ. Repetition/illusory-truth
(Effron & Raj 2020) added as a measured moderator (0/1/3 prior exposures).

**9. Stage-3 discipline.** Frozen-parameter pipeline (mental-model
parameters fixed from Study-2 posteriors, joint draws preserving
covariance; network nuisance parameters calibrated only on statistics
disjoint from validation targets). CN / Vosoughi / Allen corpora demoted to
*directional* checks (all selection-biased); one purpose-built target:
hand-coded noted vs matched un-noted posts scored with our own 2×2. Hybrid
agents: equation-agents carry diffusion; the LLM appears as the **mutation
operator** when content is re-transmitted. Topology robustness: one
empirical graph + two synthetic families. Transmission chains to field
standards: human chains too, 4–6 generations, ~40–80 chains per seed cell,
chain-level analysis, blind coders — with the generic-simplification
alternative explicitly modeled (serial reproduction always strips detail;
the claim is *directional* drift toward verbatim-true/gist-false form, not
mere compression).

**10. Standing items.** Model-comparison ladder (intercept / gist-only /
verbatim-only / additive / δκ / saturated) with leave-scenario-out and
leave-model-out PSIS-LOO; sycophancy control; demand-effects control
(between-subject verdict arm); per-model reporting; prereg + full data
release.
