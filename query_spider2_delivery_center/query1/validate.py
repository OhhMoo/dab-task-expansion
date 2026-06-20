import csv
import re
import unicodedata
from pathlib import Path


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("&", " and ").replace("@", " at ")
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")
    text = re.sub(r"[^a-z0-9\s:./|-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _is_number(value: str) -> bool:
    return re.fullmatch(r"[-+]?\d+(?:\.\d+)?", str(value).replace(",", "")) is not None


def _numbers(text: str) -> list[float]:
    values = []
    text = str(text).replace("−", "-").replace("–", "-").replace("—", "-")
    for raw in re.findall(r"(?<![A-Za-z0-9_.])-?(?:\d{1,3}(?:,\d{3})+)(?:\.\d+)?(?![A-Za-z0-9_.])", text):
        try:
            values.append(float(raw.replace(",", "")))
        except ValueError:
            pass
    for raw in re.findall(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?(?![A-Za-z0-9_.])", text.replace(",", " ")):
        try:
            values.append(float(raw))
        except ValueError:
            pass
    return values


def _contains_number(text: str, expected: str) -> bool:
    target = float(str(expected).replace(",", ""))
    tolerance = 0.04 if abs(target - round(target)) > 1e-9 else 0.001
    return any(abs(value - target) <= tolerance for value in _numbers(text))


def validate(llm_output: str):
    rows = list(csv.DictReader(Path(__file__).with_name("ground_truth.csv").open(newline="", encoding="utf-8")))
    norm_output = _norm(llm_output)
    missing = []
    for row in rows:
        for value in row.values():
            value = str(value).strip()
            if not value:
                continue
            if _is_number(value):
                if not _contains_number(llm_output, value):
                    missing.append(value)
            elif _norm(value) not in norm_output:
                missing.append(value)
    if missing:
        return False, "Missing expected value(s): " + ", ".join(missing[:12])
    return True, "Found expected value(s)."
