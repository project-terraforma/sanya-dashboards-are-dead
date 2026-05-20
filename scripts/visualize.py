"""Generate pretty visualizations of the project's results.

Outputs to viz/:
  1. missing_values.png        — missing-value counts per artifact column
  2. benchmark_results.png     — OpenAI bench_easy correctness donut
  3. context_file_scores.png   — prompt-readiness scores across context files
  4. reliability_heatmap.png   — supported vs risky per question across files
"""

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
VIZ = ROOT / "viz"
VIZ.mkdir(exist_ok=True)

PALETTE = {
    "primary":   "#5B8DEF",
    "accent":    "#F2545B",
    "good":      "#3CB371",
    "warn":      "#F2A65A",
    "muted":     "#B0B7C3",
    "bg":        "#F7F8FA",
    "ink":       "#1F2937",
}

plt.rcParams.update({
    "figure.facecolor":  PALETTE["bg"],
    "axes.facecolor":    "white",
    "axes.edgecolor":    PALETTE["muted"],
    "axes.labelcolor":   PALETTE["ink"],
    "axes.titleweight":  "bold",
    "axes.titlesize":    14,
    "axes.titlecolor":   PALETTE["ink"],
    "xtick.color":       PALETTE["ink"],
    "ytick.color":       PALETTE["ink"],
    "font.family":       "DejaVu Sans",
    "font.size":         10,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})


# ---------- 1. Missing values per artifact column ----------
def plot_missing_values():
    art = json.loads((ROOT / "artifact" / "data_artifact.json").read_text())
    total = art["total_rows"]
    missing = art["missing_values"]
    items = sorted(missing.items(), key=lambda kv: kv[1])
    cols   = [k for k, _ in items]
    counts = [v for _, v in items]
    pct    = [100 * v / total for v in counts]

    colors = []
    for p in pct:
        if p == 0:        colors.append(PALETTE["good"])
        elif p == 100:    colors.append(PALETTE["accent"])
        elif p > 50:      colors.append(PALETTE["warn"])
        else:             colors.append(PALETTE["primary"])

    fig, ax = plt.subplots(figsize=(11, 9))
    y = np.arange(len(cols))
    ax.barh(y, pct, color=colors, edgecolor="white", height=0.78)
    ax.set_yticks(y)
    ax.set_yticklabels(cols, fontsize=9)
    ax.set_xlim(0, 105)
    ax.set_xlabel("% of rows missing")
    ax.set_title(f"Missing values per column  ·  {total:,} total rows",
                 loc="left", pad=14)

    for i, (p, n) in enumerate(zip(pct, counts)):
        if p == 0:
            label = "complete"
        elif p == 100:
            label = "all missing"
        else:
            label = f"{p:.1f}%  ({n:,})"
        ax.text(p + 1.2, i, label, va="center", fontsize=8.5,
                color=PALETTE["ink"])

    # legend
    legend_items = [
        ("Complete",      PALETTE["good"]),
        ("Partial (<50%)", PALETTE["primary"]),
        ("Mostly missing (>50%)", PALETTE["warn"]),
        ("All missing",   PALETTE["accent"]),
    ]
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, c in legend_items]
    ax.legend(handles, [n for n, _ in legend_items],
              loc="lower right", frameon=False, fontsize=9)

    fig.tight_layout()
    out = VIZ / "missing_values.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 2. OpenAI benchmark correctness ----------
def plot_benchmark():
    text = (ROOT / "results" / "openai" / "results_bench_easy").read_text()
    blocks = re.split(r"\n(?=Question:)", text.strip())
    rows = []
    for b in blocks:
        q = re.search(r"Question:\s*(.+)", b)
        r = re.search(r"Result:\s*(.+)", b)
        if q and r:
            rows.append((q.group(1).strip(), r.group(1).strip()))

    def bucket(result):
        low = result.lower()
        if low.startswith("correct"):           return "Correct"
        if "partial" in low:                    return "Partial"
        if "incorrect" in low or "wrong" in low: return "Incorrect"
        return "Other"

    buckets = [bucket(r) for _, r in rows]
    counts = {k: buckets.count(k) for k in ["Correct", "Partial", "Incorrect"]}
    counts = {k: v for k, v in counts.items() if v}

    color_map = {
        "Correct":   PALETTE["good"],
        "Partial":   PALETTE["warn"],
        "Incorrect": PALETTE["accent"],
    }

    fig, (ax_donut, ax_tbl) = plt.subplots(
        1, 2, figsize=(13, 5.5), gridspec_kw={"width_ratios": [1, 1.5]}
    )

    sizes = list(counts.values())
    labels = list(counts.keys())
    colors = [color_map[k] for k in labels]
    wedges, _ = ax_donut.pie(
        sizes, colors=colors, startangle=90,
        wedgeprops=dict(width=0.38, edgecolor="white", linewidth=3),
    )
    ax_donut.text(0, 0.08, f"{sum(sizes)}", ha="center", va="center",
                  fontsize=34, fontweight="bold", color=PALETTE["ink"])
    ax_donut.text(0, -0.18, "questions", ha="center", va="center",
                  fontsize=11, color=PALETTE["muted"])
    ax_donut.set_title("OpenAI · bench_easy", loc="center", pad=14)

    legend_handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors]
    legend_text = [f"{k}  ·  {v}" for k, v in counts.items()]
    ax_donut.legend(legend_handles, legend_text, loc="lower center",
                    bbox_to_anchor=(0.5, -0.08), ncol=len(counts),
                    frameon=False, fontsize=10)

    # right panel: per-question table
    ax_tbl.axis("off")
    ax_tbl.set_title("Question-by-question outcome", loc="left", pad=14)
    for i, (q, r) in enumerate(rows):
        y = 1 - (i + 1) * (1.0 / (len(rows) + 1))
        b = bucket(r)
        color = color_map.get(b, PALETTE["muted"])
        dot = plt.Circle((0.02, y), 0.018, color=color,
                         transform=ax_tbl.transAxes, clip_on=False)
        ax_tbl.add_patch(dot)
        q_short = q if len(q) <= 70 else q[:67] + "…"
        ax_tbl.text(0.06, y, q_short, transform=ax_tbl.transAxes,
                    fontsize=10, va="center", color=PALETTE["ink"])
        ax_tbl.text(0.98, y, b, transform=ax_tbl.transAxes,
                    fontsize=9.5, va="center", ha="right",
                    color=color, fontweight="bold")

    fig.tight_layout()
    out = VIZ / "benchmark_results.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3 & 4. Context-file grounding reports ----------
QUESTIONS = [
    ("q1", "schema"),
    ("q2", "statistics"),
    ("q3", "coverage"),
    ("q4", "missing data"),
    ("q5", "version"),
    ("q6", "prompt examples"),
    ("q7", "unsupported"),
]

def parse_reports():
    reports_dir = ROOT / "context-files-analysis" / "results"
    parsed = []
    for f in sorted(reports_dir.glob("*.txt")):
        text = f.read_text()
        m = re.search(r"Prompt Readiness Score:\s*(\d+)\s*/\s*100", text)
        score = int(m.group(1)) if m else None

        rel_block = re.search(
            r"=== PROMPT RELIABILITY CHECK ===\s*\n(.*?)\n===",
            text, flags=re.S,
        )
        marks = []
        if rel_block:
            for line in rel_block.group(1).splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("[SUPPORTED]"):
                    marks.append("supported")
                elif line.startswith("[RISKY]"):
                    marks.append("risky")
                else:
                    marks.append("missing")

        # number of rubric issues (lines starting with "Issue:")
        rubric_issues = len(re.findall(r"^Issue:", text, flags=re.M))

        parsed.append({
            "name": f.stem,
            "score": score,
            "marks": marks,
            "rubric_issues": rubric_issues,
        })
    return parsed


def plot_context_scores(parsed):
    parsed_sorted = sorted(parsed, key=lambda r: r["score"] or 0)
    names = [r["name"] for r in parsed_sorted]
    scores = [r["score"] for r in parsed_sorted]
    issues = [r["rubric_issues"] for r in parsed_sorted]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    y = np.arange(len(names))
    colors = [PALETTE["good"] if s >= 85 else
              PALETTE["warn"] if s >= 70 else PALETTE["accent"]
              for s in scores]

    bars = ax.barh(y, scores, color=colors, edgecolor="white", height=0.62)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlim(0, 105)
    ax.axvline(85, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.text(85.5, -0.85, "target  ≥ 85", color=PALETTE["muted"],
            fontsize=9, style="italic")
    ax.set_xlabel("Prompt readiness score (/100)")
    ax.set_title("Context-file grounding scores", loc="left", pad=14)

    for bar, s, n_issues in zip(bars, scores, issues):
        w = bar.get_width()
        ax.text(w + 1.5, bar.get_y() + bar.get_height() / 2,
                f"{s}", va="center", fontsize=10,
                fontweight="bold", color=PALETTE["ink"])
        ax.text(2, bar.get_y() + bar.get_height() / 2,
                f"{n_issues} rubric issue{'s' if n_issues != 1 else ''}",
                va="center", fontsize=8.5, color="white")

    fig.tight_layout()
    out = VIZ / "context_file_scores.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_reliability_heatmap(parsed):
    parsed_sorted = sorted(parsed, key=lambda r: r["score"] or 0, reverse=True)
    names = [r["name"] for r in parsed_sorted]
    rows = []
    for r in parsed_sorted:
        marks = r["marks"] + ["missing"] * (len(QUESTIONS) - len(r["marks"]))
        rows.append(marks[: len(QUESTIONS)])

    val = {"supported": 1, "risky": 0.5, "missing": 0}
    grid = np.array([[val[m] for m in row] for row in rows])

    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    cmap = plt.matplotlib.colors.ListedColormap(
        [PALETTE["accent"], PALETTE["warn"], PALETTE["good"]]
    )
    ax.imshow(grid, cmap=cmap, aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(QUESTIONS)))
    ax.set_xticklabels([f"{q}\n{lbl}" for q, lbl in QUESTIONS], fontsize=9)
    ax.set_yticks(np.arange(len(names)))
    ax.set_yticklabels(names)
    ax.set_title("Reliability by question · per context file",
                 loc="left", pad=14)

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            v = grid[i, j]
            symbol = "✓" if v == 1 else "!" if v == 0.5 else "·"
            ax.text(j, i, symbol, ha="center", va="center",
                    color="white", fontsize=12, fontweight="bold")

    # custom legend
    legend_items = [
        ("Supported", PALETTE["good"]),
        ("Risky",     PALETTE["warn"]),
        ("Missing",   PALETTE["accent"]),
    ]
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, c in legend_items]
    ax.legend(handles, [n for n, _ in legend_items],
              loc="upper center", bbox_to_anchor=(0.5, -0.18),
              ncol=3, frameon=False, fontsize=9.5)
    ax.set_xticks(np.arange(-0.5, len(QUESTIONS), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(names), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=3)
    ax.tick_params(which="minor", length=0)

    fig.tight_layout()
    out = VIZ / "reliability_heatmap.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out


def main():
    outputs = []
    outputs.append(plot_missing_values())
    outputs.append(plot_benchmark())
    parsed = parse_reports()
    outputs.append(plot_context_scores(parsed))
    outputs.append(plot_reliability_heatmap(parsed))
    for p in outputs:
        print(f"wrote {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
