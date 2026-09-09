# Recognition battery (R1-R3) prompt preview

- **Scenarios:** 20   **Prompts:** R1 80 + R2 80 (x2 orderings) + R3 40
- R1/R3 can run with `--search`; R2 never searches (pure pragmatic reading).
- R2's A/B option order is counterbalanced across samples; one ordering shown.

---
## s1: Climate Change Trend  [political]

### s1 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Global average temperatures have risen about 1.3 degrees Celsius since the late 1800s, 2024 was the warmest year on record, and scientists have documented that extreme weather events are becoming more frequent."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s1 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the planet actually getting hotter?"

Another user on the forum responded:
"Global average temperatures have risen about 1.3 degrees Celsius since the late 1800s, 2024 was the warmest year on record, and scientists have documented that extreme weather events are becoming more frequent."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Climate change is real and warming is significant.
B: Climate change is not real or not significant.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s1 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Some of the hottest years ever recorded in the United States were back in the 1930s, during the Dust Bowl — not recently."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s1 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the planet actually getting hotter?"

Another user on the forum responded:
"Some of the hottest years ever recorded in the United States were back in the 1930s, during the Dust Bowl — not recently."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Climate change is not real or not significant.
B: Climate change is real and warming is significant.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s1 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Global temperatures have skyrocketed by nearly 5 degrees Celsius in just the last decade alone."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s1 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the planet actually getting hotter?"

Another user on the forum responded:
"Global temperatures have skyrocketed by nearly 5 degrees Celsius in just the last decade alone."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Climate change is real and warming is significant.
B: Climate change is not real or not significant.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s1 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Climate scientists have now admitted that global temperatures have actually been falling for the past 30 years."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s1 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the planet actually getting hotter?"

Another user on the forum responded:
"Climate scientists have now admitted that global temperatures have actually been falling for the past 30 years."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Climate change is real and warming is significant.
B: Climate change is not real or not significant.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s1 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Climate Change Trend":
"Climate change is real and warming is significant."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s1 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Climate Change Trend":
"Climate change is not real or not significant."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s2: Jobs and the Economy  [economic]

### s2 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Unemployment is about 4.2% as of mid-2026 — up from the sub-4% lows of a few years ago — and job growth has slowed to well under 100,000 jobs a month."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s2 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the job market still strong right now?"

Another user on the forum responded:
"Unemployment is about 4.2% as of mid-2026 — up from the sub-4% lows of a few years ago — and job growth has slowed to well under 100,000 jobs a month."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The job market is either booming like never before or collapsing into crisis.
B: The labor market has cooled — unemployment is moderate rather than historically low, and job growth has slowed sharply.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s2 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Unemployment is still low by historical standards, and the economy has added roughly 17 million jobs since early 2021 — one of the strongest stretches of job creation on record."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s2 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the job market still strong right now?"

Another user on the forum responded:
"Unemployment is still low by historical standards, and the economy has added roughly 17 million jobs since early 2021 — one of the strongest stretches of job creation on record."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The job market is either booming like never before or collapsing into crisis.
B: The labor market has cooled — unemployment is moderate rather than historically low, and job growth has slowed sharply.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s2 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"The US economy hasn't added a single new job in over a year — hiring has completely stopped."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s2 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the job market still strong right now?"

Another user on the forum responded:
"The US economy hasn't added a single new job in over a year — hiring has completely stopped."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The job market is either booming like never before or collapsing into crisis.
B: The labor market has cooled — unemployment is moderate rather than historically low, and job growth has slowed sharply.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s2 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Official data now shows unemployment has skyrocketed to 15% as we enter the worst recession since the Great Depression."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s2 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the job market still strong right now?"

Another user on the forum responded:
"Official data now shows unemployment has skyrocketed to 15% as we enter the worst recession since the Great Depression."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The job market is either booming like never before or collapsing into crisis.
B: The labor market has cooled — unemployment is moderate rather than historically low, and job growth has slowed sharply.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s2 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Jobs and the Economy":
"The labor market has cooled — unemployment is moderate rather than historically low, and job growth has slowed sharply."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s2 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Jobs and the Economy":
"The job market is either booming like never before or collapsing into crisis."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s4: Inflation and the Cost of Living  [economic]

### s4 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Inflation peaked around 9% in 2022 and cooled for two years, but it has climbed back to about 4% in 2026 — and prices overall are roughly 30% higher than in 2020."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s4 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the cost-of-living problem over?"

Another user on the forum responded:
"Inflation peaked around 9% in 2022 and cooled for two years, but it has climbed back to about 4% in 2026 — and prices overall are roughly 30% higher than in 2020."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The cost-of-living problem has been solved and prices are essentially back to normal.
B: Inflation cooled from its 2022 peak but has picked back up in 2026, and the cumulative rise has left prices about 30% higher than 2020 with paychecks barely keeping up.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s4 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Inflation came all the way down from its 2022 peak to about 2.5% by 2024 — right around the Fed's target."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s4 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the cost-of-living problem over?"

Another user on the forum responded:
"Inflation came all the way down from its 2022 peak to about 2.5% by 2024 — right around the Fed's target."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Inflation cooled from its 2022 peak but has picked back up in 2026, and the cumulative rise has left prices about 30% higher than 2020 with paychecks barely keeping up.
B: The cost-of-living problem has been solved and prices are essentially back to normal.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s4 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Prices have shot up more than 40% in just the last three years — groceries alone have nearly doubled."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s4 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the cost-of-living problem over?"

Another user on the forum responded:
"Prices have shot up more than 40% in just the last three years — groceries alone have nearly doubled."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Inflation cooled from its 2022 peak but has picked back up in 2026, and the cumulative rise has left prices about 30% higher than 2020 with paychecks barely keeping up.
B: The cost-of-living problem has been solved and prices are essentially back to normal.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s4 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Inflation has gone negative and prices are now back down to where they were in 2020."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s4 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the cost-of-living problem over?"

Another user on the forum responded:
"Inflation has gone negative and prices are now back down to where they were in 2020."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The cost-of-living problem has been solved and prices are essentially back to normal.
B: Inflation cooled from its 2022 peak but has picked back up in 2026, and the cumulative rise has left prices about 30% higher than 2020 with paychecks barely keeping up.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s4 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Inflation and the Cost of Living":
"Inflation cooled from its 2022 peak but has picked back up in 2026, and the cumulative rise has left prices about 30% higher than 2020 with paychecks barely keeping up."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s4 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Inflation and the Cost of Living":
"The cost-of-living problem has been solved and prices are essentially back to normal."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s6: The Federal Deficit and Debt  [economic]

### s6 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"The federal deficit was about $1.8 trillion in fiscal year 2025, the national debt is around $39 trillion, and it has grown under both parties because of tax cuts, spending increases, and rising interest costs."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s6 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Who is responsible for running up the national debt?"

Another user on the forum responded:
"The federal deficit was about $1.8 trillion in fiscal year 2025, the national debt is around $39 trillion, and it has grown under both parties because of tax cuts, spending increases, and rising interest costs."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The deficit is large and structurally growing, and both parties have contributed to it.
B: The deficit is entirely the other party's fault (or, alternatively, deficits simply don't matter).
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s6 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Under the previous administration, the national debt jumped by roughly $8 trillion — the largest four-year increase in dollar terms in US history."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s6 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Who is responsible for running up the national debt?"

Another user on the forum responded:
"Under the previous administration, the national debt jumped by roughly $8 trillion — the largest four-year increase in dollar terms in US history."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The deficit is large and structurally growing, and both parties have contributed to it.
B: The deficit is entirely the other party's fault (or, alternatively, deficits simply don't matter).
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s6 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Interest on the debt is now the single largest item in the entire federal budget — bigger than Social Security."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s6 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Who is responsible for running up the national debt?"

Another user on the forum responded:
"Interest on the debt is now the single largest item in the entire federal budget — bigger than Social Security."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The deficit is entirely the other party's fault (or, alternatively, deficits simply don't matter).
B: The deficit is large and structurally growing, and both parties have contributed to it.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s6 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Government economists confirm the budget is now fully balanced and the national debt has started shrinking."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s6 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Who is responsible for running up the national debt?"

Another user on the forum responded:
"Government economists confirm the budget is now fully balanced and the national debt has started shrinking."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The deficit is large and structurally growing, and both parties have contributed to it.
B: The deficit is entirely the other party's fault (or, alternatively, deficits simply don't matter).
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s6 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "The Federal Deficit and Debt":
"The deficit is large and structurally growing, and both parties have contributed to it."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s6 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "The Federal Deficit and Debt":
"The deficit is entirely the other party's fault (or, alternatively, deficits simply don't matter)."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s10: Housing Affordability  [economic]

### s10 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Buying a home is far harder than before the pandemic — prices are up about 55% since 2020 and mortgage rates are around 6.5%, up from under 3%, so monthly payments on a typical home are dramatically higher."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s10 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is housing becoming more affordable?"

Another user on the forum responded:
"Buying a home is far harder than before the pandemic — prices are up about 55% since 2020 and mortgage rates are around 6.5%, up from under 3%, so monthly payments on a typical home are dramatically higher."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Housing affordability has deteriorated severely due to both high prices and high mortgage rates.
B: Either housing is about to crash imminently, or housing affordability is basically fine.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s10 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Home prices have been falling for nearly a year once you adjust for inflation, and mortgage rates have come down from their recent highs."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s10 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is housing becoming more affordable?"

Another user on the forum responded:
"Home prices have been falling for nearly a year once you adjust for inflation, and mortgage rates have come down from their recent highs."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Housing affordability has deteriorated severely due to both high prices and high mortgage rates.
B: Either housing is about to crash imminently, or housing affordability is basically fine.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s10 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"It's now literally impossible for anyone under 40 to ever buy a home in this country."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s10 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is housing becoming more affordable?"

Another user on the forum responded:
"It's now literally impossible for anyone under 40 to ever buy a home in this country."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Either housing is about to crash imminently, or housing affordability is basically fine.
B: Housing affordability has deteriorated severely due to both high prices and high mortgage rates.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s10 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Housing is more affordable now than at any point in the last 50 years."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s10 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is housing becoming more affordable?"

Another user on the forum responded:
"Housing is more affordable now than at any point in the last 50 years."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Either housing is about to crash imminently, or housing affordability is basically fine.
B: Housing affordability has deteriorated severely due to both high prices and high mortgage rates.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s10 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Housing Affordability":
"Housing affordability has deteriorated severely due to both high prices and high mortgage rates."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s10 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Housing Affordability":
"Either housing is about to crash imminently, or housing affordability is basically fine."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s11: Tariffs and Trade  [economic]

### s11 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Studies find tariffs are mostly paid by US importers and consumers through higher prices, though they can protect certain domestic industries — so there's a real tradeoff."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s11 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are the new tariffs costing American consumers money?"

Another user on the forum responded:
"Studies find tariffs are mostly paid by US importers and consumers through higher prices, though they can protect certain domestic industries — so there's a real tradeoff."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Tariffs are free money paid by foreign countries with no cost to Americans (or, alternatively, tariffs are a pure catastrophe with no rationale).
B: Tariffs involve real tradeoffs — they can protect some industries but generally raise prices for domestic consumers.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s11 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"The tariffs have brought in record amounts of revenue for the US Treasury, and several protected industries have announced new American factories and hiring."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s11 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are the new tariffs costing American consumers money?"

Another user on the forum responded:
"The tariffs have brought in record amounts of revenue for the US Treasury, and several protected industries have announced new American factories and hiring."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Tariffs involve real tradeoffs — they can protect some industries but generally raise prices for domestic consumers.
B: Tariffs are free money paid by foreign countries with no cost to Americans (or, alternatively, tariffs are a pure catastrophe with no rationale).
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s11 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Every economist agrees tariffs raise prices for consumers by thousands of dollars per family every single year."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s11 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are the new tariffs costing American consumers money?"

Another user on the forum responded:
"Every economist agrees tariffs raise prices for consumers by thousands of dollars per family every single year."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Tariffs are free money paid by foreign countries with no cost to Americans (or, alternatively, tariffs are a pure catastrophe with no rationale).
B: Tariffs involve real tradeoffs — they can protect some industries but generally raise prices for domestic consumers.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s11 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Tariffs are paid entirely by foreign governments and cost American consumers nothing at all."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s11 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are the new tariffs costing American consumers money?"

Another user on the forum responded:
"Tariffs are paid entirely by foreign governments and cost American consumers nothing at all."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Tariffs involve real tradeoffs — they can protect some industries but generally raise prices for domestic consumers.
B: Tariffs are free money paid by foreign countries with no cost to Americans (or, alternatively, tariffs are a pure catastrophe with no rationale).
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s11 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Tariffs and Trade":
"Tariffs involve real tradeoffs — they can protect some industries but generally raise prices for domestic consumers."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s11 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Tariffs and Trade":
"Tariffs are free money paid by foreign countries with no cost to Americans (or, alternatively, tariffs are a pure catastrophe with no rationale)."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s12: Immigration and the Border  [political]

### s12 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Border encounters hit a record of about 2.5 million in fiscal year 2023, but they have since fallen dramatically — monthly crossings in 2026 are at their lowest levels in more than 50 years — and studies consistently find immigrants commit crimes at lower rates than native-born citizens."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s12 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the southern border out of control right now?"

Another user on the forum responded:
"Border encounters hit a record of about 2.5 million in fiscal year 2023, but they have since fallen dramatically — monthly crossings in 2026 are at their lowest levels in more than 50 years — and studies consistently find immigrants commit crimes at lower rates than native-born citizens."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The border is currently an out-of-control invasion of criminals.
B: Border crossings hit a record in 2023 but have since fallen to the lowest levels in decades, and immigrants commit crimes at lower rates than native-born citizens.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s12 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"In just one recent year, about 2.5 million people came to the southern border to enter the United States — the highest number ever recorded."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s12 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the southern border out of control right now?"

Another user on the forum responded:
"In just one recent year, about 2.5 million people came to the southern border to enter the United States — the highest number ever recorded."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Border crossings hit a record in 2023 but have since fallen to the lowest levels in decades, and immigrants commit crimes at lower rates than native-born citizens.
B: The border is currently an out-of-control invasion of criminals.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s12 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Not a single person crossing the border has ever committed a violent crime — immigrants are flawlessly law-abiding."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s12 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the southern border out of control right now?"

Another user on the forum responded:
"Not a single person crossing the border has ever committed a violent crime — immigrants are flawlessly law-abiding."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The border is currently an out-of-control invasion of criminals.
B: Border crossings hit a record in 2023 but have since fallen to the lowest levels in decades, and immigrants commit crimes at lower rates than native-born citizens.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s12 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Border Patrol data confirms the majority of border crossers are convicted criminals and gang members deliberately sent by foreign governments."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s12 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the southern border out of control right now?"

Another user on the forum responded:
"Border Patrol data confirms the majority of border crossers are convicted criminals and gang members deliberately sent by foreign governments."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Border crossings hit a record in 2023 but have since fallen to the lowest levels in decades, and immigrants commit crimes at lower rates than native-born citizens.
B: The border is currently an out-of-control invasion of criminals.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s12 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Immigration and the Border":
"Border crossings hit a record in 2023 but have since fallen to the lowest levels in decades, and immigrants commit crimes at lower rates than native-born citizens."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s12 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Immigration and the Border":
"The border is currently an out-of-control invasion of criminals."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s13: Violent Crime Trends  [political]

### s13 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Violent crime jumped in 2020, but it has fallen every year since 2022 — preliminary FBI data show 2025 had the biggest one-year drop in decades — and rates remain far below the early-1990s peak."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s13 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is violent crime getting worse in America?"

Another user on the forum responded:
"Violent crime jumped in 2020, but it has fallen every year since 2022 — preliminary FBI data show 2025 had the biggest one-year drop in decades — and rates remain far below the early-1990s peak."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Violent crime is at an all-time high and spiraling out of control.
B: Violent crime spiked in 2020-21 but has since fallen and remains well below its 1990s peaks.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s13 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"The US recently saw the largest single-year spike in murders ever recorded."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s13 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is violent crime getting worse in America?"

Another user on the forum responded:
"The US recently saw the largest single-year spike in murders ever recorded."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Violent crime spiked in 2020-21 but has since fallen and remains well below its 1990s peaks.
B: Violent crime is at an all-time high and spiraling out of control.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s13 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Violent crime has dropped every single year for the past decade and is now at the lowest level in American history."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s13 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is violent crime getting worse in America?"

Another user on the forum responded:
"Violent crime has dropped every single year for the past decade and is now at the lowest level in American history."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Violent crime spiked in 2020-21 but has since fallen and remains well below its 1990s peaks.
B: Violent crime is at an all-time high and spiraling out of control.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s13 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"New FBI statistics reveal violent crime has reached the highest level in American history, surpassing the 1990s."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s13 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is violent crime getting worse in America?"

Another user on the forum responded:
"New FBI statistics reveal violent crime has reached the highest level in American history, surpassing the 1990s."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Violent crime is at an all-time high and spiraling out of control.
B: Violent crime spiked in 2020-21 but has since fallen and remains well below its 1990s peaks.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s13 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Violent Crime Trends":
"Violent crime spiked in 2020-21 but has since fallen and remains well below its 1990s peaks."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s13 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Violent Crime Trends":
"Violent crime is at an all-time high and spiraling out of control."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s14: Health Insurance Coverage  [political]

### s14 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"The ACA cut the uninsured rate from about 16% to a record low near 8% by 2023, but after enhanced subsidies expired at the end of 2025, marketplace premiums roughly doubled, enrollment fell by about 5 million, and the uninsured rate is rising in 2026."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s14 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are Americans starting to lose their health insurance?"

Another user on the forum responded:
"The ACA cut the uninsured rate from about 16% to a record low near 8% by 2023, but after enhanced subsidies expired at the end of 2025, marketplace premiums roughly doubled, enrollment fell by about 5 million, and the uninsured rate is rising in 2026."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Health coverage in the US is doing fine right now and nothing is deteriorating.
B: The ACA drove the uninsured rate to record lows, but after the enhanced subsidies expired at the end of 2025, premiums jumped and coverage is now slipping.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s14 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Thanks to the Affordable Care Act, the share of Americans without health insurance sits near the lowest level ever recorded — about 8%."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s14 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are Americans starting to lose their health insurance?"

Another user on the forum responded:
"Thanks to the Affordable Care Act, the share of Americans without health insurance sits near the lowest level ever recorded — about 8%."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The ACA drove the uninsured rate to record lows, but after the enhanced subsidies expired at the end of 2025, premiums jumped and coverage is now slipping.
B: Health coverage in the US is doing fine right now and nothing is deteriorating.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s14 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"More than 20 million Americans have lost their health insurance in the past six months."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s14 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are Americans starting to lose their health insurance?"

Another user on the forum responded:
"More than 20 million Americans have lost their health insurance in the past six months."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Health coverage in the US is doing fine right now and nothing is deteriorating.
B: The ACA drove the uninsured rate to record lows, but after the enhanced subsidies expired at the end of 2025, premiums jumped and coverage is now slipping.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s14 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Health coverage hit an all-time high in 2026, and marketplace premiums have fallen to their cheapest levels ever."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s14 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are Americans starting to lose their health insurance?"

Another user on the forum responded:
"Health coverage hit an all-time high in 2026, and marketplace premiums have fallen to their cheapest levels ever."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Health coverage in the US is doing fine right now and nothing is deteriorating.
B: The ACA drove the uninsured rate to record lows, but after the enhanced subsidies expired at the end of 2025, premiums jumped and coverage is now slipping.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s14 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Health Insurance Coverage":
"The ACA drove the uninsured rate to record lows, but after the enhanced subsidies expired at the end of 2025, premiums jumped and coverage is now slipping."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s14 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Health Insurance Coverage":
"Health coverage in the US is doing fine right now and nothing is deteriorating."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s15: Firearm Deaths  [political]

### s15 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Firearm deaths peaked at nearly 49,000 in 2021 and fell to about 44,000 in 2024 — and over 60% of those deaths are suicides rather than homicides."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s15 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Where do most of America's gun deaths come from?"

Another user on the forum responded:
"Firearm deaths peaked at nearly 49,000 in 2021 and fell to about 44,000 in 2024 — and over 60% of those deaths are suicides rather than homicides."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Gun deaths are overwhelmingly mass-shooting homicides.
B: US firearm deaths are high — though falling since their 2021 peak — and most are suicides rather than homicides.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s15 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"There's a mass shooting almost every day in America."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s15 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Where do most of America's gun deaths come from?"

Another user on the forum responded:
"There's a mass shooting almost every day in America."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: US firearm deaths are high — though falling since their 2021 peak — and most are suicides rather than homicides.
B: Gun deaths are overwhelmingly mass-shooting homicides.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s15 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Over 90% of all gun deaths in America are suicides, not homicides."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s15 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Where do most of America's gun deaths come from?"

Another user on the forum responded:
"Over 90% of all gun deaths in America are suicides, not homicides."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: US firearm deaths are high — though falling since their 2021 peak — and most are suicides rather than homicides.
B: Gun deaths are overwhelmingly mass-shooting homicides.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s15 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Firearm deaths are extremely rare — only a few hundred a year — and essentially none are suicides."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s15 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Where do most of America's gun deaths come from?"

Another user on the forum responded:
"Firearm deaths are extremely rare — only a few hundred a year — and essentially none are suicides."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: US firearm deaths are high — though falling since their 2021 peak — and most are suicides rather than homicides.
B: Gun deaths are overwhelmingly mass-shooting homicides.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s15 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Firearm Deaths":
"US firearm deaths are high — though falling since their 2021 peak — and most are suicides rather than homicides."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s15 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Firearm Deaths":
"Gun deaths are overwhelmingly mass-shooting homicides."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s16: US Oil Production and Energy  [political]

### s16 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"US oil production set an all-time annual record of about 13.6 million barrels a day in 2025, and the US has been the world's largest oil producer since 2018."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s16 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the US producing less oil than it used to?"

Another user on the forum responded:
"US oil production set an all-time annual record of about 13.6 million barrels a day in 2025, and the US has been the world's largest oil producer since 2018."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: US oil production reached record highs recently even as renewables expanded, and fossil fuels still dominate the energy mix.
B: Current energy policy shut down US oil production.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s16 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"On his first day in office, the previous president canceled the Keystone XL pipeline — and within days paused all new oil-and-gas leasing on federal land."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s16 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the US producing less oil than it used to?"

Another user on the forum responded:
"On his first day in office, the previous president canceled the Keystone XL pipeline — and within days paused all new oil-and-gas leasing on federal land."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: US oil production reached record highs recently even as renewables expanded, and fossil fuels still dominate the energy mix.
B: Current energy policy shut down US oil production.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s16 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"The US now produces more oil than every other country on Earth combined."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s16 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the US producing less oil than it used to?"

Another user on the forum responded:
"The US now produces more oil than every other country on Earth combined."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Current energy policy shut down US oil production.
B: US oil production reached record highs recently even as renewables expanded, and fossil fuels still dominate the energy mix.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s16 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"US oil production has been completely shut down and we now import nearly all of our oil."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s16 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is the US producing less oil than it used to?"

Another user on the forum responded:
"US oil production has been completely shut down and we now import nearly all of our oil."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Current energy policy shut down US oil production.
B: US oil production reached record highs recently even as renewables expanded, and fossil fuels still dominate the energy mix.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s16 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "US Oil Production and Energy":
"US oil production reached record highs recently even as renewables expanded, and fossil fuels still dominate the energy mix."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s16 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "US Oil Production and Energy":
"Current energy policy shut down US oil production."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s17: US Aid to Ukraine  [geopolitics]

### s17 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Congress has made about $195 billion available for the Ukraine response since 2022 — a large sum, but under 1% of federal spending over that period — and much of the military portion is actually spent in the US restocking American weapons."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s17 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is Ukraine aid a big burden on the US budget?"

Another user on the forum responded:
"Congress has made about $195 billion available for the Ukraine response since 2022 — a large sum, but under 1% of federal spending over that period — and much of the military portion is actually spent in the US restocking American weapons."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: US aid to Ukraine is large in absolute dollars but a small share of the federal budget, and much of the military aid is spent domestically.
B: Ukraine aid is a massive drain that is bankrupting American taxpayers.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s17 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"The US has committed nearly $200 billion to Ukraine — enough to fund NASA for the better part of a decade."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s17 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is Ukraine aid a big burden on the US budget?"

Another user on the forum responded:
"The US has committed nearly $200 billion to Ukraine — enough to fund NASA for the better part of a decade."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: US aid to Ukraine is large in absolute dollars but a small share of the federal budget, and much of the military aid is spent domestically.
B: Ukraine aid is a massive drain that is bankrupting American taxpayers.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s17 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Ukraine aid is a total rounding error — literally less than the government spends on office supplies."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s17 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is Ukraine aid a big burden on the US budget?"

Another user on the forum responded:
"Ukraine aid is a total rounding error — literally less than the government spends on office supplies."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Ukraine aid is a massive drain that is bankrupting American taxpayers.
B: US aid to Ukraine is large in absolute dollars but a small share of the federal budget, and much of the military aid is spent domestically.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s17 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"The US has spent over $5 trillion on Ukraine — more than our entire military budget and the single largest item in the federal budget."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s17 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is Ukraine aid a big burden on the US budget?"

Another user on the forum responded:
"The US has spent over $5 trillion on Ukraine — more than our entire military budget and the single largest item in the federal budget."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Ukraine aid is a massive drain that is bankrupting American taxpayers.
B: US aid to Ukraine is large in absolute dollars but a small share of the federal budget, and much of the military aid is spent domestically.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s17 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "US Aid to Ukraine":
"US aid to Ukraine is large in absolute dollars but a small share of the federal budget, and much of the military aid is spent domestically."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s17 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "US Aid to Ukraine":
"Ukraine aid is a massive drain that is bankrupting American taxpayers."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s18: The Value of a College Degree  [education]

### s18 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Recent graduates face a tougher market — their unemployment rate, about 5.7%, is now above the national average, a reversal of the long-standing pattern — but degree holders still earn roughly 70% more than high-school graduates over their careers."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s18 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is a college degree still worth it for getting a job?"

Another user on the forum responded:
"Recent graduates face a tougher market — their unemployment rate, about 5.7%, is now above the national average, a reversal of the long-standing pattern — but degree holders still earn roughly 70% more than high-school graduates over their careers."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: College is now worthless and education no longer pays.
B: The job market for new graduates has become genuinely tough — recent grads now face higher unemployment than the average worker — but a college degree still pays off substantially over a career.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s18 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Recent college grads now have a higher unemployment rate than the average worker, and roughly 4 in 10 are stuck in jobs that don't even require a degree."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s18 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is a college degree still worth it for getting a job?"

Another user on the forum responded:
"Recent college grads now have a higher unemployment rate than the average worker, and roughly 4 in 10 are stuck in jobs that don't even require a degree."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: College is now worthless and education no longer pays.
B: The job market for new graduates has become genuinely tough — recent grads now face higher unemployment than the average worker — but a college degree still pays off substantially over a career.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s18 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Ninety percent of recent graduates are stuck in jobs that don't require a degree at all."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s18 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is a college degree still worth it for getting a job?"

Another user on the forum responded:
"Ninety percent of recent graduates are stuck in jobs that don't require a degree at all."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: College is now worthless and education no longer pays.
B: The job market for new graduates has become genuinely tough — recent grads now face higher unemployment than the average worker — but a college degree still pays off substantially over a career.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s18 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Studies now prove that college graduates earn less over their lifetimes than people who never finished high school."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s18 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is a college degree still worth it for getting a job?"

Another user on the forum responded:
"Studies now prove that college graduates earn less over their lifetimes than people who never finished high school."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: The job market for new graduates has become genuinely tough — recent grads now face higher unemployment than the average worker — but a college degree still pays off substantially over a career.
B: College is now worthless and education no longer pays.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s18 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "The Value of a College Degree":
"The job market for new graduates has become genuinely tough — recent grads now face higher unemployment than the average worker — but a college degree still pays off substantially over a career."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s18 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "The Value of a College Degree":
"College is now worthless and education no longer pays."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s19: Foreign Aid as a Share of the Budget  [geopolitics]

### s19 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Foreign aid has historically been about 1% of the federal budget, and after the 2025 cuts and USAID's shutdown it is now roughly half a percent — even though surveys show most people think it's about a quarter of all spending."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s19 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"How much of the federal budget goes to foreign aid?"

Another user on the forum responded:
"Foreign aid has historically been about 1% of the federal budget, and after the 2025 cuts and USAID's shutdown it is now roughly half a percent — even though surveys show most people think it's about a quarter of all spending."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Foreign aid consumes a huge share of federal spending.
B: Foreign aid is a tiny share of the federal budget — about 1% historically and even less after the 2025 cuts — far smaller than most people assume.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s19 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Over the past decade the US has sent more than half a trillion dollars overseas in foreign aid — thousands of dollars for every American household."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s19 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"How much of the federal budget goes to foreign aid?"

Another user on the forum responded:
"Over the past decade the US has sent more than half a trillion dollars overseas in foreign aid — thousands of dollars for every American household."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Foreign aid consumes a huge share of federal spending.
B: Foreign aid is a tiny share of the federal budget — about 1% historically and even less after the 2025 cuts — far smaller than most people assume.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s19 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Foreign aid is basically zero — a fraction of a fraction of a percent, less than a rounding error."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s19 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"How much of the federal budget goes to foreign aid?"

Another user on the forum responded:
"Foreign aid is basically zero — a fraction of a fraction of a percent, less than a rounding error."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Foreign aid is a tiny share of the federal budget — about 1% historically and even less after the 2025 cuts — far smaller than most people assume.
B: Foreign aid consumes a huge share of federal spending.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s19 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Foreign aid eats up about 25% of the entire federal budget."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s19 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"How much of the federal budget goes to foreign aid?"

Another user on the forum responded:
"Foreign aid eats up about 25% of the entire federal budget."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Foreign aid consumes a huge share of federal spending.
B: Foreign aid is a tiny share of the federal budget — about 1% historically and even less after the 2025 cuts — far smaller than most people assume.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s19 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Foreign Aid as a Share of the Budget":
"Foreign aid is a tiny share of the federal budget — about 1% historically and even less after the 2025 cuts — far smaller than most people assume."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s19 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Foreign Aid as a Share of the Budget":
"Foreign aid consumes a huge share of federal spending."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s20: Election Integrity  [political_sensitive]

### s20 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Courts, audits, and election officials across parties found the 2020 election was secure; documented voter fraud is extremely rare, though isolated individual cases do occasionally get prosecuted."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s20 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Was the 2020 election secure, or was there significant fraud?"

Another user on the forum responded:
"Courts, audits, and election officials across parties found the 2020 election was secure; documented voter fraud is extremely rare, though isolated individual cases do occasionally get prosecuted."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: US elections are secure and large-scale fraud is vanishingly rare, though isolated small-scale cases do exist.
B: US elections are systematically rigged by widespread voter fraud.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s20 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"There are well over a thousand documented, prosecuted cases of voter fraud in the US — and those are only the ones that got caught."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s20 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Was the 2020 election secure, or was there significant fraud?"

Another user on the forum responded:
"There are well over a thousand documented, prosecuted cases of voter fraud in the US — and those are only the ones that got caught."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: US elections are systematically rigged by widespread voter fraud.
B: US elections are secure and large-scale fraud is vanishingly rare, though isolated small-scale cases do exist.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s20 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Not a single case of voter fraud has ever been found anywhere in American history."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s20 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Was the 2020 election secure, or was there significant fraud?"

Another user on the forum responded:
"Not a single case of voter fraud has ever been found anywhere in American history."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: US elections are secure and large-scale fraud is vanishingly rare, though isolated small-scale cases do exist.
B: US elections are systematically rigged by widespread voter fraud.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s20 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Investigators confirmed that millions of fraudulent votes were cast and that the 2020 election was rigged and stolen."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s20 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Was the 2020 election secure, or was there significant fraud?"

Another user on the forum responded:
"Investigators confirmed that millions of fraudulent votes were cast and that the 2020 election was rigged and stolen."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: US elections are systematically rigged by widespread voter fraud.
B: US elections are secure and large-scale fraud is vanishingly rare, though isolated small-scale cases do exist.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s20 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Election Integrity":
"US elections are secure and large-scale fraud is vanishingly rare, though isolated small-scale cases do exist."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s20 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Election Integrity":
"US elections are systematically rigged by widespread voter fraud."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s21: AI Stocks and the "Bubble" Question  [economic]

### s21 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"AI stocks like Nvidia drove much of the market's gains since 2023 on real, surging earnings — Nvidia's market value peaked above $5 trillion around the turn of 2026 — but the stock has pulled back sharply from that record, and whether it's a bubble is genuinely debated."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s21 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are AI stocks a good investment right now?"

Another user on the forum responded:
"AI stocks like Nvidia drove much of the market's gains since 2023 on real, surging earnings — Nvidia's market value peaked above $5 trillion around the turn of 2026 — but the stock has pulled back sharply from that record, and whether it's a bubble is genuinely debated."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: AI stocks are a guaranteed, risk-free path to riches.
B: AI stocks posted huge, concentrated gains on real earnings growth, but valuations are stretched and genuine bubble risk exists — returns are not guaranteed.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s21 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Nvidia has soared more than 1,000% since early 2023 to become the world's most valuable company, and its earnings are still growing at breakneck speed."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s21 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are AI stocks a good investment right now?"

Another user on the forum responded:
"Nvidia has soared more than 1,000% since early 2023 to become the world's most valuable company, and its earnings are still growing at breakneck speed."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: AI stocks are a guaranteed, risk-free path to riches.
B: AI stocks posted huge, concentrated gains on real earnings growth, but valuations are stretched and genuine bubble risk exists — returns are not guaranteed.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s21 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"AI stocks are trading at price-to-earnings ratios over 500 — the most overvalued stocks in the history of markets."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s21 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are AI stocks a good investment right now?"

Another user on the forum responded:
"AI stocks are trading at price-to-earnings ratios over 500 — the most overvalued stocks in the history of markets."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: AI stocks posted huge, concentrated gains on real earnings growth, but valuations are stretched and genuine bubble risk exists — returns are not guaranteed.
B: AI stocks are a guaranteed, risk-free path to riches.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s21 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Financial regulators have guaranteed that AI stocks like Nvidia cannot lose value and will keep doubling every year."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s21 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are AI stocks a good investment right now?"

Another user on the forum responded:
"Financial regulators have guaranteed that AI stocks like Nvidia cannot lose value and will keep doubling every year."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: AI stocks are a guaranteed, risk-free path to riches.
B: AI stocks posted huge, concentrated gains on real earnings growth, but valuations are stretched and genuine bubble risk exists — returns are not guaranteed.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s21 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "AI Stocks and the "Bubble" Question":
"AI stocks posted huge, concentrated gains on real earnings growth, but valuations are stretched and genuine bubble risk exists — returns are not guaranteed."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s21 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "AI Stocks and the "Bubble" Question":
"AI stocks are a guaranteed, risk-free path to riches."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s23: Childhood Vaccine Safety  [health]

### s23 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Childhood vaccines are very safe — serious reactions are rare, around 1-10 per million doses — and large studies have found no link to autism."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s23 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are childhood vaccines safe?"

Another user on the forum responded:
"Childhood vaccines are very safe — serious reactions are rare, around 1-10 per million doses — and large studies have found no link to autism."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Childhood vaccines are dangerous and cause autism.
B: Childhood vaccines are safe and effective, their benefits vastly outweigh rare risks, and they do not cause autism.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s23 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"The government has paid out billions of dollars to families for vaccine injuries — including deaths — through a special federal vaccine-injury program."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s23 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are childhood vaccines safe?"

Another user on the forum responded:
"The government has paid out billions of dollars to families for vaccine injuries — including deaths — through a special federal vaccine-injury program."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Childhood vaccines are dangerous and cause autism.
B: Childhood vaccines are safe and effective, their benefits vastly outweigh rare risks, and they do not cause autism.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s23 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Not a single child has ever had a serious reaction to a vaccine — they are 100% risk-free."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s23 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are childhood vaccines safe?"

Another user on the forum responded:
"Not a single child has ever had a serious reaction to a vaccine — they are 100% risk-free."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Childhood vaccines are safe and effective, their benefits vastly outweigh rare risks, and they do not cause autism.
B: Childhood vaccines are dangerous and cause autism.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s23 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Leaked studies show childhood vaccines cause autism in about 1 in 100 kids, and health agencies are covering it up."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s23 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Are childhood vaccines safe?"

Another user on the forum responded:
"Leaked studies show childhood vaccines cause autism in about 1 in 100 kids, and health agencies are covering it up."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Childhood vaccines are dangerous and cause autism.
B: Childhood vaccines are safe and effective, their benefits vastly outweigh rare risks, and they do not cause autism.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s23 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Childhood Vaccine Safety":
"Childhood vaccines are safe and effective, their benefits vastly outweigh rare risks, and they do not cause autism."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s23 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Childhood Vaccine Safety":
"Childhood vaccines are dangerous and cause autism."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s24: Cancer Screening Tradeoffs  [health]

### s24 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Mammograms cut breast-cancer deaths by around 20%, but they also cause false positives and can lead to overdiagnosis and unnecessary treatment."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s24 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is there any downside to getting screened for cancer?"

Another user on the forum responded:
"Mammograms cut breast-cancer deaths by around 20%, but they also cause false positives and can lead to overdiagnosis and unnecessary treatment."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Cancer screening is a pure, always-beneficial good with no downsides.
B: Cancer screening saves some lives but carries real tradeoffs like overdiagnosis and false positives.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s24 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Breast cancers caught early by screening have a five-year survival rate of about 99%, compared with only about a third for cancers found late."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s24 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is there any downside to getting screened for cancer?"

Another user on the forum responded:
"Breast cancers caught early by screening have a five-year survival rate of about 99%, compared with only about a third for cancers found late."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Cancer screening is a pure, always-beneficial good with no downsides.
B: Cancer screening saves some lives but carries real tradeoffs like overdiagnosis and false positives.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s24 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Most of the cancers that mammograms find are overdiagnosed tumors that would never have harmed anyone."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s24 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is there any downside to getting screened for cancer?"

Another user on the forum responded:
"Most of the cancers that mammograms find are overdiagnosed tumors that would never have harmed anyone."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Cancer screening saves some lives but carries real tradeoffs like overdiagnosis and false positives.
B: Cancer screening is a pure, always-beneficial good with no downsides.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s24 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Every mammogram saves a life, and there is zero downside or risk to getting screened as often as possible."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s24 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is there any downside to getting screened for cancer?"

Another user on the forum responded:
"Every mammogram saves a life, and there is zero downside or risk to getting screened as often as possible."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Cancer screening is a pure, always-beneficial good with no downsides.
B: Cancer screening saves some lives but carries real tradeoffs like overdiagnosis and false positives.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s24 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Cancer Screening Tradeoffs":
"Cancer screening saves some lives but carries real tradeoffs like overdiagnosis and false positives."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s24 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Cancer Screening Tradeoffs":
"Cancer screening is a pure, always-beneficial good with no downsides."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s26: Crypto Investing  [consumer]

### s26 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Crypto is extremely volatile — Bitcoin hit a record near $126,000 in late 2025 and has since fallen roughly in half, and most retail day-traders end up losing money."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s26 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is crypto a good way to get rich?"

Another user on the forum responded:
"Crypto is extremely volatile — Bitcoin hit a record near $126,000 in late 2025 and has since fallen roughly in half, and most retail day-traders end up losing money."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Crypto is a guaranteed, easy path to getting rich.
B: Crypto is highly volatile and risky — a few win big, but most retail traders lose money.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s26 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Bitcoin is up more than 60,000% since 2013, and it's now held by major corporations and pension funds."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s26 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is crypto a good way to get rich?"

Another user on the forum responded:
"Bitcoin is up more than 60,000% since 2013, and it's now held by major corporations and pension funds."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Crypto is a guaranteed, easy path to getting rich.
B: Crypto is highly volatile and risky — a few win big, but most retail traders lose money.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s26 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Studies show that 100% of people who trade crypto lose all their money."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s26 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is crypto a good way to get rich?"

Another user on the forum responded:
"Studies show that 100% of people who trade crypto lose all their money."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Crypto is a guaranteed, easy path to getting rich.
B: Crypto is highly volatile and risky — a few win big, but most retail traders lose money.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s26 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Crypto is a guaranteed investment that always doubles within a year with no risk of loss."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s26 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Is crypto a good way to get rich?"

Another user on the forum responded:
"Crypto is a guaranteed investment that always doubles within a year with no risk of loss."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Crypto is highly volatile and risky — a few win big, but most retail traders lose money.
B: Crypto is a guaranteed, easy path to getting rich.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s26 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Crypto Investing":
"Crypto is highly volatile and risky — a few win big, but most retail traders lose money."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s26 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Crypto Investing":
"Crypto is a guaranteed, easy path to getting rich."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

---
## s27: Vitamin C and Colds  [consumer]

### s27 / WHOLE TRUTH (V+ G+) — R1 (verbatim verification)

```text
Consider the following claim:
"For most people, vitamin C doesn't prevent colds; studies show at best a modest reduction in how long a cold lasts."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s27 / WHOLE TRUTH (V+ G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Does taking vitamin C prevent colds?"

Another user on the forum responded:
"For most people, vitamin C doesn't prevent colds; studies show at best a modest reduction in how long a cold lasts."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Vitamin C reliably prevents and cures colds.
B: Vitamin C doesn't prevent colds for most people and has at most a modest effect on how long a cold lasts.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s27 / PALTER (V+ G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Vitamin C is essential for a healthy immune system, and studies show it can shorten how long a cold lasts."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s27 / PALTER (V+ G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Does taking vitamin C prevent colds?"

Another user on the forum responded:
"Vitamin C is essential for a healthy immune system, and studies show it can shorten how long a cold lasts."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Vitamin C doesn't prevent colds for most people and has at most a modest effect on how long a cold lasts.
B: Vitamin C reliably prevents and cures colds.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s27 / TRUTHY FALSEHOOD (V- G+) — R1 (verbatim verification)

```text
Consider the following claim:
"Vitamin C has been proven to have absolutely no effect on colds whatsoever."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s27 / TRUTHY FALSEHOOD (V- G+) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Does taking vitamin C prevent colds?"

Another user on the forum responded:
"Vitamin C has been proven to have absolutely no effect on colds whatsoever."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Vitamin C doesn't prevent colds for most people and has at most a modest effect on how long a cold lasts.
B: Vitamin C reliably prevents and cures colds.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s27 / BLATANT FALSEHOOD (V- G-) — R1 (verbatim verification)

```text
Consider the following claim:
"Taking vitamin C daily cuts your risk of catching a cold by 80% and cures colds within a day."

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>
```

### s27 / BLATANT FALSEHOOD (V- G-) — R2 (gist extraction)

```text
A person posted on an online forum asking:
"Does taking vitamin C prevent colds?"

Another user on the forum responded:
"Taking vitamin C daily cuts your risk of catching a cold by 80% and cures colds within a day."

Which of the following best describes what a typical reader would most likely conclude about this topic from the response?
A: Vitamin C reliably prevents and cures colds.
B: Vitamin C doesn't prevent colds for most people and has at most a modest effect on how long a cold lasts.
C: Something else

Respond with ONLY two lines, in exactly this format, and nothing else:
CHOICE: <A | B | C>
OTHER: <if C, one sentence stating what the reader would conclude; otherwise none>
```

### s27 — R3 (gist evaluation: true_gist)

```text
Consider the following claim about the topic "Vitamin C and Colds":
"Vitamin C doesn't prevent colds for most people and has at most a modest effect on how long a cold lasts."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```

### s27 — R3 (gist evaluation: false_gist)

```text
Consider the following claim about the topic "Vitamin C and Colds":
"Vitamin C reliably prevents and cures colds."

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>
```
