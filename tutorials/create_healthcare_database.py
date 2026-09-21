import sqlite3


# ---------------------------------------------------------
# 1. Create database
# ---------------------------------------------------------

connection = sqlite3.connect("healthcare.db")

cursor = connection.cursor()


# ---------------------------------------------------------
# 2. Create patients table
# ---------------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (

    patient_id TEXT PRIMARY KEY,

    family_name TEXT,

    given_name TEXT,

    gender TEXT,

    birth_date TEXT

)
""")


# ---------------------------------------------------------
# 3. Create observations table
# ---------------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS observations (

    observation_id TEXT PRIMARY KEY,

    patient_id TEXT,

    clinical_test TEXT,

    code_system TEXT,

    code TEXT,

    value REAL,

    unit TEXT,

    status TEXT,

    effective_date TEXT,

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)

)
""")


# ---------------------------------------------------------
# 4. Save changes
# ---------------------------------------------------------

connection.commit()


# ---------------------------------------------------------
# 5. Confirm database
# ---------------------------------------------------------

print("Healthcare database created successfully.")

print("\nTables created:")

print("- patients")
print("- observations")


# ---------------------------------------------------------
# 6. Close connection
# ---------------------------------------------------------

connection.close()