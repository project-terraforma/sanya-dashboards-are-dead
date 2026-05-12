import os
from pathlib import Path
from pyswip import Prolog

BASE_DIR = Path(__file__).resolve().parent
PL_FILE = BASE_DIR / "checker1.pl"

prolog = Prolog()
prolog.consult(str(PL_FILE))


def ask(query):
    return bool(list(prolog.query(query)))


def get_results(query):
    return list(prolog.query(query))


def clean(value):
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


question_checks = [
    ("q1_columns", "Which columns exist?"),
    ("q2_rows", "How many total rows exist?"),
    ("q3_metric_columns", "Which metric columns are present?"),
    ("q4_postal_city", "Does the dataset contain postal city information?"),
    ("q5_missing_data", "Why is some data missing?"),
]

print("\n=== CONTEXT FILE RELIABILITY CHECK ===\n")
statuses = {}
for qid, question in question_checks:
    if ask(f"supported(file1, {qid})"):
        status = "SUPPORTED"
    elif ask(f"risky(file1, {qid})"):
        status = "RISKY"
    elif ask(f"unsupported(file1, {qid})"):
        status = "UNSUPPORTED"
    else:
        status = "UNKNOWN"
    statuses[qid] = status
    print(f"[{status}] {question}")

print("\n=== ARTIFACT VS CONTEXT GAPS ===\n")
gaps = get_results("context_gap(file1, GapType, Item, Explanation)")
if gaps:
    seen = set()
    for item in gaps:
        key = (clean(item["GapType"]), clean(item["Item"]), clean(item["Explanation"]))
        if key in seen:
            continue
        seen.add(key)
        print(f"[CONTEXT GAP] {key[0]} :: {key[1]}")
        print(f"  {key[2]}\n")
else:
    print("No major artifact-vs-context gaps found.")

print("\n=== PROMPT WARNINGS ===\n")
warnings = get_results("prompt_warning(file1, Category, Warning)")
seen = set()
if warnings:
    for item in warnings:
        key = (clean(item["Category"]), clean(item["Warning"]))
        if key in seen:
            continue
        seen.add(key)
        print(f"{key[0]}: {key[1]}")
else:
    print("No warnings found.")

print("\n=== SAFER REWRITTEN PROMPTS ===\n")
fixes = get_results("prompt_fix(QID, Fix)")
for item in fixes:
    print(f"{clean(item['QID'])}: {clean(item['Fix'])}")

print("\n=== PINPOINTED CONTEXT FILE EVIDENCE ===\n")
pinpoints = get_results("evidence(file1, context_pinpoint, Term, Evidence)")
if pinpoints:
    for item in pinpoints:
        print(f"{clean(item['Term'])}: {clean(item['Evidence'])}")
else:
    print("No context-file pinpoint evidence found.")

print("\n=== ARTIFACT EVIDENCE USED AS GROUND TRUTH ===\n")
artifact_evidence = get_results("evidence(file1, artifact, Category, Evidence)")
seen = set()
for item in artifact_evidence:
    evidence = clean(item["Evidence"])
    if evidence in seen:
        continue
    seen.add(evidence)
    print(evidence)

print("\n=== RELIABILITY SCORE ===\n")
score = 100
deductions = []
for qid, status in statuses.items():
    if status == "RISKY":
        score -= 15
        deductions.append((qid, status, -15))
    elif status == "UNSUPPORTED":
        score -= 25
        deductions.append((qid, status, -25))
    elif status == "UNKNOWN":
        score -= 20
        deductions.append((qid, status, -20))

# Extra penalty for every artifact-vs-context gap beyond the first two, capped.
extra_gap_penalty = max(0, min(10, (len(gaps) - 2) * 2)) if gaps else 0
if extra_gap_penalty:
    score -= extra_gap_penalty
    deductions.append(("artifact_vs_context_gaps", "GAPS", -extra_gap_penalty))

print(f"Reliability Score: {score}/100")
print("\nScore deductions:")
if deductions:
    for qid, status, points in deductions:
        print(f"{points} points: {qid} was marked {status}")
else:
    print("No deductions.")

print("\n=== SUMMARY ===")
if score >= 80:
    print("The context file is mostly useful, but warnings should still be included for risky prompts.")
elif score >= 50:
    print("The context file is usable, but it misses important grounding/warnings. Prompts should be rewritten before using it with an LLM.")
else:
    print("The context file is weak for prompting. It needs more complete grounding before relying on it.")
