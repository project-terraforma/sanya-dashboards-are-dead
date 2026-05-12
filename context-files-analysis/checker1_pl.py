from pathlib import Path
from pyswip import Prolog

BASE_DIR = Path(__file__).resolve().parent
CONTEXT_DIR = BASE_DIR / "context-files"
PL_FILE = BASE_DIR / "checker1.pl"

SECTION_KEYWORDS = {
    "instructions": [
        "role", "rules", "constraint", "constraints", "only use", "do not infer",
        "do not guess", "answer", "reference"
    ],
    "schema": [
        "schema", "column", "columns", "field", "fields", "attribute", "attributes",
        "definition", "definitions", "type", "dataset structure"
    ],
    "statistics": [
        "statistics", "total", "records", "features", "count", "counts",
        "percentage", "percent", "top values", "distribution"
    ],
    "coverage": [
        "coverage", "country", "countries", "geographic", "source", "sources",
        "theme", "themes", "availability", "varies"
    ],
    "missing_data": [
        "missing", "missing values", "missingness", "null", "incomplete", "unavailable"
    ],
    "version": [
        "release", "version", "generated", "date", "month"
    ],
    "examples": [
        "example", "examples", "prompt", "prompts", "query", "queries", "user:"
    ],
    "unsupported_guidance": [
        "cannot answer", "not stated", "unavailable", "do not guess", "do not infer",
        "not provided", "not enough information", "only use information contained"
    ],
}

QUESTION_CHECKS = [
    ("q1_schema", "What schema/column/field information does the context file provide?"),
    ("q2_statistics", "What dataset statistics does the context file provide?"),
    ("q3_coverage", "What coverage limitations should I mention?"),
    ("q4_missing_data", "What does the context file say about missing or incomplete data?"),
    ("q5_version", "Which release/version/date is this based on?"),
    ("q6_prompt_examples", "Does the file include prompt examples or usage guidance?"),
    ("q7_unsupported", "What should I avoid asking the LLM based only on this file?"),
]


def clean(value) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def prolog_string(text: str) -> str:
    return str(text).replace("\\", "\\\\").replace('"', '\\"')


def prolog_atom(text: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in text.strip())
    while "__" in safe:
        safe = safe.replace("__", "_")
    safe = safe.strip("_")
    if not safe:
        return "unknown"
    if safe[0].isdigit():
        safe = "n_" + safe
    return safe


def query(prolog: Prolog, q: str, maxresult=None):
    if maxresult is None:
        return list(prolog.query(q))
    return list(prolog.query(q, maxresult=maxresult))


def ask(prolog: Prolog, q: str) -> bool:
    return bool(query(prolog, q, maxresult=1))


def find_context_files() -> list[Path]:
    if not CONTEXT_DIR.exists():
        raise FileNotFoundError(f"Could not find folder: {CONTEXT_DIR}")

    files = sorted(
        list(CONTEXT_DIR.glob("*.txt"))
        + list(CONTEXT_DIR.glob("*.md"))
        + list(CONTEXT_DIR.glob("*.markdown"))
    )

    if not files:
        raise FileNotFoundError(f"No .txt, .md, or .markdown files found in: {CONTEXT_DIR}")

    return files


def keyword_hits(text: str, keywords: list[str]) -> list[str]:
    lower = text.lower()
    return [keyword for keyword in keywords if keyword.lower() in lower]


def line_hits(text: str, term: str, max_hits: int = 3) -> list[str]:
    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if term.lower() in line.lower():
            hits.append(f"line {line_no}: {line.strip()}")
        if len(hits) >= max_hits:
            break
    return hits


def assert_fact(prolog: Prolog, fact: str) -> None:
    query(prolog, f"assertz(({fact}))", maxresult=1)


def add_issue(prolog: Prolog, file_id: str, issue: str, rubric: str, risk: str, fix: str) -> None:
    assert_fact(
        prolog,
        f'issue({file_id}, {issue}, "{prolog_string(rubric)}", "{prolog_string(risk)}", "{prolog_string(fix)}")'
    )


def load_file_facts(prolog: Prolog, file_id: str, path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")

    assert_fact(prolog, f"context_file({file_id})")
    assert_fact(prolog, f'file_name({file_id}, "{prolog_string(path.name)}")')

    for section, keywords in SECTION_KEYWORDS.items():
        hits = keyword_hits(text, keywords)

        # Two hits means the section is strongly present. One hit is too weak for broad keywords.
        if len(hits) >= 2:
            assert_fact(prolog, f"has_section({file_id}, {section})")
            assert_fact(
                prolog,
                f'evidence({file_id}, context_section, "{section}", "Detected keywords: {prolog_string(", ".join(hits))}")'
            )

            for keyword in hits[:3]:
                for evidence_line in line_hits(text, keyword, max_hits=2):
                    assert_fact(
                        prolog,
                        f'evidence({file_id}, context_pinpoint, "{prolog_string(keyword)}", "{prolog_string(evidence_line)}")'
                    )

    if not query(prolog, f"has_section({file_id}, missing_data)", maxresult=1):
        add_issue(
            prolog,
            file_id,
            "missing_data_guidance_weak",
            "Missing Data Documentation",
            "The file does not clearly explain missing or incomplete data, so the LLM may invent causes.",
            "Ask the LLM to only state missing-data warnings that are explicitly in the file.",
        )

    if not query(prolog, f"has_section({file_id}, coverage)", maxresult=1):
        add_issue(
            prolog,
            file_id,
            "coverage_guidance_weak",
            "Coverage Limitations",
            "The file may not clearly explain geographic, source, or theme limits, so the LLM may overgeneralize.",
            "Ask the LLM to identify file-stated limits before making conclusions.",
        )

    if not query(prolog, f"has_section({file_id}, version)", maxresult=1):
        add_issue(
            prolog,
            file_id,
            "versioning_weak",
            "Versioning",
            "The file may not clearly ground answers in a specific data release or date.",
            "Ask the LLM to state the file's release, version, or date before answering.",
        )

    if not query(prolog, f"has_section({file_id}, examples)", maxresult=1):
        add_issue(
            prolog,
            file_id,
            "example_prompts_missing",
            "Example Questions",
            "The file may not show how to ask grounded questions, so prompts may be too broad.",
            "Write prompts that explicitly say: use only this context file.",
        )

    if not query(prolog, f"has_section({file_id}, unsupported_guidance)", maxresult=1):
        add_issue(
            prolog,
            file_id,
            "unsupported_questions_not_explained",
            "Unsupported Questions",
            "The file may not clearly say what the LLM should avoid answering.",
            "Tell the LLM to say 'not stated in the context file' when the file does not provide the answer.",
        )


def main() -> None:
    prolog = Prolog()
    prolog.consult(str(PL_FILE))

    files = find_context_files()

    for index, path in enumerate(files, start=1):
        load_file_facts(prolog, f"file{index}", path)

    print("\n=== PROJECT ===\n")
    goals = query(prolog, "project_goal(Goal)", maxresult=1)
    if goals:
        print(clean(goals[0]["Goal"]))

    print("\n=== FILES FOUND ===\n")
    file_results = query(prolog, "context_file(File)")
    for item in file_results:
        file_id = clean(item["File"])
        names = query(prolog, f"file_name({file_id}, Name)", maxresult=1)
        name = clean(names[0]["Name"]) if names else file_id
        print(f"{file_id}: {name}")

    for item in file_results:
        file_id = clean(item["File"])
        names = query(prolog, f"file_name({file_id}, Name)", maxresult=1)
        name = clean(names[0]["Name"]) if names else file_id

        print("\n\n==============================")
        print(f"REPORT FOR {name}")
        print("==============================")

        print("\n=== PROMPT RELIABILITY CHECK ===\n")
        statuses = {}

        for qid, question in QUESTION_CHECKS:
            if ask(prolog, f"supported({file_id}, {qid})"):
                status = "SUPPORTED"
            elif ask(prolog, f"risky({file_id}, {qid})"):
                status = "RISKY"
            elif ask(prolog, f"unsupported({file_id}, {qid})"):
                status = "UNSUPPORTED"
            else:
                status = "UNKNOWN"

            statuses[qid] = status
            print(f"[{status}] {question}")

        print("\n=== RUBRIC-BASED PROMPT RISKS ===\n")
        issues = query(prolog, f"issue({file_id}, Issue, Rubric, Risk, Fix)")

        if issues:
            seen = set()
            for issue in issues:
                key = (
                    clean(issue["Issue"]),
                    clean(issue["Rubric"]),
                    clean(issue["Risk"]),
                    clean(issue["Fix"]),
                )
                if key in seen:
                    continue
                seen.add(key)
                print(f"Issue: {key[0]}")
                print(f"Rubric category: {key[1]}")
                print(f"Hallucination risk: {key[2]}")
                print(f"Suggested fix: {key[3]}\n")
        else:
            print("No major prompt risks were detected.")

        print("\n=== SAFER REWRITTEN PROMPTS ===\n")
        for qid, _ in QUESTION_CHECKS:
            fixes = query(prolog, f"prompt_fix({qid}, Fix)", maxresult=1)
            if fixes:
                print(f"{qid}: {clean(fixes[0]['Fix'])}")

        print("\n=== PINPOINTED CONTEXT FILE EVIDENCE ===\n")
        evidence_rows = query(prolog, f"evidence({file_id}, context_pinpoint, Term, Evidence)")
        if evidence_rows:
            seen = set()
            for row in evidence_rows[:30]:
                key = (clean(row["Term"]), clean(row["Evidence"]))
                if key in seen:
                    continue
                seen.add(key)
                print(f"{key[0]}: {key[1]}")
        else:
            print("No pinpointed context evidence found.")

        print("\n=== PROMPT READINESS SCORE ===\n")
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
        print(f"Prompt Readiness Score: {score}/100")

        print("\nScore deductions:")
        if deductions:
            for qid, status, points in deductions:
                print(f"{points} points: {qid} was marked {status}")
        else:
            print("No deductions.")

        print("\n=== SUMMARY ===")
        if score >= 80:
            print("This context file is a strong prompt reference. Still include source limits.")
        elif score >= 50:
            print("This context file is usable, but prompts need guardrails.")
        else:
            print("This context file is weak alone. Use narrow prompts and require 'not stated in the context file'.")


if __name__ == "__main__":
    main()
