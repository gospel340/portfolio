# Healthcare HL7-to-FHIR Integration & Data Quality Pipeline

A practical healthcare interoperability project demonstrating how clinical laboratory data can be processed from **HL7 v2 messages**, validated for data quality, transformed into **FHIR R4 resources**, submitted through a REST API, and verified through read-back reconciliation.

This project was developed as a practical portfolio project for demonstrating skills relevant to **Healthcare Data Analyst, Healthcare Integration Analyst, Healthcare Application Support, and Health IT** roles.

> **Data privacy:** This project uses synthetic healthcare data only. No real patient information is included.

---

## 1. Project Overview

Healthcare organisations often need to exchange clinical information between systems that use different data standards and formats.

This project simulates a laboratory integration workflow where clinical results are received as an **HL7 v2 ORU^R01 message** and transformed into modern **FHIR R4 resources**.

The pipeline demonstrates the following workflow:

```text
HL7 v2 Message
      |
      v
HL7 Parser
      |
      v
Data Validation
      |
      +----------------------+
      |                      |
    ACCEPT              REVIEW / REJECT
      |
      v
HL7 → FHIR Transformation
      |
      v
FHIR Transaction Bundle
      |
      v
FHIR REST API
      |
      v
Read-back Verification
      |
      v
Data Reconciliation
```

The project focuses on practical interoperability concepts including:

* HL7 v2 messaging
* FHIR R4
* REST APIs
* JSON
* LOINC terminology
* Clinical data validation
* Data quality
* Error handling
* Duplicate detection
* Integration testing
* Source-to-target reconciliation
* SQL healthcare analytics

---

## 2. Business Problem

Healthcare systems frequently need to exchange information between laboratory systems, electronic health records, clinical applications, and other healthcare platforms.

A typical integration challenge is that:

* A laboratory may produce HL7 v2 messages.
* A modern application may consume FHIR resources.
* Clinical values must be validated before integration.
* Invalid or incomplete records should not automatically enter downstream systems.
* Successfully transmitted data needs to be verified.
* Duplicate or failed transactions need to be handled appropriately.

This project addresses these requirements by implementing a simplified but realistic **HL7-to-FHIR integration pipeline**.

---

## 3. Project Objectives

The project was designed to demonstrate the ability to:

1. Parse HL7 v2 clinical messages.
2. Extract patient and laboratory observation data.
3. Validate healthcare data before integration.
4. Identify records requiring review.
5. Reject invalid clinical data.
6. Transform valid observations into FHIR R4 resources.
7. Build FHIR transaction Bundles.
8. Communicate with a FHIR REST API.
9. Handle successful and duplicate responses.
10. Retrieve resources from the FHIR server.
11. Reconcile source HL7 data against FHIR data.
12. Perform healthcare data quality analysis using SQL.

---

## 4. Technology Stack

| Technology        | Purpose                                     |
| ----------------- | ------------------------------------------- |
| Python            | Integration pipeline and data processing    |
| HL7 v2            | Source healthcare messaging format          |
| FHIR R4           | Target healthcare interoperability standard |
| REST API          | Communication with FHIR server              |
| JSON              | FHIR resource representation                |
| LOINC             | Laboratory terminology                      |
| SQLite            | Healthcare data storage and analysis        |
| SQL               | Data quality and analytical queries         |
| Postman           | API testing                                 |
| Git               | Version control                             |
| GitHub            | Source control and portfolio presentation   |
| GitHub Codespaces | Development environment                     |

---

# 5. System Architecture

The integration workflow can be represented as:

```text
                 +----------------------+
                 |    HL7 v2 Message    |
                 |      ORU^R01         |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |      HL7 Parser      |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |   Data Validation    |
                 +----------+-----------+
                            |
             +--------------+--------------+
             |                             |
             v                             v
       ACCEPTED RECORDS              REVIEW / REJECT
             |
             v
      +------------------+
      | HL7 → FHIR       |
      | Transformation   |
      +--------+---------+
               |
               v
      +------------------+
      | FHIR Transaction |
      | Bundle           |
      +--------+---------+
               |
               v
      +------------------+
      | FHIR REST API    |
      +--------+---------+
               |
               v
      +------------------+
      | Read-back        |
      | Verification     |
      +--------+---------+
               |
               v
      +------------------+
      | Reconciliation   |
      +------------------+
```

---

# 6. HL7 v2 Message Processing

The project uses an HL7 v2 `ORU^R01` laboratory result message.

Example:

```text
MSH|^~\&|LAB|CITYHOSP|EHR|CITYHOSP|202401151200||ORU^R01|MSG00004|P|2.5
PID|1||PAT123456^^^CITYHOSP||DOE^JOHN||19800101|M
OBR|1|ORD12348|LAB126|4548-4^Hemoglobin A1c^LN
OBX|1|NM|4548-4^Hemoglobin A1c^LN||8.2|%|||F|||202401151155
OBX|2|NM|1920-8^Aspartate Aminotransferase^LN||307|U/L|||F|||202401151156
OBX|3|NM|2324-2^Gamma-Glutamyl Transferase^LN||1192|U/L|||F|||202401151157
```

The parser extracts information including:

### Patient

* Patient ID
* Family name
* Given name
* Date of birth
* Gender

### Observation

* LOINC code
* Coding system
* Clinical value
* Unit
* Patient reference
* Effective date
* Result status

The parser converts the HL7 message into Python data structures that can be validated and transformed.

---

# 7. Data Validation

Before clinical observations are transformed into FHIR, they pass through a validation layer.

Each observation is classified as:

```text
ACCEPT
REVIEW
REJECT
```

### Validation rules

| Validation condition                                                 | Result |
| -------------------------------------------------------------------- | ------ |
| Valid LOINC + numeric value + valid unit + valid date + final status | ACCEPT |
| Missing clinical value                                               | REVIEW |
| Missing unit                                                         | REVIEW |
| Missing effective date                                               | REVIEW |
| Preliminary result                                                   | REVIEW |
| Corrected result                                                     | REVIEW |
| Missing/unknown LOINC                                                | REJECT |
| Non-numeric clinical value                                           | REJECT |
| Invalid unit for LOINC                                               | REJECT |
| Invalid status                                                       | REJECT |

This separates **data quality problems that require human review** from records that can safely continue through the automated pipeline.

---

# 8. LOINC Validation

The project uses LOINC codes to identify laboratory observations.

Examples include:

| LOINC    | Test                       | Expected Unit |
| -------- | -------------------------- | ------------- |
| `4548-4` | Hemoglobin A1c             | `%`           |
| `1920-8` | Aspartate Aminotransferase | `U/L`         |
| `2324-2` | Gamma-Glutamyl Transferase | `U/L`         |

The validator checks whether the supplied unit is appropriate for the expected LOINC code.

For example:

```text
LOINC: 4548-4
Value: 7.5
Unit: %
```

is accepted.

Whereas:

```text
LOINC: 4548-4
Value: 7.5
Unit: U/L
```

is rejected because the unit does not match the expected measurement.

---

# 9. HL7 → FHIR Transformation

Accepted HL7 observations are transformed into FHIR R4 `Observation` resources.

Example:

```json
{
  "resourceType": "Observation",
  "status": "final",
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "4548-4",
        "display": "Hemoglobin A1c"
      }
    ]
  },
  "valueQuantity": {
    "value": 7.5,
    "unit": "%"
  },
  "subject": {
    "reference": "Patient/PAT1234578"
  },
  "effectiveDateTime": "2024-01-16T11:55:00"
}
```

The transformation demonstrates how information from an HL7 v2 message can be mapped into the resource-oriented FHIR model.

---

# 10. FHIR Transaction Bundle

The pipeline creates a FHIR `transaction` Bundle containing the resources that need to be submitted.

For example:

```text
FHIR Transaction Bundle
│
├── Patient
│
└── Observation
```

The Patient uses an update-style request:

```text
PUT Patient/{patient_id}
```

The Observation uses:

```text
POST Observation
```

This allows the pipeline to send related healthcare resources as a single transaction.

---

# 11. FHIR REST API Integration

The project communicates with a public FHIR R4 server through REST.

FHIR endpoint used during development:

```text
https://hapi.fhir.org/baseR4
```

The integration client sends the transaction Bundle using:

```text
POST
Content-Type: application/fhir+json
Accept: application/fhir+json
```

The Python integration layer evaluates the HTTP response and routes the result accordingly.

---

# 12. Response Handling

The integration client distinguishes between different outcomes.

### Successful transaction

A successful response indicates that the transaction was processed by the FHIR server.

The pipeline then proceeds to resource verification.

### Duplicate resource

The pipeline detects HTTP `412` responses associated with duplicate resources.

Example:

```text
FHIR DUPLICATE DETECTED
Duplicate resource: Observation 34791
```

The system identifies the resource type and ID so that the existing resource can be retrieved and investigated.

### Other failures

Unexpected HTTP responses are reported as integration failures rather than being treated as successful transactions.

---

# 13. Read-back Verification

After successful FHIR creation, the project retrieves the resulting resources from the FHIR server.

For example:

```text
GET /Patient/PAT1234578
```

and:

```text
GET /Observation/34791
```

The returned resources are inspected to verify that the expected information was stored.

Example successful Patient response:

```text
HTTP 200

Patient/PAT1234578
```

Example Observation response:

```text
HTTP 200

Observation/34791
```

This demonstrates an important integration principle:

> A successful transmission should be verified rather than assuming that the downstream system stored the expected data.

---

# 14. Source-to-Target Reconciliation

The project includes a reconciliation layer that compares the original HL7 observation against the resulting FHIR Observation.

Six attributes are compared:

```text
1. LOINC code
2. Clinical value
3. Unit
4. Status
5. Effective date
6. Patient reference
```

Example reconciliation result:

```text
LOINC: PASS
Value: PASS
Unit: PASS
Status: PASS
Effective Date: PASS
Patient Reference: PASS
```

Overall:

```text
6 / 6 checks passed
```

This provides evidence that the transformation did not unintentionally alter important clinical information.

---

# 15. Integration Testing

The project includes test scenarios covering valid, incomplete, and invalid clinical observations.

| Test | Scenario                      | Expected Result    |
| ---- | ----------------------------- | ------------------ |
| TC01 | Valid final HbA1c             | ACCEPT → FHIR      |
| TC02 | Preliminary result            | REVIEW             |
| TC03 | Missing clinical value        | REVIEW             |
| TC04 | Non-numeric value             | REJECT             |
| TC05 | Invalid unit                  | REJECT             |
| TC06 | Duplicate FHIR resource       | Duplicate handling |
| TC07 | Successful resource read-back | Verification       |
| TC08 | Source/FHIR comparison        | Reconciliation     |

The tests demonstrate validation, routing, API behaviour, error handling, and data integrity verification.

---

# 16. Data Quality Testing

Earlier FHIR data-quality analysis was also performed against synthetic patient observations.

A sample FHIR dataset contained:

```text
20 observations
```

The initial data-quality checks evaluated:

* LOINC coding
* Numeric values
* Units
* Patient references
* Effective dates
* Observation status

The dataset contained:

```text
18 / 20 observations with LOINC coding
```

or:

```text
90% LOINC completeness
```

Two observations required further attention because coding information was missing for:

* Controlled Attenuation Parameter (CAP)
* Liver Stiffness Measurement (LSM / FibroScan)

This exercise demonstrated how healthcare data-quality issues can be identified before downstream analytics or integration.

---

# 17. SQL Healthcare Analytics

FHIR observation data was also loaded into SQLite for analytical exercises.

The database contains tables including:

```text
patients
observations
```

Example analytical tasks included:

### Missing LOINC detection

Identifying observations where terminology coding was missing.

### Repeated laboratory tests

Grouping observations by patient and clinical test.

### Clinical threshold flagging

Example:

```text
HbA1c >= 6.5
```

was flagged for review in the analytical workflow.

### Trend analysis

SQL window functions such as `LAG()` were used to compare an observation with the previous result.

The project explored percentage changes and trend flags such as:

```text
> 10% increase  → REVIEW
< 10% decrease → REVIEW
```

These exercises demonstrate the connection between interoperability data and healthcare analytics.

---

# 18. Project Structure

```text
healthcare-fhir-analytics/
│
├── README.md
│
├── main.py
│
├── .gitignore
│
├── data/
│   └── message.hl7
│
└── src/
    ├── fhir_client.py
    ├── parser.py
    ├── reconciliation.py
    ├── transformer.py
    └── validator.py
```

### Module responsibilities

| Module              | Responsibility                               |
| ------------------- | -------------------------------------------- |
| `main.py`           | Pipeline orchestration                       |
| `parser.py`         | HL7 message parsing                          |
| `validator.py`      | Clinical data validation                     |
| `transformer.py`    | HL7-to-FHIR transformation                   |
| `fhir_client.py`    | FHIR API communication and response handling |
| `reconciliation.py` | Source-to-FHIR verification                  |
| `data/message.hl7`  | Synthetic HL7 test message                   |

---

# 19. How to Run

Clone the repository and enter the project directory:

```bash
cd healthcare-fhir-analytics
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the pipeline:

```bash
python main.py
```

The application will:

```text
1. Read the HL7 message
2. Parse patient and observation data
3. Validate observations
4. Transform accepted observations
5. Build the FHIR transaction
6. Submit the transaction
7. Process the response
8. Perform verification/reconciliation where applicable
```

---

# 20. Key Integration Principles Demonstrated

This project demonstrates several principles important to healthcare integration work.

### Validate before transmission

Data should be checked before being passed into downstream systems.

### Separate automated processing from human review

Not every data-quality issue should result in automatic rejection.

The pipeline therefore distinguishes:

```text
ACCEPT
REVIEW
REJECT
```

### Preserve clinical meaning during transformation

Important source information such as:

* terminology codes
* values
* units
* dates
* status
* patient references

should be preserved during HL7-to-FHIR transformation.

### Verify downstream results

A successful HTTP transaction does not automatically guarantee that the expected resource was created correctly.

Read-back verification provides additional confidence.

### Reconcile source and target data

Source-to-target comparison helps identify transformation or integration errors.

### Handle integration failures explicitly

Duplicate resources and unexpected HTTP responses should be routed through explicit error-handling logic rather than being silently ignored.

---

# 21. Testing Environment Limitation

The project used the public HAPI FHIR R4 server for practical API integration testing.

During testing, several successful transactions were completed, including resource creation, read-back verification, and source-to-FHIR reconciliation.

Additional duplicate-handling tests exposed an inconsistent behaviour in the public sandbox where a transaction referencing a new Patient ID returned a duplicate-resource response referring to an older Patient resource.

For example, the application submitted a new Patient identifier but the server response referenced a previously created Patient.

The application therefore reports the duplicate response rather than incorrectly assuming that the transaction succeeded.

This behaviour was treated as a **test-environment limitation** rather than changing the application logic simply to accommodate an unexplained external response.

In a production environment, this would warrant investigation using server logs, transaction identifiers, correlation IDs, and the integration platform's monitoring tools.

---

# 22. Limitations

This project is intentionally a portfolio-scale implementation rather than a production healthcare integration platform.

Current limitations include:

* Synthetic healthcare data only
* Public FHIR test server
* No production authentication
* No OAuth2 implementation
* No message queue
* No enterprise integration engine
* Limited terminology validation
* Limited FHIR resource coverage
* Basic error handling
* No production monitoring
* No automated CI/CD pipeline

These limitations provide opportunities for future development.

---

# 23. Future Improvements

Potential next stages include:

### Healthcare Integration

* HL7 ACK/NACK processing
* HL7 message validation
* More HL7 message types
* HL7-to-FHIR mapping configuration
* Message queues
* Retry mechanisms
* Dead-letter queues
* Integration-engine implementation

### FHIR

* FHIR profiles
* CapabilityStatement validation
* FHIR search
* FHIR transaction responses
* Conditional create/update
* More resource types
* Terminology services

### Security

* OAuth2
* SMART on FHIR concepts
* API authentication
* Role-based access control
* Audit logging
* Secure secrets management

### Data Engineering

* ETL pipelines
* Automated data-quality reports
* Larger datasets
* Data warehouse integration
* Power BI dashboards

### DevOps

* Automated testing
* GitHub Actions
* Docker
* CI/CD
* Application monitoring

### Cloud

Potential deployment technologies include:

* Microsoft Azure
* Azure API Management
* Azure Functions
* Azure Storage
* Azure SQL
* Azure Service Bus

---

# 24. Skills Demonstrated

This project demonstrates practical experience with:

### Healthcare interoperability

* HL7 v2
* FHIR R4
* ORU^R01 messages
* Patient resources
* Observation resources
* FHIR transaction Bundles
* LOINC

### Integration

* REST APIs
* JSON
* API request/response handling
* Data transformation
* Source-to-target mapping
* Error handling
* Duplicate detection
* Reconciliation

### Data

* Python data processing
* SQL
* SQLite
* Data-quality validation
* Clinical data analysis
* Trend analysis

### Testing

* Integration testing
* Validation testing
* API testing
* Read-back verification
* Reconciliation testing
* Negative test cases

### Development

* Python
* Git
* GitHub
* GitHub Codespaces
* Modular application design

---

# 25. Portfolio Relevance

This project was developed to demonstrate practical skills relevant to roles such as:

* Healthcare Data Analyst
* Healthcare Integration Analyst
* Health IT Analyst
* Healthcare Application Support Analyst
* Clinical Systems Analyst
* Integration Support Analyst
* Junior Healthcare Business Analyst
* Healthcare Data Support Engineer

The project demonstrates an understanding of how healthcare data moves between systems rather than focusing only on isolated programming exercises.

---

# 26. Project Outcome

The completed pipeline demonstrates an end-to-end interoperability workflow:

```text
HL7 v2
  ↓
Parsing
  ↓
Validation
  ↓
Data Quality Classification
  ↓
HL7 → FHIR Transformation
  ↓
FHIR Transaction
  ↓
REST API
  ↓
Read-back Verification
  ↓
Reconciliation
```

The project provides practical evidence of the ability to work with healthcare interoperability standards, APIs, data quality, integration testing, and analytical workflows.

---

## Results Summary

The pipeline was tested end-to-end using synthetic HL7 v2 laboratory messages and a public FHIR R4 server.

Key results:

* **HL7 parsing:** Successfully extracted patient and laboratory observation data from ORU^R01 messages.
* **Data validation:** Correctly classified valid, incomplete, and invalid observations as **ACCEPT, REVIEW, or REJECT**.
* **FHIR transformation:** Successfully mapped accepted laboratory results into FHIR R4 `Patient` and `Observation` resources.
* **FHIR integration:** Successfully submitted multiple synthetic transactions to the FHIR API.
* **Read-back verification:** Successfully retrieved created Patient and Observation resources from the FHIR server.
* **Reconciliation:** Successfully compared source HL7 data with FHIR output across **6 data-integrity checks**, achieving **6/6 matches** in successful test cases.
* **Duplicate handling:** Detected HTTP `412` duplicate-resource responses and routed them through explicit error handling.
* **Data quality:** Identified LOINC completeness of **18/20 (90%)** in the analysed synthetic FHIR dataset.
* **Integration testing:** Tested valid results, missing values, non-numeric values, invalid units, preliminary results, duplicate resources, and read-back verification.

These results demonstrate practical capability across **healthcare interoperability, data validation, REST API integration, healthcare data quality, testing, and source-to-target reconciliation**.


## Synthetic Data Notice

All patient identifiers, clinical results, dates, and other healthcare information used in this project are synthetic and are intended solely for educational and portfolio purposes.

No real patient information is included.
