import re
import unicodedata


EXPECTED_GROUPS = [
    ["WrestleMania X8"],
    ["2002-03-17", "March 17 2002"],
    ["Canada"],
    ["Toronto, Ontario"],
]
EXPECTED_NUMBERS = [7]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def contains_number(text: str, expected: float, tolerance: float = 0.01) -> bool:
    for raw in re.findall(r"(?<![A-Za-z0-9_.-])-?\d+(?:,\d{3})*(?:\.\d+)?(?![A-Za-z0-9_.-])", text):
        try:
            if abs(float(raw.replace(",", "")) - expected) <= tolerance:
                return True
        except ValueError:
            pass
    return False


def validate(llm_output: str):
    text = normalize(llm_output)
    missing = []
    for group in EXPECTED_GROUPS:
        if not any(normalize(value) in text for value in group):
            missing.append(group[0])
    missing.extend(str(value) for value in EXPECTED_NUMBERS if not contains_number(llm_output, value))
    if missing:
        return False, "Missing expected value(s): " + ", ".join(missing)
    return True, "Found the non-US pay-per-view with the most title changes."
