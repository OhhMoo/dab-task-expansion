import re


EXPECTED_AGENT = "Steve Johnson"
EXPECTED_REVENUE = 8.91


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
    if EXPECTED_AGENT.lower() not in text:
        missing.append(EXPECTED_AGENT)
    if not contains_number(llm_output, EXPECTED_REVENUE):
        missing.append(f"{EXPECTED_REVENUE:.2f}")
    if missing:
        return False, "Missing expected value(s): " + ", ".join(missing)
    return True, "Found expected agent and revenue."
