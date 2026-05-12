:- discontiguous has_section/2.
:- discontiguous context_mentions/2.
:- discontiguous artifact_has_column/2.
:- discontiguous artifact_missing_count/3.
:- discontiguous artifact_total_rows/2.
:- discontiguous context_gap/4.
:- discontiguous issue/3.
:- discontiguous evidence/4.

% Facts derived from the past teams context file
has_section(file1, instructions).
evidence(file1, context_section, "instructions", "Context line 8: <<<INSTRUCTIONS_START>>>").
has_section(file1, schema).
evidence(file1, context_section, "schema", "Context line 87: <<<SCHEMA_START>>>").
has_section(file1, prompts).
evidence(file1, context_section, "prompts", "Context line 675: <<<PROMPTS_START>>>").
has_section(file1, theme_statistics).
evidence(file1, context_section, "theme_statistics", "Context line 230: ## THEME STATISTICS: ADDRESSES").
evidence(file1, context_section, "theme_statistics", "Context line 306: ## THEME STATISTICS: BUILDINGS").
evidence(file1, context_section, "theme_statistics", "Context line 376: ## THEME STATISTICS: PLACES").
evidence(file1, context_section, "theme_statistics", "Context line 439: ## THEME STATISTICS: DIVISIONS").
evidence(file1, context_section, "theme_statistics", "Context line 522: ## THEME STATISTICS: TRANSPORTATION").
context_mentions(file1, Total_Features).
evidence(file1, context_pinpoint, "Total Features", "Context line 233: **Total Features**: 445,932,761 addresses").
evidence(file1, context_pinpoint, "Total Features", "Context line 309: **Total Features**: 5,076,549,472 buildings").
evidence(file1, context_pinpoint, "Total Features", "Context line 379: **Total Features**: 143,249,058 places").
evidence(file1, context_pinpoint, "Total Features", "Context line 442: **Total Features**: 11,178,066 divisions").
evidence(file1, context_pinpoint, "Total Features", "Context line 525: **Total Features**: 1,428,054,092 features").
evidence(file1, context_pinpoint, "Total Features", "Context line 591: **Total Features**: 763,872,793 features").
context_mentions(file1, SCHEMA_REFERENCE).
evidence(file1, context_pinpoint, "SCHEMA REFERENCE", "Context line 88: ## SCHEMA REFERENCE - GROUPING COLUMNS").
evidence(file1, context_pinpoint, "SCHEMA REFERENCE", "Context line 723: - Schema Reference: https://docs.overturemaps.org/schema/reference/").
context_mentions(file1, Coverage_varies_significantly).
evidence(file1, context_pinpoint, "Coverage varies significantly", "Context line 47: - Coverage varies significantly by country").
context_mentions(file1, address_level_1).
evidence(file1, context_pinpoint, "address_level_1", "Context line 46: - Includes hierarchical administrative levels (address_level_1, 2, 3)").
evidence(file1, context_pinpoint, "address_level_1", "Context line 122: **address_level_1**").
context_mentions(file1, address_level_2).
evidence(file1, context_pinpoint, "address_level_2", "Context line 128: **address_level_2**").
context_mentions(file1, address_level_3).
evidence(file1, context_pinpoint, "address_level_3", "Context line 134: **address_level_3**").

% Optional facts derived from artifact JSON ground truth
% Artifact file not found. Artifact-vs-context gap checks are disabled.

% ── QUESTION SUPPORT RULES 
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
