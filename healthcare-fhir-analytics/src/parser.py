import datetime


def parse_hl7(message):
    segments = message.splitlines()
   
    observations = []
    patients = []



    for segment in segments:
        fields = segment.split("|")

        if fields[0] == "PID":
            fix = fields[3].split("^^^")
            patient_id = fix[0]
            name = fields[5].split("^")
            l_name = name[0]
            f_name = name[1]
            raw_DOB = fields[7]
            dob = datetime.datetime.strptime(raw_DOB, "%Y%m%d").strftime("%Y-%m-%d")
            gender = fields[8]
            if gender == "F":
                gender = "Female"
            elif gender == "M":
                gender = "Male"
            else:
                gender = "UNKNOWN"

            patient = {
                "id" : patient_id,
                "family" :   l_name,
                "given":f_name,
                "birthDate" : dob,
                "gender":      gender
   
}  
            patients.append(patient)

        if fields[0] == "OBX":       
                obx_split = fields[3].split("^")
                obx_code = obx_split[0]
                obx_display = obx_split[1]
                obx_system = obx_split[2]
                obx_value = fields[5]
                obx_unit = fields[6]
                raw_obx_date = fields[12]
                effective_date = datetime.datetime.strptime(raw_obx_date, "%Y%m%d%H%M").strftime("%Y-%m-%dT%H:%M:%S")
                status = fields[9]
                
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
                        "display": obx_display,
                        "system" : obx_system,
                        "value": obx_value,
                        "unit": obx_unit,
                        "effective_date": effective_date,
                        "status": status,
                        "patient_id": patient_id
                    }
                observations.append(observation)
            
    return patients, observations
   





  



