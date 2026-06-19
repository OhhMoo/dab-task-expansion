import re


EXPECTED_STRINGS = [
    "SE Marsh", "Sohail Tanvir", "G Gambhir", "SK Warne", "ST Jayasuriya", "SR Watson",
    "ML Hayden", "RP Singh", "AC Gilchrist", "A Kumble", "AB de Villiers", "A Nehra",
    "SR Tendulkar", "PP Ojha", "JH Kallis", "Harbhajan Singh", "SK Raina",
    "CH Gayle", "SL Malinga", "V Kohli", "MM Patel", "S Aravind",
    "M Morkel", "SP Narine", "S Dhawan", "MEK Hussey", "DJ Bravo", "JP Faulkner",
    "RV Uthappa", "DR Smith", "GJ Maxwell", "MM Sharma", "B Kumar",
    "DA Warner", "LMP Simmons", "YS Chahal",
]
EXPECTED_NUMBERS = [616, 22, 969, 23, 687, 20]


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
    return True, "Found expected season leader values."
