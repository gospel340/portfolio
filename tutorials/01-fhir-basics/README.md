# Tutorial 01 — FHIR Basics

## Overview

FHIR (Fast Healthcare Interoperability Resources) is a healthcare interoperability standard designed to support the exchange of healthcare information between different systems.

This tutorial introduces the fundamental concepts needed to work with FHIR-based healthcare APIs.

The practical exercises in this tutorial use **FHIR R4** and synthetic healthcare data.

---

## Learning Objectives

By completing this tutorial, I learned how to:

* Explain the purpose of FHIR.
* Distinguish FHIR from traditional HL7 v2 messaging.
* Understand the concept of FHIR Resources.
* Identify common healthcare resources.
* Understand FHIR resource relationships.
* Use a FHIR REST API.
* Retrieve healthcare resources using HTTP GET.
* Interpret a FHIR JSON response.

---

# 1. What is FHIR?

FHIR stands for:

**Fast Healthcare Interoperability Resources**

FHIR provides a standard way for healthcare systems to represent and exchange information.

Instead of treating a healthcare message as one large structured message, FHIR represents healthcare information as individual **Resources**.

Examples include:

```text
Patient
Observation
Condition
Encounter
Medication
Practitioner
Organization
```

These resources can be connected to represent relationships within a healthcare system.

---

# 2. FHIR vs HL7 v2

HL7 v2 is commonly used for message-based healthcare integration.

A typical HL7 v2 laboratory message may contain:

```text
MSH
PID
OBR
OBX
```

FHIR uses a resource-oriented approach.

For example:

```text
HL7 v2

PID → Patient information
OBX → Clinical result

        ↓ transformation

FHIR

Patient resource
Observation resource
```

The two standards can therefore be used together within an integration architecture.

A healthcare integration system may receive HL7 v2 messages and transform the relevant information into FHIR resources.

---

# 3. FHIR Resources

A FHIR resource represents a specific type of healthcare information.

### Patient

Represents information about an individual receiving healthcare.

Example:

```json
{
  "resourceType": "Patient",
  "id": "PAT1234578",
  "name": [
    {
      "family": "DOE",
      "given": [
        "JANE"
      ]
    }
  ],
  "gender": "female",
  "birthDate": "1985-01-15"
}
```

### Observation

Represents a clinical measurement or observation.

Examples include:

* Blood pressure
* Blood glucose
* HbA1c
* Liver enzymes
* Temperature
* Heart rate

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
  }
}
```

---

# 4. Relationships Between Resources

FHIR resources can reference other resources.

For example, an Observation can reference a Patient:

```json
{
  "subject": {
    "reference": "Patient/PAT1234578"
  }
}
```

This means:

```text
Patient
   ↑
   |
Observation
```

The relationship allows a clinical observation to be associated with the correct patient.

Understanding resource references is important when designing healthcare integration pipelines.

---

# 5. FHIR REST API

FHIR can be accessed through REST APIs.

Common HTTP operations include:

| HTTP Method | Purpose                                    |
| ----------- | ------------------------------------------ |
| GET         | Retrieve resources                         |
| POST        | Create resources                           |
| PUT         | Create/update a resource at a specified ID |
| PATCH       | Partially update a resource                |
| DELETE      | Delete a resource                          |

For example:

```text
GET /Patient/{id}
```

retrieves a specific Patient resource.

---

# 6. Practical FHIR API Exercise

For the practical exercise, I used the public HAPI FHIR R4 test server.

FHIR base URL:

```text
https://hapi.fhir.org/baseR4
```

A Patient resource was retrieved using:

```text
GET /Patient/sindhu-syn-000004
```

The request returned:

```text
HTTP 200 OK
```

The response contained a FHIR Patient resource.

The synthetic patient included:

```text
Family name: SYN-000004
Given name: Synthetic
Gender: male
Birth date: 1952-01-01
```

---

# 7. Searching for Patients

FHIR also supports resource searches.

For example:

```text
GET /Patient?name=Synthetic
```

A search response is normally returned as a FHIR `Bundle`.

The Bundle contains the matching resources.

Conceptually:

```text
Bundle
│
├── Patient
├── Patient
└── Patient
```

The search result can then be processed by an application.

---

# 8. Searching for Observations

Observation resources can also be searched.

Example:

```text
GET /Observation
```

During the practical exercise, the API returned a collection of synthetic observations.

The observations were then examined for fields such as:

```text
Observation ID
Patient reference
Clinical test
Code system
LOINC code
Value
Unit
Status
Effective date
```

---

# 9. LOINC

LOINC stands for:

**Logical Observation Identifiers Names and Codes**

LOINC provides standard identifiers for laboratory and clinical observations.

For example:

```text
4548-4
```

represents:

```text
Hemoglobin A1c
```

A FHIR Observation can identify the test using:

```json
"coding": [
  {
    "system": "http://loinc.org",
    "code": "4548-4",
    "display": "Hemoglobin A1c"
  }
]
```

This standardised coding helps systems understand that they are referring to the same clinical test.

---

# 10. Data Quality Exercise

The retrieved synthetic observations were examined for important data-quality fields.

The initial checks included:

* LOINC code
* LOINC system
* Numeric value
* Unit
* Patient reference
* Effective date

The dataset contained 20 observations.

LOINC coding was present for:

```text
18 / 20 observations
```

This represents:

```text
90% LOINC completeness
```

Two observations required attention because they did not contain LOINC coding:

```text
Controlled Attenuation Parameter (CAP)
Liver Stiffness Measurement (LSM / FibroScan)
```

This demonstrated an important healthcare data-quality principle:

> Successful API retrieval does not necessarily mean that the underlying healthcare data is complete or correctly standardised.

---

# 11. Key Lessons

The main concepts learned were:

### FHIR is resource-oriented

Healthcare information is represented as individual resources.

### Resources can reference each other

For example:

```text
Observation → Patient
```

### FHIR supports REST APIs

Applications can interact with FHIR servers using HTTP methods.

### Standard terminology matters

LOINC provides standard identifiers for clinical observations.

### Data quality must be checked

A resource can be technically valid while still containing incomplete or poor-quality data.

---

# 12. Practical Skills Demonstrated

This tutorial demonstrated practical experience with:

* FHIR R4
* REST APIs
* HTTP GET requests
* FHIR JSON
* Patient resources
* Observation resources
* FHIR Bundles
* Resource references
* LOINC
* Data-quality assessment
* Synthetic healthcare data

---

## Next Tutorial

Next:

**[Tutorial 02 — Postman FHIR API](../02-postman-fhir-api/README.md)**

This tutorial moves from understanding FHIR concepts to practically interacting with a FHIR server using Postman.
