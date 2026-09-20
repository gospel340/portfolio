import requests


FHIR_BASE_URL = "https://hapi.fhir.org/baseR4"

def submit_bundle(bundle):

    headers = {
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json"
    }

    response = requests.post(
        FHIR_BASE_URL,
        headers=headers,
        json=bundle
    )

    print("FHIR URL:", FHIR_BASE_URL)
    print("Response status:", response.status_code)

    return response

def handle_fhir_response(response):
    if 200 <= response.status_code < 300:
       print("FHIR transaction successful")
       return "SUCCESS"
       
    elif 400 <= response.status_code < 500:
        print("FHIR client error")
        try:
            error_data = response.json()
            issue = error_data.get("issue", [])
            if issue:
                diagnostic = issue[0].get("diagnostics")
                print("FHIR Error:", diagnostic)

        except ValueError:
            print("FHIR Error: Response was not valid JSON")

        return "DUPLICATE"
        
    elif 500 <= response.status_code < 600:
        print("FHIR server error")
        try:
            error_data = response.json()
            issue = error_data.get("issue", [])
            if issue:
                diagnostic = issue[0].get("diagnostics")
                print("FHIR Error:", diagnostic)
        
        except ValueError:
            print("FHIR Error: Response was not valid JSON")
        return "ERROR"
        
    else:
        print("Unexpected FHIR response")
        return False

def get_fhir_resource(resource_type, resource_id):
    
    url = (
         f"{FHIR_BASE_URL}/{resource_type}/{resource_id}"
         )

    headers = {
         "Accept": "application/fhir+json"
}

    response = requests.get(
        url,
        headers=headers
)
    return response

def extract_resource_id(response):
    data = response.json()

    if data.get("resourceType") == "OperationOutcome":
        issue = data.get("issue", [])

        if issue:
            diagnostic = issue[0].get("diagnostics", "")

            if "duplicating existing resource:" in diagnostic:
                resource_reference = diagnostic.split(
                    "duplicating existing resource: "
                )[1]

                resource_type, resource_id = resource_reference.split("/")
                return resource_type, resource_id

    return None, None

def extract_created_resources(response):

    created_resources = []

    if response.status_code < 200 or response.status_code >= 300:
        return created_resources

    data = response.json()

    if data.get("resourceType") != "Bundle":
        return created_resources

    for entry in data.get("entry", []):

        response_data = entry.get("response", {})

        location = response_data.get("location")

        if not location:
            continue

        resource_reference = location.split("/_history/")[0]

        parts = resource_reference.split("/")

        if len(parts) == 2:

            resource_type = parts[0]
            resource_id = parts[1]

            created_resources.append({
                "resource_type": resource_type,
                "resource_id": resource_id
            })

    return created_resources