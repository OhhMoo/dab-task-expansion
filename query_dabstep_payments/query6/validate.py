import re


def validate(llm_output: str):
    expected = 1546.82
    for raw in re.findall(r"\b[\d,]+(?:\.\d+)?\b", llm_output):
        try:
            if abs(float(raw.replace(",", "")) - expected) < 0.01:
                return True, "Found expected total fee."
        except ValueError:
            pass
    return False, f"Expected {expected:.2f}"
