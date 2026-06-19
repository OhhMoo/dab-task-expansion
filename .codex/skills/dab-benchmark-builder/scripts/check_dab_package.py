#!/usr/bin/env python3
"""Check the local structure of a DAB-style generated dataset."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


QUERY_RE = re.compile(r"^query(\d+)$")


def load_db_clients(config_path: Path) -> dict[str, dict[str, object]]:
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None

    if yaml is not None:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        clients = data.get("db_clients") or {}
        if not isinstance(clients, dict):
            raise RuntimeError("db_clients must be a mapping")
        return {
            str(name): spec
            for name, spec in clients.items()
            if isinstance(spec, dict)
        }

    clients: dict[str, dict[str, object]] = {}
    current: str | None = None
    for line in config_path.read_text(encoding="utf-8").splitlines():
        client_match = re.match(r"\s{2}([A-Za-z0-9_ -]+)\s*:\s*$", line)
        if client_match:
            current = client_match.group(1).strip()
            clients[current] = {}
            continue
        match = re.match(r"\s{4}([A-Za-z0-9_]+)\s*:\s*(.+?)\s*$", line)
        if current and match:
            clients[current][match.group(1)] = match.group(2).strip().strip("'\"")
    return clients


def artifact_refs(spec: dict[str, object]) -> list[str]:
    db_type = str(spec.get("db_type", "")).strip()
    if db_type in {"sqlite", "duckdb"}:
        return [str(spec["db_path"])] if spec.get("db_path") else []
    if db_type == "postgres":
        return [str(spec["sql_file"])] if spec.get("sql_file") else []
    if db_type == "mongo":
        return [str(spec["dump_folder"])] if spec.get("dump_folder") else []
    refs = []
    for key in ["db_path", "sql_file", "dump_folder"]:
        if spec.get(key):
            refs.append(str(spec[key]))
    return refs


def expected_artifact_key(db_type: str) -> str:
    if db_type in {"sqlite", "duckdb"}:
        return "db_path"
    if db_type == "postgres":
        return "sql_file"
    if db_type == "mongo":
        return "dump_folder"
    return "db_path/sql_file/dump_folder"


def has_useful_links_section(text: str) -> bool:
    return bool(re.search(r"(?im)^\s*(#+\s*)?useful links\s*:?\s*$", text))


def has_explicit_join_map_section(text: str) -> bool:
    patterns = [
        r"(?im)^\s*(#+\s*)?(joins?|join keys?|links?|relationships?)\s*:?\s*$",
        r"(?im)^\s*-\s*[^:\n]+?\s*(->|links? to|joins? to)\s*[^:\n]+",
    ]
    return any(re.search(pattern, text) for pattern in patterns)


def looks_like_full_description(text: str) -> bool:
    patterns = [
        r"(?i)\byou are working with\b",
        r"(?i)\bhere are the descriptions of\b",
        r"(?im)^\s*\d+\.\s+[A-Za-z0-9_ -]+database\b",
        r"(?im)^\s*-\s+This database is stored in\b",
        r"(?im)^\s*-\s+This database consists of\b",
        r"(?im)^\s*-\s+Fields:\s*$",
    ]
    return any(re.search(pattern, text) for pattern in patterns)


def is_hints_only_file(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith("HINTS:") and not looks_like_full_description(stripped)


def query_dirs(dataset_dir: Path) -> list[Path]:
    dirs = []
    for child in dataset_dir.iterdir():
        match = QUERY_RE.match(child.name)
        if child.is_dir() and match:
            dirs.append(child)
    return sorted(dirs, key=lambda path: int(QUERY_RE.match(path.name).group(1)))  # type: ignore[union-attr]


def import_validator(path: Path):
    spec = importlib.util.spec_from_file_location(f"validator_{path.parent.name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    validate = getattr(module, "validate", None)
    if not callable(validate):
        raise RuntimeError("validate.py does not expose callable validate(llm_output)")
    return validate


def check_query_json(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, str):
        if not data.strip():
            raise RuntimeError("query.json is an empty string")
        return
    if isinstance(data, dict) and str(data.get("query", "")).strip():
        return
    raise RuntimeError("query.json must be a JSON string or an object with a non-empty query field")


def run_visible_verify(dataset_dir: Path) -> tuple[bool, str]:
    script = dataset_dir / "manual_querycode" / "verify_visible_solve.py"
    if not script.exists():
        return False, "manual_querycode/verify_visible_solve.py not found"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(dataset_dir),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return proc.returncode == 0, proc.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_dir", type=Path)
    parser.add_argument("--run-visible-verify", action="store_true")
    parser.add_argument(
        "--allow-repeated-dbms",
        action="store_true",
        help="Allow legacy/simple datasets whose visible DBs repeat a db_type.",
    )
    parser.add_argument(
        "--allow-useful-links",
        action="store_true",
        help="Allow legacy descriptions with explicit Useful links/join-map sections.",
    )
    args = parser.parse_args()

    dataset_dir = args.dataset_dir.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not dataset_dir.exists():
        print(f"ERROR: dataset directory does not exist: {dataset_dir}")
        return 1

    required_top = [
        "db_config.yaml",
        "db_description.txt",
        "db_description_withhint.txt",
        "query_dataset",
    ]
    for rel in required_top:
        if not (dataset_dir / rel).exists():
            errors.append(f"missing {rel}")

    config_path = dataset_dir / "db_config.yaml"
    if config_path.exists():
        try:
            db_clients = load_db_clients(config_path)
            if len(db_clients) < 2:
                errors.append("db_config.yaml must define at least two logical DB clients")

            db_types = []
            supported = {"sqlite", "duckdb", "postgres", "mongo"}
            for logical_name, spec in db_clients.items():
                db_type = str(spec.get("db_type", "")).strip()
                if not db_type:
                    errors.append(f"{logical_name} missing db_type")
                    continue
                db_types.append(db_type)
                if db_type not in supported:
                    errors.append(f"{logical_name} has unsupported db_type: {db_type}")

                key = expected_artifact_key(db_type)
                refs = artifact_refs(spec)
                if not refs:
                    errors.append(f"{logical_name} missing artifact path key for {db_type}: {key}")
                for ref in refs:
                    if not (dataset_dir / ref).exists():
                        errors.append(f"db_config artifact path does not exist for {logical_name}: {ref}")

            if not args.allow_repeated_dbms and len(db_types) != len(set(db_types)):
                errors.append(
                    "visible DB clients must use different db_type values; "
                    f"found {db_types}"
                )
        except Exception as exc:
            errors.append(f"could not parse db_config.yaml: {exc}")

    for description_name in ["db_description.txt", "db_description_withhint.txt"]:
        description_path = dataset_dir / description_name
        if description_path.exists():
            text = description_path.read_text(encoding="utf-8")
            if not args.allow_useful_links and has_useful_links_section(text):
                errors.append(f"{description_name} must not contain a Useful links section")
            if not args.allow_useful_links and has_explicit_join_map_section(text):
                errors.append(f"{description_name} must not contain an explicit join map")

    hint_path = dataset_dir / "db_description_withhint.txt"
    if hint_path.exists() and not is_hints_only_file(hint_path.read_text(encoding="utf-8")):
        errors.append(
            "db_description_withhint.txt must be hints-only: start with HINTS: "
            "and do not repeat db_description.txt/schema content"
        )

    qdirs = query_dirs(dataset_dir)
    if not qdirs:
        errors.append("no queryN directories found")

    expected_numbers = list(range(1, len(qdirs) + 1))
    actual_numbers = [int(QUERY_RE.match(path.name).group(1)) for path in qdirs]  # type: ignore[union-attr]
    if actual_numbers != expected_numbers:
        warnings.append(f"query directories are not contiguous from query1: {actual_numbers}")

    for qdir in qdirs:
        for filename in ["query.json", "ground_truth.csv", "validate.py"]:
            if not (qdir / filename).exists():
                errors.append(f"{qdir.name} missing {filename}")
        if (qdir / "query.json").exists():
            try:
                check_query_json(qdir / "query.json")
            except Exception as exc:
                errors.append(f"{qdir.name}/query.json invalid: {exc}")
        if (qdir / "ground_truth.csv").exists() and not (qdir / "ground_truth.csv").read_text(
            encoding="utf-8"
        ).strip():
            warnings.append(f"{qdir.name}/ground_truth.csv is empty")
        if (qdir / "validate.py").exists():
            try:
                import_validator(qdir / "validate.py")
            except Exception as exc:
                errors.append(f"{qdir.name}/validate.py invalid: {exc}")

    if args.run_visible_verify:
        ok, output = run_visible_verify(dataset_dir)
        if ok:
            print("visible verifier: PASS")
            if output:
                print(output)
        else:
            errors.append("visible verifier failed")
            if output:
                print(output)

    print(f"dataset: {dataset_dir}")
    print(f"queries: {len(qdirs)}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        print("status: FAIL")
        return 1
    print("status: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
