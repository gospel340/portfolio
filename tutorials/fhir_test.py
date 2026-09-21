import requests

url = "https://hapi.fhir.org/baseR4/Patient/sindhu-syn-000004"

response = requests.get(url)

data = response.json()

if (
    response.status_code == 200
    and data.get("resourceType") == "Patient"
    and data.get("id") == "sindhu-syn-000004"
):
    print("PASS - Patient retrieval test passed")
else:
    print("FAIL - Patient retrieval test failed")

patient_id = data.get("id")
gender = data.get("gender")
birth_date = data.get("birthDate")

print("Patient ID:", patient_id)
print("Gender:", gender)
print("Birth Date:", birth_date)
name = data.get("name", [])

if name:
    family_name = name[0].get("family")
    given_names = name[0].get("given", [])

    print("Family Name:", family_name)
    print("Given Names:", given_names)