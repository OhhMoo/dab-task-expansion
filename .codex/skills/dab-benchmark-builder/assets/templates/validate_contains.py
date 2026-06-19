def validate(llm_output: str):
    expected = [
        # "value"
    ]
    text = llm_output.lower()
    missing = [value for value in expected if value.lower() not in text]
    if missing:
        return False, "Missing expected value(s): " + ", ".join(missing)
    return True, "Found expected value(s)."
