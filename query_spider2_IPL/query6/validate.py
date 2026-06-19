import re


EXPECTED_STRINGS = [
    "A Symonds", "Deccan Chargers", "YK Pathan", "Rajasthan Royals",
    "SR Tendulkar", "Mumbai Indians", "SR Watson", "WP Saha",
    "Kings XI Punjab", "V Kohli", "Royal Challengers Bangalore",
    "SPD Smith", "Rising Pune Supergiants",
]
EXPECTED_NUMBERS = [335995, 117, 419112, 100, 501215, 598031, 101, 734054, 115, 980942, 980954]


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
    return True, "Found expected losing-team centuries."
