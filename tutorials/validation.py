
import datetime
import requests
observations = []

fhir_patients = []
URL = "https://hapi.fhir.org/baseR4"
msgHL7= """
MSH|^~\&|LAB|CITYHOSP|EHR|CITYHOSP|202401161200||ORU^R01|MSG00005|P|2.5
PID|1||PAT123457^^^CITYHOSP||DOE^JANE||19850115|F
OBR|1|ORD12349|LAB127|4548-4^Hemoglobin A1c^LN
OBX|1|NM|4548-4^Hemoglobin A1c^LN||7.4|U/L|||F|||202401161155
OBX|2|NM|1920-8^Aspartate Aminotransferase^LN||250|U/L|||P|||202401161156
OBX|3|NM|2324-2^Gamma-Glutamyl Transferase^LN||950|U/L|||C|||202401161157"""
lines = msgHL7.splitlines()
for line in lines:
    pid_fields = line.split("|")

    if pid_fields[0] == "OBX":       
        obx_split = pid_fields[3].split("^")
        obx_code = obx_split[0]
        obx_display = obx_split[1]
        obx_value = pid_fields[5]
        obx_unit = pid_fields[6]
        raw_obx_date = pid_fields[12]
        effective_date = datetime.datetime.strptime(raw_obx_date, "%Y%m%d%H%M").strftime("%Y-%m-%dT%H:%M:%S")
        status = pid_fields[9]
        if status == "F":
            status = "final"
        elif status == "C":
            status = "corrected"
        elif status == "P":
            status = "preliminary"
        else:
            status = "unknown"

        observation = { 
                "code": obx_code,
                "value": obx_value,
                "unit": obx_unit,
                "effective_date": effective_date,
                "status": status
            }
        observations.append(observation)



    if pid_fields[0] == "PID": 
        pid_check = pid_fields[3].split("^^^")
        p_ID = pid_check[0]
        pid_name = pid_fields[5].split("^")
        pid_first_name = pid_name[1]
        pid_last_name = pid_name[0]
        raw_dob = pid_fields[7]
        pid_dob = datetime.datetime.strptime(raw_dob, "%Y%m%d").strftime("%Y-%m-%d")
        p_gender_raw = pid_fields[8]
        if p_gender_raw == "M":
            p_gender = "male"
        elif    p_gender_raw == "F":
            p_gender = "female"
        else:
            p_gender = "unknown"   


        fhir_patient = {
            "resourceType": "Patient",
            "id": p_ID,
            "name": [
                {
                    "family": pid_last_name,
                    "given": [pid_first_name]
                }
            ],
            "birthDate": pid_dob,
            "gender": p_gender
        }    
        fhir_patients.append(fhir_patient)






expected_units = {
    "4548-4": "%",
    "1920-8": "U/L",
    "2324-2": "U/L"
}
loinc_displays = {
    "4548-4": "Hemoglobin A1c",
    "1920-8": "Aspartate Aminotransferase",
    "2324-2": "Gamma-Glutamyl Transferase"
}




def validate_observation(observation):

    loinc_code = observation.get("code")
    observation_value = observation.get("value")
    observation_unit = observation.get("unit")
    effective_date = observation.get("effective_date")
    status = observation.get("status")

    print("\nVALIDATING OBSERVATION")
    
    print("LOINC:", loinc_code)
    print("Value:", observation_value)
    print("Unit:", observation_unit)
    print("Effective Date:", effective_date)
    print("Status:", status)


     
    if loinc_code == "UNKNOWN" or not loinc_code:
        return "REJECT", None, "Missing or unknown LOINC code"

    if observation_value == "UNKNOWN" or not observation_value:
        return "REVIEW", None, "Missing clinical value"

    try:
        numeric_value = float(observation_value)
    except (ValueError, TypeError):
        numeric_value = None

    if numeric_value is None:
        return "REJECT", None, "Non-numeric value"
    

    if observation_unit == "UNKNOWN" or not observation_unit:
        return "REVIEW", numeric_value, "Missing unit"
    
    if observation_unit != expected_units.get(loinc_code):
        return "REJECT", numeric_value, "Invalid unit for LOINC code"
    if effective_date == "UNKNOWN" or not effective_date:
        return "REVIEW", numeric_value, "Missing effective date"
    if status not in ["final", "corrected", "preliminary"]:
        return "REJECT", numeric_value, "Invalid status"
    if status in ["corrected", "preliminary"]:
        return "REVIEW", numeric_value, "Status is not final"

    return  "ACCEPT", numeric_value, "All validations passed"




accepted_observations = []
review_observations = []
rejected_observations = []
fhir_observations = []



print("\n========================================")
print("OBSERVATION VALIDATION") 
print("========================================")   


for observation in observations:
    result = validate_observation(observation)
    print("Result:", result)

    if result[0] == "ACCEPT":
        accepted_observations.append(observation)
        fhir_observation = {
            
        "resourceType": "Observation",
        "status": observation.get("status"),

            "code":{
                "coding": [
                {
                    "system": "http://loinc.org",
                    "code": observation.get("code"),
                    "display": loinc_displays.get(observation.get("code"))
                                   }
            ]
            },
            "valueQuantity": {
                "value": result[1],
                "unit": observation.get("unit")
            },
            "subject": {
                "reference": "Patient/" + p_ID
                
            },
            "effectiveDateTime": observation.get("effective_date"),
           

        } 
        fhir_observations.append(fhir_observation)    

    elif result[0] == "REVIEW":
        review_observations.append(observation)

    elif result[0] == "REJECT":
        rejected_observations.append(observation)

print("\n========================================")
print("VALIDATION SUMMARY") 
print("========================================")   

print("Accepted:", len(accepted_observations), accepted_observations)
print("Review:", len(review_observations), review_observations)
print("Rejected:", len(rejected_observations), rejected_observations)

print("\n========================================")
print("OBSERVATIONS APPROVED FOR FHIR")
print("========================================")

for fhir_observation in fhir_observations:
    print("FHIR Observation Accepted:", fhir_observation)

bundle = {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": []
}

for fhir_patient in fhir_patients:  
        bundle["entry"].append({
        "resource": fhir_patient,
            "request": {
                "method": "PUT",
                "url": f"Patient/{fhir_patient['id']}"
            }
    })

for observation in fhir_observations:

        bundle["entry"].append({
        "resource": observation,
        "request": {
            "method": "POST",
            "url": "Observation"
        }
    })

print("\n========================================")
print("FHIR TRANSACTION BUNDLE")
print("========================================")

print("Bundle entries:", len(bundle["entry"]))
print("\n Bundle:", bundle)

for entry in bundle["entry"]:
    print(entry["request"]["method"], entry["request"]["url"])

headers = {
    "Content-Type": "application/fhir+json",
    "Accept": "application/fhir+json"
}
response = requests.post(
   URL,
    headers=headers, 
    json=bundle
)


response_bundle = response.json()
#print("Response entries:", len(response_bundle["entry"]))

#status = response_bundle.get("status", "")
#location = response_bundle.get("location", "")
#for entry in response_bundle["entry"]:
 #   response_info = entry["response"]
    #status = response_info["status"]
    #location = response_info["location"]

    #outcome = response_info["outcome"]
    #issue = outcome["issue"][0]
    #details = issue["details"]
    #coding = details["coding"][0]
    #result_code = coding["code"]
    #result_display = coding["display"]
    #print(status, "-", location, "-", result_code, result_display)


if response.status_code == 200:
    print("FHIR transaction successful")
else:
    error_bundle = response.json()
    issue = error_bundle["issue"][0]
    print("Resource type:", error_bundle["resourceType"])
    
    print("Severity:", issue["severity"])
    print("Code:", issue["code"])
    print("Diagnostics:", issue["diagnostics"])

print(response.status_code)
print(response.text)

search_url = URL + "/Observation"

params = {
    "patient": "Patient/PAT123457",
    "code": "4548-4"
}

search_response = requests.get(
    search_url,
    params=params
)

print(search_response.status_code)

search_bundle = search_response.json()

print(search_bundle["resourceType"])
print("Results:", len(search_bundle["entry"]))