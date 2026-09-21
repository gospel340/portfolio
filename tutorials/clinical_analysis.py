import requests
import pandas as pd


# ---------------------------------------------------------
# 1. Configuration
# ---------------------------------------------------------

patient_id = "sindhu-syn-000004"

base_url = "https://hapi.fhir.org/baseR4"

url = f"{base_url}/Observation?patient={patient_id}"


# ---------------------------------------------------------
# 2. Request FHIR data
# ---------------------------------------------------------

response = requests.get(url)

print("HTTP Status:", response.status_code)

if response.status_code != 200:
    print("FHIR request failed")
    exit()


# ---------------------------------------------------------
# 3. Convert JSON response
# ---------------------------------------------------------

data = response.json()

entries = data.get("entry", [])

print("Observations returned:", len(entries))


# ---------------------------------------------------------
# 4. Extract observations
# ---------------------------------------------------------

records = []


for entry in entries:

    observation = entry.get("resource", {})

    observation_id = observation.get("id")

    status = observation.get("status")

    subject = observation.get("subject", {})

    patient_reference = subject.get("reference")


    # ---------------------------------------------
    # Clinical code
    # ---------------------------------------------

    code_data = observation.get("code", {})

    coding = code_data.get("coding", [])


    code_system = None
    code = None
    clinical_test = None


    if coding:

        first_code = coding[0]

        code_system = first_code.get("system")

        code = first_code.get("code")

        clinical_test = first_code.get("display")


    # Use text when coding is unavailable

    if not clinical_test:

        clinical_test = code_data.get("text")


    # ---------------------------------------------
    # Value
    # ---------------------------------------------

    value_quantity = observation.get("valueQuantity", {})

    value = value_quantity.get("value")

    unit = value_quantity.get("unit")


    # ---------------------------------------------
    # Date
    # ---------------------------------------------

    effective_date = observation.get("effectiveDateTime")


    # ---------------------------------------------
    # Store record
    # ---------------------------------------------

    records.append({
        "observation_id": observation_id,
        "patient_reference": patient_reference,
        "clinical_test": clinical_test,
        "code_system": code_system,
        "code": code,
        "value": value,
        "unit": unit,
        "status": status,
        "effective_date": effective_date
    })


# ---------------------------------------------------------
# 5. Create DataFrame
# ---------------------------------------------------------

df = pd.DataFrame(records)


# ---------------------------------------------------------
# 6. Convert date column
# ---------------------------------------------------------

df["effective_date"] = pd.to_datetime(df["effective_date"])


# ---------------------------------------------------------
# 7. Sort data
# ---------------------------------------------------------

df = df.sort_values(
    ["clinical_test", "effective_date"]
)


# ---------------------------------------------------------
# 8. Display basic dataset
# ---------------------------------------------------------

print("\n========================================")
print("DATASET")
print("========================================")

print(df.to_string(index=False))


# ---------------------------------------------------------
# 9. Basic statistics
# ---------------------------------------------------------

print("\n========================================")
print("BASIC STATISTICS")
print("========================================")

print(df["value"].describe())


# ---------------------------------------------------------
# 10. Number of tests
# ---------------------------------------------------------

print("\n========================================")
print("CLINICAL TESTS")
print("========================================")

print(
    df["clinical_test"]
    .value_counts()
)


# ---------------------------------------------------------
# 11. Date range
# ---------------------------------------------------------

print("\n========================================")
print("DATE RANGE")
print("========================================")

print("Earliest date:", df["effective_date"].min())

print("Latest date:", df["effective_date"].max())


# ---------------------------------------------------------
# 12. Missing LOINC
# ---------------------------------------------------------

print("\n========================================")
print("TERMINOLOGY QUALITY")
print("========================================")

missing_loinc = df["code_system"].isna().sum()

print("Observations without LOINC:", missing_loinc)

print(
    "LOINC completeness:",
    f"{(len(df) - missing_loinc) / len(df) * 100:.1f}%"
)