import requests


# ---------------------------------------------------------
# 1. Configuration
# ---------------------------------------------------------

patient_id = "sindhu-syn-000004"

base_url = "https://hapi.fhir.org/baseR4"

url = f"{base_url}/Observation?patient={patient_id}"


# ---------------------------------------------------------
# 2. Send request to FHIR server
# ---------------------------------------------------------

response = requests.get(url)


# ---------------------------------------------------------
# 3. Basic API validation
# ---------------------------------------------------------

print("HTTP Status:", response.status_code)

if response.status_code != 200:
    print("FAIL - FHIR server did not return HTTP 200")
    print("Response:", response.text)
    exit()


# ---------------------------------------------------------
# 4. Convert JSON response into Python data
# ---------------------------------------------------------

data = response.json()


# ---------------------------------------------------------
# 5. Validate FHIR Bundle
# ---------------------------------------------------------

print("Resource Type:", data.get("resourceType"))
print("Bundle Type:", data.get("type"))

if data.get("resourceType") != "Bundle":
    print("FAIL - Expected a FHIR Bundle")
    exit()

if data.get("type") != "searchset":
    print("FAIL - Expected Bundle type 'searchset'")
    exit()


# ---------------------------------------------------------
# 6. Extract Observation entries
# ---------------------------------------------------------

entries = data.get("entry", [])

total_observations = len(entries)

print("Number of observations returned:", total_observations)


# ---------------------------------------------------------
# 7. Data-quality counters
# ---------------------------------------------------------

code_present = 0
loinc_present = 0
value_quantity_present = 0
numeric_value_present = 0
unit_present = 0
subject_present = 0
effective_date_present = 0


# ---------------------------------------------------------
# 8. Process every Observation
# ---------------------------------------------------------

print("\n--- OBSERVATIONS ---")

for entry in entries:

    observation = entry.get("resource", {})

    observation_id = observation.get("id")
    status = observation.get("status")

    # ---------------------------------------------
    # Observation code
    # ---------------------------------------------

    code_data = observation.get("code", {})
    coding = code_data.get("coding", [])

    if code_data:
        code_present += 1

    if any(
        coding_item.get("system") == "http://loinc.org"
        for coding_item in coding
    ):
        loinc_present += 1


    # ---------------------------------------------
    # Observation value
    # ---------------------------------------------

    value_quantity = observation.get("valueQuantity", {})

    if value_quantity:
        value_quantity_present += 1

    if value_quantity.get("value") is not None:
        numeric_value_present += 1

    if value_quantity.get("unit"):
        unit_present += 1


    # ---------------------------------------------
    # Patient reference
    # ---------------------------------------------

    subject = observation.get("subject", {})

    if subject.get("reference"):
        subject_present += 1


    # ---------------------------------------------
    # Effective date
    # ---------------------------------------------

    if observation.get("effectiveDateTime"):
        effective_date_present += 1


    # ---------------------------------------------
    # Display Observation information
    # ---------------------------------------------

    print("\nObservation ID:", observation_id)
    print("Status:", status)
    print("Subject:", subject.get("reference"))

    if coding:

        first_code = coding[0]

        print("Code System:", first_code.get("system"))
        print("Code:", first_code.get("code"))
        print("Display:", first_code.get("display"))

    print("Value:", value_quantity.get("value"))
    print("Unit:", value_quantity.get("unit"))
    print("Effective Date:", observation.get("effectiveDateTime"))


# ---------------------------------------------------------
# 9. Data-quality report
# ---------------------------------------------------------

print("\n========================================")
print("DATA QUALITY REPORT")
print("========================================")

print(f"Observations returned: {total_observations}")
print(f"Code present: {code_present}/{total_observations}")
print(f"LOINC system present: {loinc_present}/{total_observations}")
print(f"ValueQuantity present: {value_quantity_present}/{total_observations}")
print(f"Numeric value present: {numeric_value_present}/{total_observations}")
print(f"Unit present: {unit_present}/{total_observations}")
print(f"Subject reference present: {subject_present}/{total_observations}")
print(f"Effective date present: {effective_date_present}/{total_observations}")


# ---------------------------------------------------------
# 10. Data-quality percentages
# ---------------------------------------------------------

print("\n========================================")
print("DATA QUALITY PERCENTAGES")
print("========================================")

if total_observations > 0:

    print(
        f"Code completeness: "
        f"{code_present / total_observations * 100:.1f}%"
    )

    print(
        f"LOINC completeness: "
        f"{loinc_present / total_observations * 100:.1f}%"
    )

    print(
        f"Value completeness: "
        f"{value_quantity_present / total_observations * 100:.1f}%"
    )

    print(
        f"Numeric value completeness: "
        f"{numeric_value_present / total_observations * 100:.1f}%"
    )

    print(
        f"Unit completeness: "
        f"{unit_present / total_observations * 100:.1f}%"
    )

    print(
        f"Subject completeness: "
        f"{subject_present / total_observations * 100:.1f}%"
    )

    print(
        f"Effective date completeness: "
        f"{effective_date_present / total_observations * 100:.1f}%"
    )


# ---------------------------------------------------------
# 11. Overall test result
# ---------------------------------------------------------

all_quality_checks_passed = (
    total_observations > 0
    and code_present == total_observations
    and loinc_present == total_observations
    and value_quantity_present == total_observations
    and numeric_value_present == total_observations
    and unit_present == total_observations
    and subject_present == total_observations
    and effective_date_present == total_observations
)


print("\n========================================")
print("OVERALL TEST RESULT")
print("========================================")

if all_quality_checks_passed:
    print("PASS - All Observation data-quality checks passed")
else:
    print("FAIL - One or more Observation data-quality checks failed")

    