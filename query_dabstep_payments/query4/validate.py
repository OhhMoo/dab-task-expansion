import re


def validate(llm_output: str):
    expected_merchant = "Crossfit_Hanna"
    expected_amount = 18657.35

    text = llm_output.lower()
    merchant_found = expected_merchant.lower() in text

    amount_found = False
    for raw in re.findall(r"\b[\d,]+(?:\.\d+)?\b", llm_output):
        try:
            if abs(float(raw.replace(",", "")) - expected_amount) < 0.01:
                amount_found = True
                break
        except ValueError:
            pass

    if merchant_found and amount_found:
        return True, "Found merchant and counterfactual fee increase."

    missing = []
    if not merchant_found:
        missing.append(expected_merchant)
    if not amount_found:
        missing.append(f"{expected_amount:.2f}")
    return False, f"Missing expected value(s): {', '.join(missing)}"
