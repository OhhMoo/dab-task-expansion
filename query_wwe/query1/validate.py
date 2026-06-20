import re
import unicodedata


EXPECTED_GROUPS = [
    ["Bron Breakker"],
    ["Duke Hudson"],
    ["NXT Championship"],
    ["00:43", "0:43", "43 seconds"],
    ["TV #510 Taping", "TV 510 Taping"],
    ["2022-06-08", "June 8 2022"],
]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def validate(llm_output: str):
    text = normalize(llm_output)
    missing = []
    for group in EXPECTED_GROUPS:
        if not any(normalize(value) in text for value in group):
            missing.append(group[0])
    if missing:
        return False, "Missing expected value(s): " + ", ".join(missing)
    return True, "Found the shortest non-title-change NXT title match."
