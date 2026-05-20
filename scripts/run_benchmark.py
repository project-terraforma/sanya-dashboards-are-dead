"""
Test runner: feeds the artifact + each benchmark question to Claude and ChatGPT,
saves the raw responses to results/ for later scoring by the judge script.

Usage:
    python scripts/run_benchmark.py
    python scripts/run_benchmark.py --llm claude
    python scripts/run_benchmark.py --llm gemini
    python scripts/run_benchmark.py --llm openai
    python scripts/run_benchmark.py --llm all
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from anthropic import Anthropic
import google.generativeai as genai
from openai import OpenAI

REPO_ROOT = Path(__file__).parent.parent
ARTIFACT_PATH = REPO_ROOT / "artifact" / "artifact_abby_v1.txt"
BENCHMARK_PATH = REPO_ROOT / "questions" / "bench_abby_v1.json"
PROMPT_PATH = REPO_ROOT / "prompts" / "prompts_abby_v1.txt"
RESULTS_DIR = REPO_ROOT / "results"

CLAUDE_MODEL = "claude-opus-4-7"
GEMINI_MODEL = "gemini-2.5-flash"
OPENAI_MODEL = "gpt-4o"


def build_system_prompt(prompt_instructions: str, artifact: str) -> str:
    """
    TODO (abby): decide how to assemble the system prompt.

    Currently this returns: instructions + a separator + the artifact.

    Trade-offs to consider:
    - Instructions BEFORE the artifact: model reads rules first, then sees data.
      Tends to make models more cautious and rule-following.
    - Instructions AFTER the artifact: model reads data, then sees rules.
      Some research suggests rules at the end are followed more strictly.
    - Combined into one block vs. separated with clear markers like
      "=== INSTRUCTIONS ===" and "=== DATA ===" -- markers can help the model
      treat them as distinct sections.

    This decision directly affects OKR 2 (which prompt template works best).
    Pick a default for v1 and document why. Swap and re-run later to compare.
    """
    return f"{prompt_instructions}\n\n---\n\n{artifact}"


def ask_claude(client: Anthropic, system_prompt: str, question: str) -> str:
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text


def ask_gemini_sysinstr(system_prompt: str, question: str) -> str:
    """
    TODO (abby): Variant A -- pass the artifact rules as Gemini's system_instruction.

    Hint (3 lines):
        model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompt)
        response = model.generate_content(question)
        return response.text

    This treats the rules as persistent guidance, the way Anthropic's `system=`
    parameter works. We're measuring whether this lowers hallucination rate vs.
    the inline variant below.
    """
    model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompt)
    response = model.generate_content(question)
    return response.text


def ask_gemini_inline(system_prompt: str, question: str) -> str:
    """
    TODO (abby): Variant B -- prepend the artifact rules to the user question.

    Hint (3 lines):
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(f"{system_prompt}\n\n---\n\n{question}")
        return response.text

    This treats the rules as just more user content. We're measuring whether
    this raises hallucination rate vs. the system_instruction variant above.
    """
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(f"{system_prompt}\n\n---\n\n{question}")
    return response.text


def ask_gemini(system_prompt: str, question: str) -> dict:
    """Run both variants per question so we can A/B their hallucination rates."""
    return {
        "sysinstr": ask_gemini_sysinstr(system_prompt, question),
        "inline": ask_gemini_inline(system_prompt, question),
    }


def ask_openai(client: OpenAI, system_prompt: str, question: str) -> str:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


def run_benchmark(llm: str):
    load_dotenv(REPO_ROOT / ".env")

    artifact = ARTIFACT_PATH.read_text()
    prompt_instructions = PROMPT_PATH.read_text()
    benchmark = json.loads(BENCHMARK_PATH.read_text())
    system_prompt = build_system_prompt(prompt_instructions, artifact)

    if llm == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            sys.exit("ANTHROPIC_API_KEY not found in .env")
        client = Anthropic(api_key=api_key)
        ask_fn = lambda q: ask_claude(client, system_prompt, q)
    elif llm == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            sys.exit("GEMINI_API_KEY not found in .env")
        genai.configure(api_key=api_key)
        ask_fn = lambda q: ask_gemini(system_prompt, q)
    elif llm == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            sys.exit("OPENAI_API_KEY not found in .env")
        client = OpenAI(api_key=api_key)
        ask_fn = lambda q: ask_openai(client, system_prompt, q)
    else:
        sys.exit(f"Unknown llm: {llm}. Use 'claude', 'gemini', or 'openai'.")

    results = []
    for q in benchmark["questions"]:
        if q.get("deferred"):
            print(f"  [skip] {q['id']} (deferred)")
            continue
        print(f"  [ask]  {q['id']} ({q['category']})")
        try:
            answer = ask_fn(q["question"])
            row = {
                "id": q["id"],
                "category": q["category"],
                "scored": q.get("scored", True),
                "question": q["question"],
                "expected_behavior": q["expected_behavior"],
                "expected_answer": q["expected_answer"],
                "scoring_rubric": q["scoring_rubric"],
            }
            if isinstance(answer, dict):
                row["actual_answer_sysinstr"] = answer["sysinstr"]
                row["actual_answer_inline"] = answer["inline"]
            else:
                row["actual_answer"] = answer
            results.append(row)
        except Exception as e:
            print(f"  [err]  {q['id']}: {e}")
            results.append({
                "id": q["id"],
                "error": str(e),
            })

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = RESULTS_DIR / llm
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"run_{timestamp}.json"
    model_name = {"claude": CLAUDE_MODEL, "gemini": GEMINI_MODEL, "openai": OPENAI_MODEL}[llm]
    out_path.write_text(json.dumps({
        "llm": llm,
        "model": model_name,
        "timestamp": timestamp,
        "artifact_path": str(ARTIFACT_PATH.relative_to(REPO_ROOT)),
        "benchmark_path": str(BENCHMARK_PATH.relative_to(REPO_ROOT)),
        "results": results,
    }, indent=2))
    print(f"\nSaved: {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", choices=["claude", "gemini", "openai", "all"], default="all")
    args = parser.parse_args()

    if args.llm in ("claude", "all"):
        print("=== Running Claude ===")
        run_benchmark("claude")
    if args.llm in ("gemini", "all"):
        print("\n=== Running Gemini ===")
        run_benchmark("gemini")
    if args.llm in ("openai", "all"):
        print("\n=== Running OpenAI ===")
        run_benchmark("openai")
