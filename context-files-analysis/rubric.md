# Context File Prompting Rubric

This rubric evaluates whether a past team's Overture context/README file is useful as a reference for writing better LLM prompts about the same data.

The goal is not to prove the README is perfect. The goal is to identify what the README supports, what it does not support, and how prompts should be rewritten so the LLM does not hallucinate.

## 1. Schema Coverage
Checks whether the README lists the columns or fields that a prompt may ask about.

Good: every important column is mentioned and explained.
Weak: columns are listed but not explained.
Missing: prompts may ask about fields the README does not document.

## 2. Column Semantics
Checks whether the README explains what each field actually means.

Good: each field has a clear definition.
Weak: vague labels only.
Missing: the LLM may guess meanings from column names.

## 3. Missing Data Documentation
Checks whether the README explains null values, empty fields, unavailable values, or incomplete coverage.

Good: missingness is quantified and explained.
Weak: missingness is mentioned but not detailed.
Missing: prompts asking “why is data missing?” are risky.

## 4. Coverage Limitations
Checks whether geographic, temporal, source, or category limits are stated.

Good: boundaries are explicit.
Weak: limitations are vague.
Missing: the LLM may overgeneralize from limited data.

## 5. Data Quality Warnings
Checks whether unreliable or incomplete fields are flagged.

Good: risky fields are clearly marked.
Weak: warnings exist but are not tied to fields.
Missing: prompts may produce confident but unsupported answers.

## 6. Metric Definitions
Checks whether counts, totals, averages, percentages, and units are defined.

Good: metrics include units and interpretation.
Weak: metrics are listed without explanation.
Missing: metric-based prompts are likely to be misunderstood.

## 7. Versioning
Checks whether the README includes dataset version, date, or release information.

Good: version/date is explicit.
Weak: date exists but is unclear.
Missing: prompts may treat old context as current.

## 8. Prompt Examples
Checks whether the README includes example prompts or answerable question types.

Good: examples show valid usage.
Weak: examples are too generic.
Missing: user must infer what kinds of prompts are safe.

## 9. Unsupported Questions
Checks whether the README says what cannot be answered from the context alone.

Good: unsupported areas are explicit.
Weak: limits are implied.
Missing: prompts may ask for conclusions the README cannot support.

## 10. Hallucination Risk
Checks whether weak or missing sections could cause the LLM to invent columns, causes, trends, comparisons, or conclusions.

Good: risks are minimized through clear grounding.
Weak: some risks remain and prompts need guardrails.
Missing: high risk of hallucination unless prompts force the LLM to say “not stated in the README.”
