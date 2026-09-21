import sqlite3
import requests


# =========================================================
# 1. Configuration
# =========================================================

FHIR_BASE_URL = "https://hapi.fhir.org/baseR4"

PATIENT_ID = "sindhu-syn-000004"

DATABASE = "healthcare.db"


# =========================================================
# 2. Connect to SQLite
# =========================================================

connection = sqlite3.connect(DATABASE)

cursor = connection.cursor()


# =========================================================
# 3. Retrieve Patient from FHIR
# =========================================================

patient_url = f"{FHIR_BASE_URL}/Patient/{PATIENT_ID}"

patient_response = requests.get(patient_url)

print("Patient HTTP Status:", patient_response.status_code)


if patient_response.status_code != 200:

    print("ERROR - Patient could not be retrieved.")

    connection.close()

    exit()


patient = patient_response.json()


# =========================================================
# 4. Extract Patient information
# =========================================================

patient_id = patient.get("id")

gender = patient.get("gender")

birth_date = patient.get("birthDate")


# ---------------------------------------------------------
# Patient name
# ---------------------------------------------------------

names = patient.get("name", [])

family_name = None

given_name = None


if names:

    first_name = names[0]

    family_name = first_name.get("family")

    given_names = first_name.get("given", [])

    if given_names:

        given_name = " ".join(given_names)


# =========================================================
# 5. Insert Patient into SQL
# =========================================================

cursor.execute(
    """
    INSERT OR REPLACE INTO patients
    (
        patient_id,
        family_name,
        given_name,
        gender,
        birth_date
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        patient_id,
        family_name,
        given_name,
        gender,
        birth_date
    )
)


print("\nPatient loaded successfully.")

print("Patient ID:", patient_id)

print("Family Name:", family_name)

print("Given Name:", given_name)

print("Gender:", gender)

print("Birth Date:", birth_date)


# =========================================================
# 6. Retrieve Observations from FHIR
# =========================================================

observation_url = (
    f"{FHIR_BASE_URL}/Observation"
    f"?patient={PATIENT_ID}"
)


observation_response = requests.get(
    observation_url
)


print(
    "\nObservation HTTP Status:",
    observation_response.status_code
)


if observation_response.status_code != 200:

    print("ERROR - Observations could not be retrieved.")

    connection.close()

    exit()


bundle = observation_response.json()


# =========================================================
# 7. Extract Observation entries
# =========================================================

entries = bundle.get("entry", [])


print(
    "Observations retrieved:",
    len(entries)
)


# =========================================================
# 8. Insert Observations
# =========================================================

observation_count = 0


for entry in entries:

    observation = entry.get("resource", {})


    # -----------------------------------------------------
    # Observation ID
    # -----------------------------------------------------

    observation_id = observation.get("id")


    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    status = observation.get("status")


    # -----------------------------------------------------
    # Subject
    # -----------------------------------------------------

    subject = observation.get("subject", {})

    subject_reference = subject.get("reference")


    # Extract patient ID from:

    # Patient/sindhu-syn-000004

    observation_patient_id = None


    if subject_reference:

        observation_patient_id = (
            subject_reference.split("/")[-1]
        )


    # -----------------------------------------------------
    # Code
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Fallback to text
    # -----------------------------------------------------

    if not clinical_test:

        clinical_test = code_data.get("text")


    # -----------------------------------------------------
    # Value
    # -----------------------------------------------------

    value_quantity = observation.get(
        "valueQuantity",
        {}
    )


    value = value_quantity.get("value")

    unit = value_quantity.get("unit")


    # -----------------------------------------------------
    # Effective date
    # -----------------------------------------------------

    effective_date = observation.get(
        "effectiveDateTime"
    )


    # -----------------------------------------------------
    # Insert into database
    # -----------------------------------------------------

    cursor.execute(
        """
        INSERT OR REPLACE INTO observations
        (
            observation_id,
            patient_id,
            clinical_test,
            code_system,
            code,
            value,
            unit,
            status,
            effective_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            observation_id,
            observation_patient_id,
            clinical_test,
            code_system,
            code,
            value,
            unit,
            status,
            effective_date
        )
    )


    observation_count += 1


# =========================================================
# 9. Save database changes
# =========================================================

connection.commit()


# =========================================================
# 10. Close database
# =========================================================

connection.close()


# =========================================================
# 11. Final result
# =========================================================

print("\n========================================")

print("FHIR → SQL LOAD COMPLETE")

print("========================================")

print(
    "Patient loaded:",
    patient_id
)

print(
    "Observations loaded:",
    observation_count
)

print(
    "Database:",
    DATABASE
)