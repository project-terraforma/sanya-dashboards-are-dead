import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONTEXT_FILE = BASE_DIR / "context-files" / "README_generation_output.txt"
# ARTIFACT_FILE = BASE_DIR / "data_artifact.json" 
PROLOG_FILE = BASE_DIR / "checker1.pl"

METRIC_COLUMNS = [
    "average_geometry_length_km",
    "total_geometry_length_km",
    "average_geometry_area_km2",
    "total_geometry_area_km2",
]

QUESTIONS = [
    ("q1_columns", "Which columns exist?"),
    ("q2_rows", "How many total rows exist?"),
    ("q3_metric_columns", "Which metric columns are present?"),
    ("q4_postal_city", "Does the dataset contain postal city information?"),
    ("q5_missing_data", "Why is some data missing?"),
]


def prolog_atom(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_]", "_", text)
    if text and text[0].isdigit():
        text = "n_" + text
    return text or "unknown"


def prolog_string(text: str) -> str:
    return str(text).replace("\\", "\\\\").replace('"', '\\"')


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Could not find context file: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def load_artifact(path: Path) -> dict | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def line_hits(text: str, term: str):
    hits = []
    for i, line in enumerate(text.splitlines(), start=1):
        if term.lower() in line.lower():
            hits.append((i, line.strip()))
    return hits


def context_mentions(text: str, *terms: str) -> bool:
    low = text.lower()
    return any(t.lower() in low for t in terms)


def context_has_warning_for_fully_missing(text: str, col: str) -> bool:
    # Strong enough evidence that the past context warns the column is unusable.
    low = text.lower()
    col_low = col.lower()
    warning_words = ["100% missing", "fully missing", "all missing", "no usable values", "unusable"]
    return col_low in low and any(w in low for w in warning_words)


def build_prolog(context_text: str, artifact: dict | None) -> str:
    facts = [
        ":- discontiguous has_section/2.",
        ":- discontiguous context_mentions/2.",
        ":- discontiguous artifact_has_column/2.",
        ":- discontiguous artifact_missing_count/3.",
        ":- discontiguous artifact_total_rows/2.",
        ":- discontiguous context_gap/4.",
        ":- discontiguous issue/3.",
        ":- discontiguous evidence/4.",
        "",
        "% Facts derived from the past team's context file",
    ]

    sections = {
        "instructions": "<<<INSTRUCTIONS_START>>>",
        "schema": "<<<SCHEMA_START>>>",
        "prompts": "<<<PROMPTS_START>>>",
        "theme_statistics": "## THEME STATISTICS",
    }
    for section, marker in sections.items():
        hits = line_hits(context_text, marker)
        if hits:
            facts.append(f"has_section(file1, {section}).")
            for ln, text in hits[:5]:
                facts.append(f'evidence(file1, context_section, "{section}", "Context line {ln}: {prolog_string(text)}").')

    terms_to_track = [
        "Total Features", "SCHEMA REFERENCE", "Coverage varies significantly", "missing", "missing values",
        "average_geometry_length_km", "total_geometry_length_km", "average_geometry_area_km2",
        "total_geometry_area_km2", "postal_city_count", "address_level_1", "address_level_2", "address_level_3",
    ]
    for term in terms_to_track:
        hits = line_hits(context_text, term)
        if hits:
            atom = prolog_atom(term)
            facts.append(f"context_mentions(file1, {atom}).")
            for ln, text in hits[:8]:
                facts.append(f'evidence(file1, context_pinpoint, "{prolog_string(term)}", "Context line {ln}: {prolog_string(text)}").')

    facts.append("")
    facts.append("% Optional facts derived from artifact JSON ground truth")
    if artifact is None:
        facts.append('% Artifact file not found. Artifact-vs-context gap checks are disabled.')
    else:
        total_rows = int(artifact.get("total_rows", 0))
        facts.append(f"artifact_total_rows(file1, {total_rows}).")
        facts.append(f'evidence(file1, artifact, "total_rows", "Artifact: total_rows = {total_rows}").')
        for col in artifact.get("columns", []):
            atom = prolog_atom(col)
            facts.append(f"artifact_has_column(file1, {atom}).")
            facts.append(f'evidence(file1, artifact, "column", "Artifact column exists: {prolog_string(col)}").')
        for col, missing in artifact.get("missing_values", {}).items():
            atom = prolog_atom(col)
            missing = int(missing)
            facts.append(f"artifact_missing_count(file1, {atom}, {missing}).")
            facts.append(f'evidence(file1, artifact, "missing_values", "Artifact missing_values.{prolog_string(col)} = {missing}").')

        # Context gaps: artifact says something important, context does not ground/warn it.
        for col in METRIC_COLUMNS:
            missing = int(artifact.get("missing_values", {}).get(col, -1))
            if col in artifact.get("columns", []) and total_rows and missing == total_rows:
                if not context_has_warning_for_fully_missing(context_text, col):
                    facts.append(
                        f'context_gap(file1, metric_column_warning_missing, "{prolog_string(col)}", "Artifact says {prolog_string(col)} is 100% missing ({missing}/{total_rows}), but the context file does not clearly warn that this column is unusable.").'
                    )
                    facts.append(
                        f'issue(file1, metric_column_unusable, "{prolog_string(col)} exists in the artifact but is 100% missing ({missing}/{total_rows}).").'
                    )

        if "postal_city_count" in artifact.get("columns", []):
            missing = int(artifact.get("missing_values", {}).get("postal_city_count", -1))
            if not context_mentions(context_text, "postal_city_count"):
                facts.append(
                    f'context_gap(file1, postal_city_missing_from_context, "postal_city_count", "Artifact says postal_city_count exists with {missing} missing values, but the context file does not mention postal_city_count.").'
                )

        # The context has broad coverage warning, but not exact missing-value cause for this CSV artifact.
        if "missing_values" in artifact:
            if not context_mentions(context_text, "missing_values", "missing values"):
                facts.append(
                    'context_gap(file1, missing_values_section_missing, "missing_values", "Artifact contains missing-value counts, but the context file does not include a clear missing_values section.").'
                )
            facts.append(
                'issue(file1, missing_reason_not_explained, "Artifact gives missing-value counts, but neither artifact nor context clearly explains the real-world cause of each missing value.").'
            )

    rules = r'''

% ── QUESTION SUPPORT RULES ──────────────────────────────────────────────────
% supported = safe to ask from context/artifact
% risky = ask only with warning / rewritten prompt
% unsupported = not enough grounding

supported(file1, q1_columns) :-
    has_section(file1, schema).

supported(file1, q2_rows) :-
    context_mentions(file1, Total_Features).

risky(file1, q3_metric_columns) :-
    context_gap(file1, metric_column_warning_missing, _, _).

supported(file1, q3_metric_columns) :-
    \+ context_gap(file1, metric_column_warning_missing, _, _),
    artifact_has_column(file1, average_geometry_length_km),
    artifact_has_column(file1, total_geometry_length_km),
    artifact_has_column(file1, average_geometry_area_km2),
    artifact_has_column(file1, total_geometry_area_km2).

supported(file1, q4_postal_city) :-
    artifact_has_column(file1, postal_city_count),
    artifact_missing_count(file1, postal_city_count, 0).

risky(file1, q4_postal_city) :-
    context_gap(file1, postal_city_missing_from_context, _, _).

risky(file1, q5_missing_data) :-
    issue(file1, missing_reason_not_explained, _).

unsupported(file1, q5_missing_data) :-
    \+ artifact_missing_count(file1, _, _).

prompt_warning(file1, geometry_metrics, Warning) :-
    context_gap(file1, metric_column_warning_missing, _, Warning).

prompt_warning(file1, missing_data, Warning) :-
    issue(file1, missing_reason_not_explained, Warning).

prompt_fix(q3_metric_columns, "Instead of asking only which metric columns are present, ask: Which metric columns are present, and which are unusable because all values are missing?").
prompt_fix(q5_missing_data, "Instead of asking why data is missing, ask: Which columns have missing values? Do not guess causes unless the context gives a reason.").
'''
    return "\n".join(facts) + rules


def main() -> None:
    context_text = load_text(CONTEXT_FILE)
    artifact = load_artifact(ARTIFACT_FILE)
    PROLOG_FILE.write_text(build_prolog(context_text, artifact), encoding="utf-8")
    print(f"Created {PROLOG_FILE}")
    print(f"Context file: {CONTEXT_FILE.name}")
    if artifact:
        print(f"Artifact file: {ARTIFACT_FILE.name} (used as optional ground truth)")
    else:
        print("Artifact file not found; only context scanning was used.")


if __name__ == "__main__":
    main()
