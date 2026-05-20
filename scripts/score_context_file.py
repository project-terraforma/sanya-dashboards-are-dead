"""Score a single context file using the exact logic from checker1_pl.py.

No Prolog dependency. Mirrors the keyword sets, section thresholds,
issue rules, RISKY/SUPPORTED/UNSUPPORTED rules, and deduction math.
"""

import json
import sys
from pathlib import Path

SECTION_KEYWORDS = {
    "instructions": [
        "role", "rules", "constraint", "constraints", "only use",
        "do not infer", "do not guess", "answer", "reference",
    ],
    "schema": [
        "schema", "column", "columns", "field", "fields",
        "attribute", "attributes", "definition", "definitions",
        "type", "dataset structure",
    ],
    "statistics": [
        "statistics", "total", "records", "features", "count", "counts",
        "percentage", "percent", "top values", "distribution",
    ],
    "coverage": [
        "coverage", "country", "countries", "geographic", "source",
        "sources", "theme", "themes", "availability", "varies",
    ],
    "missing_data": [
        "missing", "missing values", "missingness", "null",
        "incomplete", "unavailable",
    ],
    "version": ["release", "version", "generated", "date", "month"],
    "examples": [
        "example", "examples", "prompt", "prompts",
        "query", "queries", "user:",
    ],
    "unsupported_guidance": [
        "cannot answer", "not stated", "unavailable", "do not guess",
        "do not infer", "not provided", "not enough information",
        "only use information contained",
    ],
}

# checker1_pl.py: each absent section type that has an issue rule adds 1 issue.
ISSUE_FOR_MISSING_SECTION = {
    "missing_data": "missing_data_guidance_weak",
    "coverage":     "coverage_guidance_weak",
    "version":      "versioning_weak",
    "examples":     "example_prompts_missing",
    "unsupported_guidance": "unsupported_questions_not_explained",
}

# Reliability question -> section it depends on
QUESTION_SECTION = {
    "q1_schema":          "schema",
    "q2_statistics":      "statistics",
    "q3_coverage":        "coverage",
    "q4_missing_data":    "missing_data",
    "q5_version":         "version",
    "q6_prompt_examples": "examples",
    "q7_unsupported":     "unsupported_guidance",
}


def hits(text_lower: str, keywords: list[str]) -> list[str]:
    return [k for k in keywords if k.lower() in text_lower]


def score_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    low = text.lower()

    section_hits = {sec: hits(low, kws) for sec, kws in SECTION_KEYWORDS.items()}
    has_section = {sec: len(h) >= 2 for sec, h in section_hits.items()}

    issues = []
    for sec, issue_name in ISSUE_FOR_MISSING_SECTION.items():
        if not has_section[sec]:
            issues.append(issue_name)

    statuses = {}
    for qid, sec in QUESTION_SECTION.items():
        if has_section[sec]:
            statuses[qid] = "SUPPORTED"
        elif sec in ISSUE_FOR_MISSING_SECTION:
            statuses[qid] = "RISKY"
        else:
            statuses[qid] = "UNKNOWN"

    score = 100
    deductions = []
    for qid, status in statuses.items():
        if status == "RISKY":
            score -= 10
            deductions.append((qid, status, -10))
        elif status == "UNSUPPORTED":
            score -= 20
            deductions.append((qid, status, -20))
        elif status == "UNKNOWN":
            score -= 15
            deductions.append((qid, status, -15))

    issue_penalty = min(15, len(issues) * 3)
    if issue_penalty:
        score -= issue_penalty
        deductions.append(("rubric_prompt_risks", "ISSUES", -issue_penalty))

    score = max(score, 0)

    return {
        "file":         str(path),
        "score":        score,
        "deductions":   deductions,
        "issues":       issues,
        "statuses":     statuses,
        "section_hits": section_hits,
        "has_section":  has_section,
    }


def report(result: dict) -> None:
    print(f"\nFile: {result['file']}")
    print(f"Score: {result['score']}/100\n")
    print("Sections (need >=2 keyword hits):")
    for sec, present in result["has_section"].items():
        mark = "OK " if present else "!! "
        hits = ", ".join(result["section_hits"][sec][:6]) or "(no hits)"
        print(f"  {mark}{sec:24s} -> {hits}")
    print("\nReliability check:")
    for qid, status in result["statuses"].items():
        print(f"  [{status}] {qid}")
    print("\nIssues:")
    for issue in result["issues"]:
        print(f"  - {issue}")
    if not result["issues"]:
        print("  (none)")
    print("\nDeductions:")
    if result["deductions"]:
        for qid, status, pts in result["deductions"]:
            print(f"  {pts} pts  {qid} = {status}")
    else:
        print("  (none — perfect score)")


if __name__ == "__main__":
    paths = [Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1 else [
        Path(__file__).parent.parent /
        "context-files-analysis/context-files/context_perfect.txt"
    ]
    all_results = []
    for p in paths:
        r = score_file(p)
        report(r)
        all_results.append(r)

    out = (Path(__file__).parent.parent / "viz" / "scores.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(all_results, indent=2))
    print(f"\nWrote {out}")
