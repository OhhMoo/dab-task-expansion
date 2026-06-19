import re


EXPECTED_NUMBERS = [84, 1124.29]


def contains_number(text: str, expected: float, tolerance: float = 0.01) -> bool:
    for raw in re.findall(r"\b[\d,]+(?:\.\d+)?\b", text):
        try:
            if abs(float(raw.replace(",", "")) - expected) <= tolerance:
                return True
        except ValueError:
            pass
    return False


def validate(llm_output: str):
    missing = [str(value) for value in EXPECTED_NUMBERS if not contains_number(llm_output, value)]
    if missing:
        return False, "Missing expected value(s): " + ", ".join(missing)
    return True, "Found expected eligible count and average."
