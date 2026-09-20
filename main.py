
from src.parser import parse_hl7
from src.validator import validate_observation
from src.transformer import transform_observation
from src.fhir_client import (
    submit_bundle,
    handle_fhir_response,
    get_fhir_resource,
    extract_resource_id,
    extract_created_resources
)
from src.reconciliation import reconcile_observation


# --------------------------------------------------
# 1. Load HL7 message
# --------------------------------------------------

with open("data/message.hl7", "r") as file:
    message = file.read()


# --------------------------------------------------
# 2. Parse HL7
# --------------------------------------------------

patients, observations = parse_hl7(message)

print("\n" + "=" * 60)
print("HL7 MESSAGE PARSED")
print("=" * 60)

print("Patients:", len(patients))
print("Observations:", len(observations))


# --------------------------------------------------
# 3. Validate and transform observations
# --------------------------------------------------

accepted_observations = []
review_observations = []
rejected_observations = []
fhir_observations = []

for observation in observations:

    decision, numeric_value, reason = validate_observation(observation)

    if decision == "ACCEPT":

        accepted_observations.append(observation)

        fhir_observation = transform_observation(
            observation,
            patients[0]["id"]
        )

        fhir_observations.append(fhir_observation)

    elif decision == "REVIEW":

        review_observations.append(observation)

    elif decision == "REJECT":

        rejected_observations.append(observation)


# --------------------------------------------------
# 4. Validation summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)

print("Accepted:", len(accepted_observations))
print("Review:", len(review_observations))
print("Rejected:", len(rejected_observations))
print("FHIR observations created:", len(fhir_observations))


# --------------------------------------------------
# 5. Build FHIR transaction Bundle
# --------------------------------------------------

bundle = {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": []
}


# Add Patient resources
for patient in patients:

    fhir_patient = {
        "resourceType": "Patient",
        "id": patient["id"],
        "name": [
            {
                "family": patient["family"],
                "given": [patient["given"]]
            }
        ],
        "birthDate": patient["birthDate"],
        "gender": patient["gender"].lower()
    }

    bundle["entry"].append({
        "resource": fhir_patient,
        "request": {
            "method": "PUT",
            "url": f"Patient/{patient['id']}"
        }
    })


# Add accepted Observation resources
for observation in fhir_observations:

    bundle["entry"].append({
        "resource": observation,
        "request": {
            "method": "POST",
            "url": "Observation"
        }
    })


# --------------------------------------------------
# 6. Submit FHIR transaction
# --------------------------------------------------

print("\n" + "=" * 60)
print("FHIR TRANSACTION")
print("=" * 60)

print("Patient:", patients[0]["id"])
print("Observations submitted:", len(fhir_observations))

response = submit_bundle(bundle)

result = handle_fhir_response(response)


# --------------------------------------------------
# 7. Handle successful transaction
# --------------------------------------------------

if result == "SUCCESS":

    print("\n" + "=" * 60)
    print("FHIR TRANSACTION SUCCESSFUL")
    print("=" * 60)

    print("Patient submitted:", patients[0]["id"])
    print("Observations submitted:", len(fhir_observations))

    # Read back each accepted Observation
    created_resources = extract_created_resources(response)

    print("\nFHIR READ-BACK")

    for resource in created_resources:

        print(
        f"{resource['resource_type']}/"
        f"{resource['resource_id']}"
    )

# --------------------------------------------------
# 8. Handle duplicate resource
# --------------------------------------------------

elif result == "DUPLICATE":

    print("\n" + "=" * 60)
    print("FHIR DUPLICATE DETECTED")
    print("=" * 60)

    resource_type, resource_id = extract_resource_id(response)

    if resource_type and resource_id:

        print("Duplicate resource:", resource_type, resource_id)

        if resource_type == "Observation":

            fhir_response = get_fhir_resource(
                resource_type,
                resource_id
            )

            if fhir_response.status_code == 200:

                fhir_observation = fhir_response.json()

                print("\nFHIR OBSERVATION RETRIEVED")
                print("Observation ID:", resource_id)

                reconciliation_result = reconcile_observation(
                    accepted_observations[0],
                    fhir_observation
                )

                print("\nRECONCILIATION RESULT")
                print(
                    f"{reconciliation_result['passed']}/"
                    f"{reconciliation_result['total']} checks passed."
                )

                print(
                    "Overall:",
                    "PASS" if reconciliation_result["overall"]
                    else "FAIL"
                )

            else:

                print(
                    "Could not retrieve duplicate Observation."
                )

        elif resource_type == "Patient":

            print("Duplicate is a Patient resource.")
            print("Observation reconciliation will not run.")

    else:

        print(
            "Could not identify the duplicated FHIR resource."
        )


# --------------------------------------------------
# 9. Handle FHIR error
# --------------------------------------------------

else:

    print("\n" + "=" * 60)
    print("FHIR TRANSACTION FAILED")
    print("=" * 60)

    print("HTTP Status:", response.status_code)
    print("The transaction was not completed.")
