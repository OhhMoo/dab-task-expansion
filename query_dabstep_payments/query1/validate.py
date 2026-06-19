def validate(llm_output: str):
    expected_mcc = "7993"
    expected_desc = "Video Amusement Game Supplies"
    text = llm_output.lower()
    if expected_mcc in llm_output and expected_desc.lower() in text:
        return True, "Found MCC and category description."
    missing = []
    if expected_mcc not in llm_output:
        missing.append(expected_mcc)
    if expected_desc.lower() not in text:
        missing.append(expected_desc)
    return False, f"Missing expected value(s): {', '.join(missing)}"
