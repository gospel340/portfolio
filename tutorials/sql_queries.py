import sqlite3


# ---------------------------------------------------------
# 1. Connect to database
# ---------------------------------------------------------

connection = sqlite3.connect("healthcare.db")

cursor = connection.cursor()


# ---------------------------------------------------------
# 2. Query patient
# ---------------------------------------------------------

print("\n========================================")
print("PATIENT")
print("========================================")


cursor.execute(
    """
    SELECT
        patient_id,
        family_name,
        given_name,
        gender,
        birth_date
    FROM patients
    """
)


patients = cursor.fetchall()


for patient in patients:

    print(patient)


# ---------------------------------------------------------
# 3. Count observations
# ---------------------------------------------------------

print("\n========================================")
print("OBSERVATION COUNT")
print("========================================")


cursor.execute(
    """
    SELECT COUNT(*)
    FROM observations
    """
)


count = cursor.fetchone()[0]


print(
    "Total observations:",
    count
)


# ---------------------------------------------------------
# 4. List clinical tests
# ---------------------------------------------------------

print("\n========================================")
print("CLINICAL TESTS")
print("========================================")


cursor.execute(
    """
    SELECT
        clinical_test,
        COUNT(*) AS observation_count
    FROM observations
    GROUP BY clinical_test
    ORDER BY clinical_test
    """
)


tests = cursor.fetchall()


for test in tests:

    print(
        test[0],
        "->",
        test[1]
    )


print("\n========================================")
print("Question A")
print("========================================")
cursor.execute(
    """
   SELECT
     observation_id,
     clinical_test,
     value,
     unit
FROM observations
WHERE code_system  IS Null
    """
)
A = cursor.fetchall()
for row in A:
    print(row)


print("\n========================================")
print("Question B")
print("========================================")
cursor.execute(
    """
    SELECT COUNT(*)
    code_system    
    FROM observations 
    WHERE code_system IS Null
    """
)
count = cursor.fetchone()[0]
print("Observations with Null code_system:", count)

print("\n========================================")
print("Question C")
print("========================================")

cursor.execute(
    """
SELECT
    clinical_test,
    COUNT(*) AS observation_count
FROM observations
GROUP BY clinical_test
HAVING COUNT(*) > 1
    """
)
list = cursor.fetchall()
for row in list:
    print(row)

print("\n========================================")
print("Question D")
print("========================================")

cursor.execute(
    """
    SELECT
      p.patient_id,  p.given_name,
      p.family_name,
      o.clinical_test,
      o.value,
      o.unit,
      o.effective_date
    FROM patients p
    JOIN observations o 
    ON p.patient_id  = o.patient_id;
    """
)
show = cursor.fetchall()
for row in show:
    print(row)  


print("\n========================================")
print("Question F"  )
print("========================================")

cursor.execute(
    """
    SELECT
      Patient_id,  
      count (*) AS observation_count
    FROM observations
    WHERE clinical_test = 'HbA1c'
    GROUP BY patient_id
    HAVING COUNT(*) > 1
    
    """
)
show = cursor.fetchall()
if show:
    for row in show:
        print(row)


print("\n========================================")
print("Question G")
print("========================================")

cursor.execute(
    """
    SELECT
      Patient_id,
      clinical_test,
      value,
      unit,
      CASE
      WHEN value >= 6.5 Then 'Review'
      ELSE 'Normal'
      END AS analytical_flag
    FROM observations
    WHERE clinical_test = 'HbA1c'; 
        """
)
HB = cursor.fetchall()
for row in HB:
    print(row)

print("\n========================================")
print("Question H")
print("========================================")

cursor.execute(
    """
   SELECT
    COUNT(*) AS missing_loinc_count
FROM observations
WHERE code_system IS NULL;
            """
)
QH = cursor.fetchall()
for row in QH:
    print(row)


print("\n========================================")
print("LOINC DATA QUALITY")
print("========================================")

cursor.execute(
    """
  SELECT 
     COUNT(*) AS total_observations,
    SUM(
    CASE
      WHEN code_system = 'http://loinc.org' 
      THEN 1 
      ELSE 0 
      END
      ) AS loinc_observations,
    SUM(
    CASE
      WHEN code_system = 'http://loinc.org'
      THEN 0
      ELSE 1
      END
      ) AS missing_loinc,
    (SUM(CASE WHEN code_system = 'http://loinc.org' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS loinc_completeness
FROM 
    observations;

    """
)
data_quality = cursor.fetchall()
for row in data_quality:
    print(row)  

print("\n========================================")
print("Question J")
print("========================================")
cursor.execute(
    """
   SELECT
     observation_id,
     clinical_test,
     value,
     unit
FROM observations
WHERE code_system  IS Null
GROUP BY clinical_test
    """
)
J= cursor.fetchall()
for row in J:
    print(row)

print("\n========================================")
print("Question K")
print("========================================")
cursor.execute(
    """
  SELECT
    clinical_test,
    value,
    unit,
    effective_date
FROM observations
WHERE clinical_test IN (
    SELECT clinical_test
    FROM observations
    GROUP BY clinical_test
    HAVING COUNT(*) > 1
)
ORDER BY clinical_test, effective_date;
    """
)
K= cursor.fetchall()
for row in K:
    print(row)

    print("\n========================================")
print("CLINICAL TREND ANALYSIS")
print("========================================")
cursor.execute(
    """
    WITH repeated_tests AS (
        SELECT
            patient_id,
            clinical_test,
            value,
            effective_date,
        LAG(value) OVER (
            PARTITION BY patient_id, clinical_test
            ORDER BY effective_date
        ) AS previous_value,
    
        value - LAG(value) OVER (
        PARTITION BY patient_id, clinical_test
        ORDER BY effective_date
    ) AS absolute_change
    FROM observations
          ),
   second AS (
          SELECT
           patient_id,
            clinical_test,
            value,
            effective_date,
            absolute_change,
            previous_value,
             (absolute_change / NULLIF(previous_value, 0)) * 100 AS percentage_change,
                CASE
                WHEN previous_value IS NULL
                    THEN 'NO_PREVIOUS_VALUE'
                 WHEN (absolute_change / NULLIF(previous_value, 0)) * 100 > 10 OR (absolute_change / NULLIF(previous_value, 0)) * 100 < -10 THEN 'REVIEW'
                ELSE 'NORMAL'
            END AS trend_flag
            

            
FROM  repeated_tests
            )     
SELECT
    patient_id,
    clinical_test,
    value,
    effective_date,
    previous_value,
    absolute_change,
    percentage_change,
    trend_flag,

 
    CASE
        WHEN trend_flag = 'NO_PREVIOUS_VALUE' THEN 'BASELINE'
        WHEN trend_flag = 'REVIEW' THEN 'REVIEW'
                 ELSE 'NORMAL'
    END AS data_quality_flag  

FROM  second

WHERE (patient_id, clinical_test) IN (
    SELECT
        patient_id,
        clinical_test
    FROM observations
    GROUP BY patient_id, clinical_test
    HAVING COUNT(*) > 1
)

ORDER BY patient_id, clinical_test, effective_date;
    """
)
K5= cursor.fetchall()
for row in K5:
    print(row)


# ---------------------------------------------------------
# 5. Close database
# ---------------------------------------------------------

connection.close()



