import json
import requests

FHIR_SERVER = "https://hapi.fhir.org/baseR4"

headers = {
    "Content-Type": "application/fhir+json",
    "Accept": "application/fhir+json"
}

patient_url = f"{FHIR_SERVER}/Patient/PAT123456"

patient_response = requests.get(
    patient_url,
    headers=headers
)

print("\n========================================")
print("PATIENT READ-BACK")
print("========================================")

print("HTTP Status:", patient_response.status_code)

print(
    json.dumps(
        patient_response.json(),
        indent=2
    )
)

observation_ids = [
    "138116854",
    "138116855",
    "138116856"
]

print("\n========================================")
print("OBSERVATION READ-BACK")
print("========================================")

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

    print(
        json.dumps(
            observation_response.json(),
            indent=2
        )
    )