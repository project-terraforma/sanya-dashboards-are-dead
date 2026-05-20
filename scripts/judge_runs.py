"""
LLM-as-judge: scores the latest run from each LLM in results/ using GPT-4o.

Reads the newest run_*.json from results/{claude,gemini,openai}/, asks GPT-4o
to grade each answer for (a) correctness vs. expected behavior+answer and
(b) whether it hallucinated facts not in the artifact. Writes scored copies
to results/scored/ with the same per-LLM folder layout.

Gemini results have two variants per question (sysinstr + inline). Both get
graded independently so the A/B comparison can be visualized.

Usage:
    python scripts/judge_runs.py
"""

import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

REPO_ROOT = Path(__file__).parent.parent
RESULTS_DIR = REPO_ROOT / "results"
SCORED_DIR = RESULTS_DIR / "scored"
ARTIFACT_PATH = REPO_ROOT / "artifact" / "artifact_abby_v1.txt"

JUDGE_MODEL = "gpt-4o"

JUDGE_SYSTEM = """You are an evaluation judge for an LLM benchmark. For each
item you receive: a question, the expected behavior, the expected answer, a
scoring rubric, the source artifact the model was given, and the model's
actual answer.

Return ONLY a JSON object with these exact keys:
  "correct":      1 if the actual_answer satisfies the expected_behavior AND
                  scoring_rubric, else 0.
  "hallucinated": 1 if the actual_answer asserts any fact not supported by
                  the artifact (made-up numbers, fabricated categories,
                  invented dates, etc.), else 0.
  "reason":       one short sentence explaining the scores.

A refusal counts as correct when the expected_behavior asks for refusal.
A confident answer to a refusal question counts as incorrect AND usually
hallucinated. Be strict: partial answers that include fabricated detail
should be marked hallucinated even if the gist is right."""


def latest_run(llm_dir: Path) -> Path | None:
    runs = sorted(llm_dir.glob("run_*.json"))
    return runs[-1] if runs else None


def judge_one(client: OpenAI, artifact: str, row: dict, answer: str) -> dict:
    user_msg = json.dumps({
        "question": row["question"],
        "expected_behavior": row["expected_behavior"],
        "expected_answer": row["expected_answer"],
        "scoring_rubric": row["scoring_rubric"],
        "artifact": artifact,
        "actual_answer": answer,
    }, indent=2)
    delay = 2
    for attempt in range(6):
        try:
            response = client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[
                    {"role": "system", "content": JUDGE_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except RateLimitError:
            print(f"    [rate-limited] sleeping {delay}s (attempt {attempt + 1}/6)")
            time.sleep(delay)
            delay = min(delay * 2, 30)
    raise RuntimeError("judge_one: exceeded retry budget on rate limits")


def score_run(client: OpenAI, artifact: str, run_path: Path) -> dict:
    run = json.loads(run_path.read_text())
    print(f"\n=== Judging {run['llm']} ({run_path.name}) ===")
    for row in run["results"]:
        if "error" in row:
            print(f"  [skip] {row['id']} (run errored)")
            continue
        if not row.get("scored", True):
            print(f"  [skip] {row['id']} (unscored question)")
            continue

        if "actual_answer" in row:
            print(f"  [judge] {row['id']}")
            row["score"] = judge_one(client, artifact, row, row["actual_answer"])
        else:
            print(f"  [judge] {row['id']} (sysinstr + inline)")
            row["score_sysinstr"] = judge_one(client, artifact, row, row["actual_answer_sysinstr"])
            row["score_inline"] = judge_one(client, artifact, row, row["actual_answer_inline"])
    return run


def main():
    load_dotenv(REPO_ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("OPENAI_API_KEY not found in .env")
    client = OpenAI(api_key=api_key)
    artifact = ARTIFACT_PATH.read_text()

    SCORED_DIR.mkdir(exist_ok=True)
    for llm in ("claude", "gemini", "openai"):
        run_path = latest_run(RESULTS_DIR / llm)
        if not run_path:
            print(f"[warn] no runs in results/{llm}/, skipping")
            continue
        scored = score_run(client, artifact, run_path)
        out_dir = SCORED_DIR / llm
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / run_path.name
        out_path.write_text(json.dumps(scored, indent=2))
        print(f"Saved: {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
