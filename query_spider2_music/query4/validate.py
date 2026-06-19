import re


EXPECTED_COUNTRY = "Finland"
EXPECTED_REVENUE = 7.96


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
    missing = []
    if EXPECTED_COUNTRY.lower() not in text:
        missing.append(EXPECTED_COUNTRY)
    if not contains_number(llm_output, EXPECTED_REVENUE):
        missing.append(f"{EXPECTED_REVENUE:.2f}")
    if missing:
        return False, "Missing expected value(s): " + ", ".join(missing)
    return True, "Found expected country and revenue."
