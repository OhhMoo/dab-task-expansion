# DAB Artifact Contract

## Required Structure

```text
query_<dataset>/
  db_config.yaml
  db_description.txt
  db_description_withhint.txt
  query_dataset/
    ...
  query1/
    query.json
    ground_truth.csv
    validate.py
```

Use `query1`, `query2`, etc. with contiguous numeric IDs unless extending an existing dataset.

## DB Config

`db_config.yaml` must use logical DB names that match `db_description.txt`.

Example:

```yaml
db_clients:
  facts_db:
    db_type: duckdb
    db_path: query_dataset/facts.duckdb
  context_db:
    db_type: sqlite
    db_path: query_dataset/context.db
```

Supported scaffold types include `sqlite`, `duckdb`, `postgres`, and `mongo`.

Generated DAB-style datasets must use at least two logical databases with different `db_type` values. Do not use two SQLite files, two DuckDB files, or any repeated DBMS type for the visible split unless the user explicitly requests a legacy/simple variant.

Artifact path keys by DBMS:

- `sqlite`: `db_path`
- `duckdb`: `db_path`
- `postgres`: `sql_file`
- `mongo`: `dump_folder`

`db_description.txt` must describe each logical database in DAB's prose format. It should not include physical paths, SQL examples, "Useful links", or an explicit join-key map.

`db_description_withhint.txt` must contain only hints. In the original DAB runner, this file is appended to `db_description.txt` when `--use_hints` is enabled, so it must not repeat the database descriptions or schema. It should normally start with `HINTS:`.

## Query Folder Contract

`query.json` may be a JSON string or an object with a `query` field. Prefer a JSON string for consistency with current generated datasets.

`ground_truth.csv` should contain exactly the deterministic answer values expected by the validator. Keep it simple: a line such as `Crossfit_Hanna,18657.35` is fine.

`validate.py` must expose:

```python
def validate(llm_output: str):
    ...
    return bool_value, "reason"
```

## Local-Only Files

Keep these out of DAB-facing packages unless explicitly requested:

```text
clean/
logs/
query*/logs/
__pycache__/
*.pyc
```

`manual_querycode/` is optional. Include it when provenance/reproducibility matters; omit it for a minimal task-only package.

## Readiness Checks

A dataset is ready to hook into DAB when:

- `db_config.yaml` paths exist.
- At least two logical DBs exist and their DBMS types are different.
- Every logical DB is described.
- `db_description.txt` has no "Useful links" or explicit join map section.
- `db_description_withhint.txt` is hints-only and does not repeat the database description.
- Every `queryN` has query, ground truth, and validator files.
- Every final query requires at least two logical DBs plus key repair, text extraction, domain knowledge/formula, or another documented semantic transformation.
- Validators import successfully.
- `manual_querycode/verify_visible_solve.py` passes if present.
- No final query requires `clean/` or source files.
