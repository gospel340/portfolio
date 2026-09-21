import requests
import pandas as pd


# ---------------------------------------------------------
# 1. Configuration
# ---------------------------------------------------------

patient_id = "sindhu-syn-000004"

base_url = "https://hapi.fhir.org/baseR4"

url = f"{base_url}/Observation?patient={patient_id}"


# ---------------------------------------------------------
# 2. Retrieve FHIR data
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


    # ---------------------------------------------
    # Patient
    # ---------------------------------------------

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


    # Use text if no coding exists

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
# 6. Convert date
# ---------------------------------------------------------

df["effective_date"] = pd.to_datetime(
    df["effective_date"]
)


# ---------------------------------------------------------
# 7. Sort observations
# ---------------------------------------------------------

df = df.sort_values(
    ["clinical_test", "effective_date"]
)


# ---------------------------------------------------------
# 8. Find repeated clinical tests
# ---------------------------------------------------------

test_counts = (
    df["clinical_test"]
    .value_counts()
)


repeated_tests = test_counts[
    test_counts > 1
].index


print("\n========================================")
print("REPEATED CLINICAL TESTS")
print("========================================")

print(
    df[
        df["clinical_test"].isin(repeated_tests)
    ][
        [
            "clinical_test",
            "value",
            "unit",
            "effective_date"
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# 9. Calculate trends
# ---------------------------------------------------------

trend_records = []


for test in repeated_tests:

    test_data = df[
        df["clinical_test"] == test
    ].sort_values("effective_date")


    first_record = test_data.iloc[0]

    latest_record = test_data.iloc[-1]


    first_value = first_record["value"]

    latest_value = latest_record["value"]


    absolute_change = (
        latest_value - first_value
    )


    # Avoid division by zero

    if first_value != 0:

        percentage_change = (
            absolute_change / first_value
        ) * 100

    else:

        percentage_change = None


    trend_records.append({

        "clinical_test": test,

        "unit": latest_record["unit"],

        "first_date": first_record["effective_date"],

        "first_value": first_value,

        "latest_date": latest_record["effective_date"],

        "latest_value": latest_value,

        "absolute_change": absolute_change,

        "percentage_change": percentage_change

    })


# ---------------------------------------------------------
# 10. Create trend DataFrame
# ---------------------------------------------------------

trend_df = pd.DataFrame(
    trend_records
)

# ---------------------------------------------------------
# 10A. Flag significant percentage changes
# ---------------------------------------------------------

threshold = 20.0

trend_df["change_flag"] = (
    trend_df["percentage_change"].abs() > threshold
)

# ---------------------------------------------------------
# 11. Display trend analysis
# ---------------------------------------------------------

print("\n========================================")
print("CLINICAL TREND ANALYSIS")
print("========================================")

if not trend_df.empty:

    print(
        trend_df.to_string(
            index=False
        )
    )

else:

    print(
        "No repeated clinical tests found."
    )


# ---------------------------------------------------------
# 12. Save results
# ---------------------------------------------------------

trend_df.to_csv(
    "clinical_trends.csv",
    index=False
)


print("\n========================================")
print("OUTPUT")
print("========================================")

print(
    "Trend analysis saved to clinical_trends.csv"
)  
# ---------------------------------------------------------
# 10B. Display flagged observations
# ---------------------------------------------------------

print("\n========================================")
print("SIGNIFICANT CHANGE FLAGS")
print("========================================")

flagged = trend_df[
    trend_df["change_flag"] == True
]

if not flagged.empty:

    print(
        flagged[
            [
                "clinical_test",
                "first_value",
                "latest_value",
                "absolute_change",
                "percentage_change"
            ]
        ].to_string(index=False)
    )

else:

    print("No observations exceeded the threshold.")