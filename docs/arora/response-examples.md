# Arora Response Examples

Source: GEN Health Developers V2 API Beta docs, copied from rendered browser text.
Captured: 2026-06-27

## Pasted Examples

## POST /v2/client/patients

Create patient record.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/patients",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "patient": {
            "email": "jane@example.com",
            "firstName": "Jane",
            "lastName": "Smith",
            "phone": "5551234567",
            "partnerPatientId": "partner_001",
            "dateOfBirth": "1990-05-15",
            "sexAtBirth": "female",
            "address": {
                "street1": "123 Main Street",
                "city": "Austin",
                "state": "TX",
                "zip": "78701",
            },
            "customFields": {"referralSource": "web"},
        },
        "send_email": False,
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "message": "Patient created successfully",
  "data": {
    "patientId": "abc123",
    "partnerPatientId": "partner_001",
    "status": "pending",
    "emailSent": false,
    "magicLink": "https://app.gen-health.app/magic-login?email=jane%40example.com&token=a1b2c3..."
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Patient profile incomplete. Remediation: provide patient.email, firstName, lastName, phone, dateOfBirth, and address.street1/city/state/zip."
}
```

## GET /v2/client/patients

List client patients.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/patients",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "patients": [
      {
        "patientId": "abc123",
        "partnerPatientId": "partner_001",
        "status": "active",
        "requiresOnboarding": false,
        "firstName": "Jane",
        "lastName": "Smith",
        "fullName": "Jane Smith",
        "email": "jane@example.com",
        "phone": "5551234567",
        "phoneNumber": "+15551234567",
        "dateOfBirth": "1990-05-15",
        "sexAtBirth": "Female",
        "genderIdentity": "Woman",
        "languagePreference": "english",
        "address": {
          "street1": "123 Main St",
          "street2": "Apt 4B",
          "city": "Austin",
          "state": "TX",
          "zip": "78701"
        },
        "treatmentProgram": "weight-loss",
        "medicationDuration": "3-months",
        "allergies": ["penicillin"],
        "currentMedications": ["aspirin"],
        "weightJourney": {
          "currentWeight": 200,
          "height": 68,
          "goalWeight": 180
        },
        "customFields": {
          "memberNumber": "M-42"
        },
        "createdAt": "2026-01-10T12:00:00.000Z",
        "updatedAt": "2026-03-01T08:30:00.000Z"
      }
    ],
    "pagination": {
      "limit": 100,
      "hasMore": false,
      "nextCursor": null
    }
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Patient not found for this client. Remediation: use an email for a patient on this client, or GET /clientPatients/:patientId."
}
```

### 401 Response

```json
{
  "success": false,
  "error": "API key required or invalid."
}
```

### 405 Response

```json
{
  "success": false,
  "error": "Method not allowed. Use the documented HTTP method for this endpoint."
}
```

## GET /v2/client/patients/:patientId

Get patient detail.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/patients/:patientId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "patient": {
      "patientId": "abc123",
      "partnerPatientId": "partner_001",
      "status": "active",
      "requiresOnboarding": false,
      "firstName": "Jane",
      "lastName": "Smith",
      "fullName": "Jane Smith",
      "email": "jane@example.com",
      "phone": "5551234567",
      "phoneNumber": "+15551234567",
      "dateOfBirth": "1990-05-15",
      "sexAtBirth": "Female",
      "genderIdentity": "Woman",
      "languagePreference": "english",
      "address": {
        "street1": "123 Main St",
        "street2": "Apt 4B",
        "city": "Austin",
        "state": "TX",
        "zip": "78701"
      },
      "treatmentProgram": "weight-loss",
      "medicationDuration": "3-months",
      "allergies": ["penicillin"],
      "currentMedications": ["aspirin"],
      "weightJourney": {
        "currentWeight": 200,
        "height": 68,
        "goalWeight": 180
      },
      "customFields": {
        "memberNumber": "M-42"
      },
      "createdAt": "2026-01-10T12:00:00.000Z",
      "updatedAt": "2026-03-01T08:30:00.000Z"
    }
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Patient not found for client. Remediation: use patientId or partnerPatientId values returned by the client patients endpoints."
}
```

## POST /v2/client/patients/:patientId/health-logs

Write patient health logs.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/patients/:patientId/health-logs",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "category": "body",
        "date": "2026-01-15",
        "externalId": "crm-body-2026-01-15",
        "weight": 184.2,
        "unit": "lbs",
        "height": 68,
        "bodyFatPct": 24.5,
        "source": "partner_import",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "patientId": "abc123",
    "partnerPatientId": "partner_001",
    "healthLogs": [
      {
        "id": "partner_import_body_crm-body-2026-01-15",
        "category": "body",
        "date": "2026-01-15",
        "loggedAt": "2026-01-15T00:00:00.000Z",
        "weight": 184.2,
        "loggedWeight": 184.2,
        "currentWeight": 184.2,
        "unit": "lbs",
        "height": 68,
        "bodyFatPct": 24.5,
        "source": "partner_import"
      }
    ]
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "category is required. Remediation: use one of activity, nutrition, sleep, body, mind, symptom."
}
```

## GET /v2/client/patients/:patientId/health-logs

List patient health logs.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/patients/:patientId/health-logs",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "patientId": "abc123",
    "partnerPatientId": "partner_001",
    "healthLogs": [
      {
        "id": "partner_import_body_crm-body-2026-01-15",
        "category": "body",
        "date": "2026-01-15",
        "loggedAt": "2026-01-15T00:00:00.000Z",
        "weight": 184.2,
        "unit": "lbs",
        "height": 68
      }
    ],
    "pagination": {
      "limit": 100,
      "hasMore": false,
      "nextCursor": null
    }
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Patient not found for this client. Remediation: use patientId or partnerPatientId values returned by the client patients endpoints."
}
```

## POST /v2/client/patients/:patientId/onboarding-id

Upload patient onboarding photo.

### Python Request

Multipart mode:

```text
multipart/form-data: patientId=abc123, slotKey=selfie, file=<binary>
```

URL mode:

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/patients/:patientId/onboarding-id",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "patientId": "abc123",
        "slotKey": "selfie",
        "imageUrl": "https://example.com/photos/selfie.jpg",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "patientId": "abc123",
    "slotKey": "selfie"
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "415 — Unsupported Content-Type (use multipart/form-data or application/json)."
}
```

## POST /v2/client/patients/:patientId/continuation-sessions

Create continuation session.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/patients/:patientId/continuation-sessions",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "patientId": "abc123",
        "orderId": "order456",
        "allowedOrigin": "https://storefront.example.com",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "patientId": "abc123",
    "continuationSessionId": "sfps_...",
    "continuationSessionToken": "sfpt_...",
    "requiredActions": ["uploads", "forms", "patient_continuation"],
    "requirementSummary": {
      "totalForms": 2,
      "hasForms": true,
      "uploads": {
        "required": true,
        "completed": 0,
        "remaining": 2
      }
    },
    "uploadRequirements": {
      "sessionSlotKey": "requiredPhotos",
      "slots": [
        {
          "key": "idFront",
          "uploaded": false
        },
        {
          "key": "idBack",
          "uploaded": false
        }
      ]
    }
  }
}
```

## GET /v2/client/categories

List categories.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/categories",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "categoryId": "cat123",
        "categoryName": "Weight Loss",
        "status": "active"
      },
      {
        "categoryId": "cat456",
        "categoryName": "Skin Care",
        "status": "active"
      }
    ]
  }
}
```

### 401 Response

```json
{
  "success": false,
  "error": "API key required or invalid."
}
```

### 405 Response

```json
{
  "success": false,
  "error": "Method not allowed. Use the documented HTTP method for this endpoint."
}
```

## GET /v2/client/products

List consult products.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/products",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "products": [
      {
        "clientProductId": "prodX_1",
        "productId": "prodX",
        "sourceProductId": "prodX",
        "productRelationship": "duplicate",
        "name": "Client Display Name",
        "displayName": "Client Display Name",
        "description": "Video visit, personalized care plan, and follow-up messaging.",
        "categories": ["clientCategoryDocId"],
        "displayCategoryIds": ["clientCategoryDocId"],
        "PNcategories": ["networkCategoryCodeOrId"]
      },
      {
        "clientProductId": "clientA_network1_prodY",
        "productId": "prodY",
        "sourceProductId": null,
        "productRelationship": "original",
        "name": "Original Product",
        "displayName": "Original Product",
        "description": "Original product description.",
        "categories": ["clientCategoryDocId"],
        "displayCategoryIds": ["clientCategoryDocId"],
        "PNcategories": ["networkCategoryCodeOrId"]
      }
    ]
  }
}
```

### 401 Response

```json
{
  "success": false,
  "error": "API key required or invalid."
}
```

### 405 Response

```json
{
  "success": false,
  "error": "Method not allowed. Use the documented HTTP method for this endpoint."
}
```

## GET /v2/client/products/:clientProductId

Get product detail.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/products/:clientProductId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "product": {
      "clientProductId": "prodX_1",
      "productId": "prodX",
      "sourceProductId": "prodX",
      "productRelationship": "duplicate",
      "name": "Client Display Name",
      "displayName": "Client Display Name",
      "description": "Video visit, personalized care plan, and follow-up messaging.",
      "categories": ["clientCategoryDocId"],
      "displayCategoryIds": ["clientCategoryDocId"],
      "PNcategories": ["networkCategoryCodeOrId"]
    }
  }
}
```

## POST /v2/client/products

Create client product or package.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/products",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "itemType": "package",
        "name": "Metabolic Care Bundle",
        "displayName": "Metabolic Care Bundle",
        "displayDescription": "Two protocols purchased together.",
        "customerPrice": "249.00",
        "includedProducts": [
            {"clientProductId": "weight_loss_protocol"},
            {"clientProductId": "lab_review_protocol"},
        ],
        "status": "active",
        "showPatient": True,
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "product": {
      "clientProductId": "pkg_123",
      "productId": "pkg_123",
      "catalogScope": "client",
      "itemType": "package",
      "displayName": "Metabolic Care Bundle",
      "customerPrice": 249,
      "pricing": {
        "amount": 249,
        "currency": "USD"
      },
      "status": "active",
      "showPatient": true,
      "includedProducts": [
        {
          "clientProductId": "weight_loss_protocol",
          "name": "Weight Loss",
          "customerPrice": 159
        }
      ]
    }
  }
}
```

## PATCH /v2/client/products/:clientProductId

Update client product or package.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/products/:clientProductId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "displayName": "Metabolic Care Bundle",
        "customerPrice": "229.00",
        "status": "active",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "product": {
      "clientProductId": "pkg_123",
      "displayName": "Metabolic Care Bundle",
      "customerPrice": 229,
      "status": "active",
      "showPatient": true,
      "updatedAt": "2026-03-01T12:00:00.000Z"
    }
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Image fields are not editable through the Client API."
}
```

## DELETE /v2/client/products/:clientProductId

Deactivate client product or package.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.delete(
    "https://api.gen-health.app/v2/client/products/:clientProductId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "product": {
      "clientProductId": "pkg_123",
      "status": "inactive",
      "showPatient": false
    }
  }
}
```

## GET /v2/client/products/:clientProductId/forms

List product forms.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/products/:clientProductId/forms",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "product": {
      "clientProductId": "clientA_network1_prodX",
      "productId": "prodX",
      "providerNetworkId": "network1",
      "displayName": "Weight Loss Program"
    },
    "patient": {
      "patientId": "abc123",
      "partnerPatientId": "partner_patient_001",
      "email": "jane@example.com"
    },
    "requirementSummary": {
      "totalForms": 2,
      "completedForms": 0,
      "remainingForms": 2,
      "hasForms": true,
      "formsCompletionStatus": "pending"
    },
    "forms": [
      {
        "formKey": "provider_network:network1:intakeA",
        "formId": "intakeA",
        "scopeType": "provider_network",
        "providerNetworkId": "network1",
        "productId": "prodX",
        "name": "Medical Intake",
        "formType": "intake",
        "version": 3,
        "associationType": "product",
        "completed": false,
        "completionStatus": "pending",
        "detailPath": "/v2/client/products/clientA_network1_prodX/forms/provider_network%3Anetwork1%3AintakeA?patientId=abc123"
      }
    ]
  }
}
```

## GET /v2/client/products/:clientProductId/forms/:formKey

Get product form detail.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/products/:clientProductId/forms/:formKey",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "product": {
      "clientProductId": "clientA_network1_prodX",
      "productId": "prodX",
      "providerNetworkId": "network1",
      "displayName": "Weight Loss Program"
    },
    "patient": null,
    "form": {
      "formKey": "provider_network:network1:intakeA",
      "formId": "intakeA",
      "scopeType": "provider_network",
      "providerNetworkId": "network1",
      "name": "Medical Intake",
      "formType": "intake",
      "completionStatus": "pending",
      "detailPath": "/v2/client/products/clientA_network1_prodX/forms/provider_network%3Anetwork1%3AintakeA",
      "sections": [
        {
          "sectionId": "medical_history",
          "title": "Medical history",
          "questions": [
            {
              "questionId": "allergies",
              "label": "Known allergies",
              "type": "textarea",
              "required": false,
              "options": []
            }
          ]
        }
      ]
    }
  }
}
```

## GET /v2/client/products/forms

List forms for multiple products.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/products/forms",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "products": [
      {
        "clientProductId": "clientA_network1_prodX",
        "productId": "prodX",
        "providerNetworkId": "network1",
        "displayName": "Weight Loss Program"
      }
    ],
    "patient": null,
    "requirementSummary": {
      "totalForms": 1,
      "completedForms": 0,
      "remainingForms": 1,
      "hasForms": true,
      "formsCompletionStatus": "pending"
    },
    "forms": [
      {
        "formKey": "client:clientA:consent1",
        "formId": "consent1",
        "scopeType": "client",
        "clientId": "clientA",
        "name": "Consent",
        "formType": "consent",
        "coveredProductIds": ["clientA_network1_prodX", "clientA_network1_prodY"],
        "completionStatus": "pending",
        "detailPath": "/v2/client/products/clientA_network1_prodX/forms/client%3AclientA%3Aconsent1"
      }
    ]
  }
}
```

## POST /v2/client/orders

Create product order.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/orders",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "patient": {
            "email": "jane@example.com",
            "firstName": "Jane",
            "lastName": "Smith",
            "phone": "5551234567",
            "partnerPatientId": "partner_patient_001",
            "dateOfBirth": "1990-05-15",
            "address": {
                "street1": "123 Main Street",
                "city": "Austin",
                "state": "TX",
                "zip": "78701",
            },
            "customFields": {"referralSource": "web"},
        },
        "order": {
            "clientProductId": "clientA_network1_prodX",
            "amount": "200.00",
            "couponCode": "JASON20",
            "tracking": {
                "source": "partner-checkout",
                "utmSource": "jason-newsletter",
                "utmMedium": "email",
                "utmCampaign": "spring-launch",
            },
            "sendReceipt": True,
            "customFields": {
                "campaign": "spring_launch",
                "crmOrderId": "crm_981",
            },
        },
        "send_email": False,
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "patientId": "abc123",
    "partnerPatientId": "partner_patient_001",
    "orderId": "order456",
    "orderIds": ["order456"],
    "visitId": null,
    "chartReviewId": null,
    "patientStatus": "pending",
    "orderStatus": "pending_payment",
    "orderType": "product",
    "paymentStatus": "unpaid",
    "paymentVerificationStatus": "not_required",
    "paymentVerification": null,
    "requiredActions": ["forms", "patient_continuation"],
    "requirementSummary": {
      "totalForms": 2,
      "hasForms": true
    },
    "continuationSupported": true,
    "duplicateOrder": false,
    "emailSent": false,
    "orders": [
      {
        "orderId": "order456",
        "visitId": null,
        "chartReviewId": null,
        "clientProductId": "clientA_network1_prodX",
        "productId": "prodX",
        "orderType": "product",
        "orderStatus": "pending_payment",
        "paymentStatus": "unpaid",
        "paymentVerificationStatus": "not_required",
        "paymentVerification": null,
        "amount": "200.00",
        "customFields": {
          "campaign": "spring_launch",
          "crmOrderId": "crm_981"
        },
        "duplicateOrder": false
      }
    ],
    "magicLink": "https://app.gen-health.app/magic-login?email=jane%40example.com&token=a1b2c3..."
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Patient profile incomplete. Remediation: provide firstName, lastName, email, phone, dateOfBirth, and address.street1/city/state/zip when creating a new patient."
}
```

## GET /v2/client/orders

List client orders.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/orders",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "orders": [
      {
        "orderId": "order456",
        "patientId": "abc123",
        "partnerPatientId": "partner_001",
        "clientId": "clientA",
        "providerNetworkId": "network1",
        "clientProductId": "clientA_network1_prodX",
        "productId": "prodX",
        "productName": "Weight Loss Program",
        "displayName": "Weight Loss Program",
        "orderType": "product",
        "orderStatus": "pending_review",
        "paymentStatus": "paid",
        "paymentVerificationStatus": "not_required",
        "amount": 19900,
        "quantity": 1,
        "items": [],
        "prescriptions": [
          {
            "prescriptionId": "rx_123",
            "orderId": "order456",
            "medicationName": "Medication name",
            "status": "sent",
            "trackingNumber": null,
            "createdAt": "2026-03-01T12:10:00.000Z"
          }
        ],
        "reviewRequired": "async",
        "visitId": null,
        "customFields": {
          "crmOrderId": "crm_981"
        },
        "paymentGateway": "client_api",
        "createdAt": "2026-03-01T12:00:00.000Z",
        "updatedAt": "2026-03-01T12:00:00.000Z"
      }
    ],
    "pagination": {
      "limit": 50,
      "hasMore": false,
      "nextCursor": null
    }
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Patient not found for client. Remediation: use a patientId or partnerPatientId from List client patients."
}
```

### 401 Response

```json
{
  "success": false,
  "error": "API key required or invalid."
}
```

## GET /v2/client/orders/:orderId

Get order detail.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/orders/:orderId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "order": {
      "orderId": "order456",
      "patientId": "abc123",
      "partnerPatientId": "partner_001",
      "clientProductId": "clientA_network1_prodX",
      "orderType": "product",
      "orderStatus": "pending_review",
      "paymentStatus": "paid",
      "amount": 19900,
      "prescriptions": [
        {
          "prescriptionId": "rx_123",
          "orderId": "order456",
          "medicationName": "Medication name",
          "status": "sent",
          "trackingNumber": null
        }
      ],
      "visitId": null,
      "customFields": {
        "crmOrderId": "crm_981"
      },
      "createdAt": "2026-03-01T12:00:00.000Z",
      "updatedAt": "2026-03-01T12:00:00.000Z"
    }
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Order not found for client. Remediation: use an orderId returned by List client orders, Create consult order, or Create lab order."
}
```

## PATCH /v2/client/orders/:orderId

Cancel order, or mark an unpaid product order as paid.

### Python Request: Cancel Order

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/orders/:orderId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "status": "cancelled",
    },
)
print(response.status_code, response.json())
```

### 200 Response: Cancel Order

```json
{
  "success": true,
  "data": {
    "order": {
      "orderId": "order456",
      "patientId": "abc123",
      "partnerPatientId": "partner_001",
      "clientId": "clientA",
      "providerNetworkId": "network1",
      "clientProductId": "clientA_network1_prodX",
      "productId": "prodX",
      "productName": "Weight Loss Program",
      "displayName": "Weight Loss Program",
      "orderType": "product",
      "orderStatus": "cancelled",
      "paymentStatus": "unpaid",
      "paymentVerificationStatus": "not_required",
      "amount": 19900,
      "quantity": 1,
      "items": [],
      "reviewRequired": "async",
      "visitId": null,
      "customFields": {
        "crmOrderId": "crm_981"
      },
      "paymentGateway": "client_api",
      "createdAt": "2026-03-01T12:00:00.000Z",
      "updatedAt": "2026-03-01T12:05:00.000Z"
    }
  }
}
```

### Python Request: Mark Order Paid

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/orders/:orderId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "payment_status": "paid",
        "transaction_id": "pi_3abc123",
    },
)
print(response.status_code, response.json())
```

### 200 Response: Mark Order Paid

```json
{
  "success": true,
  "data": {
    "order": {
      "orderId": "order456",
      "patientId": "abc123",
      "partnerPatientId": "partner_001",
      "clientId": "clientA",
      "providerNetworkId": "network1",
      "clientProductId": "clientA_network1_prodX",
      "productId": "prodX",
      "productName": "Weight Loss Program",
      "displayName": "Weight Loss Program",
      "orderType": "product",
      "orderStatus": "pending_review",
      "paymentStatus": "paid",
      "paymentVerificationStatus": "trusted",
      "amount": 19900,
      "quantity": 1,
      "items": [],
      "reviewRequired": "async",
      "visitId": "order_order456",
      "customFields": {
        "crmOrderId": "crm_981"
      },
      "paymentGateway": "client_api",
      "paymentDate": "2026-03-01T12:05:00.000Z",
      "createdAt": "2026-03-01T12:00:00.000Z",
      "updatedAt": "2026-03-01T12:05:00.000Z"
    },
    "visitId": "order_order456",
    "chartReviewId": "order_order456",
    "requiredActions": [],
    "requirementSummary": {
      "totalForms": 0,
      "hasForms": false
    },
    "duplicateOrder": false
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "400 Invalid status. Remediation: use status: \"cancelled\" or payment_status: \"paid\"."
}
```

### 405 Response

```json
{
  "success": false,
  "error": "Method not allowed. Use the documented HTTP method for this endpoint."
}
```

## DELETE /v2/client/orders/:orderId

Cancel order with DELETE.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.delete(
    "https://api.gen-health.app/v2/client/orders/:orderId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "order": {
      "orderId": "order456",
      "orderStatus": "cancelled"
    }
  }
}
```

## POST /v2/client/patients/:patientId/consults

Create product order for patient.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/patients/:patientId/consults",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "order": {
            "clientProductId": "clientA_network1_prodX",
            "payment_status": "paid",
            "amount": "199.00",
        },
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "orderId": "order456",
    "patientId": "abc123",
    "productId": "prodX",
    "clientProductId": "clientA_network1_prodX",
    "orderType": "product",
    "orderStatus": "pending_forms",
    "paymentStatus": "paid",
    "requiredActions": [
      {
        "type": "forms",
        "status": "required"
      }
    ]
  }
}
```

## GET /v2/client/orders/:orderId/forms

List order forms.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/orders/:orderId/forms",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "order": {
      "orderId": "order456",
      "orderStatus": "pending_forms",
      "formsCompletionStatus": "pending",
      "clientProductId": "clientA_network1_prodX",
      "productId": "prodX"
    },
    "requirementSummary": {
      "totalForms": 2,
      "completedForms": 0,
      "remainingForms": 2,
      "hasForms": true,
      "formsCompletionStatus": "pending"
    },
    "forms": [
      {
        "formKey": "provider_network:network1:intakeA",
        "formId": "intakeA",
        "scopeType": "provider_network",
        "providerNetworkId": "network1",
        "name": "Medical Intake",
        "formType": "intake",
        "version": 3,
        "completed": false,
        "detailPath": "/v2/client/forms/provider_network%3Anetwork1%3AintakeA?orderId=order456"
      }
    ]
  }
}
```

## GET /v2/client/orders/:orderId/forms/:formKey

Get order form detail.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/orders/:orderId/forms/:formKey",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "form": {
      "formKey": "provider_network:network1:intakeA",
      "formId": "intakeA",
      "scopeType": "provider_network",
      "name": "Medical Intake",
      "formType": "intake",
      "version": 3,
      "sections": [
        {
          "sectionId": "medical_history",
          "title": "Medical history",
          "questions": [
            {
              "questionId": "allergies",
              "label": "Known allergies",
              "type": "textarea",
              "required": false
            }
          ]
        }
      ]
    }
  }
}
```

## POST /v2/client/orders/:orderId/forms/submissions

Submit order forms.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/orders/:orderId/forms/submissions",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "orderId": "order456",
        "patientId": "abc123",
        "submissions": [
            {
                "formKey": "provider_network:network1:intakeA",
                "responses": {
                    "medical_history": {
                        "allergies": "No known allergies",
                    },
                },
            },
        ],
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "submissions": [
      {
        "formKey": "provider_network:network1:intakeA",
        "submissionId": "api_form_...",
        "duplicate": false
      }
    ],
    "formsCompletionStatus": "complete",
    "visitId": "order_order456",
    "chartReviewId": "order_order456"
  }
}
```

## GET /v2/client/forms

List order forms by query.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/forms",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "order": {
      "orderId": "order456",
      "formsCompletionStatus": "pending"
    },
    "patient": {
      "patientId": "abc123",
      "partnerPatientId": "partner_patient_001"
    },
    "requirementSummary": {
      "totalForms": 1,
      "remainingForms": 1,
      "formsCompletionStatus": "pending"
    },
    "forms": [
      {
        "formKey": "provider_network:network1:intakeA",
        "formId": "intakeA",
        "scopeType": "provider_network",
        "name": "Medical Intake",
        "completionStatus": "pending",
        "detailPath": "/v2/client/forms/provider_network%3Anetwork1%3AintakeA?orderId=order456"
      }
    ]
  }
}
```

## GET /v2/client/forms/:formKey

Get order form detail by query.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/forms/:formKey",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "order": {
      "orderId": "order456",
      "formsCompletionStatus": "pending"
    },
    "patient": {
      "patientId": "abc123",
      "partnerPatientId": "partner_patient_001"
    },
    "form": {
      "formKey": "provider_network:network1:intakeA",
      "formId": "intakeA",
      "scopeType": "provider_network",
      "name": "Medical Intake",
      "sections": [
        {
          "sectionId": "medical_history",
          "questions": [
            {
              "questionId": "allergies",
              "label": "Known allergies",
              "type": "textarea",
              "required": false
            }
          ]
        }
      ]
    }
  }
}
```

## POST /v2/client/forms/submissions

Submit order forms by body orderId.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/forms/submissions",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "orderId": "order456",
        "patientId": "abc123",
        "submissions": [
            {
                "formKey": "provider_network:network1:intakeA",
                "responses": {
                    "medical_history": {
                        "allergies": "No known allergies",
                    },
                },
            },
        ],
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "order": {
      "orderId": "order456",
      "formsCompletionStatus": "complete"
    },
    "patient": {
      "patientId": "abc123",
      "partnerPatientId": "partner_patient_001"
    },
    "submissions": [
      {
        "formKey": "provider_network:network1:intakeA",
        "formId": "intakeA",
        "scopeType": "provider_network",
        "submissionId": "api_form_order456_provider_network_network1_intakeA",
        "duplicate": false
      }
    ],
    "formsCompletionStatus": "complete",
    "visitId": "order_order456",
    "chartReviewId": "order_order456"
  }
}
```

## GET /v2/client/labs

List lab products.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/labs",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "labs": [
      {
        "clientProductId": "clientA_network1_labY",
        "productId": "labY",
        "name": "Comprehensive Lab Panel",
        "displayName": "Comprehensive Lab Panel"
      }
    ]
  }
}
```

### 401 Response

```json
{
  "success": false,
  "error": "API key required or invalid."
}
```

### 405 Response

```json
{
  "success": false,
  "error": "Method not allowed. Use the documented HTTP method for this endpoint."
}
```

## POST /v2/client/patients/:patientId/labs/submissions

Upload lab results.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/patients/:patientId/labs/submissions",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "patientId": "partner_patient_001",
        "labName": "CMP",
        "resultDate": "2026-03-01",
        "notes": "Fasting sample collected at clinic",
        "results": [
            {
                "biomarker": "Glucose",
                "value": "92",
                "unit": "mg/dL",
            },
        ],
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "documentId": "doc_123",
    "patientId": "abc123",
    "partnerPatientId": "partner_patient_001",
    "type": "Lab Results",
    "name": "CMP - 2026-03-01"
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Patient not found for client. Remediation: use a patientId or partnerPatientId returned by the client patients endpoints."
}
```

## GET /v2/client/labs/:clientProductId

Get lab detail.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/labs/:clientProductId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "lab": {
      "clientProductId": "clientA_network1_labY"
    }
  }
}
```

## POST /v2/client/labs/requests

Create lab request.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/labs/requests",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "patient_id": "abc123",
        "order": {
            "clientProductId": "clientA_network1_labY",
            "payment_status": "paid",
            "amount": "150.00",
        },
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "orderId": "order456",
    "patientId": "abc123",
    "productId": "labY",
    "clientProductId": "clientA_network1_labY",
    "orderType": "lab",
    "orderStatus": "pending",
    "paymentStatus": "paid",
    "requiredActions": []
  }
}
```

## POST /v2/client/patients/:patientId/visit-requests

Create visit request.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/patients/:patientId/visit-requests",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "patient": {
            "email": "jane@example.com",
            "firstName": "Jane",
            "lastName": "Smith",
            "phone": "5551234567",
            "dateOfBirth": "1990-05-15",
            "address": {
                "street1": "123 Main Street",
                "city": "Austin",
                "state": "TX",
                "zip": "78701",
            },
        },
        "visit": {
            "date": "2026-03-10",
            "time": "14:30",
            "visitType": "Consultation",
            "preferredMethod": "video",
            "duration": 30,
            "notes": "Initial consultation",
        },
        "send_email": False,
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "patientId": "abc123",
    "partnerPatientId": null,
    "visitId": "abc123_4_consultation",
    "visitNumber": 4,
    "visitStatus": "Pending Review",
    "visitType": "Consultation",
    "date": "2026-03-10",
    "time": "14:30",
    "preferredMethod": "video",
    "duration": 30,
    "patientStatus": "pending",
    "requiredActions": [
      "sync_visit",
      "patient_continuation"
    ],
    "continuationSupported": true,
    "emailSent": false,
    "magicLink": "https://app.gen-health.app/magic-login?email=jane%40example.com&token=a1b2c3..."
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Patient profile incomplete. Remediation: provide firstName, lastName, email, phone, dateOfBirth, and address.street1/city/state/zip when creating a new patient."
}
```

## GET /v2/client/visits

List visit products.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/visits",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "visits": [
      {
        "clientProductId": "clientA_network1_visitZ",
        "productId": "visitZ",
        "name": "Initial Visit",
        "displayName": "Initial Visit"
      }
    ]
  }
}
```

## GET /v2/client/patients/:patientId/visit-availability

Get sync visit availability.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/patients/:patientId/visit-availability",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "availability": {
      "2026-04-22": [
        "09:00",
        "09:30"
      ]
    },
    "recommendedProvider": {
      "providerId": "provider_123"
    }
  }
}
```

## POST /v2/client/patients/:patientId/visits

Book sync visit.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/patients/:patientId/visits",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "patientId": "abc123",
        "visit": {
            "providerId": "provider_123",
            "date": "2026-04-20",
            "time": "09:30",
            "scheduledAtMillis": 1776682200000,
            "relatedOrderId": "order456",
            "patientTimezone": "America/New_York",
        },
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "visitId": "visit_123",
    "visitStatus": "Confirmed",
    "requiredActions": []
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "visit.date and visit.time are required. Remediation: include visit.date (YYYY-MM-DD) and visit.time (HH:mm, 24-hour format)."
}
```

## PATCH /v2/client/visits/:visitId

Update sync visit.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/visits/:visitId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "scheduledAtMillis": 1776768600000,
        "patientTimezone": "America/New_York",
        "status": "Confirmed",
    },
)
print(response.status_code, response.json())
```

### Response

No example response provided in the API docs.

## DELETE /v2/client/visits/:visitId

Cancel sync visit.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.delete(
    "https://api.gen-health.app/v2/client/visits/:visitId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "cancellationReason": "Patient requested a new time",
    },
)
print(response.status_code, response.json())
```

### Response

No example response provided in the API docs.

## POST /v2/client/visits/:visitId/magic-links

Create visit access link.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/visits/:visitId/magic-links",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "visitId": "visit_123",
    "visitAccessUrl": "https://gen-health.app/magic-login?...",
    "expiresAt": "2026-04-17T15:30:00.000Z"
  }
}
```

## GET /v2/client/post-visit-redirect

Get post-visit redirect settings.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/post-visit-redirect",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "postVisitRedirectEnabled": true,
    "postVisitRedirectUrl": "https://example.com/thank-you"
  }
}
```

## PATCH /v2/client/post-visit-redirect

Update post-visit redirect settings.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/post-visit-redirect",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "postVisitRedirectEnabled": True,
        "postVisitRedirectUrl": "https://example.com/thank-you",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "postVisitRedirectEnabled": true,
    "postVisitRedirectUrl": "https://example.com/thank-you"
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "postVisitRedirectEnabled is required. Remediation: send a boolean postVisitRedirectEnabled field in the request body."
}
```

## GET /v2/client/patients/:patientId/visits

List patient visits.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/patients/:patientId/visits",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "visits": []
  }
}
```

## GET /v2/client/visits/:visitId

Get visit detail.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/visits/:visitId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "visit": {
      "visitId": "visit_123"
    }
  }
}
```

## GET /v2/client/conversations

List conversations.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/conversations",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "conversations": []
  }
}
```

## POST /v2/client/conversations

Create conversation.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/conversations",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "patientId": "abc123",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "conversation": {
      "conversationId": "conv_123"
    }
  }
}
```

## GET /v2/client/conversations/:conversationId

Get or update conversation.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/conversations/:conversationId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "conversation": {
      "conversationId": "conv_123",
      "status": "active"
    }
  }
}
```

## POST /v2/client/conversations/:conversationId/messages

Send client-authored message.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/conversations/:conversationId/messages",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "author": "client",
        "senderUserId": "client_staff_123",
        "text": "Your order is ready for review.",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "message": {
      "messageId": "msg_123",
      "text": "Your order is ready for review.",
      "senderId": "client_staff_123",
      "senderName": "Care Team",
      "senderType": "Client Staff",
      "deliveryStatus": "sent",
      "direction": "outbound",
      "sentVia": "api",
      "actorId": "client_api:api_key_123",
      "onBehalfOfUserId": "client_staff_123",
      "sentOnBehalfOfPatient": false
    }
  }
}
```

## POST /v2/client/conversations/:conversationId/messages

Send patient-authored message.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/conversations/:conversationId/messages",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "author": "patient",
        "patientId": "abc123",
        "text": "I uploaded my intake form.",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "message": {
      "messageId": "msg_456",
      "text": "I uploaded my intake form.",
      "senderId": "abc123",
      "senderName": "Jane Smith",
      "senderType": "Patient",
      "deliveryStatus": "received",
      "direction": "inbound",
      "sentVia": "api",
      "actorId": "client_api:api_key_123",
      "onBehalfOfUserId": "abc123",
      "sentOnBehalfOfPatient": true
    }
  }
}
```

## PATCH /v2/client/conversations/:conversationId

Update conversation status.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/conversations/:conversationId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "status": "closed",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "conversation": {
      "conversationId": "conv_123",
      "patientId": "abc123",
      "status": "closed",
      "escalatedToProvider": false,
      "providerInboxVisible": false,
      "lastMessageText": "Your order is ready for review."
    }
  }
}
```

## DELETE /v2/client/conversations/:conversationId

Archive conversation.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.delete(
    "https://api.gen-health.app/v2/client/conversations/:conversationId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "conversation": {
      "conversationId": "conv_123",
      "patientId": "abc123",
      "status": "archived"
    }
  }
}
```

## POST /v2/client/conversations/:conversationId/escalations

Escalate conversation to provider network.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/conversations/:conversationId/escalations",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "reason": "Patient needs clinical review",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "conversation": {
      "conversationId": "conv_123",
      "patientId": "abc123",
      "status": "active",
      "escalatedToProvider": true,
      "providerInboxVisible": true,
      "providerNetworkId": "network1"
    }
  }
}
```

## GET /v2/client/conversations/:conversationId/messages

List conversation messages.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/conversations/:conversationId/messages",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "messageId": "msg_123",
        "text": "Your order is ready for review.",
        "senderName": "Client API",
        "senderType": "Client API",
        "attachments": [],
        "deliveryStatus": "sent",
        "direction": "outbound",
        "sentVia": "api",
        "createdAt": "2026-03-01T12:00:00.000Z"
      }
    ]
  }
}
```

## GET /v2/client/conversations/:conversationId/messages/:messageId

Get conversation message.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/conversations/:conversationId/messages/:messageId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "message": {
      "messageId": "msg_123",
      "text": "Your order is ready for review.",
      "senderName": "Client API",
      "senderType": "Client API",
      "attachments": [],
      "deliveryStatus": "sent",
      "direction": "outbound",
      "sentVia": "api"
    }
  }
}
```

## PATCH /v2/client/conversations/:conversationId/messages/:messageId

Update conversation message.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/conversations/:conversationId/messages/:messageId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "text": "Your order is ready for review today.",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "message": {
      "messageId": "msg_123",
      "text": "Your order is ready for review today.",
      "updatedAt": "2026-03-01T12:05:00.000Z"
    }
  }
}
```

## DELETE /v2/client/conversations/:conversationId/messages/:messageId

Delete conversation message.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.delete(
    "https://api.gen-health.app/v2/client/conversations/:conversationId/messages/:messageId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "message": {
      "messageId": "msg_123",
      "text": "Your order is ready for review.",
      "deletedAt": "2026-03-01T12:05:00.000Z"
    }
  }
}
```

## GET /v2/client/prescriptions

List prescriptions.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/prescriptions",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "prescriptions": [
      {
        "prescriptionId": "rx_123",
        "patientId": "abc123",
        "clientId": "clientA",
        "orderId": "order456",
        "chartReviewId": "review_123",
        "providerNetworkId": "network1",
        "providerUserId": "provider_123",
        "providerName": "Dr. Example",
        "source": "scriptsure",
        "medicationName": "Medication name",
        "dosage": "10 mg",
        "units": "tablet",
        "instructions": "Take once daily",
        "quantity": 30,
        "daysSupply": 30,
        "refills": 0,
        "status": "sent",
        "submittedToPharmacy": true,
        "trackingNumber": null,
        "trackingCarrier": null,
        "trackingUrl": null,
        "prescribedDate": "2026-03-01T12:00:00.000Z",
        "submittedAt": "2026-03-01T12:05:00.000Z",
        "shippedAt": null,
        "deliveredAt": null,
        "createdAt": "2026-03-01T12:00:00.000Z",
        "updatedAt": "2026-03-01T12:05:00.000Z"
      }
    ]
  }
}
```

## GET /v2/client/prescriptions/:prescriptionId

Get prescription detail.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/prescriptions/:prescriptionId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "prescription": {
      "prescriptionId": "rx_123",
      "patientId": "abc123",
      "orderId": "order456",
      "medicationName": "Medication name",
      "status": "sent",
      "submittedToPharmacy": true,
      "trackingNumber": null,
      "createdAt": "2026-03-01T12:00:00.000Z",
      "updatedAt": "2026-03-01T12:05:00.000Z"
    }
  }
}
```

## POST /v2/client/prescriptions/:prescriptionId/notification-rules

Manage prescription notification rules.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/prescriptions/:prescriptionId/notification-rules",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "anchor": "submittedAt",
        "direction": "after",
        "unit": "days",
        "amount": 3,
        "channels": {
            "email": True,
        },
        "messageHtml": "<p>Your prescription is being processed.</p>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "notificationRule": {
      "ruleId": "rule_123"
    }
  }
}
```

## GET /v2/client/prescriptions/:prescriptionId/notification-rules

List prescription notification rules.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/prescriptions/:prescriptionId/notification-rules",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "prescription": {
      "prescriptionId": "rx_123",
      "patientId": "abc123",
      "status": "sent",
      "medicationName": "Semaglutide"
    },
    "notificationRules": [
      {
        "ruleId": "rule_123",
        "enabled": true,
        "anchor": "submittedAt",
        "direction": "after",
        "unit": "days",
        "amount": 3,
        "channels": {
          "email": true
        },
        "messageHtml": "<p>Your prescription is being processed.</p>",
        "nextJob": null,
        "jobs": []
      }
    ]
  }
}
```

## PATCH /v2/client/prescriptions/:prescriptionId/notification-rules/:ruleId

Update prescription notification rule.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/prescriptions/:prescriptionId/notification-rules/:ruleId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "enabled": True,
        "anchor": "submittedAt",
        "direction": "after",
        "unit": "days",
        "amount": 5,
        "channels": {
            "email": True,
        },
        "messageText": "Your prescription is still being processed.",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "notificationRule": {
      "ruleId": "rule_123",
      "enabled": true,
      "anchor": "submittedAt",
      "direction": "after",
      "unit": "days",
      "amount": 5,
      "channels": {
        "email": true
      },
      "messageText": "Your prescription is still being processed."
    },
    "rebuild": {
      "created": 1,
      "cancelled": 1
    }
  }
}
```

## DELETE /v2/client/prescriptions/:prescriptionId/notification-rules/:ruleId

Delete prescription notification rule.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.delete(
    "https://api.gen-health.app/v2/client/prescriptions/:prescriptionId/notification-rules/:ruleId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "ruleId": "rule_123",
    "deleted": true,
    "rebuild": {
      "created": 0,
      "cancelled": 1
    }
  }
}
```

## POST /v2/client/payments/affiliate/sessions

Create affiliate payment session.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/payments/affiliate/sessions",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "clientProductId": "clientA_network1_prodX",
        "idempotencyKey": "checkout_2026_03_01_abc123",
        "patient": {
            "email": "jane@example.com",
            "firstName": "Jane",
            "lastName": "Smith",
            "partnerPatientId": "partner_001",
        },
        "couponCode": "SPRING100",
        "send_receipt": True,
        "successUrl": "https://storefront.example.com/success",
        "cancelUrl": "https://storefront.example.com/cancel",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "paymentSessionId": "aps_...",
  "paymentSessionToken": "apst_...",
  "mode": "stripe",
  "status": "pending_payment",
  "expiresAt": "2026-03-01T12:30:00.000Z",
  "summary": {
    "primaryItem": {
      "name": "Weight Loss Program"
    },
    "pricing": {
      "subtotalAmount": 199,
      "discountAmount": 0,
      "totalAmount": 199
    }
  },
  "pricing": {
    "baseAmountCents": 19900,
    "discountAmountCents": 0,
    "finalAmountCents": 19900,
    "baseAmount": 199,
    "discountAmount": 0,
    "finalAmount": 199
  },
  "appliedCoupon": null,
  "publicKey": "pk_live_...",
  "stripeCheckoutSessionId": "cs_test_..."
}
```

### 400 Response

```json
{
  "success": false,
  "error": "idempotencyKey already used with a different payload. Remediation: generate a new idempotencyKey for the new payload."
}
```

## POST /v2/client/payments/affiliate/session-completions

Complete affiliate payment session.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/payments/affiliate/session-completions",
    headers={
        "X-Payment-Session-Id": "<paymentSessionId>",
        "X-Payment-Session-Token": "<paymentSessionToken>",
    },
    json={
        "paymentSessionId": "aps_...",
        "paymentSessionToken": "apst_...",
        "billingInfo": {
            "firstName": "Jane",
            "lastName": "Smith",
            "street1": "123 Main St",
            "city": "Austin",
            "state": "TX",
            "zip": "78701",
            "email": "jane@example.com",
            "phone": "5551234567",
        },
        "sameAsBilling": True,
        "opaqueData": {
            "dataDescriptor": "COMMON.ACCEPT.INAPP.PAYMENT",
            "dataValue": "...",
        },
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "paymentSessionId": "aps_...",
  "status": "paid",
  "paid": true,
  "orderId": "order_xyz",
  "patientId": "abc123",
  "paymentStatus": "paid",
  "paymentGateway": "authorize",
  "magicLoginUrl": "https://gen-health.app/magic-login?...",
  "summary": {
    "primaryItem": {
      "name": "Weight Loss Program"
    }
  },
  "pricing": {
    "finalAmount": 199
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Session mode is not authorize (HTTP 422). Remediation: for Stripe sessions, redirect the shopper to the returned checkout URL instead."
}
```

## GET /v2/client/payments/affiliate/session-status

Get affiliate payment session status.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/payments/affiliate/session-status",
    headers={
        "X-Payment-Session-Id": "<paymentSessionId>",
        "X-Payment-Session-Token": "<paymentSessionToken>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "paymentSessionId": "aps_...",
  "mode": "stripe",
  "status": "paid",
  "paid": true,
  "orderId": "order_xyz",
  "patientId": "abc123",
  "paymentStatus": "paid",
  "paymentGateway": "stripe",
  "magicLoginUrl": "https://gen-health.app/magic-login?...",
  "expiresAt": "2026-03-01T12:30:00.000Z",
  "summary": {
    "primaryItem": {
      "name": "Weight Loss Program"
    }
  },
  "pricing": {
    "finalAmount": 199
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Invalid or expired paymentSessionToken. Remediation: the token is invalid or the session expired — start a new checkout with createAffiliatePaymentSession."
}
```

## POST /v2/client/payments/affiliate/session-status

Get affiliate payment session status with JSON body.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/payments/affiliate/session-status",
    headers={},
    json={
        "paymentSessionId": "aps_...",
        "paymentSessionToken": "apst_...",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "paymentSessionId": "aps_...",
  "mode": "stripe",
  "status": "paid",
  "paid": true,
  "orderId": "order_xyz",
  "patientId": "abc123",
  "paymentStatus": "paid",
  "paymentGateway": "stripe"
}
```

## GET /v2/client/promocodes

List promocodes.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/promocodes",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "promocodes": [
      {
        "promocodeId": "doc_abc123",
        "code": "JASON20",
        "normalizedCode": "JASON20",
        "name": "Jason 20% off",
        "status": "active",
        "discount": {
          "type": "percentage_off",
          "value": 20
        },
        "assignmentType": "locked",
        "affiliates": [
          {
            "affiliateId": "aff_jason",
            "utmSlug": "jason-lab"
          }
        ],
        "utmSlug": "jason-lab",
        "applicability": {
          "scope": "category_ids",
          "productIds": [],
          "categoryIds": [
            "cat_mens_health"
          ]
        },
        "eligibleClientProductIds": [],
        "maxUsage": 500,
        "usageCount": 12,
        "validity": {
          "startsAt": "2026-01-01T00:00:00.000Z",
          "endsAt": "2026-12-31T23:59:59.000Z"
        },
        "createdAt": "2026-01-15T10:00:00.000Z",
        "updatedAt": "2026-04-10T18:30:00.000Z"
      }
    ],
    "pagination": {
      "limit": 50,
      "hasMore": false,
      "nextCursor": null
    }
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "400 Invalid status. Remediation: use one of [\"active\", \"inactive\"]."
}
```

## GET /v2/client/promocodes/:code

Get promocode by code.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/promocodes/:code",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "promocode": {
      "promocodeId": "doc_abc123",
      "code": "JASON20",
      "normalizedCode": "JASON20",
      "name": "Jason 20% off",
      "status": "active",
      "discount": {
        "type": "percentage_off",
        "value": 20
      },
      "assignmentType": "locked",
      "affiliates": [
        {
          "affiliateId": "aff_jason",
          "utmSlug": "jason-lab"
        }
      ],
      "utmSlug": "jason-lab",
      "applicability": {
        "scope": "all_products",
        "productIds": [],
        "categoryIds": []
      },
      "eligibleClientProductIds": [],
      "maxUsage": null,
      "usageCount": 12,
      "validity": null,
      "createdAt": "2026-01-15T10:00:00.000Z",
      "updatedAt": "2026-04-10T18:30:00.000Z"
    }
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "404 Promocode '<code>' was not found for this client. Remediation: use GET /v2/client/promocodes to list valid codes."
}
```

## PATCH /v2/client/promocodes/:code

Update promocode (sync utmSlug or affiliate metadata).

### Python Request

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/promocodes/:code",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "utmSlug": "jason-lab",
        "affiliateId": "aff_jason",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "promocode": {
      "promocodeId": "doc_abc123",
      "code": "JASON20",
      "normalizedCode": "JASON20",
      "name": "Jason 20% off",
      "status": "active",
      "discount": {
        "type": "percentage_off",
        "value": 20
      },
      "assignmentType": "locked",
      "affiliates": [
        {
          "affiliateId": "aff_jason",
          "utmSlug": "jason-lab"
        }
      ],
      "utmSlug": "jason-lab",
      "applicability": {
        "scope": "all_products",
        "productIds": [],
        "categoryIds": []
      },
      "eligibleClientProductIds": [],
      "maxUsage": null,
      "usageCount": 12,
      "validity": null,
      "createdAt": "2026-01-15T10:00:00.000Z",
      "updatedAt": "2026-05-01T09:00:00.000Z"
    }
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "400 code is required. Remediation: include the code in the URL."
}
```

## GET /v2/client/promocodes/validations

Validate promocode for one or more products (read-only).

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/promocodes/validations",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "valid": true,
    "reasonCodes": [],
    "promocode": {
      "code": "JASON20",
      "name": "Jason 20% off",
      "assignmentType": "locked",
      "discount": {
        "type": "percentage_off",
        "value": 20
      },
      "applicability": {
        "scope": "all_products",
        "productIds": [],
        "categoryIds": []
      },
      "utmSlug": "jason-lab"
    },
    "product": {
      "clientProductId": "clientA_network1_prodX",
      "productId": "prodX",
      "name": "PT-141 / Oxytocin / Tadalafil"
    },
    "pricing": {
      "currency": "usd",
      "quantity": 1,
      "unitPrice": {
        "amountCents": 19900,
        "amount": 199.00,
        "currency": "usd"
      },
      "unitDiscount": {
        "amountCents": 3980,
        "amount": 39.80,
        "currency": "usd"
      },
      "unitTotal": {
        "amountCents": 15920,
        "amount": 159.20,
        "currency": "usd"
      },
      "lineSubtotal": {
        "amountCents": 19900,
        "amount": 199.00,
        "currency": "usd"
      },
      "lineDiscount": {
        "amountCents": 3980,
        "amount": 39.80,
        "currency": "usd"
      },
      "lineTotal": {
        "amountCents": 15920,
        "amount": 159.20,
        "currency": "usd"
      }
    }
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "403 This origin is not allowed for the provided storefront key. Remediation: add the origin under the storefront key allowlist."
}
```

## POST /v2/client/promocodes/validations

Validate promocode with JSON body.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.post(
    "https://api.gen-health.app/v2/client/promocodes/validations",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "code": "JASON20",
        "clientProductIds": [
            "clientA_network1_prodX",
            "clientA_network1_prodY",
        ],
        "quantity": 1,
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "valid": true,
    "appliesToAny": true,
    "allValid": true,
    "reasonCodes": [],
    "items": [
      {
        "clientProductId": "clientA_network1_prodX",
        "valid": true,
        "reasonCodes": [],
        "pricing": {
          "lineTotal": {
            "amount": 159.20,
            "currency": "usd"
          }
        }
      }
    ]
  }
}
```

## PATCH /v2/client/business/branding

Get or update business branding.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/business/branding",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "displayName": "Acme Health",
        "brandingSlug": "acme-health",
        "accentColor": "#2563eb",
        "layoutOptions": {
            "checkoutTheme": {
                "layoutPreset": "editorial",
                "headline": "Complete checkout",
            },
        },
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "branding": {
      "clientId": "clientA",
      "displayName": "Acme Health",
      "website": "https://acme.example",
      "supportEmail": "support@acme.example",
      "phoneNumber": "+15551234567",
      "brandingSlug": "acme-health",
      "customDomain": null,
      "layoutOptions": {
        "checkoutTheme": {
          "layoutPreset": "editorial",
          "headline": "Complete checkout"
        },
        "loginTheme": null,
        "emailTheme": null,
        "formTheme": null
      },
      "colors": {
        "accentColor": "#2563eb",
        "primaryColor": "#2563eb",
        "secondaryColor": null,
        "backgroundColor": null,
        "sidebarHeaderBackgroundColor": null
      }
    }
  }
}
```

## GET /v2/client/business/branding

Get business branding.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/business/branding",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "branding": {
      "clientId": "clientA",
      "displayName": "Acme Health",
      "brandingSlug": "acme-health",
      "layoutOptions": {
        "checkoutTheme": {
          "layoutPreset": "editorial"
        },
        "loginTheme": null,
        "emailTheme": null,
        "formTheme": null
      }
    }
  }
}
```

## PATCH /v2/client/business/payment-processor

Get or update payment processor.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/business/payment-processor",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "paymentProcessor": "stripe",
        "credentials": {
            "publicKey": "pk_live_...",
            "secretKey": "sk_live_...",
        },
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "paymentProcessor": "stripe",
    "customPaymentInstructions": null,
    "credentialStatus": {
      "stripe": {
        "exists": true,
        "hasKeys": true,
        "fieldStatus": {
          "publicKey": true,
          "secretKey": true
        },
        "updatedAt": "2026-03-01T12:00:00.000Z"
      }
    }
  }
}
```

## GET /v2/client/business/payment-processor

Get payment processor.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/business/payment-processor",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "paymentProcessor": "stripe",
    "customPaymentInstructions": null,
    "credentialStatus": {
      "stripe": {
        "exists": true,
        "hasKeys": true,
        "fieldStatus": {
          "publicKey": true,
          "secretKey": true
        }
      }
    }
  }
}
```

## PATCH /v2/client/business/checkout-options

Get or update checkout options.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/business/checkout-options",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "patientCheckout": {
            "sequence": {
                "products": "intake_before_payment",
                "labs": "payment_before_intake",
            },
        },
        "patientReceipts": {"enabled": True},
        "queuePrescriptionReview": {"enabled": False},
        "postVisitRedirectEnabled": True,
        "postVisitRedirectUrl": "https://example.com/thank-you",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "checkoutOptions": {
      "patientCheckout": {
        "sequence": {
          "products": "intake_before_payment",
          "labs": "payment_before_intake"
        }
      },
      "patientReceipts": {
        "enabled": true
      },
      "queuePrescriptionReview": {
        "enabled": false
      },
      "postVisitRedirectEnabled": true,
      "postVisitRedirectUrl": "https://example.com/thank-you",
      "defaultShippingPrice": null
    }
  }
}
```

## GET /v2/client/business/checkout-options

Get checkout options.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/business/checkout-options",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "checkoutOptions": {
      "patientCheckout": {
        "sequence": {
          "products": "intake_before_payment",
          "labs": "payment_before_intake"
        }
      },
      "patientReceipts": {
        "enabled": true
      },
      "queuePrescriptionReview": {
        "enabled": false
      },
      "postVisitRedirectEnabled": true,
      "postVisitRedirectUrl": "https://example.com/thank-you",
      "defaultShippingPrice": null
    }
  }
}
```

## GET /v2/client/branding

Get client branding.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.get(
    "https://api.gen-health.app/v2/client/branding",
    headers={},
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "id": "clientA",
    "name": "Acme Health",
    "iconUrl": "https://storage.googleapis.com/.../icon.png",
    "logoUrl": "https://storage.googleapis.com/.../logo.png",
    "accentColor": "#2563eb",
    "primaryColor": "#2563eb",
    "secondaryColor": "#0f172a",
    "backgroundColor": "#ffffff",
    "logoWhiteBackground": false
  }
}
```

## PATCH /v2/client/patients/:patientId

Update patient record.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.patch(
    "https://api.gen-health.app/v2/client/patients/:patientId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
    json={
        "firstName": "Jane",
        "lastName": "Smith",
        "phone": "5551234567",
        "address": {
            "street1": "123 Main St",
            "city": "Austin",
            "state": "TX",
            "zip": "78701",
        },
        "customFields": {
            "memberNumber": "M-42",
        },
        "weightJourney": {
            "height": 68,
        },
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "patient": {
      "patientId": "abc123",
      "partnerPatientId": "partner_001",
      "status": "active",
      "requiresOnboarding": false,
      "firstName": "Jane",
      "lastName": "Smith",
      "fullName": "Jane Smith",
      "email": "jane@example.com",
      "phone": "+15551234567",
      "phoneNumber": "+15551234567",
      "dateOfBirth": "1990-05-15",
      "sexAtBirth": "Female",
      "genderIdentity": "Woman",
      "languagePreference": "english",
      "address": {
        "street1": "123 Main St",
        "street2": "",
        "city": "Austin",
        "state": "TX",
        "zip": "78701"
      },
      "treatmentProgram": "weight-loss",
      "medicationDuration": "3-months",
      "allergies": ["penicillin"],
      "currentMedications": ["aspirin"],
      "weightJourney": {
        "currentWeight": 200,
        "height": 68,
        "goalWeight": 180
      },
      "customFields": {
        "memberNumber": "M-42"
      },
      "createdAt": "2026-01-10T12:00:00.000Z",
      "updatedAt": "2026-03-01T08:30:00.000Z"
    }
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "patientId is required. Remediation: include patientId in the endpoint URL."
}
```

## DELETE /v2/client/patients/:patientId

Archive patient.

### Python Request

```python
# requests >= 2.31
import requests

response = requests.delete(
    "https://api.gen-health.app/v2/client/patients/:patientId",
    headers={
        "X-API-Key": "<your-api-key>",
    },
)
print(response.status_code, response.json())
```

### 200 Response

```json
{
  "success": true,
  "data": {
    "patient": {
      "patientId": "abc123",
      "partnerPatientId": "partner_001",
      "status": "archived",
      "requiresOnboarding": false,
      "firstName": "Jane",
      "lastName": "Smith",
      "email": "jane@example.com",
      "updatedAt": "2026-03-01T08:30:00.000Z"
    }
  }
}
```

### 400 Response

```json
{
  "success": false,
  "error": "Patient not found for client. Remediation: use patientId or partnerPatientId values returned by the client patients endpoints."
}
```
