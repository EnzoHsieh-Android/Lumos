# 判定者派工詞(2026-09-27 小實驗實際用的那份,兩席逐字相同,只差模型)

You are classifying sentences taken from a project's knowledge notes. The project's code is at /Users/enzo/rtb-mainwt (Python, source under src/rtb/, tests under tests/). Read-only: do not modify any file in that repo.

Input: judge_input.md — 68 numbered sentences, each prefixed with the note it came from in [brackets]. Sentences are short paraphrases, in Chinese.

For EACH sentence decide one label:
- CODE — everything the sentence asserts is about what the code/tests/config currently do, contain, or lack (values, flags, counts of things in the repo, which function calls what, "there is no guard for X", "only N kinds of Y"). A reader with only the current repository (no notes, no git history, no running anything) could confirm or refute it. The sentence may be TRUE OR FALSE today — judge the TYPE of claim, not whether it is correct.
- CONTEXT — asserts something reading the current code cannot establish: why a choice was made, rejected alternatives, incidents, external/legal/business constraints, intentions and goals, results that require running something (timings, test pass counts from a run), plans.
- MIXED — contains both; say which part is CODE and which is CONTEXT.

For CODE and MIXED you must cite at least one file:line in /Users/enzo/rtb-mainwt that confirms or refutes the code part (open the file and check — do not guess). If you cannot find any code location after a genuine search, say so and lower confidence.

Output: a markdown table with columns: n | label | confidence (high/med/low) | code location (or —) | one-line reason. Then a count per label.
