"""Modal app exposing /api/chat for the GitHub Pages frontend.

Deploy:
    modal secret create overture-openai OPENAI_API_KEY=sk-...
    modal deploy backend/modal_app.py

The deployed URL is printed at the end of `modal deploy`. Set it as the
`VITE_API_URL` repo secret on GitHub so the Pages build picks it up.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parent.parent
CONTEXT_FILE = ROOT / "context-files-analysis" / "context-files" / "context_perfect.txt"
ARTIFACT = ROOT / "artifact" / "data_artifact.json"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("openai>=1.50.0", "fastapi>=0.115.0")
    .add_local_file(CONTEXT_FILE, "/app/context_perfect.txt")
    .add_local_file(ARTIFACT, "/app/data_artifact.json")
)

app = modal.App("overture-chat", image=image)

MODEL = "gpt-4o-mini"
MAX_TOKENS = 600

# CORS — allow any origin so the same backend serves local dev and Pages.
# The endpoint exposes no sensitive data; the API key never leaves Modal.
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def build_system_prompt() -> str:
    context = Path("/app/context_perfect.txt").read_text(encoding="utf-8")
    artifact = Path("/app/data_artifact.json").read_text(encoding="utf-8")
    return (
        f"{context}\n\n"
        f"================================================================\n"
        f"ARTIFACT DATA (data_artifact.json)\n"
        f"================================================================\n"
        f"{artifact}\n"
    )


@app.function(
    secrets=[modal.Secret.from_name("overture-openai")],
    timeout=60,
    min_containers=0,
)
@modal.fastapi_endpoint(method="POST")
def chat(payload: dict) -> dict:
    from fastapi.responses import JSONResponse
    from openai import OpenAI

    query = (payload or {}).get("query", "").strip()
    if not query:
        return JSONResponse(
            {"error": "missing query"}, status_code=400, headers=CORS_HEADERS
        )

    client = OpenAI()
    start = time.perf_counter()
    completion = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=0.0,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": query},
        ],
    )
    latency_ms = int((time.perf_counter() - start) * 1000)

    reply = completion.choices[0].message.content or ""
    usage = completion.usage
    body = {
        "reply": reply,
        "model": MODEL,
        "latency_ms": latency_ms,
        "tokens": {
            "prompt": usage.prompt_tokens if usage else None,
            "completion": usage.completion_tokens if usage else None,
            "total": usage.total_tokens if usage else None,
        },
    }
    return JSONResponse(body, headers=CORS_HEADERS)


@app.function()
@modal.fastapi_endpoint(method="OPTIONS")
def chat_preflight() -> dict:
    from fastapi.responses import Response

    return Response(status_code=204, headers=CORS_HEADERS)
