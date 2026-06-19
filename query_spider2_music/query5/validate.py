import re


EXPECTED_ALBUM = "Van Halen III"
EXPECTED_ARTIST = "Van Halen"
EXPECTED_GAP = 0.90


def contains_number(text: str, expected: float, tolerance: float = 0.01) -> bool:
    for raw in re.findall(r"\b[\d,]+(?:\.\d+)?\b", text):
        try:
            if abs(float(raw.replace(",", "")) - expected) <= tolerance:
                return True
        except ValueError:
            pass
    return False


def contains_artist(text: str) -> bool:
    return re.search(r"\bvan\s+halen\b(?!\s+iii)", text, re.IGNORECASE) is not None


def validate(llm_output: str):
    text = llm_output.lower()
    missing = []
    if EXPECTED_ALBUM.lower() not in text:
        missing.append(EXPECTED_ALBUM)
    if not contains_artist(llm_output):
        missing.append(EXPECTED_ARTIST)
    if not contains_number(llm_output, EXPECTED_GAP):
        missing.append(f"{EXPECTED_GAP:.2f}")
    if missing:
        return False, "Missing expected value(s): " + ", ".join(missing)
    return True, "Found expected album, artist, and gap."
