# Validation Patterns

## DAB Validator Shape

Each `queryN/validate.py` must define:

```python
def validate(llm_output: str):
    ...
    return True, "reason"
```

Return `(False, reason)` when expected values are missing.

## String or Set Answer

Use substring checks for deterministic names, codes, and IDs.

```python
def validate(llm_output: str):
    expected = ["Crossfit_Hanna", "18657.35"]
    missing = [value for value in expected if value.lower() not in llm_output.lower()]
    if missing:
        return False, "Missing expected value(s): " + ", ".join(missing)
    return True, "Found expected values."
```

## Numeric Answer

Extract numbers and compare with tolerance. Handle commas.

```python
import re

def contains_number(text: str, expected: float, tolerance: float = 0.01) -> bool:
    for raw in re.findall(r"\b[\d,]+(?:\.\d+)?\b", text):
        try:
            if abs(float(raw.replace(",", "")) - expected) <= tolerance:
                return True
        except ValueError:
            pass
    return False
```

## Set-Valued Answer

For a list of IDs/names, require every expected element. DAB validators usually favor recall over precision; do not reject extra text unless the user explicitly wants stricter validation.

## What Not To Do

- Do not read source data or clean DB from `validate.py`.
- Do not call LLMs or internet.
- Do not use nondeterministic checks.
- Do not require exact formatting unless the query is explicitly about format.
