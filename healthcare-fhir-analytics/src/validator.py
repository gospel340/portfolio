

expected_units = {
    "4548-4": "%",
    "1920-8": "U/L",
    "2324-2": "U/L"
}

loinc_displays = {
    "4548-4": "Hemoglobin A1c",
    "1920-8": "Aspartate Aminotransferase",
    "2324-2": "Gamma-Glutamyl Transferase"
}


def validate_observation(observation):

    loinc_code = observation.get("code")
    observation_value = observation.get("value")
    observation_unit = observation.get("unit")
    effective_date = observation.get("effective_date")
    status = observation.get("status")
    Display = observation.get("dispaly")

    print("\nVALIDATING OBSERVATION")
    
    print("LOINC:", loinc_code)
    print("Value:", observation_value)
    print("Unit:", observation_unit)
    print("Effective Date:", effective_date)
    print("Status:", status)


     
    if loinc_code == "UNKNOWN" or not loinc_code:
        return "REJECT", None, "Missing or unknown LOINC code"

    if observation_value == "UNKNOWN" or not observation_value:
        return "REVIEW", None, "Missing clinical value"

    try:
        numeric_value = float(observation_value)
    except (ValueError, TypeError):
        numeric_value = None

    if numeric_value is None:
        return "REJECT", None, "Non-numeric value"
    

    if observation_unit == "UNKNOWN" or not observation_unit:
        return "REVIEW", numeric_value, "Missing unit"
    
    if observation_unit != expected_units.get(loinc_code):
        return "REJECT", numeric_value, "Invalid unit for LOINC code"
    if effective_date == "UNKNOWN" or not effective_date:
        return "REVIEW", numeric_value, "Missing effective date"
    if status not in ["final", "corrected", "preliminary"]:
        return "REJECT", numeric_value, "Invalid status"
    if status in ["corrected", "preliminary"]:
        return "REVIEW", numeric_value, "Status is not final"
    if Display != loinc_displays.get(Display):
        return "REVIEW", numeric_value, "Display code wrong"

    return  "ACCEPT", numeric_value, "All validations passed"



