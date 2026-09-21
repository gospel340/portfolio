import requests
import pandas as pd


# ---------------------------------------------------------
# 1. Configuration
# ---------------------------------------------------------

patient_id = "sindhu-syn-000004"

base_url = "https://hapi.fhir.org/baseR4"

url = f"{base_url}/Observation?patient={patient_id}"


# ---------------------------------------------------------
# 2. Request FHIR Observations
# ---------------------------------------------------------

response = requests.get(url)

print("HTTP Status:", response.status_code)

if response.status_code != 200:
    print("FHIR request failed")
    exit()


# ---------------------------------------------------------
# 3. Convert response to JSON
# ---------------------------------------------------------

data = response.json()


# ---------------------------------------------------------
# 4. Extract Bundle entries
# ---------------------------------------------------------

entries = data.get("entry", [])

print("Observations returned:", len(entries))


# ---------------------------------------------------------
# 5. Create analytical records
# ---------------------------------------------------------

records = []


for entry in entries:

    observation = entry.get("resource", {})


    # Observation ID
    observation_id = observation.get("id")


    # Status
    status = observation.get("status")


    # Patient reference
    subject = observation.get("subject", {})
    subject_reference = subject.get("reference")


    # Clinical code
    code_data = observation.get("code", {})

    coding = code_data.get("coding", [])


    # Default terminology values
    code_system = None
    code = None
    display = None


    # Extract coding if available
    if coding:

        first_code = coding[0]

        code_system = first_code.get("system")
        code = first_code.get("code")
        display = first_code.get("display")


    # If no coding display exists, use code.text
    if not display:

        display = code_data.get("text")


    # Observation value
    value_quantity = observation.get("valueQuantity", {})

    value = value_quantity.get("value")
    unit = value_quantity.get("unit")


    # Effective date
    effective_date = observation.get("effectiveDateTime")


    # Add record
    records.append({
        "observation_id": observation_id,
        "patient_reference": subject_reference,
        "clinical_test": display,
        "code_system": code_system,
        "code": code,
        "value": value,
        "unit": unit,
        "status": status,
        "effective_date": effective_date
    })


# ---------------------------------------------------------
# 6. Create pandas DataFrame
# ---------------------------------------------------------

df = pd.DataFrame(records)


# ---------------------------------------------------------
# 7. Display DataFrame
# ---------------------------------------------------------

print("\n========================================")
print("FHIR OBSERVATION DATAFRAME")
print("========================================")

print(df.to_string(index=False))


# ---------------------------------------------------------
# 8. Basic DataFrame information
# ---------------------------------------------------------

print("\n========================================")
print("DATASET INFORMATION")
print("========================================")

print("Rows:", len(df))

print("Columns:", len(df.columns))

print("\nColumn names:")

for column in df.columns:
    print("-", column)