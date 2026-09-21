hl7_message = """MSH|^~\\&|LAB|CITYHOSP|EHR|CITYHOSP|202401151200||ORU^R01|MSG00004|P|2.5
PID|1||123456^^^CITYHOSP||DOE^JOHN||19800101|M
PV1|1|O|LAB^01
OBR|1|ORD12348|LAB126|4548-4^Hemoglobin A1c^LN
OBX|1|NM|4548-4^Hemoglobin A1c^LN||8.2|%|||F|||202401151155
OBX|2|NM|1920-8^Aspartate Aminotransferase^LN||307|U/L|||F|||202401151156
OBX|3|NM|2324-2^Gamma-Glutamyl Transferase^LN||1192|U/L|||F|||202401151157"""

segments = hl7_message.splitlines()

for segment in segments:
    fields = segment.split('|')

    if fields[0] == 'OBX':
        observation_n = fields[1]
        observation_type = fields[2]
        

        identifier_parts = fields[3].split('^')
        loinc_code = identifier_parts[0]
        test_name = identifier_parts[1]
        coding_system = identifier_parts[2]

        observation_value = fields[5]
        unit = fields[6]
        status = fields[9]
        numeric_value = float(observation_value)
    

        print(
            f"Observation Number: {observation_n}, Type: {observation_type}, "
            f"Value: {numeric_value}, Unit: {unit}, Status: {status}, "
            f"LOINC Code: {loinc_code}, Test Name: {test_name}, Coding System: {coding_system}\n"
            f"--------------------------------"
        )


print("\n========================================")
print("HL72 PARSER")
print("========================================")

hl7_message1 = """MSH|^~\\&|LAB|CITYHOSP|EHR|CITYHOSP|202401151200||ORU^R01|MSG00004|P|2.5
PID|1||123456^^^CITYHOSP||DOE^JOHN||19800101|M
PV1|1|O|LAB^01
OBR|1|ORD12348|LAB126|4548-4^Hemoglobin A1c^LN
OBX|1|NM|4548-4^Hemoglobin A1c^LN||8.2|%|||F|||202401151155
OBX|2|NM|1920-8^Aspartate Aminotransferase^LN||307|U/L|||F|||202401151156
OBX|3|NM|2324-2^Gamma-Glutamyl Transferase^LN||1192|U/L|||F|||202401151157
OBX|4|NM|UNKNOWN^Unknown Test^LN||ABC|mg/dL|||F|||202401151158
OBX|5|NM|4548-4^Hemoglobin A1c^LN||||%|||F|||202401151159
OBX|6|NM|4548-4^Hemoglobin A1c^LN||9.5||||F|||202401151160"""

segments1 = hl7_message1.splitlines()

for segment in segments1:
    field1s = segment.split('|')

    if field1s[0] == 'OBX':
        observation_n1 = field1s[1]
        observation_type1 = field1s[2]

        identifier_parts1 = field1s[3].split('^')
        loinc_code1 = identifier_parts1[0]
        test_name1 = identifier_parts1[1]
        coding_system1 = identifier_parts1[2]

        observation_value1 = field1s[5]
        unit1 = field1s[6]
        status1 = field1s[9]
        date_time1 = field1s[11]

        def is_numeric(value):
            try:
                float(value)
                return True
            except ValueError:
                return False


        if loinc_code1 == "UNKNOWN" or not loinc_code1:
            decision = "REJECT"
            reason = "Invalid or missing LOINC code"

        elif not observation_value1:
            decision = "REVIEW"
            reason = "Missing value"

        elif not is_numeric(observation_value1):
            decision = "REJECT"
            reason = "Non-numeric value"

        elif not unit1:
            decision = "REVIEW"
            reason = "Missing unit"

        else:
            decision = "ACCEPT"
            reason = "All required fields valid"

        print(
             
            f"Observation Number: {observation_n1}, Type: {observation_type1}, "
            f"Value: {observation_value1}, Unit: {unit1}, Status: {status1}, "
            f"LOINC Code: {loinc_code1}, Test Name: {test_name1}, Coding System: {coding_system1}\n",
          
        )
        if decision == "REJECT" or decision == "REVIEW":
            print(f"Decision: {decision}, Reason: {reason}\n")
        else:
            print(f"Decision: {decision}")
        print("--------------------------------")


