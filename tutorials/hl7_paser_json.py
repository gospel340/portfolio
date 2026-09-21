print("\n========================================")
print("HL7 → FHIR TRANSFORMER")
print("========================================")
from datetime import datetime
import json

hl7_message12= """MSH|^~\&|LAB|CITYHOSP|EHR|CITYHOSP|202401151200||ORU^R01|MSG00004|P|2.5
PID|1||PAT123456^^^CITYHOSP||DOE^JOHN||19800101|M
OBX|1|NM|4548-4^Hemoglobin A1c^LN||8.2|%|||F|||202401151155
OBX|2|NM|1920-8^Aspartate Aminotransferase^LN||307|U/L|||F|||202401151156
OBX|3|NM|2324-2^Gamma-Glutamyl Transferase^LN||1192|U/L|||F|||202401151157"""


segments12 = hl7_message12.splitlines()
fhir_observations = []
for segment in segments12:
    fields12 = segment.split('|')

    if fields12[0] == 'PID':
        no_id = fields12[3].split('^^^')
        id = no_id[0]
        patient_name_parts = fields12[5].split('^')
        patient_last_name = patient_name_parts[0]
        patient_first_name = patient_name_parts[1]
        patient_dob_raw = fields12[7]
        patient_gender_raw = fields12[8]

 
        patient_dob = datetime.strptime(
            patient_dob_raw,
            "%Y%m%d"
        ).strftime("%Y-%m-%d")

      

        
        if patient_gender_raw == "M":
            patient_gender = "male"
        elif patient_gender_raw == "F":
            patient_gender = "female"
        else:
            patient_gender = "unknown"

        if not id or id == "UNKNOWN":
            decision = "REJECT"
            reason = "Invalid or missing patient ID"
        elif not patient_last_name or not patient_first_name:
            decision = "REVIEW"
            reason = "Missing patient name"
        elif not patient_dob:
            decision = "REVIEW"
            reason = "Missing patient date of birth"
        elif not patient_gender:
            decision = "REVIEW"
            reason = "Missing patient gender"
        else:
            decision = "ACCEPT"
            reason = "All required fields valid"

        patient_data = {
                    "resourceType": "Patient",
                    "id": id,
                    "name": [
                        {
                            "family": patient_last_name,
                            "given": [patient_first_name]
                        }
                    ],
                    "birthDate": patient_dob,
                    "gender": patient_gender
                }
        
   

        

    if fields12[0] == 'OBX':
        observation_n2 = fields12[1]
        observation_type2 = fields12[2]

        identifier_parts2 = fields12[3].split('^')
        loinc_code2 = identifier_parts2[0]
        test_name2 = identifier_parts2[1]
        coding_system2 = identifier_parts2[2]

        observation_value2 = fields12[5]
        unit2 = fields12[6]
        status2 = fields12[9]
        date_time_raw = fields12[12]

        if status2 == 'F':
            fhir_status = 'final'
        else:
            fhir_status = 'unknown'

        effective_datetime2 = datetime.strptime(
            date_time_raw,
            "%Y%m%d%H%M"
        ).strftime("%Y-%m-%dT%H:%M:%S")
    

        if coding_system2 == "LN":
            fhir_system = "http://loinc.org"
        else:
            fhir_system = coding_system2

        try:
            numeric_value = float(observation_value2)
        except (ValueError, TypeError):
            numeric_value = None

        if loinc_code2 == "UNKNOWN" or not loinc_code2:
            decision = "REJECT"
            reason = "Invalid or missing LOINC code"
        
        elif observation_value2 == "":

            decision = "REVIEW"
            reason = "Missing value"

        elif numeric_value is None:

            decision = "REJECT"
            reason = "Non-numeric value"
        
        elif not unit2:
            decision = "REVIEW"
            reason = "Missing unit"
        
        else:
            decision = "ACCEPT"
            reason = "All required fields valid"
            
        observation_data = {
            
        "resourceType": "Observation",

        "status": fhir_status,
            "code":{
                "coding": [
                {
                     "system": fhir_system,
                    "code": loinc_code2,
                    "display": test_name2,
                                   }
            ]
            },
            "valueQuantity": {
                "value": numeric_value,
                "unit": unit2
            },
            "subject": {
                "reference": f"Patient/{id}"
            },     
            "effectiveDateTime": effective_datetime2
        }

        fhir_observations.append(observation_data)

#print("\nFHIR PATIENT")
#print(json.dumps(patient_data, indent=2))
#print(f"Decision: {decision}, Reason: {reason}\n")
#print("\nFHIR OBSERVATIONS")
    
#print(json.dumps(observation_data, indent=2))
#print(f"Decision: {decision}, Reason: {reason}\n")       


    
                    
                    
fhir_bundle = {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": []
}


fhir_bundle["entry"].append({
    "resource": patient_data,
    "request": {
        "method": "PUT",
        "url": f"Patient/{patient_data['id']}"
    }
})


for observation in fhir_observations:

    fhir_bundle["entry"].append({
        "resource": observation,
        "request": {
            "method": "POST",
            "url": "Observation"
        }
    })
       
patient_count = sum(
    1 for entry in fhir_bundle["entry"]
    if entry["resource"]["resourceType"] == "Patient"
)

observation_count = sum(
    1 for entry in fhir_bundle["entry"]
    if entry["resource"]["resourceType"] == "Observation"
)

total_resources = len(fhir_bundle["entry"])

print("\n========================================")
print("FHIR BUNDLE SUMMARY")
print("========================================")
print(json.dumps(fhir_bundle, indent=2))

print(f"Patient resources: {patient_count}")
print(f"Observation resources: {observation_count}")
print(f"Total resources: {total_resources}")
print("Bundle status: READY")


 
import requests

FHIR_SERVER = "https://hapi.fhir.org/baseR4"

headers = {
    "Content-Type": "application/fhir+json",
    "Accept": "application/fhir+json"
}

response = requests.post(
    FHIR_SERVER,
    headers=headers,
    json=fhir_bundle
)

print("\n========================================")
print("FHIR SERVER RESPONSE")
print("========================================")

print("HTTP Status:", response.status_code)

print("\nResponse:")
print(response.text)

response_data = response.json()

print("\n========================================")
print("FHIR TRANSACTION VALIDATION")
print("========================================")

print("HTTP Status:", response.status_code)

successful_resources = 0
failed_resources = 0

if response.status_code == 200:

    print("Overall transaction: SUCCESS")

    for number, entry in enumerate(
        response_data.get("entry", []),
        start=1
    ):

        response_info = entry.get("response", {})

        status = response_info.get("status", "")
        location = response_info.get("location", "")

        print(f"\nEntry {number}")
        print("Status:", status)
        print("Location:", location)

        if status.startswith("2"):
            successful_resources += 1
            print("Result: PASS")
        else:
            failed_resources += 1
            print("Result: FAIL")

else:

    print("Overall transaction: FAILED")

    issues = response_data.get("issue", [])

    for issue in issues:

        severity = issue.get("severity", "unknown")
        code = issue.get("code", "unknown")
        diagnostics = issue.get("diagnostics", "No diagnostics provided")

        print("\nFHIR ERROR")
        print("Severity:", severity)
        print("Code:", code)
        print("Diagnostics:", diagnostics)

    failed_resources = len(issues)

print("\n========================================")
print("INTEGRATION TEST RESULT")
print("========================================")

expected_resources = len(fhir_bundle["entry"])

print("Expected resources:", expected_resources)
print("Successful resources:", successful_resources)
print("Failed resources:", failed_resources)

if (
    response.status_code == 200
    and successful_resources == expected_resources
    and failed_resources == 0
):
    print("\nRESULT: PASS")
else:
    print("\nRESULT: FAIL")





