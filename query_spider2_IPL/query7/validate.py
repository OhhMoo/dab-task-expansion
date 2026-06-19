import re


EXPECTED_STRINGS = ["CH Gayle", "KP Pietersen", "S Dhawan", "CL White", "SR Watson"]
EXPECTED_NUMBERS = [162, 733, 52.36, 158, 305, 38.13, 42, 569, 37.93, 10, 479, 36.85, 32, 255, 36.43]


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
    return True, "Found expected season 5 batting averages."
