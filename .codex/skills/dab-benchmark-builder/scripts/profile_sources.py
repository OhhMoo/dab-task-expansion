#!/usr/bin/env python3
"""Profile local source data without loading full datasets into memory."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


NULL_STRINGS = {"", "null", "none", "nan", "na", "n/a"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?)?$")


def qident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def normalize_col(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def scalar_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, (list, dict)):
        return type(value).__name__
    text = str(value).strip()
    if text.lower() in NULL_STRINGS:
        return "null"
    if text.lower() in {"true", "false"}:
        return "bool"
    try:
        int(text)
        return "int"
    except ValueError:
        pass
    try:
        float(text)
        return "float"
    except ValueError:
        pass
    if DATE_RE.match(text):
        return "date"
    return "text"


def summarize_rows(rows: list[dict[str, Any]], columns: list[str] | None = None) -> dict[str, Any]:
    if columns is None:
        seen: list[str] = []
        for row in rows:
            for key in row:
                if key not in seen:
                    seen.append(key)
        columns = seen

    summaries: list[dict[str, Any]] = []
    for col in columns:
        values = [row.get(col) for row in rows]
        type_counts = Counter(scalar_type(value) for value in values)
        non_null_values = [
            "" if value is None else str(value)
            for value in values
            if scalar_type(value) != "null"
        ]
        examples: list[str] = []
        for value, _count in Counter(non_null_values).most_common():
            if value not in examples:
                examples.append(value)
            if len(examples) >= 5:
                break
        summaries.append(
            {
                "name": col,
                "normalized_name": normalize_col(col),
                "sample_non_null": len(non_null_values),
                "sample_null": len(values) - len(non_null_values),
                "type_counts": dict(type_counts),
                "examples": examples,
            }
        )
    return {"columns": summaries, "sample_rows": rows[:3], "sample_row_count": len(rows)}


def read_csv_sample(path: Path, sample_rows: int) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        prefix = handle.read(8192)
        handle.seek(0)
        delimiter = "\t" if path.suffix.lower() == ".tsv" else None
        if delimiter is None:
            try:
                dialect = csv.Sniffer().sniff(prefix)
            except csv.Error:
                dialect = csv.excel
        else:
            dialect = csv.excel_tab
        reader = csv.DictReader(handle, dialect=dialect)
        rows = []
        for row in reader:
            rows.append(dict(row))
            if len(rows) >= sample_rows:
                break
    profile = summarize_rows(rows, list(reader.fieldnames or []))
    profile.update({"kind": "csv", "delimiter": getattr(dialect, "delimiter", ",")})
    return profile


def read_jsonl_sample(path: Path, sample_rows: int) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_no}: {exc}")
                continue
            rows.append(obj if isinstance(obj, dict) else {"value": obj})
            if len(rows) >= sample_rows:
                break
    profile = summarize_rows(rows)
    profile.update({"kind": "jsonl", "errors": errors[:5]})
    return profile


def read_json_sample(path: Path, sample_rows: int, max_json_bytes: int) -> dict[str, Any]:
    if path.stat().st_size > max_json_bytes:
        return {
            "kind": "json",
            "skipped": True,
            "reason": f"larger than max JSON load limit ({max_json_bytes} bytes)",
            "columns": [],
            "sample_rows": [],
            "sample_row_count": 0,
        }
    with path.open("r", encoding="utf-8") as handle:
        obj = json.load(handle)
    if isinstance(obj, list):
        raw_rows = obj[:sample_rows]
    elif isinstance(obj, dict):
        raw_rows = None
        for key, value in obj.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                raw_rows = value[:sample_rows]
                break
        if raw_rows is None:
            raw_rows = [obj]
    else:
        raw_rows = [{"value": obj}]
    rows = [row if isinstance(row, dict) else {"value": row} for row in raw_rows]
    profile = summarize_rows(rows)
    profile.update({"kind": "json"})
    return profile


def read_sqlite_profile(path: Path, sample_rows: int) -> dict[str, Any]:
    tables: list[dict[str, Any]] = []
    uri = f"file:{path}?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        conn.row_factory = sqlite3.Row
        table_rows = conn.execute(
            "select name, type from sqlite_master where type in ('table', 'view') order by name"
        ).fetchall()
        for table_row in table_rows:
            table_name = str(table_row["name"])
            cols = conn.execute(f"pragma table_info({qident(table_name)})").fetchall()
            column_names = [str(col["name"]) for col in cols]
            rows = [
                dict(row)
                for row in conn.execute(
                    f"select * from {qident(table_name)} limit ?", (sample_rows,)
                ).fetchall()
            ]
            summary = summarize_rows(rows, column_names)
            tables.append(
                {
                    "database_file": str(path),
                    "table": table_name,
                    "relation_type": str(table_row["type"]),
                    "declared_columns": [
                        {
                            "name": str(col["name"]),
                            "type": str(col["type"]),
                            "pk": bool(col["pk"]),
                            "not_null": bool(col["notnull"]),
                        }
                        for col in cols
                    ],
                    **summary,
                }
            )
    return {"kind": "sqlite", "tables": tables}


def read_duckdb_profile(path: Path, sample_rows: int) -> dict[str, Any]:
    try:
        import duckdb  # type: ignore
    except ImportError:
        return {"kind": "duckdb", "skipped": True, "reason": "duckdb module is not installed"}

    tables: list[dict[str, Any]] = []
    conn = duckdb.connect(str(path), read_only=True)
    try:
        table_rows = conn.execute("show tables").fetchall()
        for (table_name,) in table_rows:
            table_name = str(table_name)
            desc_rows = conn.execute(f"describe {qident(table_name)}").fetchall()
            column_names = [str(row[0]) for row in desc_rows]
            data_rows = conn.execute(
                f"select * from {qident(table_name)} limit {int(sample_rows)}"
            ).fetchall()
            rows = [dict(zip(column_names, row)) for row in data_rows]
            summary = summarize_rows(rows, column_names)
            tables.append(
                {
                    "database_file": str(path),
                    "table": table_name,
                    "relation_type": "table",
                    "declared_columns": [
                        {"name": str(row[0]), "type": str(row[1])} for row in desc_rows
                    ],
                    **summary,
                }
            )
    finally:
        conn.close()
    return {"kind": "duckdb", "tables": tables}


def collect_files(source: Path) -> list[Path]:
    if source.is_file():
        return [source]
    return sorted(path for path in source.rglob("*") if path.is_file())


def profile_file(path: Path, sample_rows: int, max_json_bytes: int) -> dict[str, Any]:
    suffix = path.suffix.lower()
    base: dict[str, Any] = {
        "path": str(path),
        "name": path.name,
        "suffix": suffix,
        "size_bytes": path.stat().st_size,
    }
    try:
        if suffix in {".csv", ".tsv"}:
            base.update(read_csv_sample(path, sample_rows))
        elif suffix == ".jsonl":
            base.update(read_jsonl_sample(path, sample_rows))
        elif suffix == ".json":
            base.update(read_json_sample(path, sample_rows, max_json_bytes))
        elif suffix in {".sqlite", ".sqlite3", ".db"}:
            base.update(read_sqlite_profile(path, sample_rows))
        elif suffix == ".duckdb":
            base.update(read_duckdb_profile(path, sample_rows))
        else:
            base.update({"kind": "unsupported", "columns": [], "sample_rows": []})
    except Exception as exc:  # pragma: no cover - profiling should report and continue.
        base.update({"kind": "error", "error": repr(exc), "columns": [], "sample_rows": []})
    return base


def relation_entries(profile: dict[str, Any]) -> list[dict[str, Any]]:
    if "tables" in profile:
        return [
            {
                "source": profile["path"],
                "relation": table["table"],
                "kind": profile["kind"],
                "columns": table.get("columns", []),
                "sample_row_count": table.get("sample_row_count", 0),
            }
            for table in profile["tables"]
        ]
    if profile.get("columns"):
        return [
            {
                "source": profile["path"],
                "relation": Path(profile["path"]).stem,
                "kind": profile["kind"],
                "columns": profile.get("columns", []),
                "sample_row_count": profile.get("sample_row_count", 0),
            }
        ]
    return []


def find_column_overlaps(relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_col: dict[str, list[str]] = defaultdict(list)
    for relation in relations:
        label = f"{Path(relation['source']).name}:{relation['relation']}"
        for col in relation.get("columns", []):
            normalized = col.get("normalized_name") or normalize_col(col.get("name", ""))
            if normalized:
                by_col[normalized].append(label)
    overlaps = []
    for col, labels in sorted(by_col.items()):
        unique_labels = sorted(set(labels))
        if len(unique_labels) > 1:
            overlaps.append({"normalized_column": col, "relations": unique_labels})
    return overlaps


def write_markdown(report: dict[str, Any], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# Source Data Profile")
    lines.append("")
    lines.append(f"- Source: `{report['source']}`")
    lines.append(f"- Files scanned: {len(report['files'])}")
    lines.append(f"- Sample rows per relation: {report['sample_rows']}")
    lines.append("")

    lines.append("## Files")
    lines.append("")
    for file_profile in report["files"]:
        lines.append(f"### `{file_profile['path']}`")
        lines.append("")
        lines.append(f"- Kind: {file_profile.get('kind')}")
        lines.append(f"- Size: {file_profile.get('size_bytes')} bytes")
        if file_profile.get("skipped"):
            lines.append(f"- Skipped: {file_profile.get('reason')}")
        if file_profile.get("error"):
            lines.append(f"- Error: `{file_profile.get('error')}`")
        if file_profile.get("tables"):
            for table in file_profile["tables"]:
                lines.append("")
                lines.append(f"#### Table `{table['table']}`")
                lines.extend(format_columns(table.get("columns", [])))
        elif file_profile.get("columns"):
            lines.extend(format_columns(file_profile.get("columns", [])))
        lines.append("")

    if report["column_overlaps"]:
        lines.append("## Possible Join/Link Columns")
        lines.append("")
        for overlap in report["column_overlaps"][:100]:
            rels = ", ".join(f"`{rel}`" for rel in overlap["relations"])
            lines.append(f"- `{overlap['normalized_column']}`: {rels}")
        lines.append("")

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def format_columns(columns: list[dict[str, Any]]) -> list[str]:
    if not columns:
        return ["", "No sampled columns."]
    lines = ["", "| Column | Sample types | Examples |", "| --- | --- | --- |"]
    for col in columns:
        type_counts = ", ".join(f"{key}:{value}" for key, value in col["type_counts"].items())
        examples = "; ".join(str(value).replace("|", "\\|") for value in col["examples"])
        lines.append(f"| `{col['name']}` | {type_counts} | {examples} |")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Source file or directory to profile")
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    parser.add_argument("--sample-rows", type=int, default=25)
    parser.add_argument("--max-json-mb", type=float, default=5.0)
    args = parser.parse_args()

    source = args.source.resolve()
    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    files = collect_files(source)
    profiles = [
        profile_file(path, args.sample_rows, int(args.max_json_mb * 1024 * 1024))
        for path in files
    ]
    relations = []
    for profile in profiles:
        relations.extend(relation_entries(profile))

    report = {
        "source": str(source),
        "sample_rows": args.sample_rows,
        "files": profiles,
        "relations": relations,
        "column_overlaps": find_column_overlaps(relations),
    }

    (out_dir / "schema_profile.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    write_markdown(report, out_dir / "schema_profile.md")
    print(f"Wrote {out_dir / 'schema_profile.json'}")
    print(f"Wrote {out_dir / 'schema_profile.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
