"""Build a multi-page PDF presentation summarizing the project work.

Pages:
  1. Title
  2. Project setup & OKR
  3. Benchmark result (donut)
  4. Diagnosis: the hallucination breakdown
  5. Audit: reliability heatmap across 5 context files
  6. Design principles
  7. Anatomy of the perfect context file
  8. Validation: score comparison (74 / 87 / 100)
  9. Workflow & takeaways
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.image import imread
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parent.parent
VIZ = ROOT / "viz"

PALETTE = {
    "primary": "#5B8DEF", "accent":  "#F2545B", "good":  "#3CB371",
    "warn":    "#F2A65A", "muted":   "#B0B7C3", "bg":    "#F7F8FA",
    "ink":     "#1F2937", "ink2":    "#374151", "panel": "#FFFFFF",
}

PAGE = (13.33, 7.5)  # 16:9 presentation
plt.rcParams.update({
    "figure.facecolor":  PALETTE["bg"],
    "axes.facecolor":    PALETTE["panel"],
    "axes.edgecolor":    PALETTE["muted"],
    "axes.labelcolor":   PALETTE["ink"],
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})


def new_page():
    fig = plt.figure(figsize=PAGE)
    fig.patch.set_facecolor(PALETTE["bg"])
    return fig


def header_band(fig, title, subtitle=None):
    band = fig.add_axes([0, 0.90, 1, 0.10])
    band.set_facecolor(PALETTE["ink"])
    band.set_xticks([]); band.set_yticks([])
    for s in band.spines.values():
        s.set_visible(False)
    band.text(0.04, 0.55, title, color="white", fontsize=22,
             fontweight="bold", va="center")
    if subtitle:
        band.text(0.04, 0.18, subtitle, color="#9CA3AF",
                 fontsize=11.5, va="center")


def footer(fig, n):
    fig.text(0.5, 0.022, f"Dashboards are Dead  ·  Sanya Bhatia  ·  slide {n}",
             ha="center", fontsize=9, color=PALETTE["muted"])


def panel(fig, rect, fc=PALETTE["panel"]):
    ax = fig.add_axes(rect)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_facecolor(fc)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    return ax


def image_panel(fig, rect, image_path):
    """Plain image axes — no fixed xlim/ylim that distort the image."""
    ax = fig.add_axes(rect)
    img = imread(image_path)
    ax.imshow(img)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_aspect("auto")
    return ax


def metric_card(fig, rect, label, value, color):
    ax = panel(fig, rect, fc="white")
    ax.add_patch(FancyBboxPatch(
        (0.02, 0.05), 0.96, 0.9, boxstyle="round,pad=0.02",
        linewidth=0, facecolor="white"))
    ax.add_patch(Rectangle((0.02, 0.05), 0.04, 0.9, color=color, lw=0))
    ax.text(0.10, 0.65, value, fontsize=34, fontweight="bold",
            color=PALETTE["ink"], va="center")
    ax.text(0.10, 0.25, label, fontsize=11, color=PALETTE["ink2"], va="center")


# ---------- Page 1: Title ----------
def slide_title(pdf):
    fig = new_page()
    fig.text(0.5, 0.62, "From 74 → 87 → 100", ha="center",
             fontsize=52, fontweight="bold", color=PALETTE["ink"])
    fig.text(0.5, 0.53,
             "Designing a context file that stops the LLM from "
             "hallucinating on Overture data",
             ha="center", fontsize=16, color=PALETTE["ink2"])
    fig.text(0.5, 0.40,
             "Diagnosis  →  Design  →  Validation",
             ha="center", fontsize=13, color=PALETTE["primary"],
             style="italic")
    fig.text(0.5, 0.20, "Sanya Bhatia  ·  Dashboards are Dead",
             ha="center", fontsize=12, color=PALETTE["muted"])
    fig.text(0.5, 0.16, "2026-05-20", ha="center", fontsize=10,
             color=PALETTE["muted"])
    pdf.savefig(fig); plt.close(fig)


# ---------- Page 2: Setup ----------
def slide_setup(pdf):
    fig = new_page()
    header_band(fig, "Project setup",
                "What we're testing and why")
    ax = panel(fig, [0.05, 0.10, 0.42, 0.78])
    ax.text(0.0, 0.95, "The pipeline", fontsize=14, fontweight="bold",
            color=PALETTE["ink"])
    lines = [
        ("1.", "Overture Maps monthly CSV  ·  573,795 rows  ·  23 columns"),
        ("2.", "analyze.py  →  data_artifact.json (ground truth)"),
        ("3.", "Context file (one of 5 from peer teams) frames the LLM"),
        ("4.", "System prompt v1 enforces 'only artifact facts'"),
        ("5.", "Benchmark questions tested against OpenAI"),
        ("6.", "Results compared to artifact for correctness"),
    ]
    for i, (n, t) in enumerate(lines):
        y = 0.82 - i * 0.11
        ax.text(0.0, y, n, fontsize=12, color=PALETTE["primary"],
                fontweight="bold")
        ax.text(0.06, y, t, fontsize=11.5, color=PALETTE["ink"])

    ax2 = panel(fig, [0.52, 0.10, 0.43, 0.78])
    ax2.text(0.0, 0.95, "OKR we're chasing", fontsize=14, fontweight="bold",
             color=PALETTE["ink"])
    okr = [
        ("KR1", "Test LLM answers on ~10 benchmark questions"),
        ("KR2", "Reach F1 in [0.8, 1.0] across evaluated responses"),
        ("KR3", "Reach 85%+ accuracy or properly refused responses"),
    ]
    for i, (k, v) in enumerate(okr):
        y = 0.78 - i * 0.14
        ax2.add_patch(FancyBboxPatch((0.0, y - 0.04), 0.10, 0.08,
                                     boxstyle="round,pad=0.01",
                                     facecolor=PALETTE["primary"], lw=0))
        ax2.text(0.05, y, k, ha="center", va="center", color="white",
                 fontsize=10.5, fontweight="bold")
        ax2.text(0.13, y, v, fontsize=11.5, color=PALETTE["ink"], va="center")

    ax2.text(0.0, 0.25, "Hypothesis", fontsize=13, fontweight="bold",
             color=PALETTE["accent"])
    ax2.text(0.0, 0.16,
             "Hallucinations on this dataset are downstream of\n"
             "context-file gaps. Fix the upstream file, fix the answer.",
             fontsize=11, color=PALETTE["ink"])

    footer(fig, 2)
    pdf.savefig(fig); plt.close(fig)


# ---------- Page 3: Benchmark result ----------
def slide_benchmark(pdf):
    fig = new_page()
    header_band(fig, "The benchmark",
                "5 correct, 1 partial — and the partial is the interesting one")
    image_panel(fig, [0.04, 0.10, 0.55, 0.75], VIZ / "benchmark_results.png")
    ax_txt = panel(fig, [0.62, 0.10, 0.34, 0.78])
    ax_txt.text(0.0, 0.96, "The one wrong answer", fontsize=14,
                fontweight="bold", color=PALETTE["accent"])
    ax_txt.text(0.0, 0.86, "Q: Why is some data missing?", fontsize=11.5,
                color=PALETTE["ink"], fontweight="bold")
    ax_txt.text(0.0, 0.78,
                "A: «fields are not applicable or unavailable\n"
                "    for every record.»",
                fontsize=10.5, color=PALETTE["ink2"], style="italic")
    ax_txt.text(0.0, 0.62, "Why it's wrong:", fontsize=12,
                fontweight="bold", color=PALETTE["ink"])
    ax_txt.text(0.0, 0.45,
                "The artifact records how many values are\n"
                "missing per column. It does not record any\n"
                "reason. The LLM invented a plausible cause.",
                fontsize=11, color=PALETTE["ink2"])
    ax_txt.text(0.0, 0.27, "This is the canonical hallucination",
                fontsize=12, fontweight="bold", color=PALETTE["primary"])
    ax_txt.text(0.0, 0.14,
                "Describing observation as causation. The fix\n"
                "is upstream — in the context file.",
                fontsize=11, color=PALETTE["ink2"])
    footer(fig, 3)
    pdf.savefig(fig); plt.close(fig)


# ---------- Page 4: Audit / heatmap ----------
def slide_audit(pdf):
    fig = new_page()
    header_band(fig, "The audit",
                "Every existing context file fails on the same dimension")
    image_panel(fig, [0.04, 0.20, 0.62, 0.62], VIZ / "reliability_heatmap.png")
    ax_txt = panel(fig, [0.69, 0.20, 0.27, 0.64])
    ax_txt.text(0.0, 0.95, "Pattern", fontsize=14, fontweight="bold",
                color=PALETTE["ink"])
    ax_txt.text(0.0, 0.85,
                "q4 = missing-data documentation\n"
                "is RISKY on all 5 files.",
                fontsize=11.5, color=PALETTE["ink2"])
    ax_txt.text(0.0, 0.66, "What the checker scores",
                fontsize=12, fontweight="bold", color=PALETTE["primary"])
    ax_txt.text(0.0, 0.46,
                "•  ≥2 hits per keyword set\n"
                "•  −10 pts per RISKY question\n"
                "•  −3 pts per rubric issue\n"
                "•  Cap: −15 from rubric",
                fontsize=11, color=PALETTE["ink2"])
    ax_txt.text(0.0, 0.20,
                "Translation",
                fontsize=12, fontweight="bold", color=PALETTE["accent"])
    ax_txt.text(0.0, 0.05,
                "No file uses the words\n"
                "'missing' / 'null' / 'incomplete'.",
                fontsize=11, color=PALETTE["ink2"])
    footer(fig, 4)
    pdf.savefig(fig); plt.close(fig)


# ---------- Page 5: Design principles ----------
def slide_principles(pdf):
    fig = new_page()
    header_band(fig, "Design principles",
                "What the perfect context file must do")
    cards = [
        ("01", "Cover all 7 rubric sections",
         "instructions, schema, statistics,\n"
         "coverage, missing data, version,\n"
         "examples, unsupported.",
         PALETTE["primary"]),
        ("02", "Quantify, don't explain",
         "List exact null counts.\n"
         "Never speculate on causes.\n"
         "Bake the refusal in.",
         PALETTE["accent"]),
        ("03", "Examples are format only",
         "'Demonstrations of format —\n"
         "compute every answer fresh\n"
         "from the artifact.'",
         PALETTE["warn"]),
        ("04", "Refusal templates inline",
         "Five canned refusals for causal,\n"
         "out-of-scope, and outside-\n"
         "knowledge questions.",
         PALETTE["good"]),
        ("05", "Description ≠ causation",
         "The rule that would have\n"
         "stopped the Q5 hallucination\n"
         "on the benchmark.",
         PALETTE["primary"]),
        ("06", "Ground every claim",
         "Field name + exact number,\n"
         "every time. If it isn't in the\n"
         "artifact, say so.",
         PALETTE["accent"]),
    ]
    for i, (num, title, body, color) in enumerate(cards):
        col = i % 3
        row = i // 3
        x = 0.04 + col * 0.32
        y = 0.50 - row * 0.36
        ax = panel(fig, [x, y, 0.28, 0.32])
        ax.add_patch(FancyBboxPatch((0.02, 0.04), 0.96, 0.92,
                                    boxstyle="round,pad=0.02",
                                    facecolor="white", lw=0))
        ax.add_patch(Rectangle((0.02, 0.04), 0.04, 0.92, color=color, lw=0))
        ax.text(0.10, 0.87, num, fontsize=11, fontweight="bold", color=color)
        ax.text(0.10, 0.73, title, fontsize=13, fontweight="bold",
                color=PALETTE["ink"])
        ax.text(0.10, 0.36, body, fontsize=10.5, color=PALETTE["ink2"],
                va="center")
    footer(fig, 5)
    pdf.savefig(fig); plt.close(fig)


# ---------- Page 6: Anatomy ----------
def slide_anatomy(pdf):
    fig = new_page()
    header_band(fig, "Anatomy of the perfect context file",
                "context_perfect.txt  ·  9 sections, 200+ lines")
    sections = [
        ("§1", "YOUR ROLE",
         "Define the LLM's scope: report what the artifact contains."),
        ("§2", "RULES",
         "7 explicit rules. Includes 'treat examples as format only' (+10)."),
        ("§3", "SCHEMA",
         "All 23 columns, grouped: identifiers, geometry metrics, counts."),
        ("§4", "STATISTICS",
         "Total rows, complete vs partial vs fully-null columns."),
        ("§5", "COVERAGE & LIMITATIONS",
         "What this file covers and what it doesn't (countries, themes…)."),
        ("§6", "MISSING DATA  ← the critical addition",
         "Exact counts + 'do NOT speculate' guardrail. Closes the q4 gap."),
        ("§7", "VERSIONING",
         "Generation date stated; release month explicitly NOT stated."),
        ("§8", "EXAMPLE QUERIES",
         "5 demonstrations including the 'why is data missing?' refusal."),
        ("§9", "UNSUPPORTED QUESTIONS",
         "5 refusal templates (T1–T5) keyed to question types."),
    ]
    ax = panel(fig, [0.04, 0.05, 0.92, 0.83])
    for i, (tag, title, body) in enumerate(sections):
        y = 0.95 - i * 0.105
        color = PALETTE["accent"] if "MISSING DATA" in title else PALETTE["primary"]
        ax.add_patch(FancyBboxPatch((0.0, y - 0.04), 0.05, 0.08,
                                    boxstyle="round,pad=0.005",
                                    facecolor=color, lw=0))
        ax.text(0.025, y, tag, ha="center", va="center", color="white",
                fontsize=10.5, fontweight="bold")
        ax.text(0.075, y, title, fontsize=12.5, fontweight="bold",
                va="center", color=PALETTE["ink"])
        ax.text(0.42, y, body, fontsize=11, va="center",
                color=PALETTE["ink2"])
    footer(fig, 6)
    pdf.savefig(fig); plt.close(fig)


# ---------- Page 7: Validation ----------
def slide_validation(pdf):
    fig = new_page()
    header_band(fig, "Validation",
                "Scored with the existing checker — no human eyeballing")

    scores = json.loads((VIZ / "scores.json").read_text())
    by_name = {Path(s["file"]).stem: s for s in scores}
    order = ["context_Ashwin", "context_fetch_4-30", "context_fetch",
             "context_ATLASV4-8-20", "context_ATLAS-9-24", "context_perfect"]
    labels = [n.replace("context_", "") for n in order]
    values = [by_name[n]["score"] for n in order]
    colors = [PALETTE["good"] if v == 100 else
              PALETTE["primary"] if v >= 85 else
              PALETTE["warn"] for v in values]

    ax = fig.add_axes([0.16, 0.16, 0.46, 0.68])
    bars = ax.barh(np.arange(len(values)), values, color=colors,
                   edgecolor="white", height=0.7)
    ax.set_yticks(np.arange(len(values)))
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlim(0, 110)
    ax.set_xlabel("Prompt readiness score (/100)")
    ax.axvline(85, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.text(85.5, -0.8, "OKR target ≥ 85", fontsize=9,
            color=PALETTE["muted"], style="italic")
    for bar, v in zip(bars, values):
        ax.text(v + 1.5, bar.get_y() + bar.get_height() / 2,
                f"{v}", va="center", fontweight="bold", fontsize=11,
                color=PALETTE["ink"])

    metric_card(fig, [0.66, 0.60, 0.30, 0.18],
                "context_perfect.txt", "100", PALETTE["good"])
    metric_card(fig, [0.66, 0.40, 0.30, 0.18],
                "vs Ashwin (74)", "+26", PALETTE["primary"])
    metric_card(fig, [0.66, 0.20, 0.30, 0.18],
                "vs 87-tier average", "+13", PALETTE["accent"])

    footer(fig, 7)
    pdf.savefig(fig); plt.close(fig)


# ---------- Page 8: Workflow & takeaways ----------
def slide_workflow(pdf):
    fig = new_page()
    header_band(fig, "Workflow & takeaways",
                "What this generalizes to")

    ax = panel(fig, [0.04, 0.55, 0.92, 0.32])
    steps = [
        ("Diagnose",   "Run benchmark.  Mark partial / wrong answers."),
        ("Locate",     "Score every context file.  Find shared failure dim."),
        ("Author",     "Write a file that hits every rubric section."),
        ("Validate",   "Re-score.  Re-run benchmark.  Compare."),
        ("Iterate",    "If a new question fails, add a refusal template."),
    ]
    for i, (label, body) in enumerate(steps):
        x = 0.02 + i * 0.196
        ax.add_patch(FancyBboxPatch((x, 0.15), 0.18, 0.70,
                                    boxstyle="round,pad=0.02",
                                    facecolor=PALETTE["primary"], lw=0))
        ax.text(x + 0.09, 0.68, str(i + 1), ha="center", color="white",
                fontsize=22, fontweight="bold")
        ax.text(x + 0.09, 0.46, label, ha="center", color="white",
                fontsize=12, fontweight="bold")
        ax.text(x + 0.09, 0.28, body, ha="center", color="white",
                fontsize=9.5, wrap=True)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 0.196, 0.5), xytext=(x + 0.180, 0.5),
                        arrowprops=dict(arrowstyle="->", color=PALETTE["ink"],
                                        lw=1.5))

    ax2 = panel(fig, [0.04, 0.08, 0.92, 0.42])
    ax2.text(0.0, 0.92, "Three things this proves", fontsize=14,
             fontweight="bold", color=PALETTE["ink"])
    points = [
        ("Hallucination is upstream.",
         "The LLM didn't fail at reasoning — it filled a gap the "
         "context file left open. Patching the file would patch the answer."),
        ("Rubric coverage is necessary but not sufficient.",
         "Four of five files cover the rubric and still score RISKY on q4. "
         "Keywords matter; the words 'missing' / 'null' must appear."),
        ("The refusal IS the answer.",
         "For causal questions on observational data, the correct answer "
         "is a refusal. Templates make that easy to produce consistently."),
    ]
    for i, (head, body) in enumerate(points):
        y = 0.72 - i * 0.24
        ax2.text(0.0, y, "•", fontsize=18, color=PALETTE["accent"],
                 fontweight="bold")
        ax2.text(0.03, y, head, fontsize=12, fontweight="bold",
                 color=PALETTE["ink"])
        ax2.text(0.03, y - 0.10, body, fontsize=10.5,
                 color=PALETTE["ink2"], wrap=True)

    footer(fig, 8)
    pdf.savefig(fig); plt.close(fig)


def main():
    out = VIZ / "presentation.pdf"
    with PdfPages(out) as pdf:
        slide_title(pdf)
        slide_setup(pdf)
        slide_benchmark(pdf)
        slide_audit(pdf)
        slide_principles(pdf)
        slide_anatomy(pdf)
        slide_validation(pdf)
        slide_workflow(pdf)
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
