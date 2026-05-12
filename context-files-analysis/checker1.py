import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONTEXT_DIR = BASE_DIR / "context-files"
FACTS_FILE = BASE_DIR / "generated_facts.pl"

SECTION_KEYWORDS = {
    "instructions": [
        "role", "rules", "constraint", "only use", "do not infer",
        "do not guess", "answer", "reference"
    ],
    "schema": [
        "schema", "column", "columns", "field", "fields",
        "attribute", "attributes", "definition", "definitions", "type"
    ],
    "statistics": [
        "statistics", "total", "records", "features",
        "count", "counts", "percentage", "percent"
    ],
    "coverage": [
        "coverage", "country", "countries", "geographic",
        "source", "sources", "theme", "themes", "availability"
    ],
    "version": [
        "release", "version", "generated", "date", "month"
    ],
    "examples": [
        "example", "examples", "prompt", "prompts",
        "query", "queries", "user:"
    ],
    "unsupported_guidance": [
        "cannot answer", "not stated", "unavailable",
        "do not guess", "do not infer", "not provided",
        "not enough information"
    ],
}

TERMS_TO_TRACK = sorted({
    keyword
    for keywords in SECTION_KEYWORDS.values()
    for keyword in keywords
})


def prolog_atom(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_]", "_", text.strip().lower())
    if text and text[0].isdigit():
        text = "n_" + text
    return text or "unknown"


def prolog_string(text: str) -> str:
    return str(text).replace("\\", "\\\\").replace('"', '\\"')


def line_hits(text: str, term: str):
    hits = []
    for i, line in enumerate(text.splitlines(), start=1):
        if term.lower() in line.lower():
            hits.append((i, line.strip()))
    return hits


def context_mentions(text: str, *terms: str) -> bool:
    low = text.lower()
    return any(term.lower() in low for term in terms)


def detect_sections(text: str) -> dict[str, list[str]]:
    low = text.lower()
    detected = {}

    for section, keywords in SECTION_KEYWORDS.items():
        hits = [keyword for keyword in keywords if keyword in low]
        detected[section] = hits

    return detected


def add_issue(facts, file_id, issue_type, rubric, risk, fix):
    facts.append(
        f'issue({file_id}, {issue_type}, "{prolog_string(rubric)}", '
        f'"{prolog_string(risk)}", "{prolog_string(fix)}").'
    )


def build_facts_for_file(file_id: str, path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")

    facts = [
        "",
        f"% Facts for {path.name}",
        f"context_file({file_id}).",
        f'file_name({file_id}, "{prolog_string(path.name)}").',
    ]

    detected_sections = detect_sections(text)

    for section, hits in detected_sections.items():
        if len(hits) >= 2:
            facts.append(f"has_section({file_id}, {section}).")
            facts.append(
                f'evidence({file_id}, context_section, "{section}", '
                f'"Detected keywords: {prolog_string(", ".join(hits))}").'
            )

    for term in TERMS_TO_TRACK:
        hits = line_hits(text, term)

        if hits:
            atom = prolog_atom(term)
            facts.append(f"context_mentions({file_id}, {atom}).")

            for ln, line in hits[:5]:
                facts.append(
                    f'evidence({file_id}, context_pinpoint, "{prolog_string(term)}", '
                    f'"{path.name} line {ln}: {prolog_string(line)}").'
                )

    if "missing" not in detected_sections or len(detected_sections["unsupported_guidance"]) < 2:
        pass

    if not context_mentions(text, "missing", "missing values", "missingness", "null", "incomplete"):
        add_issue(
            facts,
            file_id,
            "missing_data_guidance_weak",
            "Missing Data Documentation",
            "The file does not clearly explain missing or incomplete data, so the LLM may invent causes.",
            "Ask the LLM to only state missing-data warnings that are explicitly in the file.",
        )

    if not context_mentions(text, "coverage", "geographic", "country", "source", "availability"):
        add_issue(
            facts,
            file_id,
            "coverage_guidance_weak",
            "Coverage Limitations",
            "The file may not clearly explain geographic, source, or theme limits, so the LLM may overgeneralize.",
            "Ask the LLM to identify file-stated limits before making conclusions.",
        )

    if not context_mentions(text, "release", "version", "generated", "date", "month"):
        add_issue(
            facts,
            file_id,
            "versioning_weak",
            "Versioning",
            "The file may not clearly ground answers in a specific data release or date.",
            "Ask the LLM to state the file's release, version, or date before answering.",
        )

    if not context_mentions(text, "prompt", "example", "query", "user:"):
        add_issue(
            facts,
            file_id,
            "example_prompts_missing",
            "Example Questions",
            "The file may not show how to ask grounded questions, so prompts may be too broad.",
            "Write prompts that explicitly say: use only this context file.",
        )

    if not context_mentions(
        text,
        "cannot answer",
        "not stated",
        "unavailable",
        "do not guess",
        "do not infer",
        "not provided",
        "not enough information",
    ):
        add_issue(
            facts,
            file_id,
            "unsupported_questions_not_explained",
            "Unsupported Questions",
            "The file may not clearly say what the LLM should avoid answering.",
            "Tell the LLM to say 'not stated in the context file' when the file does not provide the answer.",
        )

    return facts


def main():
    if not CONTEXT_DIR.exists():
        raise FileNotFoundError(f"Could not find context-files folder: {CONTEXT_DIR}")

    files = sorted(
        list(CONTEXT_DIR.glob("*.txt"))
        + list(CONTEXT_DIR.glob("*.md"))
        + list(CONTEXT_DIR.glob("*.markdown"))
    )

    if not files:
        raise FileNotFoundError(f"No .txt, .md, or .markdown files found in {CONTEXT_DIR}")

    facts = [
        ":- discontiguous context_file/1.",
        ":- discontiguous file_name/2.",
        ":- discontiguous has_section/2.",
        ":- discontiguous context_mentions/2.",
        ":- discontiguous issue/5.",
        ":- discontiguous evidence/4.",
        "",
        "% AUTO-GENERATED FACTS ONLY.",
        "% Do not edit this file by hand.",
        "% Edit checker1.py or checker1.pl instead.",
    ]

    for i, path in enumerate(files, start=1):
        facts.extend(build_facts_for_file(f"file{i}", path))

    FACTS_FILE.write_text("\n".join(facts), encoding="utf-8")

    print(f"Created {FACTS_FILE}")
    print(f"Scanned {len(files)} context file(s).")
    print("No artifact file was used.")


if __name__ == "__main__":
    main()