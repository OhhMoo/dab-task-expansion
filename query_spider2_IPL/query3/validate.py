import re


EXPECTED_STRINGS = ["P Parameswaran", "RS Bopara", "P Awana"]
EXPECTED_NUMBERS = [294, 501252, 37, 161, 419144, 33, 333, 734052]


def contains_number(text: str, expected: float, tolerance: float = 0.01) -> bool:
    for raw in re.findall(r"\b[\d,]+(?:\.\d+)?\b", text):
        try:
            if abs(float(raw.replace(",", "")) - expected) <= tolerance:
                return True
        except ValueError:
            pass
    return False


def validate(llm_output: str):
    text = llm_output.lower()
    missing = [value for value in EXPECTED_STRINGS if value.lower() not in text]
    missing.extend(str(value) for value in EXPECTED_NUMBERS if not contains_number(llm_output, value))
    if missing:
        return False, "Missing expected value(s): " + ", ".join(missing)
    return True, "Found expected expensive-over bowlers."
