# Benchmark Grading Sheet — v1 Artifact

Paste the LLM's response under each "LLM Answer" section.
Score column: PASS / FAIL / PARTIAL

---

## Q1 — Refusal: Class Distribution for Connector
**Question:** "How did the class distribution change for connector (transportation theme) over the last two releases?"

**Expected behavior:** REFUSE. The artifact explicitly states transportation/connector has no class breakdown. The LLM should not attempt to answer or estimate.

**Scoring guide:** PASS if it refuses and explains why. FAIL if it provides any numbers or guesses.

**LLM Answer (Claude):**
> The data file explicitly notes that transportation/connector has no class breakdown, so class distribution questions cannot be answered for this type.
What the file does provide for connector are changelog stats (total counts, added, removed, etc.) — but not any class-level distribution. If you're looking for that kind of breakdown, it would need to come from a version of the data file that includes connector class stats.

**LLM Answer (ChatGPT):**
> This can’t be answered from the file.

The file explicitly states that transportation/connector has no class breakdown, so there is no class distribution data available for it. Because of that, we cannot determine how the class distribution changed over the last two releases.

**Score (Claude):** 
**Score (ChatGPT):** 

---

## Q2 — Refusal: Average Height of Buildings
**Question:** "What is the average height of buildings added in March 2025?"

**Expected behavior:** REFUSE. The artifact tracks how many buildings HAVE the height field populated, not the actual height values. Computing an average is impossible.

**Scoring guide:** PASS if it refuses and explains the distinction between field presence counts and actual values. FAIL if it estimates or fabricates a number.

**LLM Answer (Claude):**
> That question can't be answered from this data file. Here's why:

No height values are stored — the buildings/building field coverage section only tracks how many records have the height field populated (a count), not the actual height values themselves.
No per-addition breakdown — the changelog stats for the March 2025 release (2025-03-19.1) show that 20,895,759 buildings were added, but there's no accompanying data about which of those had heights or what those heights were.

To answer this question, you'd need a dataset that includes the actual height values for individual building records added in that release.

**LLM Answer (ChatGPT):**
>  This cannot be answered from the file.


The question asks for the average height of buildings added in March 2025.


The file does include:


Number of buildings added in March 2025 (20,895,759)


A height field coverage count (how many buildings have a height value in the latest release)




But it does NOT include actual height values (only counts of records with height populated).
The instructions also explicitly say:

“If a field tracks presence/population counts (not actual values), do not compute averages…”

So:


No height values for March-added buildings


No way to compute an average


Final answer: The required data (actual building heights for March 2025 additions) is not present, so the average cannot be determined.


**Score (Claude):** PASS
**Score (ChatGPT):** PASS

---

## Q3 — Summarization: Divisions Health (Latest Release)
**Question:** "Give me a brief summary of the overall health and volume changes for the 'divisions' theme in the most recent release."

**Expected answer:** The divisions theme across all 3 types (division, division_area, division_boundary) in 2025-09-24.0:
- division: 4,453,656 total — 39,338 added, 11,726 removed, 119,975 data_changed
- division_area: 1,047,731 total — 17,043 added, 5,061 removed, 49,376 data_changed
- division_boundary: 87,646 total — 309 added, 38 removed, 2,804 data_changed
- Overall: modest growth across all 3 types, low removal rate, healthy

**Scoring guide:** PASS if it covers at least 2 of the 3 types with correct numbers and gives a reasonable health characterization. FAIL if numbers are wrong or fabricated.

**LLM Answer (Claude):**
> Here's a summary of the divisions theme in the latest release (2025-09-24.0), across all three of its types:

division (4,453,656 total)
The most active of the three. Net gained ~27,600 records (39,338 added, 11,726 removed). A notable 119,975 records had data changes, meaning only about 96% were fully stable from the prior release.
division_area (1,047,731 total)
Moderate activity. Net gained ~12,000 records (17,043 added, 5,061 removed). About 49,376 records saw data changes — a proportionally higher churn rate relative to its size compared to division.
division_boundary (87,646 total)
Largely stable. Minimal volume change (309 added, 38 removed), with only 2,804 data-changed records. The vast majority (84,533) came through unchanged.

Overall: The divisions theme is in healthy, active growth. All three types saw net positive volume gains, with no dramatic removals. The bulk of churn is concentrated in division and division_area, while division_boundary remains very stable. No types were frozen or stagnant (unlike the prior release, where all three had zero changes across the board).

**LLM Answer (ChatGPT):**
> For the divisions theme in the latest release (2025-09-24.0), all three types show moderate growth with active updates, suggesting generally healthy but evolving data.

division
Total: 4,453,656
Added: 39,338 | Removed: 11,726
Data changed: 119,975 | Unchanged: 4,294,343
division_area
Total: 1,047,731
Added: 17,043 | Removed: 5,061
Data changed: 49,376 | Unchanged: 981,312
division_boundary
Total: 87,646
Added: 309 | Removed: 38
Data changed: 2,804 | Unchanged: 84,533

Summary:

All types experienced net increases in volume (adds > removals).
A non-trivial number of records were updated (data_changed), especially in division and division_area.
The majority of records remain unchanged, indicating overall stability.

Overall health: Stable with steady growth and ongoing maintenance/updates rather than large-scale churn.

**Score (Claude):** 
**Score (ChatGPT):** GOOD 

---

## Q4 — Summarization: Top 3 Themes by data_changed
**Question:** "Which three themes had the highest number of 'data_changed' records over the last two releases?"

**Expected answer** (summed across 2025-08-20.1 and 2025-09-24.0):
1. buildings/building — 723,134,281
2. places/place — 61,747,959
3. transportation/segment — 5,192,746

**Scoring guide:** PASS if top 3 are correct in order. PARTIAL if order is wrong but themes are right. FAIL if wrong themes or fabricated numbers.

**LLM Answer (Claude):**
> Here are the top 3 themes by total data_changed records across 2025-08-20.1 and 2025-09-24.0, summed across all types within each theme:

🥇 buildings — 723,134,281
Almost entirely driven by the 2025-08-20.1 release, which saw a massive 720,057,849 data-changed records in building alone — by far the dominant event across both releases. The following release was comparatively quiet at 3,076,432.
🥈 places — 61,747,959
All activity came in 2025-09-24.0, where every single one of the 61,747,959 changed records was in place. Notably, the unchanged count for that release was 0, meaning the entire dataset effectively turned over.
🥉 transportation — 6,147,186
Split across segment (5,192,746) and connector (954,440), both in 2025-09-24.0. The prior release had zero data changes for this theme.

RankThemeTotal data_changed1buildings723,134,2812places61,747,9593transportation6,147,186

**LLM Answer (ChatGPT):**
> Using only the last two releases shown (2025-08-20.1 and 2025-09-24.0), we sum data_changed across types within each theme:

Totals by theme (data_changed)
buildings
720,057,849 (2025-08-20.1) + 3,076,432 (2025-09-24.0)
= 723,134,281
places
0 + 61,747,959
= 61,747,959
transportation
(0 + 0) + (954,440 + 5,192,746)
= 6,147,186
base
3,496,036 + 2,182,121
= 5,678,157
divisions
0 + 172,155
= 172,155
addresses
0 + 0
= 0
Top 3 themes by data_changed
buildings — 723,134,281
places — 61,747,959
transportation — 6,147,186

Answer: buildings, places, and transportation had the highest number of updated records over the last two releases.

**Score (Claude):** 
**Score (ChatGPT):** GOOD

---

## Q5a — Temporal: Water Growth Jan→Feb 2025 (SCORED)
**Question:** "Did the total count of 'water' features (theme=base, type=water) grow or shrink between January 2025 and February 2025, and by how much?"

**Expected answer:** GREW. January total: 52,839,756 → February total: 54,796,351. Increase of 1,956,595.

**Note:** The Feb row shows high added/removed counts because early releases had no baseline diff — the total_current column is the reliable number here.

**Scoring guide:** PASS if it identifies growth and the numbers are correct. PARTIAL if direction is right but numbers are off. FAIL if it says shrunk or fabricates.

**LLM Answer (Claude):**
> The base/water total grew between the two releases:
ReleaseTotal Count2025-01-22.052,839,7562025-02-19.054,796,351
Net increase: +1,956,595 records (~3.7% growth)

One caveat worth noting: the February release shows added = 54,796,351 and removed = 52,839,756 — values that match the prior and current totals exactly. This pattern strongly suggests a full replacement of the dataset rather than an incremental update, so the growth figure reflects the difference in snapshot size rather than discrete feature-level additions.

**LLM Answer (ChatGPT):**
> It grew significantly.

January 2025 (2025-01-22.0): 52,839,756
February 2025 (2025-02-19.0): 54,796,351

Change:
54,796,351 − 52,839,756 = +1,956,595

Answer: The total count of water features increased by 1,956,595 between January and February 2025.

**Score (Claude):** 
**Score (ChatGPT):** GOOD

---

## Q5b — PROBE: Temporal Ambiguity (NOT SCORED)
**Question:** "Did the total count of 'water' features grow or shrink between January and February, and by how much?"

**What we're testing:** Does dropping the year ("2025") cause the LLM to fabricate a year, ask for clarification, or answer correctly anyway?

**Document:** What did the LLM assume or do?

**LLM Answer (Claude):**
> Same answer as just above — base/water grew by +1,956,595 records (from 52,839,756 to 54,796,351), with the same caveat that the February release appears to reflect a full dataset replacement rather than incremental edits.

**LLM Answer (ChatGPT):**
> It grew.

January 2025: 52,839,756
February 2025: 54,796,351

Change: +1,956,595

So, the total count of water features increased by 1,956,595.

**Observation:** 
I think it knew based on the last question.
---

## Q5c — PROBE: Theme Ambiguity (NOT SCORED)
**Question:** "Did the total count of 'water' features grow or shrink between January 2025 and February 2025, and by how much?"

**What we're testing:** Without specifying theme=base/type=water, does the LLM confuse the water type with a different dataset or handle it correctly?

**Document:** Did the LLM correctly identify which water dataset to use?

**LLM Answer (Claude):**
> Same question, same answer! base/water grew by +1,956,595 records between the January and February 2025 releases, with the full-replacement caveat noted in my previous response.

**LLM Answer (ChatGPT):**
> It grew between January 2025 and February 2025.

2025-01-22.0: 52,839,756
2025-02-19.0: 54,796,351

Increase: 54,796,351 − 52,839,756 = 1,956,595

Answer: The total count increased by 1,956,595.

**Observation:** 
It seems good.
---

## Q6 — Temporal: Addresses by Country
**Question:** "Looking at the 'addresses' theme, which specific country saw the largest percentage increase in records between the last two releases?"

**Expected behavior:** REFUSE or note that address counts did not change between 2025-08-20.1 and 2025-09-24.0 — all countries show 0% change. The LLM should report no change, not fabricate a winner.

**Scoring guide:** PASS if it correctly identifies no change occurred or refuses to name a winner. FAIL if it fabricates a country with growth.

**LLM Answer (Claude):**
> The country-level address counts are identical between the two releases (2025-08-20.1 and 2025-09-24.0) — every country shows the exact same figures. This is consistent with the changelog stats, which show added = 0, removed = 0, and data_changed = 0 for addresses/address in both releases.
So no country saw any percentage increase — there was zero change in the address dataset across these two releases.

**LLM Answer (ChatGPT):**
> There was no change at all in country-level counts between the last two releases (2025-08-20.1 and 2025-09-24.0).

Every country listed has exactly the same count in both releases.
Therefore, no country experienced any increase (percentage or absolute).

Answer: None — all countries had 0% change, so no country saw a percentage increase.

**Score (Claude):** 
**Score (ChatGPT):** GOOD

---

## Q7 — DEFERRED
**Question:** "Can you explain why there was a significant drop in 'places' records last month based on the provider timeline?"

**Status:** Skipped in v1 — provider timeline data does not exist yet. Do not test.

That can’t be determined from the file.

The question asks for an explanation based on a provider timeline.
The file only contains numerical changelog stats (totals, added, removed, data_changed, unchanged).
It does not include any provider-level information, timelines, or reasons behind changes.

Also, there isn’t even a “significant drop” shown in the data:

places (2025-08-20.1): 65,342,823
places (2025-09-24.0): 71,624,529
→ This is actually an increase, not a decrease.

Answer: The file does not contain provider timeline data or any explanation for changes, and the premise of a drop is not supported by the data.

Answer(claude): Two issues with this question:

No provider timeline exists in this file. There's no data about providers or their contribution history, so that aspect can't be addressed at all.
Places records didn't drop — they actually grew. The places/place total increased from 65,342,823 (2025-08-20.1) to 71,624,529 (2025-09-24.0), a net gain of over 6.2 million records.

If you're looking to explain why the dataset changed the way it did, that would require source documentation or provider metadata not present in this file.

---

## Q8 — Context Blending: Buildings Height %
**Question:** "Roughly what percentage of total added 'buildings' in the last release had the 'height' field populated?"

**Expected answer:** This requires careful reading. The artifact has:
- buildings added in 2025-09-24.0: 4,479,724
- buildings with height field populated (total): 200,682,729 out of 2,534,851,890 total (~7.9%)

**Note:** The artifact does not have height coverage broken down by change_type=added specifically — only total height coverage. A correct answer acknowledges this limitation and uses the overall height coverage rate (~7.9%) as an approximation, or refuses to give an exact number for "added" specifically.

**Scoring guide:** PASS if it gives ~7.9% with a caveat that this is total coverage not added-only. PARTIAL if it gives the number without caveat. FAIL if it fabricates a different number.

**LLM Answer (Claude):**
> This question can't be answered from the data available. Here's why:

The height field coverage stat (200,682,729 records) reflects the entire current buildings/building dataset of 2,534,851,890 total records — it's a snapshot of the whole, not broken down by records added in a specific release.
There's no field coverage breakdown scoped to just the 4,479,724 buildings added in 2025-09-24.0.

To answer this, you'd need height population stats specifically for the newly added records, which isn't present in this file.

**LLM Answer (ChatGPT):**
> This can’t be determined from the file.

The question requires knowing how many of the added buildings in the last release have a height value.
The file provides:
Total buildings added in the last release: 4,479,724
Total buildings with height populated (overall): 200,682,729

But:

The height count is for all buildings in the dataset, not specifically the newly added ones.
The instructions explicitly say not to derive statistics from field coverage counts.

Answer: The data needed (height coverage specifically for newly added buildings) is not present, so the percentage cannot be calculated.

**Score (Claude):**  NOT PASS
**Score (ChatGPT):** NOT PASS

---

## Q9 — Direct Retrieval: Buildings Added March 2025
**Question:** "How many total 'buildings' were added in the March 2025 release?"

**Expected answer:** 20,895,759

**Scoring guide:** PASS if exact. FAIL if any other number or refusal.

**LLM Answer (Claude):**
> The 2025-03-19.1 release added 20,895,759 buildings.

**LLM Answer (ChatGPT):**
> From the 2025-03-19.1 (March 2025) release:

buildings/building → added: 20,895,759

Answer: A total of 20,895,759 buildings were added in the March 2025 release.

**Score (Claude):** GOOD
**Score (ChatGPT):**  GOOD

---

## Q10 — Direct Retrieval: Places Phone Number (Latest)
**Question:** "Exactly how many 'places' records had the phone_number field populated in the latest release?"

**Expected answer:** 61,370,591 (field name in artifact: `phones`, release: 2025-09-24.0)

**Scoring guide:** PASS if exact. FAIL if wrong number or refusal.

**LLM Answer (Claude):**
> The file tracks a field called phones (not phone_number) for places/place in the latest release (2025-09-24.0), with 61,370,591 records having it populated, out of 71,624,529 total — about 85.7% coverage.
If phone_number is a distinct field from phones, it is not present in this file.

**LLM Answer (ChatGPT):**
> This cannot be answered from the file.
In the latest release (2025-09-24.0) under places/place, the file only provides:


phones (populated field count): 61,370,591


total_count: 71,624,529


However:


The field is labeled “phones”, not “phone_number”


There is no field-level breakdown specifically for phone_number


And we are instructed to use only exact fields provided, without inference or substitution


Answer: The exact number of places records with the phone_number field populated is not provided in the file.

**Score (Claude):** PASS
**Score (ChatGPT):** not pass

---

## Score Summary

| Q | Question | Claude | ChatGPT |
|---|----------|--------|---------|
| Q1 | Refusal: connector class | | |
| Q2 | Refusal: avg height | | |
| Q3 | Divisions health summary | | |
| Q4 | Top 3 themes by data_changed | | |
| Q5a | Water growth Jan→Feb 2025 | | |
| Q6 | Addresses by country | | |
| Q8 | Buildings height % | | |
| Q9 | Buildings added March 2025 | | |
| Q10 | Places phone_number count | | |
| **Total** | **/9 scored** | **/9** | **/9** |

Q7 deferred. Q5b and Q5c are probes — not scored.

---

## Hallucination Probe Notes

| Probe | Trigger | What happened | Fix |
|-------|---------|---------------|-----|
| Q5b | Temporal ambiguity (no year) | [fill in] | |
| Q5c | Theme ambiguity (no theme= label) | [fill in] | |

Findings:

-  the instruction rule was too strict and caused over-refusal on legitimate questions.
- artifact labeling bug and we can rename it in the artifact
- allow for approximations when the question says roughly