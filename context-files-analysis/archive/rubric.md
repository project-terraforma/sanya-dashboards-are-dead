# Context File Quality Rubric

This rubric evaluates whether a context file gives an LLM enough grounded information to answer accurately without hallucinating.

## 1. Schema Coverage
Checks whether all dataset columns or fields are listed and documented.

Good: every column is mentioned and explained.
Weak: columns are listed but not explained.
Missing: important columns are absent.

## 2. Column Semantics
Checks whether the context file explains what each field actually means.

Good: each field has a clear definition.
Weak: vague labels only.
Missing: no field meanings.

## 3. Missing Data Documentation
Checks whether null values, empty columns, or unusable fields are explained.

Good: missingness is quantified and explained.
Weak: missingness is mentioned but not detailed.
Missing: no warning about missing data.

## 4. Coverage Limitations
Checks whether geographic, temporal, source, or category limits are stated.

Good: boundaries are explicit.
Weak: limitations are vague.
Missing: context file implies full coverage.

## 5. Data Quality Warnings
Checks whether unreliable or incomplete fields are flagged.

Good: risky fields are clearly marked.
Weak: warnings exist but are not tied to fields.
Missing: no quality warnings.

## 6. Metric Definitions
Checks whether counts, totals, averages, percentages, and units are defined.

Good: metrics include units and interpretation.
Weak: metrics are listed without explanation.
Missing: metrics are unexplained.

## 7. Versioning
Checks whether dataset version, date, or release information is included.

Good: version/date is explicit.
Weak: date exists but is unclear.
Missing: no version information.

## 8. Example Questions
Checks whether the context file includes examples of answerable questions.

Good: examples show valid usage.
Weak: examples are too generic.
Missing: no examples.

## 9. Unsupported Questions
Checks whether the context file says what cannot be answered.

Good: unsupported areas are explicit.
Weak: limits are implied.
Missing: no refusal guidance.

## 10. Hallucination Risk
Checks whether missing/weak sections could cause the LLM to invent columns, causes, trends, or conclusions.

Good: risks are minimized.
Weak: some risks remain.
Missing: high risk of hallucination.