# Healthcare HL7-to-FHIR Integration Test Cases

## 1. Purpose

This document describes the integration and data-quality tests performed on the Healthcare HL7-to-FHIR Integration Pipeline.

The tests verify that the pipeline can:

* Parse HL7 v2 laboratory messages
* Validate clinical observations
* Correctly classify valid and invalid data
* Transform accepted observations into FHIR R4 resources
* Submit FHIR transaction Bundles
* Handle successful and duplicate responses
* Retrieve resources from the FHIR server
* Reconcile source HL7 data against FHIR output

All test data is synthetic.

---

## 2. Test Environment

| Component               | Environment                |
| ----------------------- | -------------------------- |
| Programming language    | Python                     |
| Source format           | HL7 v2 ORU^R01             |
| Target standard         | FHIR R4                    |
| API                     | REST                       |
| FHIR server             | HAPI FHIR public R4 server |
| API testing             | Postman                    |
| Database testing        | SQLite / SQL               |
| Development environment | GitHub Codespaces          |
| Data                    | Synthetic                  |

---

## 3. Test Strategy

The testing approach combines:

1. **Unit-level validation** — individual observation rules are tested.
2. **Transformation testing** — HL7 fields are checked against generated FHIR fields.
3. **Integration testing** — FHIR transaction Bundles are submitted to the API.
4. **Negative testing** — invalid and incomplete observations are tested.
5. **Read-back verification** — resources are retrieved after successful submission.
6. **Reconciliation testing** — source and target clinical data are compared.

The expected processing flow is:

```text
HL7 Message
     |
     v
Parse
     |
     v
Validate
     |
     +----------------------+
     |                      |
   ACCEPT              REVIEW / REJECT
     |
     v
Transform
     |
     v
FHIR Bundle
     |
     v
FHIR API
     |
     v
Verify
     |
     v
Reconcile
```

---

# 4. Validation Test Cases

## TC01 — Valid Final HbA1c

**Objective:** Verify that a valid laboratory observation is accepted.

**Input:**

```text
LOINC: 4548-4
Value: 7.5
Unit: %
Status: final
Effective date: 2024-01-16T11:55:00
```

**Expected result:**

```text
ACCEPT
```

The observation should be transformed into a FHIR `Observation` resource.

**Result:** PASS

---

## TC02 — Preliminary Result

**Objective:** Verify that preliminary clinical results are not automatically accepted.

**Input:**

```text
LOINC: 4548-4
Value: 7.5
Unit: %
Status: preliminary
```

**Expected result:**

```text
REVIEW
```

The observation should not be submitted as an accepted observation.

**Result:** PASS

---

## TC03 — Missing Clinical Value

**Objective:** Verify that an observation without a clinical value is routed for review.

**Input:**

```text
LOINC: 4548-4
Value: UNKNOWN
Unit: %
Status: final
```

**Expected result:**

```text
REVIEW
```

**Result:** PASS

---

## TC04 — Non-Numeric Clinical Value

**Objective:** Verify that a non-numeric value is rejected.

**Input:**

```text
LOINC: 4548-4
Value: ABC
Unit: %
Status: final
```

**Expected result:**

```text
REJECT
```

**Reason:**

```text
Non-numeric value
```

**Result:** PASS

---

## TC05 — Invalid Unit

**Objective:** Verify that a clinical result with an invalid unit is rejected.

**Input:**

```text
LOINC: 4548-4
Value: 7.5
Unit: U/L
Status: final
```

The expected unit for LOINC `4548-4` is `%`.

**Expected result:**

```text
REJECT
```

**Reason:**

```text
Invalid unit for LOINC code
```

**Result:** PASS

---

# 5. FHIR Transformation Testing

## TC06 — HL7 Observation to FHIR Observation

**Objective:** Verify that an accepted HL7 observation is transformed into the expected FHIR structure.

The source HL7 observation contains:

```text
LOINC: 4548-4
Value: 7.5
Unit: %
Patient: PAT1234578
Status: final
Effective date: 2024-01-16T11:55:00
```

Expected FHIR representation includes:

```json
{
  "resourceType": "Observation",
  "status": "final",
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "4548-4"
      }
    ]
  },
  "valueQuantity": {
    "value": 7.5,
    "unit": "%"
  },
  "subject": {
    "reference": "Patient/PAT1234578"
  }
}
```

**Result:** PASS

---

# 6. FHIR API Integration Testing

## TC07 — Successful FHIR Transaction

**Objective:** Verify that a valid Patient and Observation can be submitted to the FHIR server.

The transaction Bundle contains:

```text
Patient
Observation
```

The Patient uses:

```text
PUT Patient/{patient_id}
```

The Observation uses:

```text
POST Observation
```

**Expected result:**

```text
HTTP 200 / 201
Successful transaction
```

Successful transactions were completed using synthetic patient and observation identifiers.

**Result:** PASS

---

## TC08 — Duplicate FHIR Resource

**Objective:** Verify that the application identifies a duplicate resource response.

The FHIR server returned:

```text
HTTP 412
```

with a duplicate-resource error.

Example:

```text
HAPI-2840:
Can not create resource duplicating existing resource
```

The application identifies the duplicate resource and routes it through duplicate handling rather than treating the transaction as successful.

**Expected result:**

```text
DUPLICATE DETECTED
```

**Result:** PASS

---

# 7. Read-back Verification

## TC09 — Patient Read-back

**Objective:** Verify that a successfully submitted Patient can be retrieved from the FHIR server.

Example:

```text
GET /Patient/PAT1234578
```

**Expected result:**

```text
HTTP 200
```

The returned resource should contain the expected Patient identifier and demographic information.

**Result:** PASS

---

## TC10 — Observation Read-back

**Objective:** Verify that a successfully submitted Observation can be retrieved.

Example:

```text
GET /Observation/34791
```

**Expected result:**

```text
HTTP 200
```

The returned Observation should contain the expected:

* LOINC code
* clinical value
* unit
* status
* effective date
* patient reference

**Result:** PASS

---

# 8. Source-to-FHIR Reconciliation

## TC11 — Observation Reconciliation

**Objective:** Verify that the resulting FHIR Observation preserves the important information from the source HL7 observation.

The reconciliation process compares six attributes:

| Attribute         | Expected |
| ----------------- | -------- |
| LOINC             | Match    |
| Value             | Match    |
| Unit              | Match    |
| Status            | Match    |
| Effective Date    | Match    |
| Patient Reference | Match    |

Example result:

```text
LOINC: PASS
Value: PASS
Unit: PASS
Status: PASS
Effective Date: PASS
Patient Reference: PASS
```

Overall result:

```text
6 / 6 checks passed
```

**Result:** PASS

---

# 9. Data Quality Testing

The project also tested the quality of a synthetic FHIR observation dataset.

The dataset contained:

```text
20 observations
```

LOINC completeness was measured as:

```text
18 / 20 = 90%
```

Two observations were identified as missing LOINC coding:

```text
Controlled Attenuation Parameter (CAP)
Liver Stiffness Measurement (LSM / FibroScan)
```

This demonstrated the ability to identify terminology-completeness issues in healthcare datasets.

**Result:** PASS

---

# 10. Test Summary

| Test ID | Test Area                 | Expected Result       | Result |
| ------- | ------------------------- | --------------------- | ------ |
| TC01    | Valid final HbA1c         | ACCEPT                | PASS   |
| TC02    | Preliminary result        | REVIEW                | PASS   |
| TC03    | Missing value             | REVIEW                | PASS   |
| TC04    | Non-numeric value         | REJECT                | PASS   |
| TC05    | Invalid unit              | REJECT                | PASS   |
| TC06    | HL7 → FHIR transformation | Correct FHIR resource | PASS   |
| TC07    | FHIR transaction          | Successful submission | PASS   |
| TC08    | Duplicate resource        | Duplicate handling    | PASS   |
| TC09    | Patient read-back         | HTTP 200              | PASS   |
| TC10    | Observation read-back     | HTTP 200              | PASS   |
| TC11    | Reconciliation            | 6/6 checks            | PASS   |

---

# 11. Test Findings

The testing demonstrated that the pipeline can distinguish between:

```text
Valid clinical data
       ↓
     ACCEPT
```

```text
Incomplete / non-final data
       ↓
     REVIEW
```

```text
Invalid clinical data
       ↓
     REJECT
```

The successful integration tests also demonstrated:

* FHIR resource creation
* API communication
* Resource retrieval
* Duplicate detection
* Source-to-target reconciliation

One additional test identified inconsistent duplicate-resource behaviour in the public HAPI FHIR sandbox. The application correctly reported the HTTP `412` response rather than assuming that the transaction succeeded.

This was documented as a limitation of the public testing environment.

---

# 12. Testing Outcome

The testing provides evidence that the pipeline supports an end-to-end healthcare integration workflow:

```text
Parse
  ↓
Validate
  ↓
Classify
  ↓
Transform
  ↓
Submit
  ↓
Verify
  ↓
Reconcile
```

The test suite demonstrates practical experience with **healthcare integration testing, API testing, data-quality validation, error handling, and source-to-target data integrity**.
