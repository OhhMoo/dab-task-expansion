import re
import unicodedata


EXPECTED_GROUPS = [
    ["Nikki A.S.H. & Rhea Ripley", "Nikki ASH and Rhea Ripley"],
    ["Natalya & Tamina", "Natalya and Tamina"],
    ["Monday Night Raw"],
    ["2021-09-20", "September 20 2021"],
    ["WWE Womens Tag Team Championship", "WWE Women's Tag Team Championship"],
    ["02:35", "2:35"],
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
    return True, "Found the shortest multi-person women's title change."
