

project_goal("Using context files, optimize prompt engineering. Using Files from ").

% Python will assert these facts at runtime:
% context_file(File).
% file_name(File, Name).
% has_section(File, Section).
% issue(File, Issue, Rubric, Risk, Fix).
% evidence(File, Category, Term, Evidence).

:- dynamic context_file/1.
:- dynamic file_name/2.
:- dynamic has_section/2.
:- dynamic issue/5.
:- dynamic evidence/4.

supported(File, q1_schema) :-
    has_section(File, schema),
    !.

supported(File, q2_statistics) :-
    has_section(File, statistics),
    !.

supported(File, q3_coverage) :-
    has_section(File, coverage),
    !.

supported(File, q4_missing_data) :-
    has_section(File, missing_data),
    !.

supported(File, q5_version) :-
    has_section(File, version),
    !.

supported(File, q6_prompt_examples) :-
    has_section(File, examples),
    !.

supported(File, q7_unsupported) :-
    has_section(File, unsupported_guidance),
    !.

risky(File, q4_missing_data) :-
    issue(File, missing_data_guidance_weak, _, _, _),
    !.

risky(File, q3_coverage) :-
    issue(File, coverage_guidance_weak, _, _, _),
    !.

risky(File, q5_version) :-
    issue(File, versioning_weak, _, _, _),
    !.

risky(File, q6_prompt_examples) :-
    issue(File, example_prompts_missing, _, _, _),
    !.

risky(File, q7_unsupported) :-
    issue(File, unsupported_questions_not_explained, _, _, _),
    !.

unsupported(File, q7_unsupported) :-
    \+ has_section(File, unsupported_guidance),
    !.

prompt_fix(q1_schema,
"Using only this context file, summarize what schema, column, field, or attribute information it provides. If something is not explained, say it is not explained in the file.").

prompt_fix(q2_statistics,
"Using only this context file, list the dataset statistics it provides. Do not calculate new totals unless the file explicitly gives enough information.").

prompt_fix(q3_coverage,
"Using only this context file, explain what coverage limitations are stated. Mention geography, sources, themes, or availability only if the file states them.").

prompt_fix(q4_missing_data,
"Using only this context file, explain what it says about missing or incomplete data. Do not guess causes that the file does not state.").

prompt_fix(q5_version,
"Before answering, identify the release, version, date, or generation time from this context file. Answer only for that stated release or date.").

prompt_fix(q6_prompt_examples,
"Use this context file as reference material. Write a specific prompt that tells the LLM what information to rely on and what not to guess.").

prompt_fix(q7_unsupported,
"Ask: What can this context file not support? If the file does not state something, say 'not stated in the context file' instead of guessing.").
