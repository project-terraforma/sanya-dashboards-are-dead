import os
import glob
import pandas as pd
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
METRICS_DIR = os.path.join(BASE, "data", "metrics")
COL_STATS_DIR = os.path.join(BASE, "data", "theme_column_summary_stats")
CLASS_STATS_DIR = os.path.join(BASE, "data", "theme_class_summary_stats")
OUTPUT = os.path.join(BASE, "artifact_v1.txt")

RELEASES = sorted([
    d for d in os.listdir(METRICS_DIR)
    if os.path.isdir(os.path.join(METRICS_DIR, d)) and not d.startswith(".")
])

# Releases that have pre-aggregated changelog_stats
CHANGELOG_RELEASES = {
    r for r in RELEASES
    if os.path.isdir(os.path.join(METRICS_DIR, r, "changelog_stats"))
}


def get_changelog_row(release, theme, type_):
    """Return a dict of change stats for a theme/type from changelog_stats CSV."""
    pattern = os.path.join(METRICS_DIR, release, "changelog_stats", "*.csv")
    files = glob.glob(pattern)
    if not files:
        return None
    df = pd.read_csv(files[0], sep="\t")
    row = df[(df["theme"] == theme) & (df["type"] == type_)]
    if row.empty:
        return None
    return row.iloc[0].to_dict()


def get_rowcounts_totals(release, theme, type_):
    """Aggregate total_count by change_type from raw row_counts for early releases."""
    pattern = os.path.join(METRICS_DIR, release, "row_counts", f"theme={theme}", f"type={type_}", "*.csv")
    files = glob.glob(pattern)
    if not files:
        return None
    df = pd.read_csv(files[0])
    totals = df.groupby("change_type")["total_count"].sum().to_dict()
    total_current = sum(v for k, v in totals.items() if k != "removed")
    return {
        "theme": theme,
        "type": type_,
        "total_current": int(total_current),
        "added": int(totals.get("added", 0)),
        "removed": int(totals.get("removed", 0)),
        "data_changed": int(totals.get("data_changed", 0)),
        "unchanged": int(totals.get("unchanged", 0)),
    }


def get_change_stats(release, theme, type_):
    """Get change stats from changelog_stats if available, else compute from row_counts."""
    if release in CHANGELOG_RELEASES:
        return get_changelog_row(release, theme, type_)
    return get_rowcounts_totals(release, theme, type_)


def get_column_stats(release, theme, type_, fields):
    """Return specific field coverage counts from theme_column_summary_stats."""
    pattern = os.path.join(COL_STATS_DIR, f"{release}.theme={theme}.type={type_}.csv")
    files = glob.glob(pattern)
    if not files:
        return None
    df = pd.read_csv(files[0])
    row = df.iloc[0]
    return {f: int(row[f]) for f in fields if f in row}


def get_class_stats(release, theme, type_):
    """Return all class/count rows from theme_class_summary_stats."""
    pattern = os.path.join(CLASS_STATS_DIR, f"{release}.theme={theme}.type={type_}.csv")
    files = glob.glob(pattern)
    if not files:
        return None
    df = pd.read_csv(files[0])
    df = df[df["country"].notna() & (df["country"] != "")]
    return df[["country", "count"]].sort_values("count", ascending=False)


def fmt_num(n):
    return f"{int(n):,}" if n is not None else "N/A"


lines = []

# ── Header ────────────────────────────────────────────────────────────────────
lines += [
    "# Overture Release Metrics — LLM Context File (v1)",
    f"# Generated: {datetime.today().strftime('%Y-%m-%d')}",
    "",
    "## Instructions",
    "- Only answer using data explicitly present in this file.",
    "- If a question requires a value not present here, say so and refuse to estimate.",
    "- If a field tracks presence/population counts (not actual values), do not compute averages or distributions from it.",
    "- Releases are listed in chronological order. The final entry is the latest release.",
    "",
]

# ── Release Index ──────────────────────────────────────────────────────────────
lines.append("## Release Index")
for r in RELEASES:
    suffix = "  ← latest" if r == RELEASES[-1] else ""
    lines.append(f"- {r}{suffix}")
lines.append("")

# ── Theme & Type Reference ─────────────────────────────────────────────────────
lines += [
    "## Theme & Type Reference",
    "7 themes, 15 types total.",
    "",
    "| Theme | Type |",
    "|-------|------|",
    "| addresses | address |",
    "| buildings | building |",
    "| buildings | building_part |",
    "| base | bathymetry |",
    "| base | infrastructure |",
    "| base | land |",
    "| base | land_cover |",
    "| base | land_use |",
    "| base | water |",
    "| divisions | division |",
    "| divisions | division_area |",
    "| divisions | division_boundary |",
    "| places | place |",
    "| transportation | connector |",
    "| transportation | segment |",
    "",
    "Note: The following types have NO class breakdown and cannot answer class distribution questions:",
    "- transportation/connector",
    "- buildings/building_part",
    "- base/bathymetry",
    "- base/land_cover",
    "",
]

# ── Changelog Stats ────────────────────────────────────────────────────────────
lines.append("## Changelog Stats")
lines.append("Columns: theme | type | release | total_current | added | removed | data_changed | unchanged")
lines.append("")

# Q3: divisions latest release
# Q4: all themes last 2 releases
# Q5a: base/water Jan + Feb 2025
# Q8: buildings latest release
# Q9: buildings March 2025

changelog_queries = [
    # (release, theme, type, label)
    ("2025-01-22.0", "base", "water", "Q5a — water Jan 2025"),
    ("2025-02-19.0", "base", "water", "Q5a — water Feb 2025"),
    ("2025-03-19.1", "buildings", "building", "Q9 — buildings March 2025"),
    ("2025-08-20.1", "addresses", "address", "Q4"),
    ("2025-08-20.1", "base", "bathymetry", "Q4"),
    ("2025-08-20.1", "base", "infrastructure", "Q4"),
    ("2025-08-20.1", "base", "land", "Q4"),
    ("2025-08-20.1", "base", "land_cover", "Q4"),
    ("2025-08-20.1", "base", "land_use", "Q4"),
    ("2025-08-20.1", "base", "water", "Q4"),
    ("2025-08-20.1", "buildings", "building", "Q4"),
    ("2025-08-20.1", "divisions", "division", "Q4"),
    ("2025-08-20.1", "divisions", "division_area", "Q4"),
    ("2025-08-20.1", "divisions", "division_boundary", "Q4"),
    ("2025-08-20.1", "places", "place", "Q4"),
    ("2025-08-20.1", "transportation", "connector", "Q4"),
    ("2025-08-20.1", "transportation", "segment", "Q4"),
    ("2025-09-24.0", "addresses", "address", "Q4"),
    ("2025-09-24.0", "base", "bathymetry", "Q4"),
    ("2025-09-24.0", "base", "infrastructure", "Q4"),
    ("2025-09-24.0", "base", "land", "Q4"),
    ("2025-09-24.0", "base", "land_cover", "Q4"),
    ("2025-09-24.0", "base", "land_use", "Q4"),
    ("2025-09-24.0", "base", "water", "Q4"),
    ("2025-09-24.0", "buildings", "building", "Q3/Q4/Q8"),
    ("2025-09-24.0", "divisions", "division", "Q3/Q4"),
    ("2025-09-24.0", "divisions", "division_area", "Q3/Q4"),
    ("2025-09-24.0", "divisions", "division_boundary", "Q3/Q4"),
    ("2025-09-24.0", "places", "place", "Q4"),
    ("2025-09-24.0", "transportation", "connector", "Q4"),
    ("2025-09-24.0", "transportation", "segment", "Q4"),
]

lines.append("| theme | type | release | total_current | added | removed | data_changed | unchanged |")
lines.append("|-------|------|---------|--------------|-------|---------|--------------|-----------|")

for release, theme, type_, _ in changelog_queries:
    s = get_change_stats(release, theme, type_)
    if s:
        lines.append(
            f"| {theme} | {type_} | {release} | {fmt_num(s.get('total_current'))} | "
            f"{fmt_num(s.get('added'))} | {fmt_num(s.get('removed'))} | "
            f"{fmt_num(s.get('data_changed'))} | {fmt_num(s.get('unchanged'))} |"
        )
lines.append("")

# ── Field Coverage Stats ───────────────────────────────────────────────────────
lines.append("## Field Coverage Stats")
lines.append("Counts represent number of records with that field populated (not the field's value).")
lines.append("")

# Q8: buildings height coverage in latest release
building_fields = get_column_stats("2025-09-24.0", "buildings", "building", ["height", "total_count"])
if building_fields:
    lines.append("### buildings/building — 2025-09-24.0 (latest)")
    for k, v in building_fields.items():
        lines.append(f"- {k}: {fmt_num(v)}")
    lines.append("")

# Q10: places phone_number coverage in latest release
places_fields = get_column_stats("2025-09-24.0", "places", "place", ["phones", "total_count"])
if places_fields:
    lines.append("### places/place — 2025-09-24.0 (latest)")
    for k, v in places_fields.items():
        lines.append(f"- {k}: {fmt_num(v)}")
    lines.append("")

# ── Class Distribution Stats ───────────────────────────────────────────────────
lines.append("## Class Distribution Stats (Addresses by Country)")
lines.append("Q6: addresses/address — country-level record counts for last 2 releases.")
lines.append("")

for release in ["2025-08-20.1", "2025-09-24.0"]:
    df = get_class_stats(release, "addresses", "address")
    if df is not None:
        lines.append(f"### addresses/address — {release}")
        lines.append("| country | count |")
        lines.append("|---------|-------|")
        for _, row in df.iterrows():
            lines.append(f"| {row['country']} | {fmt_num(row['count'])} |")
        lines.append("")

# ── Write output ───────────────────────────────────────────────────────────────
with open(OUTPUT, "w") as f:
    f.write("\n".join(lines))

print(f"Artifact written to: {OUTPUT}")
print(f"Lines: {len(lines)}")
