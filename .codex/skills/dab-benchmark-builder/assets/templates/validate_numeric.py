import re


def validate(llm_output: str):
    expected_label = "TODO"
    expected_amount = 0.0

    label_found = expected_label.lower() in llm_output.lower()
    amount_found = False
    for raw in re.findall(r"\b[\d,]+(?:\.\d+)?\b", llm_output):
        try:
            if abs(float(raw.replace(",", "")) - expected_amount) <= 0.01:
                amount_found = True
                break
        except ValueError:
            pass

    missing = []
    if not label_found:
        missing.append(expected_label)
    if not amount_found:
        missing.append(f"{expected_amount:.2f}")
    if missing:
        return False, "Missing expected value(s): " + ", ".join(missing)
    return True, "Found expected label and numeric value."
