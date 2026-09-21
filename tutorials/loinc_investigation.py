import requests


patient_id = "sindhu-syn-000004"

url = f"https://hapi.fhir.org/baseR4/Observation?patient={patient_id}"


response = requests.get(url)

print("HTTP Status:", response.status_code)

if response.status_code != 200:
    print("Request failed")
    exit()


data = response.json()

entries = data.get("entry", [])

print("Total Observations:", len(entries))

print("\n========================================")
print("LOINC INVESTIGATION")
print("========================================")


for entry in entries:

    observation = entry.get("resource", {})

    observation_id = observation.get("id")

    code_data = observation.get("code", {})

    coding = code_data.get("coding", [])


    has_loinc = any(
        item.get("system") == "http://loinc.org"
        for item in coding
    )

    if not has_loinc:

        print("\nNON-LOINC / MISSING-LOINC OBSERVATION")
        print("----------------------------------------")

        print("Observation ID:", observation_id)

        print("\nComplete code element:")
        print(code_data)

        print("\nCoding entries:")

        if coding:
            for item in coding:
                print("  System:", item.get("system"))
                print("  Code:", item.get("code"))
                print("  Display:", item.get("display"))
        else:
            print("  NO CODING ENTRIES FOUND")


  