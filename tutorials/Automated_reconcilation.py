import json
import requests

FHIR_SERVER = "https://hapi.fhir.org/baseR4"

headers = {
    "Content-Type": "application/fhir+json",
    "Accept": "application/fhir+json"
}

#response = requests.post(
 #   FHIR_SERVER,
  #  headers=headers,
   # json=fhir_bundle
#)

hl7_message = r"""MSH|^~\&|LAB|CITYHOSP|EHR|CITYHOSP|202401161200||ORU^R01|MSG00005|P|2.5
PID|1||PAT123457^^^CITYHOSP||DOE^JANE||19850115|F
OBR|1|ORD12349|LAB127|4548-4^Hemoglobin A1c^LN
OBX|1|NM|4548-4^Hemoglobin A1c^LN||7.4|%|||F|||202401161155
OBX|2|NM|1920-8^Aspartate Aminotransferase^LN||250|U/L|||F|||202401161156
OBX|3|NM|2324-2^Gamma-Glutamyl Transferase^LN||950|U/L|||F|||202401161157
"""

segments = hl7_message.strip().splitlines()

print("\n========================================")
print("HL7 MESSAGE PARSING")
print("========================================")

fhir_observations = []

for segment in segments:
    #print(segment)
    fields = segment.split('|')
    #print(fields)
    if fields[0] == 'PID':
        patient_id = fields[3].split('^^^')[0]
        patient_name = fields[5].replace('^', ' ')
        patient_dob = fields[7]
        patient_gender = fields[8]

        patient_data = {
        "resourceType": "Patient",
        "id": patient_id,
        "name": [
            {
                "family": patient_name.split(" ")[0],
                "given": [patient_name.split(" ")[1]]
            }
        ],
        "birthDate": (
            f"{patient_dob[:4]}-"
            f"{patient_dob[4:6]}-"
            f"{patient_dob[6:]}"
        ),
        "gender": {
            "M": "male",
            "F": "female"
        }.get(patient_gender, "unknown")
        }   

        patient_entry = {
        "resource": patient_data,
        "request": {
            "method": "PUT",
            "url": f"Patient/{patient_id}"
        }
        }
 

    if fields[0] == 'OBX':

        observation_code = fields[3].split('^')[0]
        observation_name = fields[3].split('^')[1]
        observation_value = fields[5]
        observation_unit = fields[6]
        observation_date = fields[12]

        observation = {
        "code": observation_code,
        "name": observation_name,
        "value": float(observation_value),
        "unit": observation_unit,
        "date": observation_date
        }
        fhir_observations.append(observation)

print("\n========================================")
print("EXTRACTED OBSERVATIONS")
print("========================================")

for observation in fhir_observations:
    print(observation)

print("\n========================================")
print("FHIR PATIENT")
print("========================================")

print(json.dumps(patient_data, indent=2))

fhir_observation_resources = []

for observation in fhir_observations:

    raw_date = observation["date"]

    formatted_date = (
        f"{raw_date[:4]}-"
        f"{raw_date[4:6]}-"
        f"{raw_date[6:8]}T"
        f"{raw_date[8:10]}:"
        f"{raw_date[10:12]}:00"
    )

    fhir_observation = {
        "resourceType": "Observation",
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": observation["code"],
                    "display": observation["name"]
                }
            ]
        },
        "valueQuantity": {
            "value": observation["value"],
            "unit": observation["unit"]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": formatted_date
    }

    fhir_observation_resources.append(fhir_observation)

    print("\n========================================")
print("FHIR OBSERVATIONS")
print("========================================")

print(
    json.dumps(
        fhir_observation_resources,
        indent=2
    )
)


fhir_bundle = {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": []
}
fhir_bundle["entry"].append(patient_entry) 
for observation in fhir_observation_resources:

    observation_entry = {
        "resource": observation,
        "request": {
            "method": "POST",
            "url": "Observation"
        }
    }

    fhir_bundle["entry"].append(observation_entry)

print("\n========================================")
print("FHIR TRANSACTION BUNDLE")
print("========================================")

print(json.dumps(fhir_bundle, indent=2))

print("\nPatient resources:", 1)
print(
    "Observation resources:",
    len(fhir_observation_resources)
)
print(
    "Total resources:",
    len(fhir_bundle["entry"])
)

#response = requests.post(
 #   FHIR_SERVER,
  #  headers=headers,
   # json=fhir_bundle
#)

#response_data = response.json()

patient_resource_id = "PAT123457"

observation_ids = [
    "138207597",
    "138207598",
    "138207599"
]

#print("\n========================================")
#print("FHIR SERVER RESPONSE")
#print("========================================")

#print("HTTP Status:", response.status_code)

#print(json.dumps(response_data, indent=2))

# ========================================
# FHIR READ-BACK
# ========================================

print("\n========================================")
print("FHIR READ-BACK")
print("========================================")

# Read Patient

patient_url = (
    f"{FHIR_SERVER}/Patient/{patient_resource_id}"
)

patient_response = requests.get(
    patient_url,
    headers=headers
)

print("\nPatient ID:", patient_resource_id)
print("HTTP Status:", patient_response.status_code)

patient_fhir = patient_response.json()

print(
    json.dumps(
        patient_fhir,
        indent=2
    )
)

# Read Observations

fhir_observations_from_server = []

for observation_id in observation_ids:

    observation_url = (
        f"{FHIR_SERVER}/Observation/{observation_id}"
    )

    observation_response = requests.get(
        observation_url,
        headers=headers
    )

    print("\nObservation ID:", observation_id)
    print("HTTP Status:", observation_response.status_code)

    observation_fhir = observation_response.json()

    fhir_observations_from_server.append(
        observation_fhir
    )


    
    print("\n========================================")
print("PATIENT RECONCILIATION")
print("========================================")

server_patient_id = patient_fhir.get("id")

server_family_name = (
    patient_fhir.get("name", [{}])[0]
    .get("family")
)

server_given_name = (
    patient_fhir.get("name", [{}])[0]
    .get("given", [None])[0]
)

server_birth_date = patient_fhir.get("birthDate")

server_gender = patient_fhir.get("gender")

print("Patient ID:")
print("Source:", patient_id)
print("FHIR:  ", server_patient_id)

print("\nFamily name:")
print("Source:", patient_name.split(" ")[0])
print("FHIR:  ", server_family_name)

print("\nGiven name:")
print("Source:", patient_name.split(" ")[1])
print("FHIR:  ", server_given_name)

print("\nDate of birth:")
print("Source:", patient_dob)
print("FHIR:  ", server_birth_date)

print("\nGender:")
print("Source:", patient_gender)
print("FHIR:  ", server_gender)


print("\n========================================")
print("OBSERVATION RECONCILIATION DATA")
print("========================================")

for observation in fhir_observations_from_server:

    coding = (
        observation
        .get("code", {})
        .get("coding", [{}])[0]
    )

    value_quantity = observation.get(
        "valueQuantity",
        {}
    )

    code = coding.get("code")
    display = coding.get("display")
    value = value_quantity.get("value")
    unit = value_quantity.get("unit")
    subject = (
        observation
        .get("subject", {})
        .get("reference")
    )
    effective_date = observation.get(
        "effectiveDateTime"
    )

    print("\nObservation:")
    print("Code:", code)
    print("Display:", display)
    print("Value:", value)
    print("Unit:", unit)
    print("Subject:", subject)
    print("Effective:", effective_date)

def compare_field(field_name, source_value, fhir_value):
    """
    Compare one source HL7 value with one FHIR value.
    """

    if source_value == fhir_value:
        print(f"{field_name:<25} PASS")
        return True

    else:
        print(f"{field_name:<25} FAIL")
        print("  Source:", source_value)
        print("  FHIR:  ", fhir_value)
        return False
source_family_name = patient_name.split(" ")[0]
source_given_name = patient_name.split(" ")[1]

source_birth_date = (
    f"{patient_dob[0:4]}-"
    f"{patient_dob[4:6]}-"
    f"{patient_dob[6:8]}"
)

source_gender = {
    "M": "male",
    "F": "female"
}.get(patient_gender)

source_patient_reference = f"Patient/{patient_id}"

server_patient_id = patient_fhir.get("id")

server_family_name = (
    patient_fhir
    .get("name", [{}])[0]
    .get("family")
)

server_given_name = (
    patient_fhir
    .get("name", [{}])[0]
    .get("given", [None])[0]
)

server_birth_date = patient_fhir.get("birthDate")
server_gender = patient_fhir.get("gender")

print("\n========================================")
print("HL7 → FHIR RECONCILIATION REPORT")
print("========================================")

mismatches = 0
fields_checked = 0

patient_checks = [
    ("Patient ID", patient_id, server_patient_id),
    ("Patient family name", source_family_name, server_family_name),
    ("Patient given name", source_given_name, server_given_name),
    ("Patient date of birth", source_birth_date, server_birth_date),
    ("Patient gender", source_gender, server_gender)
]

for field_name, source_value, fhir_value in patient_checks:

    fields_checked += 1

    if not compare_field(
        field_name,
        source_value,
        fhir_value
    ):
        mismatches += 1

source_observation_map = {
    observation["code"]: observation
    for observation in fhir_observations
}

for observation in fhir_observations_from_server:

    coding = (
        observation
        .get("code", {})
        .get("coding", [{}])[0]
    )

    value_quantity = observation.get(
        "valueQuantity",
        {}
    )

    fhir_code = coding.get("code")
    fhir_display = coding.get("display")
    fhir_value = value_quantity.get("value")
    fhir_unit = value_quantity.get("unit")
    fhir_subject = (
        observation
        .get("subject", {})
        .get("reference")
    )
    fhir_effective_date = observation.get(
        "effectiveDateTime"
    )

    source_observation = source_observation_map.get(
        fhir_code
    )

    if source_observation is None:

        print(
            f"\nObservation {fhir_code} "
            "not found in source data"
        )

        mismatches += 1
        continue

    print(f"\n{fhir_display}")

    observation_checks = [
        (
            "Code",
            source_observation["code"],
            fhir_code
        ),
        (
            "Display",
            source_observation["name"],
            fhir_display
        ),
        (
            "Value",
            source_observation["value"],
            fhir_value
        ),
        (
            "Unit",
            source_observation["unit"],
            fhir_unit
        ),
        (
            "Subject",
            source_patient_reference,
            fhir_subject
        )
    ]

    for field_name, source_value, fhir_value in observation_checks:

        fields_checked += 1

        if not compare_field(
            field_name,
            source_value,
            fhir_value
        ):
            mismatches += 1


print("\n========================================")
print("FINAL RECONCILIATION RESULT")
print("========================================")

print("Fields checked:", fields_checked)
print("Mismatches:", mismatches)

if mismatches == 0:

    print("RESULT: PASS")
    print("All source HL7 values match the FHIR read-back.")

else:

    print("RESULT: FAIL")
    print("One or more source values do not match the FHIR data.")


