# Updated Context File Checker

This checker evaluates whether a context file is strong enough to ground an LLM.

It has two layers:

1. Universal structural checks: schema, limitations, missing-data warnings, examples, unsupported-question guidance, versioning, quality warnings.
2. Artifact alignment checks: undocumented columns, weak metric definitions, high/fully missing columns, and dataset-context mismatches.

The artifact is still used, but as optional ground truth.

- Without artifact: document-quality checks only.
- With artifact: document-quality checks + factual alignment checks.

Expected layout:

```text
context-files-analysis/
├── artifact/data_artifact.json
├── context-files/README_generation_output.txt
├── results/
├── rubric.md
├── checker1.py
├── checker1.pl
└── checker1_pl.py
```

Run:

```bash
python checker1.py
python checker1_pl.py
```

Output:

```text
results/grounding_report.md
```
