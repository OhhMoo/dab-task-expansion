import re


EXPECTED_STRINGS = [
    "YK Pathan", "SR Watson", "HH Gibbs", "RG Sharma", "SK Raina", "MS Dhoni",
    "M Vijay", "MEK Hussey", "MS Bisla", "JH Kallis", "KA Pollard", "AT Rayudu",
    "WP Saha", "M Vohra", "LMP Simmons", "CH Gayle", "V Kohli",
]
EXPECTED_NUMBERS = [336045, 61, 392244, 49, 501276, 152, 548386, 129, 981024, 108]


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
    return True, "Found expected last-match partnership values."
