
loinc_displays = {
    "4548-4": "Hemoglobin A1c",
    "1920-8": "Aspartate Aminotransferase",
    "2324-2": "Gamma-Glutamyl Transferase"
}


def transform_observation(observation, patient_id):
       
        loinc_code = observation.get("code")
        observation_value = observation.get("value")
        observation_unit = observation.get("unit")
        effective_date = observation.get("effective_date")
        status = observation.get("status")
        coding_s = observation.get("system")
        display = loinc_displays.get(loinc_code)
        if coding_s == "LN":
                system = "http://loinc.org"
        else:
                system = coding_s

       
        
  
        observation_T = {
            
            "resourceType": "Observation",

            "status": status,
                "code":{
                    "coding": [
                    {
                        "system": system,
                        "code": loinc_code,
                        "display": display,
                                    }
                ]
                },
                "valueQuantity": {
                    "value": float(observation_value),
                    "unit": observation_unit
                },
                "subject": {
                    "reference": f"Patient/{patient_id}"
                },     
                "effectiveDateTime": effective_date
            }
        return observation_T

