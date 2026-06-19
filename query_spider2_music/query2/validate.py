import re


EXPECTED_ARTIST = "U2"
EXPECTED_REVENUE = 90.09


def contains_number(text: str, expected: float, tolerance: float = 0.01) -> bool:
    for raw in re.findall(r"\b[\d,]+(?:\.\d+)?\b", text):
        try:
            if abs(float(raw.replace(",", "")) - expected) <= tolerance:
                return True
        except ValueError:
            pass
    return False


def validate(llm_output: str):
    missing = []
    if not re.search(r"(?<![A-Za-z0-9])u2(?![A-Za-z0-9])", llm_output, re.IGNORECASE):
        missing.append(EXPECTED_ARTIST)
    if not contains_number(llm_output, EXPECTED_REVENUE):
        missing.append(f"{EXPECTED_REVENUE:.2f}")
    if missing:
        return False, "Missing expected value(s): " + ", ".join(missing)
    return True, "Found expected artist and revenue."
