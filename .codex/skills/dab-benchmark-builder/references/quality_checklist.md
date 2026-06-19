# Quality Checklist

Before calling a generated DAB dataset ready, verify:

- Clean DB exists and ground truth was computed from it.
- Visible DBs exist and are referenced by `db_config.yaml`.
- Visible split uses at least two logical DBs and no repeated DBMS type unless explicitly marked as a legacy/simple variant.
- `db_description.txt` matches actual visible DB schemas.
- `db_description.txt` follows DAB prose format and contains no "Useful links", explicit join map, physical paths, or solve strategy.
- `db_description_withhint.txt` is hints-only: it starts with `HINTS:`, includes necessary semantic conventions, and has no repeated database description, schema listing, solve strategy, or answer leaks.
- Each query is natural language, not SQL instructions.
- Each query requires at least two logical DBs from `db_config.yaml`.
- Each query requires key normalization/fuzzy matching, text extraction/classification, domain knowledge/formula, semi-structured parsing, or another documented semantic transformation.
- Each query has a unique deterministic answer or explicit tie-breaker.
- Each `validate.py` imports and returns `(bool, reason)`.
- `verify_visible_solve.py` solves from visible DBs only.
- `compute_ground_truth.py` and `verify_visible_solve.py` agree.
- Logs, caches, and clean/source-only files are not in the final DAB-facing package.

Difficulty sanity:

- If a weak agent gets 5/5 repeatedly, consider reducing hints or adding a more compositional task.
- If a strong agent gets 5/5 repeatedly, inspect whether clean keys, same-DBMS splits, direct answer columns, or explicit join maps made the task too direct.
- If a weak agent gets 0/5, inspect for underspecified formulas, hidden tie-breaks, brittle parsing, or excessive composition.
- For RL training, 1-3/5 on harder tasks can be acceptable.
