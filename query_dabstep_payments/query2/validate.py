import re


def validate(llm_output: str):
    expected_merchant = "Rafa_AI"
    expected_country = "NL"
    expected_count = 27696

    text = llm_output.lower()
    merchant_found = expected_merchant.lower() in text
    country_found = re.search(rf"\b{expected_country}\b", llm_output, re.IGNORECASE) is not None

    count_found = False
    for raw in re.findall(r"\b[\d,]+\b", llm_output):
        try:
            if int(raw.replace(",", "")) == expected_count:
                count_found = True
                break
        except ValueError:
            pass

    if merchant_found and country_found and count_found:
        return True, "Found merchant, acquiring country, and routed payment count."

    missing = []
    if not merchant_found:
        missing.append(expected_merchant)
    if not country_found:
        missing.append(expected_country)
    if not count_found:
        missing.append(str(expected_count))
    return False, f"Missing expected value(s): {', '.join(missing)}"
