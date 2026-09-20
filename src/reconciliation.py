def reconcile_observation(source_observation, fhir_observation):

    results = {}
    passed = 0
    total = 6


    source_code = source_observation.get("code")
    fhir_code = fhir_observation["code"]["coding"][0]["code"]
    source_value = float(source_observation.get("value"))
    fhir_value = fhir_observation["valueQuantity"]["value"]
    source_unit = source_observation.get("unit")
    fhir_unit = fhir_observation["valueQuantity"]["unit"]
    source_status = source_observation.get("status")
    fhir_status = fhir_observation.get("status")
    source_effective_date = source_observation.get("effective_date")
    fhir_effective_date = fhir_observation.get("effectiveDateTime")
    source_patient_id = source_observation.get("patient_id")
    fhir_patient_reference = fhir_observation.get("subject", {}).get("reference")
    expected_patient_reference = f"Patient/{source_patient_id}"


   

    if source_code == fhir_code:
        print("LOINC: PASS")
        results["LOINC"] = True
        passed += 1
    else:
        print("LOINC: FAIL")
        results["LOINC"] = False

    if source_value == fhir_value:
        print("Value: PASS")
        results["Value"] = True
        passed += 1
    else:
        print("Value: FAIL")
        results["Value"] = False

    if source_unit == fhir_unit:
        print("Unit: PASS")
        results["Unit"] = True
        passed += 1
    else:
        print("Unit: FAIL")
        results["Unit"] = False

    if source_status == fhir_status:
        print("Status: PASS")
        results["Status"] = True
        passed += 1
    else:
        print("Status: FAIL")
        results["Status"] = False

    if source_effective_date == fhir_effective_date:
        print("Effective Date: PASS")
        results["Effective Date"] = True
        passed += 1
    else:
        print("Effective Date: FAIL")
        results["Effective Date"] = False

    if expected_patient_reference == fhir_patient_reference:
        print("Patient Reference: PASS")
        results["Patient Reference"] = True
        passed += 1
    else:
        print("Patient Reference: FAIL")
        results["Patient Reference"] = False

    
    overall = passed == total

    return {
        "overall": overall,
        "passed": passed,
        "total": total,
        "results": results
        
    }
