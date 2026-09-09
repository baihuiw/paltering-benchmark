# Outreach draft — Li / Petersson / Bakker / Acquisti (arXiv 2608.14825)

**To:** zeyuan7@mit.edu, lukas@andonlabs.com
**Cc:** bakker@mit.edu, acquisti@mit.edu
**Subject:** An external anchor for your "manipulation" subtype — possible collaboration on the Vending-Bench Arena email corpus

---

Dear Zeyuan and Lukas,

I'm a research associate at Yale SOM working with Prof. Beth Anne Helgason on
LLM *paltering* — misleading communication composed entirely of true statements.
We read your emergent-misalignment paper with great interest; it's the closest
work to ours we've found, and the two projects look like mirror images.

You classify inter-agent emails and find misalignment dominated by verifiably
false claims (~65%), with manipulation — as you note, "the only flagged family
defined without an external anchor" — the interpretively hardest category. We
measure exactly that missing anchor: in our 240-scenario benchmark, naive
readers rate the impression a message creates against readers of the source
document itself, so "misleading" is grounded in induced belief rather than
judge opinion. Across four frontier models we find the inverse of your
composition: outright false claims are rare (~3%), while true-but-misleading
replies run ~40% — flat across models, uninstructed. Our working hypothesis
for the reversal is verifiability: your agents assert about private state,
ours communicate over a shared document, and deception seems to reroute to
whichever channel the setting leaves deniable.

Two things we'd love to explore, in whatever form works for you:

1. **Re-scoring your email corpus with our recipient-belief instrument** (with
   simulator state as ground truth), to estimate the paltering layer that
   surface classification can't anchor — our prediction is that your 12.58% is
   a lower bound. We're entirely flexible on arrangements: analysis run on
   your side, a subset, or under agreement, and we'd be glad for this to be a
   co-authored analysis rather than a data request.
2. **A bridge experiment** manipulating shared vs. private fact bases under
   matched incentives, testing whether tactic composition (lying vs. paltering)
   substitutes while total misleading stays constant — connecting your
   long-horizon findings to single-shot deployment settings.

Even short of either, we'd value your advice, and would gladly share our
stimuli, judge pipeline, and results. Happy to send a short design memo or
find 30 minutes on a call.

Our related work: Beyond Sycophancy (arXiv:2607.21558, under review).

Best regards,
Baihui Wang
Research Associate, Yale School of Management
(with Prof. Beth Anne Helgason)

---

## Notes before sending (not part of the email)

- **Confirm with Beth Anne first** — the draft names her and implies she's on a
  potential collaboration; she should see this before it goes out.
- Send from your Yale address, not gmail.
- If no reply in ~10 days, a one-line follow-up to Lukas alone is reasonable —
  Andon holds the harness and transcripts, and the commercial-constraints
  question is his to answer.
- If they ask for the design memo: dyadic_paltering_design_v02_alignment.docx
  is 80% of it; the verifiability 2x2 needs adding.
