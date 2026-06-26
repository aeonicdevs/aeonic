# Arora API Reference

Source: GEN Health Developers V2 API Beta docs, copied from rendered browser text.
Captured: 2026-06-27
Base URL: `https://api.gen-health.app`

This file is generated from a browser text paste. It currently captures endpoint paths, headers, request parameters, key details, and common errors. It does not yet include full response bodies from the code examples; add those to `response-examples.md`.

## Table Of Contents

- [V2 API Beta Notes](#v2-api-beta-notes)
- [Get Started](#get-started)
- [Patients](#patients)
  - [POST /v2/client/patients](#post-v2clientpatients)
  - [GET /v2/client/patients](#get-v2clientpatients)
  - [GET /v2/client/patients/:patientId](#get-v2clientpatientspatientid)
  - [PATCH /v2/client/patients/:patientId](#patch-v2clientpatientspatientid)
  - [DELETE /v2/client/patients/:patientId](#delete-v2clientpatientspatientid)
  - [POST /v2/client/patients/:patientId/health-logs](#post-v2clientpatientspatientidhealth-logs)
  - [GET /v2/client/patients/:patientId/health-logs](#get-v2clientpatientspatientidhealth-logs)
  - [POST /v2/client/patients/:patientId/onboarding-id](#post-v2clientpatientspatientidonboarding-id)
  - [POST /v2/client/patients/:patientId/continuation-sessions](#post-v2clientpatientspatientidcontinuation-sessions)
- [Products](#products)
  - [GET /v2/client/categories](#get-v2clientcategories)
  - [GET /v2/client/products](#get-v2clientproducts)
  - [GET /v2/client/products/:clientProductId](#get-v2clientproductsclientproductid)
  - [POST /v2/client/products](#post-v2clientproducts)
  - [PATCH /v2/client/products/:clientProductId](#patch-v2clientproductsclientproductid)
  - [DELETE /v2/client/products/:clientProductId](#delete-v2clientproductsclientproductid)
  - [GET /v2/client/products/:clientProductId/forms](#get-v2clientproductsclientproductidforms)
  - [GET /v2/client/products/:clientProductId/forms/:formKey](#get-v2clientproductsclientproductidformsformkey)
  - [GET /v2/client/products/forms](#get-v2clientproductsforms)
- [Orders](#orders)
  - [POST /v2/client/orders](#post-v2clientorders)
  - [GET /v2/client/orders](#get-v2clientorders)
  - [GET /v2/client/orders/:orderId](#get-v2clientordersorderid)
  - [PATCH /v2/client/orders/:orderId](#patch-v2clientordersorderid)
  - [DELETE /v2/client/orders/:orderId](#delete-v2clientordersorderid)
  - [POST /v2/client/patients/:patientId/consults](#post-v2clientpatientspatientidconsults)
- [Order Forms](#order-forms)
  - [GET /v2/client/orders/:orderId/forms](#get-v2clientordersorderidforms)
  - [GET /v2/client/orders/:orderId/forms/:formKey](#get-v2clientordersorderidformsformkey)
  - [POST /v2/client/orders/:orderId/forms/submissions](#post-v2clientordersorderidformssubmissions)
  - [GET /v2/client/forms](#get-v2clientforms)
  - [GET /v2/client/forms/:formKey](#get-v2clientformsformkey)
  - [POST /v2/client/forms/submissions](#post-v2clientformssubmissions)
- [Labs](#labs)
  - [GET /v2/client/labs](#get-v2clientlabs)
  - [POST /v2/client/patients/:patientId/labs/submissions](#post-v2clientpatientspatientidlabssubmissions)
  - [GET /v2/client/labs/:clientProductId](#get-v2clientlabsclientproductid)
  - [POST /v2/client/labs/requests](#post-v2clientlabsrequests)
- [Visits](#visits)
  - [POST /v2/client/patients/:patientId/visit-requests](#post-v2clientpatientspatientidvisit-requests)
  - [GET /v2/client/visits](#get-v2clientvisits)
  - [GET /v2/client/patients/:patientId/visit-availability](#get-v2clientpatientspatientidvisit-availability)
  - [POST /v2/client/patients/:patientId/visits](#post-v2clientpatientspatientidvisits)
  - [PATCH /v2/client/visits/:visitId](#patch-v2clientvisitsvisitid)
  - [DELETE /v2/client/visits/:visitId](#delete-v2clientvisitsvisitid)
  - [POST /v2/client/visits/:visitId/magic-links](#post-v2clientvisitsvisitidmagic-links)
  - [GET /v2/client/post-visit-redirect](#get-v2clientpost-visit-redirect)
  - [PATCH /v2/client/post-visit-redirect](#patch-v2clientpost-visit-redirect)
  - [GET /v2/client/patients/:patientId/visits](#get-v2clientpatientspatientidvisits)
  - [GET /v2/client/visits/:visitId](#get-v2clientvisitsvisitid)
- [Messages](#messages)
  - [GET /v2/client/conversations](#get-v2clientconversations)
  - [POST /v2/client/conversations](#post-v2clientconversations)
  - [GET /v2/client/conversations/:conversationId](#get-v2clientconversationsconversationid)
  - [POST /v2/client/conversations/:conversationId/messages](#post-v2clientconversationsconversationidmessages)
  - [POST /v2/client/conversations/:conversationId/messages](#post-v2clientconversationsconversationidmessages-1)
  - [PATCH /v2/client/conversations/:conversationId](#patch-v2clientconversationsconversationid)
  - [DELETE /v2/client/conversations/:conversationId](#delete-v2clientconversationsconversationid)
  - [POST /v2/client/conversations/:conversationId/escalations](#post-v2clientconversationsconversationidescalations)
  - [GET /v2/client/conversations/:conversationId/messages](#get-v2clientconversationsconversationidmessages)
  - [GET /v2/client/conversations/:conversationId/messages/:messageId](#get-v2clientconversationsconversationidmessagesmessageid)
  - [PATCH /v2/client/conversations/:conversationId/messages/:messageId](#patch-v2clientconversationsconversationidmessagesmessageid)
  - [DELETE /v2/client/conversations/:conversationId/messages/:messageId](#delete-v2clientconversationsconversationidmessagesmessageid)
- [Prescriptions](#prescriptions)
  - [GET /v2/client/prescriptions](#get-v2clientprescriptions)
  - [GET /v2/client/prescriptions/:prescriptionId](#get-v2clientprescriptionsprescriptionid)
  - [POST /v2/client/prescriptions/:prescriptionId/notification-rules](#post-v2clientprescriptionsprescriptionidnotification-rules)
  - [GET /v2/client/prescriptions/:prescriptionId/notification-rules](#get-v2clientprescriptionsprescriptionidnotification-rules)
  - [PATCH /v2/client/prescriptions/:prescriptionId/notification-rules/:ruleId](#patch-v2clientprescriptionsprescriptionidnotification-rulesruleid)
  - [DELETE /v2/client/prescriptions/:prescriptionId/notification-rules/:ruleId](#delete-v2clientprescriptionsprescriptionidnotification-rulesruleid)
- [Payments](#payments)
  - [POST /v2/client/payments/affiliate/sessions](#post-v2clientpaymentsaffiliatesessions)
  - [POST /v2/client/payments/affiliate/session-completions](#post-v2clientpaymentsaffiliatesession-completions)
  - [GET /v2/client/payments/affiliate/session-status](#get-v2clientpaymentsaffiliatesession-status)
  - [POST /v2/client/payments/affiliate/session-status](#post-v2clientpaymentsaffiliatesession-status)
- [Promocodes](#promocodes)
  - [GET /v2/client/promocodes](#get-v2clientpromocodes)
  - [GET /v2/client/promocodes/:code](#get-v2clientpromocodescode)
  - [PATCH /v2/client/promocodes/:code](#patch-v2clientpromocodescode)
  - [GET /v2/client/promocodes/validations](#get-v2clientpromocodesvalidations)
  - [POST /v2/client/promocodes/validations](#post-v2clientpromocodesvalidations)
- [Business](#business)
  - [PATCH /v2/client/business/branding](#patch-v2clientbusinessbranding)
  - [GET /v2/client/business/branding](#get-v2clientbusinessbranding)
  - [PATCH /v2/client/business/payment-processor](#patch-v2clientbusinesspayment-processor)
  - [GET /v2/client/business/payment-processor](#get-v2clientbusinesspayment-processor)
  - [PATCH /v2/client/business/checkout-options](#patch-v2clientbusinesscheckout-options)
  - [GET /v2/client/business/checkout-options](#get-v2clientbusinesscheckout-options)
  - [GET /v2/client/branding](#get-v2clientbranding)
- [Important Defaults](#important-defaults)

## V2 API Beta Notes

- V2 is currently in beta and remains subject to change. Single base URL: https://api.gen-health.app. V1 endpoints remain available for existing integrations but will no longer receive feature updates.

## Get Started

Follow these V2 resource steps to connect your marketing site or app to the GEN Health API.

1. Create an API key

Open Settings → Client API and click “New API Key.” Copy the key once — it is only shown at creation. Paste it into the API Key field above to enable “Try it” for every GET/POST/PATCH/PUT endpoint on this page.

2. List the products you sell

Use the documented Cloud Run URLs for List consult products, List lab products, and List visits to populate your marketing site. Always reference products by clientProductId — never hard-code prices.

3. Create the patient and the order

Create or find the patient, then call POST /v2/client/orders with the chosen clientProductId. Returning customers can pass patient_id or patientId.

4. Process required actions

Read the order response. If requiredActions includes forms, fetch the order form manifest, render each form detail, and submit answers. If uploads or sync visits are required, use continuation, upload-token, availability, and booking endpoints.

Your client model is not set yet

The payment path differs by model. Ask your GEN admin to configure this client as affiliate, gfe_only, or gfe_prescribe, then revisit this page.

5. Reconcile orders and webhooks

Configure your webhook URL in Settings → Client API → Webhooks and choose the specific events you want delivered. Copy the signing secret and verify every request with X-Webhook-Signature (HMAC-SHA256 of the raw body) before trusting it. Common production handlers are patient.created, patient.updated, form.started, form.submitted, order.payment_succeeded, order.status_updated, async_visit.claimed, visit.joined, prescription.sent, prescription.tracking_updated, lab.ordered, and lab.status_updated.

If a webhook is dropped, call the Get order detail endpoint to reconcile state directly.

When to pick Hosted Checkout or SDK

Use Hosted Checkout or the SDK when GEN should run the browser checkout UI, continuation forms, uploads, and sync-visit scheduling. Use server-to-server V2 endpoints when your app owns that patient experience.

## Patients

### POST /v2/client/patients

**Create patient record**

- Full URL: `https://api.gen-health.app/v2/client/patients`

Create a patient record, or update and reuse an existing patient on the same client when the email already exists.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patient.email` _(required)_: Patient email
- `patient.firstName` _(required)_: Patient first name
- `patient.lastName` _(required)_: Patient last name
- `patient.phone` _(required)_: Patient phone number
- `patient.partnerPatientId`: External patient reference
- `patient.dateOfBirth` _(required)_: Date of birth (YYYY-MM-DD)
- `patient.sexAtBirth`: Sex at birth
- `patient.genderIdentity`: Gender identity
- `patient.address` _(required)_: Full address object. Required keys: street1, city, state, zip. Legacy aliases like street/addressLine1 are normalized.
- `patient.treatmentProgram`: Treatment program name
- `patient.medicationDuration`: Medication duration
- `patient.allergies`: Array of known allergies
- `patient.currentMedications`: Array of current medications
- `patient.weightJourney`: Profile summary object, not dated history. Send current height as total inches.
- `patient.customFields`: Key-value object of custom metadata (merged on update)
- `send_email`: Explicit false to suppress welcome email (default true)

**Key Details**

- magicLink is included for new patients and re-issued for returning patients on order creation; it expires after one hour.

**Common Errors And Remediation**

- Patient profile incomplete. Remediation: provide patient.email, firstName, lastName, phone, dateOfBirth, and address.street1/city/state/zip.
- Existing patient belongs to another client. Remediation: use a patient tied to your client.
- If you need an order, use the Create consult order or Create lab order API endpoint instead.

### GET /v2/client/patients

**List client patients**

- Full URL: `https://api.gen-health.app/v2/client/patients`

Without email: list all patients for this client (Users) with optional pagination. With ?email= or ?patient_email=: return a single patient in the same shape as GET /clientPatients/:patientId (trimmed, case-insensitive email). Do not combine email with limit/startAfter.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `email`: When set to a non-empty value, returns one patient by login email for this client (same response shape as GET /clientPatients/:patientId).
- `patient_email`: Alias for email.
- `limit`: Optional page size when not using email. When supplied, the response includes pagination metadata.
- `startAfter`: Optional cursor from the previous page pagination.nextCursor value.

**Key Details**

- Email lookup example: GET same function URL with `?email=jane@example.com` — response uses `data.patient` (not `data.patients`).

**Common Errors And Remediation**

- Method not allowed. Remediation: use the client patients read endpoint with GET.
- API key required or invalid. Remediation: provide valid X-API-Key.
- Patient not found for this client. Remediation: use an email for a patient on this client, or GET /clientPatients/:patientId.

### GET /v2/client/patients/:patientId

**Get patient detail**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId`

Fetch one patient profile by patientId or partnerPatientId. Equivalent to GET /clientPatients?email=... when you only have the email.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId` _(required)_: System patientId or partnerPatientId

**Common Errors And Remediation**

- Patient not found for client. Remediation: use patientId or partnerPatientId values returned by the client patients endpoints.

### PATCH /v2/client/patients/:patientId

**Update patient record**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId`

Update an existing patient profile by patientId or partnerPatientId. Email cannot be changed here. weightJourney is merged into the existing profile and is not a dated measurement history.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId` _(required)_: System patientId or partnerPatientId
- `firstName`: Patient first name
- `lastName`: Patient last name
- `phone`: Phone number. Stored in normalized form when possible.
- `dateOfBirth`: Date of birth (e.g. YYYY-MM-DD)
- `sexAtBirth`: Sex at birth
- `genderIdentity`: Gender identity
- `address`: Address object. If provided, it is normalized and must include street1, city, state, and zip after merging with any existing address.
- `partnerPatientId`: External patient reference
- `treatmentProgram`: Treatment program name
- `medicationDuration`: Medication duration
- `allergies`: Array of known allergies
- `currentMedications`: Array of current medications
- `weightJourney`: Profile summary object merged into existing data. Send current height as total inches, for example 5'8" as 68.
- `customFields`: Key-value object merged into existing customFields

**Key Details**

- weightJourney is the current patient profile summary. Use POST /v2/client/patients/:patientId/health-logs for historical body measurements.

**Common Errors And Remediation**

- patientId is required. Remediation: include patientId in the endpoint URL.
- email cannot be changed via this endpoint. Remediation: keep the existing patient email.
- Patient address incomplete. Remediation: send a full address with street1, city, state, and zip.
- No valid fields to update. Remediation: send at least one supported mutable patient field.
- weightJourney must be an object. Remediation: send an object such as {"height":68}.

### DELETE /v2/client/patients/:patientId

**Archive patient**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId`

Archive a patient profile by patientId or partnerPatientId. Sets status to archived; does not hard-delete the record. Idempotent when the patient is already archived.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId` _(required)_: System patientId or partnerPatientId

**Common Errors And Remediation**

- Patient not found for client. Remediation: use patientId or partnerPatientId values returned by the client patients endpoints.

### POST /v2/client/patients/:patientId/health-logs

**Write patient health logs**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId/health-logs`

Write dated patient health data by patientId or partnerPatientId. Accepts one log object or logs[] for bulk imports.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId` _(required)_: System patientId or partnerPatientId
- `category` _(required)_: activity, nutrition, sleep, body, mind, or symptom
- `date`: YYYY-MM-DD. Required when loggedAt is omitted.
- `loggedAt`: ISO timestamp. Required when date is omitted.
- `externalId`: Stable source record id for idempotent imports
- `logs`: Array of up to 100 health log objects
- `weight`: Body category weight. Aliases: loggedWeight, currentWeight, value.
- `height`: Body category historical height in total inches. Does not update current profile height.
- `steps`: Activity category step count
- `hoursSlept`: Sleep category hours slept
- `symptom`: Symptom category symptom name

**Key Details**

- Body logs support historical height, weight, body composition, blood pressure, glucose, oxygen, heart rate, HRV, respiratory rate, and VO2 max.
- Historical height stays on the health log. Use PATCH /v2/client/patients/:patientId with weightJourney.height for current profile height.
- When body logs include weight, the patient profile currentWeight is refreshed from the latest body log by loggedAt.
- Bulk import shape: {"logs":[{"category":"activity","date":"2026-01-15","steps":8400,"externalId":"activity-2026-01-15"}]}.

**Common Errors And Remediation**

- category is required. Remediation: use one of activity, nutrition, sleep, body, mind, symptom.
- date or loggedAt is required. Remediation: send date as YYYY-MM-DD or loggedAt as an ISO timestamp.
- Patient not found for this client. Remediation: use patientId or partnerPatientId values returned by the client patients endpoints.

### GET /v2/client/patients/:patientId/health-logs

**List patient health logs**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId/health-logs`

List dated patient health logs by patientId or partnerPatientId.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId` _(required)_: System patientId or partnerPatientId
- `category`: activity, nutrition, sleep, body, mind, or symptom
- `limit`: Result limit, max 200
- `startDate`: Earliest loggedAt/date to include
- `endDate`: Latest loggedAt/date to include
- `startAfter`: ISO cursor from pagination.nextCursor

**Common Errors And Remediation**

- Patient not found for this client. Remediation: use patientId or partnerPatientId values returned by the client patients endpoints.

### POST /v2/client/patients/:patientId/onboarding-id

**Upload patient onboarding photo**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId/onboarding-id`

Upload government ID front, ID back, or selfie for a patient. Uses the same Storage path, Documents row, and Users.onboardingUploads updates as portal onboarding. Authenticate with X-API-Key; patient must belong to this client. Supports multipart/form-data with a file part, or application/json with an imageUrl. Files must be JPEG/JPG, PNG, HEIC/HEIF, or WebP, up to 12 MB. There is no resolution limit.

**Headers**

- `X-API-Key`: `<your-api-key>`
- `Content-Type`: `multipart/form-data OR application/json`

**Parameters**

- `patientId`: System Firebase patient id or partnerPatientId string. Required unless partnerPatientId is sent.
- `partnerPatientId`: External patient id for this client. Required unless patientId is sent.
- `slotKey` _(required)_: idFront, idBack, or selfie. Aliases: patient_id_front / patient_id_back / patient_selfie, front / back.
- `file`: Binary image (multipart mode); field name file. JPEG/JPG, PNG, HEIC/HEIF, or WebP. Max 12 MB. MIME can be inferred from file bytes or filename when the upload sends application/octet-stream.
- `imageUrl`: Publicly accessible image URL (JSON mode). The server fetches the image bytes. URL response must be a JPEG/JPG, PNG, HEIC/HEIF, or WebP image up to 12 MB.

**Common Errors And Remediation**

- 415 — Unsupported Content-Type (use multipart/form-data or application/json).
- patientId is required.
- Patient not found for client.
- slotKey is required.
- file or imageUrl is required.
- 413 — Image is too large. Maximum upload size is 12 MB.
- 415 — Unsupported image type. Use a JPEG/JPG, PNG, HEIC/HEIF, or WebP image up to 12 MB. There is no resolution limit.
- Unable to fetch image from the provided URL.

### POST /v2/client/patients/:patientId/continuation-sessions

**Create continuation session**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId/continuation-sessions`

Mint a short-lived GEN patient session after server-side checkout or order creation. Use this instead of submitting clinical answers directly from your backend.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId`: System patientId or partnerPatientId
- `partnerPatientId`: External patient reference
- `orderId`: Associated order when continuation is tied to a purchase
- `clientProductId`: Associated clientProductId when no orderId is available yet
- `allowedOrigin`: Browser origin that will mount the continuation UI

## Products

### GET /v2/client/categories

**List categories**

- Full URL: `https://api.gen-health.app/v2/client/categories`

List active product categories available for this client. Inactive (soft-deleted) categories are excluded; each returned category includes its status (always "active" on this endpoint).

**Headers**

- `X-API-Key`: `<your-api-key>`

**Common Errors And Remediation**

- Method not allowed. Remediation: use the List categories API endpoint with GET.
- API key required or invalid. Remediation: provide a valid X-API-Key.

### GET /v2/client/products

**List consult products**

- Full URL: `https://api.gen-health.app/v2/client/products`

List storefront-available consult products for this client. Optionally filter by category using a categoryId (client-assigned or provider-network category id). Each product returns categories (resolved client-assigned, includes legacy categoryId fallback) and displayCategoryIds (array from the client product row); both exclude inactive (soft-deleted) category ids. Also returns PNcategories (provider-network catalog) and description (client-configured display copy when set; otherwise the provider-network catalog description).

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `category`: Optional categoryId; matches client-assigned categories on the client product row or provider-network categories on the catalog product

**Common Errors And Remediation**

- Method not allowed. Remediation: use the List consult products API endpoint with GET.
- API key required or invalid. Remediation: provide a valid X-API-Key.

### GET /v2/client/products/:clientProductId

**Get product detail**

- Full URL: `https://api.gen-health.app/v2/client/products/:clientProductId`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `clientProductId` _(required)_: Client product id returned by List products

### POST /v2/client/products

**Create client product or package**

- Full URL: `https://api.gen-health.app/v2/client/products`

Create a client-owned product or package. Packages combine active, patient-visible client product rows by clientProductId. Provider-network source catalog fields and image fields are not accepted.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `name` _(required)_: Internal product/package name
- `displayName`: Patient-facing name
- `customerPrice` _(required)_: Non-negative price in USD
- `itemType`: Use package for packages; omitted creates a product
- `includedProducts[].clientProductId`: Required for packages; at least 2 active, non-package client product ids
- `status`: active or inactive
- `showPatient`: Boolean patient visibility
- `displayCategoryIds`: Client category ids
- `description`: Internal description
- `displayDescription`: Patient-facing description

**Key Details**

- Images are excluded from V2 product CRUD. Use the existing app upload path for image management.

### PATCH /v2/client/products/:clientProductId

**Update client product or package**

- Full URL: `https://api.gen-health.app/v2/client/products/:clientProductId`

Update editable client product fields. Provider-network-owned products are updated only through the client overlay row and reject source catalog ownership fields.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `clientProductId` _(required)_: Client product document id
- `displayName`: Patient-facing name
- `displayDescription`: Patient-facing description
- `customerPrice`: Non-negative price in USD
- `status`: active or inactive; also updates showPatient to match
- `showPatient`: Boolean patient visibility
- `includedProducts`: Package-only replacement array
- `clientPrescribingNote`: Client overlay note

**Common Errors And Remediation**

- Image fields are not editable through the Client API.
- Catalog ownership fields are not editable.
- Provider-network rows only accept overlay fields available in the client Products page.

### DELETE /v2/client/products/:clientProductId

**Deactivate client product or package**

- Full URL: `https://api.gen-health.app/v2/client/products/:clientProductId`

Soft-delete a product or package by setting status inactive and showPatient false. This does not delete provider-network source catalog rows.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `clientProductId` _(required)_: Client product document id

### GET /v2/client/products/:clientProductId/forms

**List product forms**

- Full URL: `https://api.gen-health.app/v2/client/products/:clientProductId/forms`

Preview required intake and consent forms for a catalog product before order creation. Forms may be provider-network scoped or client scoped.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `clientProductId` _(required)_: Client product id returned by List products
- `patientId`: Optional system patientId or partnerPatientId for completion status

### GET /v2/client/products/:clientProductId/forms/:formKey

**Get product form detail**

- Full URL: `https://api.gen-health.app/v2/client/products/:clientProductId/forms/:formKey`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `clientProductId` _(required)_: Client product id returned by List products
- `formKey` _(required)_: Opaque form key returned by List product forms
- `patientId`: Optional system patientId or partnerPatientId

### GET /v2/client/products/forms

**List forms for multiple products**

- Full URL: `https://api.gen-health.app/v2/client/products/forms`

Preview deduplicated required forms across multiple catalog products.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `clientProductIds` _(required)_: Comma-separated clientProductId values
- `patientId`: Optional system patientId or partnerPatientId

## Orders

### POST /v2/client/orders

**Create product order**

- Full URL: `https://api.gen-health.app/v2/client/orders`

Create a product order and create or reference the patient in one request. Set order.type to product or omit it.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patient_id`: Existing system patientId or partnerPatientId for repeat requests
- `patientId`: Alias for patient_id
- `patient.email` _(required)_: Patient email. Required when creating a new patient.
- `patient.firstName` _(required)_: Patient first name. Required when creating a new patient.
- `patient.lastName` _(required)_: Patient last name. Required when creating a new patient.
- `patient.phone` _(required)_: Patient phone number. Required when creating a new patient.
- `patient.partnerPatientId`: External patient reference stored when the patient is first created. Use top-level patient_id/patientId on repeat requests.
- `patient.dateOfBirth` _(required)_: Date of birth (YYYY-MM-DD). Required when creating a new patient.
- `patient.sexAtBirth`: Sex at birth
- `patient.genderIdentity`: Gender identity
- `patient.address` _(required)_: Full address object required when creating a new patient. Required keys: street1, city, state, zip. Legacy aliases like street/addressLine1 are normalized.
- `patient.treatmentProgram`: Treatment program name
- `patient.medicationDuration`: Medication duration
- `patient.allergies`: Array of known allergies
- `patient.currentMedications`: Array of current medications
- `patient.weightJourney`: Profile summary object, not dated history. Send current height as total inches.
- `patient.customFields`: Key-value object of custom metadata (merged on update)
- `order.customFields`: Key-value object stored on each created order for downstream reconciliation and reporting
- `order.couponCode`: Promocode the partner applied to this order (case-insensitive). When the code exists in this client's CouponCodes, Gen-Health validates active status, validity, and remaining maxUsage before order creation. If the code applies to at least one ordered product, a snapshot — including affiliateId/utmSlug — is persisted, usageCount is incremented once per new order line, and the data is surfaced in the order.* webhook attribution block. If it applies to none, the order is still created without a coupon snapshot. Returns HTTP 400 when the code is unknown or inactive/expired/exhausted. order.amount remains authoritative; pricing is not re-derived. Aliased as order.coupon_code.
- `order.tracking`: Affiliate / UTM attribution captured at checkout. Object with optional source, utmSource, utmMedium, utmCampaign (snake_case aliases utm_source/utm_medium/utm_campaign accepted). Each value is trimmed to 256 chars; empty values are dropped. Persisted on the order and emitted in attribution.tracking on order.* webhooks.
- `order.payment_status`: Optional: paid | unpaid (default: unpaid for requestConsult). Sending "paid" means your system already collected payment; GEN trusts that status and does not verify the external transaction.
- `order.transactionId`: Optional external payment reference (transaction_id alias supported). Stored for audit and used as the idempotency key when present; no processor verification is performed.
- `order.sendReceipt`: Boolean receipt preference (send_receipt alias supported). true queues a branded receipt after payment, false suppresses it, omitted follows the client Patient Experience receipt setting.
- `order.clientProductId`: Preferred single-item product reference
- `order.productId`: Legacy single-item global product reference
- `order.productIds[].clientProductId`: Preferred multi-item product reference
- `order.productIds[].productId`: Legacy multi-item global product reference
- `order.productIds[].amount`: Required for multi-item requests
- `send_email`: Explicit false to suppress welcome email (default true)

**Key Details**

- New patient creation requires firstName, lastName, email, phone, dateOfBirth, and address.street1/city/state/zip.
- For returning patients, send top-level patient_id or patientId using the previously returned patientId or your stored partnerPatientId.
- If you send only patient.email for a patient that already exists, the API returns HTTP 409 and tells you to retry with patient_id.
- magicLink is included for new patients and re-issued for returning patients on order creation; it expires after one hour.
- Trusted payment flow: when you send order.payment_status="paid", GEN stores the order as paid without processor verification. If the product is provider-backed and async/sync review is required, the response includes visitId and chartReviewId.
- Idempotency: re-submitting the same order.transactionId for the same (clientId, productId) returns the original order with duplicateOrder=true instead of creating a second one. Without transactionId, the legacy patient/product dedupe applies.
- order.transactionId is optional. Store your own payment reference there when useful for audit or retry safety.
- order.sendReceipt=true sends a branded receipt after the order is paid. order.sendReceipt=false suppresses receipts for that order. Omit it to use the Patient Experience receipt setting, which defaults off.
- When order.payment_status is omitted or "unpaid", the order stays in pending_payment and no Visit is created until payment is completed by another channel.
- When subscribed, order.created fires immediately. Paid provider-backed consults can also emit async_visit.* webhooks with both legacy asyncVisitId and canonical visitId.
- Attribution: order.tracking and order.couponCode are persisted on the order at creation, even when payment_status is omitted. Both fields show up on every order.* and lab.* webhook attribution payload (attribution.tracking.utm_source, attribution.promo.code, attribution.promo.utm_slug). Validate the code with GET /v2/client/promocodes/validations before submitting if you want to confirm it would apply.
- Pricing trust: order.amount is treated as the partner-confirmed total and is not re-derived from the coupon. Snapshotted coupons are echoed for attribution/reconciliation only — Gen-Health does not adjust the charged amount based on order.couponCode.
- Coupon resolution is loose: any code that exists in this client's CouponCodes is snapshotted, regardless of validity window or usage caps. Codes that do not exist are silently dropped (no error, no snapshot). Use GET /v2/client/promocodes/validations if you need a hard validity check before submitting.

**Common Errors And Remediation**

- Patient profile incomplete. Remediation: provide firstName, lastName, email, phone, dateOfBirth, and address.street1/city/state/zip when creating a new patient.
- Client product is unavailable. Remediation: use an available clientProductId from the List consult products API endpoint.
- Lab product used in a consult request. Remediation: use a non-lab clientProductId from the List consult products API endpoint.
- A patient with this email already exists. Remediation: retry with top-level patient_id or patientId instead of patient.email.
- order.payment_status rejected (API Orders disabled). Remediation: omit it or enable API Orders.

### GET /v2/client/orders

**List client orders**

- Full URL: `https://api.gen-health.app/v2/client/orders`

List all orders for this client. Supports filtering by patient, status, payment status, or order type, plus cursor pagination.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId`: Filter by system patientId or partnerPatientId
- `partnerPatientId`: Alias for patientId
- `status`: Filter by order status (e.g. pending_payment, pending_review, completed)
- `paymentStatus`: Filter by payment status (paid, unpaid)
- `orderType`: Filter by type: product, lab
- `limit`: Page size (1-500). When supplied, the response includes pagination metadata.
- `startAfter`: Cursor from the previous page pagination.nextCursor value

**Common Errors And Remediation**

- Patient not found for client. Remediation: use a patientId or partnerPatientId from List client patients.
- API key required or invalid. Remediation: provide valid X-API-Key.

### GET /v2/client/orders/:orderId

**Get order detail**

- Full URL: `https://api.gen-health.app/v2/client/orders/:orderId`

Fetch one order by orderId. Returns 404 if the order does not belong to this client.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `orderId` _(required)_: Order ID

**Common Errors And Remediation**

- Order not found for client. Remediation: use an orderId returned by List client orders, Create consult order, or Create lab order.

### PATCH /v2/client/orders/:orderId

**Cancel order**

- Full URL: `https://api.gen-health.app/v2/client/orders/:orderId`

Cancel a client-owned order. Use DELETE for the resource-first form or PATCH with status = cancelled for compatibility.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `orderId` _(required)_: Order ID to update
- `status`: "cancelled" to cancel the order.
- `payment_status`: "paid" to mark an unpaid order as paid. Aliased as paymentStatus. Requires apiOrders feature enabled.
- `transaction_id`: External payment reference for audit. Aliased as transactionId. Only used with payment_status: "paid". Must be unique per client/product; replays on the same order return duplicateOrder: true.

**Key Details**

- Two-phase paid flow: create the order with payment_status omitted (defaults to "unpaid"), charge the patient externally, then PATCH with payment_status: "paid". Status becomes pending_forms, pending_labs, or pending_review. The clinical encounter is created when forms/labs gates are satisfied.
- Cancel: send status: "cancelled". Orders already in a terminal state (cancelled, completed, delivered, shipped, sent_to_pharmacy, sent_to_lab, results_received, denied, refunded) cannot be cancelled and will return 409.
- The order document is updated in place and never hard-deleted.

**Common Errors And Remediation**

- 400 Invalid status. Remediation: use status: "cancelled" or payment_status: "paid".
- 400 orderId is required. Remediation: include orderId in the URL.
- 400 status is required. Remediation: include a status or payment_status field in the request body.
- 400 Payment status updates are only supported for product orders.
- 403 Payment status updates are not enabled for this account. Remediation: contact support to enable payment status updates.
- 404 Order '<id>' was not found for this client. Remediation: use an orderId returned by List client orders.
- 405 Method not allowed. Remediation: use PATCH /updateOrder/:orderId.
- 409 Order cannot be cancelled in its current state. Remediation: check the current orderStatus before cancelling.
- 409 Order cannot be marked as paid in its current state. Only orders with status pending_payment can be marked as paid.
- 409 transaction_id is already associated with another order.
- 500 Unable to update order. Remediation: retry the request or contact support.

### DELETE /v2/client/orders/:orderId

**Cancel order with DELETE**

- Full URL: `https://api.gen-health.app/v2/client/orders/:orderId`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `orderId` _(required)_: Order ID to cancel

### POST /v2/client/patients/:patientId/consults

**Create product order for patient**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId/consults`

Compatibility product order endpoint for an existing patient. The resource-first /v2/client/orders endpoint is preferred for new integrations.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId` _(required)_: System patientId or partnerPatientId
- `order.clientProductId` _(required)_: Product clientProductId returned by List products
- `order.payment_status`: paid or unpaid

## Order Forms

### GET /v2/client/orders/:orderId/forms

**List order forms**

- Full URL: `https://api.gen-health.app/v2/client/orders/:orderId/forms`

Return the required intake and consent form manifest for an order.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `orderId` _(required)_: Order returned by create consult order
- `patientId`: Optional system patientId or partnerPatientId; must match the order patient

**Key Details**

- `orderId` is required so form completion can update the order and downstream clinical records.
- Forms may be provider-network scoped or client scoped. Use `formKey` as the opaque identifier for follow-up calls.

### GET /v2/client/orders/:orderId/forms/:formKey

**Get order form detail**

- Full URL: `https://api.gen-health.app/v2/client/orders/:orderId/forms/:formKey`

Return one required form definition for an order, including sections, questions, answer types, response options, and renderable validation metadata.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `formKey` _(required)_: Opaque form key returned by list order forms
- `orderId` _(required)_: Order returned by create consult order

### POST /v2/client/orders/:orderId/forms/submissions

**Submit order forms**

- Full URL: `https://api.gen-health.app/v2/client/orders/:orderId/forms/submissions`

Submit one or more order-bound form responses. The API writes deterministic submissions per orderId and formKey, links them to the order, and updates form completion status.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `orderId` _(required)_: Order returned by create consult order
- `patientId` _(required)_: System patientId or partnerPatientId; must match the order patient
- `submissions[].formKey` _(required)_: Opaque form key returned by list order forms
- `submissions[].responses` _(required)_: Section-keyed object: { [sectionId]: { [questionId]: value } }

**Key Details**

- Retrying the same `orderId` + `formKey` reuses the same submissionId.
- When all required forms are complete, a paid provider-backed order advances out of `pending_forms` and links Visit/ChartReview records when required.

### GET /v2/client/forms

**List order forms by query**

- Full URL: `https://api.gen-health.app/v2/client/forms`

Compatibility form manifest endpoint for an order. The nested /orders/:orderId/forms path returns the same shape.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `orderId` _(required)_: Order returned by Create product order or Create lab order
- `patientId`: Optional system patientId or partnerPatientId; must match the order patient

### GET /v2/client/forms/:formKey

**Get order form detail by query**

- Full URL: `https://api.gen-health.app/v2/client/forms/:formKey`

Compatibility form detail endpoint for an order. The nested /orders/:orderId/forms/:formKey path returns the same shape.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `formKey` _(required)_: Opaque form key returned by List order forms
- `orderId` _(required)_: Order returned by Create product order or Create lab order

### POST /v2/client/forms/submissions

**Submit order forms by body orderId**

- Full URL: `https://api.gen-health.app/v2/client/forms/submissions`

Compatibility form submission endpoint. Send orderId in the body; the nested /orders/:orderId/forms/submissions path accepts the same submissions without body orderId.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `orderId` _(required)_: Order returned by Create product order or Create lab order
- `patientId` _(required)_: System patientId or partnerPatientId; must match the order patient
- `submissions[].formKey` _(required)_: Opaque form key returned by List order forms
- `submissions[].responses` _(required)_: Section-keyed object: { [sectionId]: { [questionId]: value } }

## Labs

### GET /v2/client/labs

**List lab products**

- Full URL: `https://api.gen-health.app/v2/client/labs`

List storefront-available lab products for this client.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `category`: Optional category filter

**Common Errors And Remediation**

- Method not allowed. Remediation: use the List lab products API endpoint with GET.
- API key required or invalid. Remediation: provide a valid X-API-Key.

### POST /v2/client/patients/:patientId/labs/submissions

**Upload lab results**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId/labs/submissions`

Upload lab results as JSON biomarkers or a PDF file for a client-owned patient. Supports JSON body (results array) or multipart/form-data (PDF upload).

**Headers**

- `Content-Type`: `application/json or multipart/form-data`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId`: System patientId or partnerPatientId (can also be provided in body)
- `labName`: Lab panel name (e.g. "CMP", "CBC") — defaults to "Lab Results"
- `resultDate`: Result date string (YYYY-MM-DD) — defaults to today
- `results[]`: Biomarker result array (JSON upload path)
- `notes`: Free-text notes stored with the lab document
- `fileBase64`: Base64-encoded PDF content (PDF upload path)
- `fileName`: Original filename for the PDF (default: lab_result.pdf)
- `mimeType`: Must be application/pdf when using fileBase64

**Key Details**

- Use JSON when sending structured biomarker results. Use multipart/form-data when uploading a PDF file.
- For multipart uploads, send patientId in the path or form fields plus a single PDF file part. Non-PDF files are rejected.

**Common Errors And Remediation**

- Patient not found for client. Remediation: use a patientId or partnerPatientId returned by the client patients endpoints.
- Only PDF uploads are supported for file uploads. Remediation: send application/pdf in multipart or set mimeType to application/pdf for fileBase64.

### GET /v2/client/labs/:clientProductId

**Get lab detail**

- Full URL: `https://api.gen-health.app/v2/client/labs/:clientProductId`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `clientProductId` _(required)_: Lab clientProductId returned by List labs

### POST /v2/client/labs/requests

**Create lab request**

- Full URL: `https://api.gen-health.app/v2/client/labs/requests`

Compatibility lab order endpoint for callers already using the lab-specific route. The resource-first /v2/client/orders endpoint is preferred for new integrations.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patient_id`: System patientId or partnerPatientId for an existing patient
- `patient`: Patient payload when creating the patient inline
- `order.clientProductId` _(required)_: Lab clientProductId returned by List labs
- `order.payment_status`: paid or unpaid

## Visits

### POST /v2/client/patients/:patientId/visit-requests

**Create visit request**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId/visit-requests`

Create a visit for a new patient, or for an existing patient referenced by patient_id/patientId.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patient_id`: Existing system patientId or partnerPatientId for repeat requests
- `patientId`: Alias for patient_id
- `patient.email` _(required)_: Patient email. Required when creating a new patient.
- `patient.firstName` _(required)_: Patient first name. Required when creating a new patient.
- `patient.lastName` _(required)_: Patient last name. Required when creating a new patient.
- `patient.phone` _(required)_: Patient phone number. Required when creating a new patient.
- `patient.partnerPatientId`: External patient reference stored when the patient is first created. Use top-level patient_id/patientId on repeat requests.
- `patient.dateOfBirth` _(required)_: Date of birth (YYYY-MM-DD). Required when creating a new patient.
- `patient.sexAtBirth`: Sex at birth
- `patient.genderIdentity`: Gender identity
- `patient.address` _(required)_: Full address object required when creating a new patient. Required keys: street1, city, state, zip. Legacy aliases like street/addressLine1 are normalized.
- `patient.treatmentProgram`: Treatment program name
- `patient.medicationDuration`: Medication duration
- `patient.allergies`: Array of known allergies
- `patient.currentMedications`: Array of current medications
- `patient.weightJourney`: Profile summary object, not dated history. Send current height as total inches.
- `patient.customFields`: Key-value object of custom metadata (merged on update)
- `visit.date` _(required)_: Visit date in YYYY-MM-DD format. Alias: visit.requestedDate.
- `visit.time` _(required)_: Visit time in HH:mm (24h). Alias: visit.requestedTime.
- `visit.requestedDate`: Alias for visit.date
- `visit.requestedTime`: Alias for visit.time
- `visit.visitType`: Visit type label — defaults to "Consultation"
- `visit.visitTypeKey`: Machine-friendly visit type key (auto-derived from visitType if omitted)
- `visit.providerId`: Assign a specific provider by user ID
- `visit.preferredMethod`: "video" (default) or "phone"
- `visit.duration`: Duration in minutes (default 30)
- `visit.status`: "Confirmed" to pre-confirm; otherwise defaults to "Pending Review"
- `visit.scheduledAtMillis`: UTC epoch millis — required when visit.status is "Confirmed"
- `visit.relatedOrderId`: Link visit to an existing order
- `visit.orderId`: Alias for visit.relatedOrderId
- `visit.notes`: Free-text notes
- `visit.providerNetworkId`: Override provider network (defaults to client primary)
- `visit.patientTimezone`: IANA timezone for patient email display (e.g. "America/Chicago")
- `send_email`: Explicit false to suppress welcome email (default true)

**Key Details**

- New patient creation requires firstName, lastName, email, phone, dateOfBirth, and address.street1/city/state/zip.
- For returning patients, send top-level patient_id or patientId using the previously returned patientId or your stored partnerPatientId.
- If you send only patient.email for a patient that already exists, the API returns HTTP 409 and tells you to retry with patient_id.
- magicLink is included for new patients and re-issued for returning patients on order creation; it expires after one hour.

**Common Errors And Remediation**

- Patient profile incomplete. Remediation: provide firstName, lastName, email, phone, dateOfBirth, and address.street1/city/state/zip when creating a new patient.
- visit.date and visit.time required. Remediation: include visit.date and visit.time.
- A patient with this email already exists. Remediation: retry with top-level patient_id or patientId instead of patient.email.
- Invalid visit data. Remediation: verify visit fields and retry.
- Provider slot unavailable (HTTP 409). Remediation: choose a different visit time and retry.

### GET /v2/client/visits

**List visit products**

- Full URL: `https://api.gen-health.app/v2/client/visits`

List storefront-available visit products for this client.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Common Errors And Remediation**

- Method not allowed. Remediation: use the List visit products API endpoint with GET.
- API key required or invalid. Remediation: provide valid X-API-Key.

### GET /v2/client/patients/:patientId/visit-availability

**Get sync visit availability**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId/visit-availability`

Resolve provider availability for a client-owned patient with the same scheduling rules used by the patient app.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId` _(required)_: System patientId or partnerPatientId
- `orderId`: Order used to resolve visit context
- `startDate`: YYYY-MM-DD range start
- `endDate`: YYYY-MM-DD range end
- `providerId`: Optional provider override
- `patientTimezone`: IANA timezone for display labels

### POST /v2/client/patients/:patientId/visits

**Book sync visit**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId/visits`

Create a confirmed sync visit for an existing patient and optionally link it to an order.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId` _(required)_: System patientId or partnerPatientId
- `visit.providerId` _(required)_: Assigned provider
- `visit.date` _(required)_: Visit date in YYYY-MM-DD format. Alias: visit.requestedDate.
- `visit.time` _(required)_: Visit time in HH:mm (24h). Alias: visit.requestedTime.
- `visit.requestedDate`: Alias for visit.date
- `visit.requestedTime`: Alias for visit.time
- `visit.scheduledAtMillis` _(required)_: Canonical UTC epoch millis for the confirmed visit start
- `visit.relatedOrderId`: Order to associate with the visit
- `visit.patientTimezone`: IANA timezone for patient-facing labels

**Key Details**

- Book sync visit creates a confirmed visit, so send both display date/time and canonical scheduledAtMillis.
- Use date/time from Get sync visit availability, then send the matching UTC scheduledAtMillis for the same slot.

**Common Errors And Remediation**

- visit.date and visit.time are required. Remediation: include visit.date (YYYY-MM-DD) and visit.time (HH:mm, 24-hour format).
- Invalid scheduledAtMillis. Remediation: provide visit.scheduledAtMillis as the canonical UTC start for confirmed visits.
- Provider slot unavailable (HTTP 409). Remediation: choose a different visit time and retry.

### PATCH /v2/client/visits/:visitId

**Update sync visit**

- Full URL: `https://api.gen-health.app/v2/client/visits/:visitId`

Reschedule or update a client-owned sync visit.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `visitId` _(required)_: Visit ID
- `scheduledAtMillis`: UTC epoch millis for a confirmed reschedule
- `providerId`: Optional provider reassignment
- `status`: Usually Confirmed when rescheduling

### DELETE /v2/client/visits/:visitId

**Cancel sync visit**

- Full URL: `https://api.gen-health.app/v2/client/visits/:visitId`

Cancel a scheduled visit and stop future reminder jobs.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `visitId` _(required)_: Visit ID
- `cancellationReason`: Stored on the visit record

### POST /v2/client/visits/:visitId/magic-links

**Create visit access link**

- Full URL: `https://api.gen-health.app/v2/client/visits/:visitId/magic-links`

Issue a patient-facing access URL for a scheduled visit. The client receives the URL and expiry, not raw meeting tokens.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `visitId` _(required)_: Visit ID

### GET /v2/client/post-visit-redirect

**Get post-visit redirect settings**

- Full URL: `https://api.gen-health.app/v2/client/post-visit-redirect`

Retrieve the post-visit redirect configuration for this client. When enabled, patients are automatically sent to the configured URL after completing a sync video visit.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Common Errors And Remediation**

- Client not found. Remediation: verify the API key belongs to an active client.

### PATCH /v2/client/post-visit-redirect

**Update post-visit redirect settings**

- Full URL: `https://api.gen-health.app/v2/client/post-visit-redirect`

Enable or disable post-visit redirect for sync video visits, and set the destination URL. When postVisitRedirectEnabled is true, a valid postVisitRedirectUrl is required. When false, the URL field is stored but has no effect.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `postVisitRedirectEnabled` _(required)_: Boolean. Set to true to redirect patients after a sync video visit, false to disable.
- `postVisitRedirectUrl`: Absolute URL (http:// or https://) patients are sent to after the visit. Required when postVisitRedirectEnabled is true.

**Common Errors And Remediation**

- postVisitRedirectEnabled is required. Remediation: send a boolean postVisitRedirectEnabled field in the request body.
- postVisitRedirectUrl is required when postVisitRedirectEnabled is true. Remediation: provide a valid URL starting with http:// or https://.
- postVisitRedirectUrl is not a valid URL. Remediation: provide a valid absolute URL starting with http:// or https://.

### GET /v2/client/patients/:patientId/visits

**List patient visits**

- Full URL: `https://api.gen-health.app/v2/client/patients/:patientId/visits`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId` _(required)_: System patientId or partnerPatientId

### GET /v2/client/visits/:visitId

**Get visit detail**

- Full URL: `https://api.gen-health.app/v2/client/visits/:visitId`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `visitId` _(required)_: Visit ID

## Messages

### GET /v2/client/conversations

**List conversations**

- Full URL: `https://api.gen-health.app/v2/client/conversations`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId`: Filter by patientId or partnerPatientId
- `status`: Filter by active, closed, or archived
- `updatedSince`: ISO timestamp or Unix epoch milliseconds for changed conversations
- `activitySince`: Alias for updatedSince
- `limit`: Page size, capped at 200

### POST /v2/client/conversations

**Create conversation**

- Full URL: `https://api.gen-health.app/v2/client/conversations`

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId` _(required)_: System patientId or partnerPatientId

### GET /v2/client/conversations/:conversationId

**Get or update conversation**

- Full URL: `https://api.gen-health.app/v2/client/conversations/:conversationId`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `conversationId` _(required)_: Conversation ID

**Key Details**

- PATCH the same path with status active, closed, or archived. DELETE archives the conversation.

### POST /v2/client/conversations/:conversationId/messages

**Send client-authored message**

- Full URL: `https://api.gen-health.app/v2/client/conversations/:conversationId/messages`

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `conversationId` _(required)_: Patient conversation ID
- `author`: client. Default value when omitted.
- `senderUserId`: Active Client Admin or Client Staff userId to include as the sender
- `senderName`: Display name override for the Client API sender when senderUserId is omitted
- `text`: Message text, capped at 5000 characters. Required unless attachments are sent.
- `attachments[]`: Up to 10 external attachment URLs with optional name, mimeType, and size

**Key Details**

- Provider, provider-network, practice, and internal sender types are rejected. PATCH/DELETE can only modify messages created by the Client API.

### POST /v2/client/conversations/:conversationId/messages

**Send patient-authored message**

- Full URL: `https://api.gen-health.app/v2/client/conversations/:conversationId/messages`

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `conversationId` _(required)_: Patient conversation ID
- `author` _(required)_: patient
- `patientId`: Optional guard; when present must match the conversation patient
- `text`: Message text, capped at 5000 characters. Required unless attachments are sent.
- `attachments[]`: Up to 10 external attachment URLs with optional name, mimeType, and size

**Key Details**

- Patient-authored messages use the conversation patient as senderId and are routed as inbound care-team messages. The API actor is preserved in metadata.

### PATCH /v2/client/conversations/:conversationId

**Update conversation status**

- Full URL: `https://api.gen-health.app/v2/client/conversations/:conversationId`

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `conversationId` _(required)_: Conversation ID
- `status` _(required)_: active, closed, or archived

### DELETE /v2/client/conversations/:conversationId

**Archive conversation**

- Full URL: `https://api.gen-health.app/v2/client/conversations/:conversationId`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `conversationId` _(required)_: Conversation ID

### POST /v2/client/conversations/:conversationId/escalations

**Escalate conversation to provider network**

- Full URL: `https://api.gen-health.app/v2/client/conversations/:conversationId/escalations`

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `conversationId` _(required)_: Conversation ID
- `reason`: Short escalation reason stored on the conversation

### GET /v2/client/conversations/:conversationId/messages

**List conversation messages**

- Full URL: `https://api.gen-health.app/v2/client/conversations/:conversationId/messages`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `conversationId` _(required)_: Conversation ID
- `limit`: Page size, capped at 200

### GET /v2/client/conversations/:conversationId/messages/:messageId

**Get conversation message**

- Full URL: `https://api.gen-health.app/v2/client/conversations/:conversationId/messages/:messageId`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `conversationId` _(required)_: Conversation ID
- `messageId` _(required)_: Message ID

### PATCH /v2/client/conversations/:conversationId/messages/:messageId

**Update conversation message**

- Full URL: `https://api.gen-health.app/v2/client/conversations/:conversationId/messages/:messageId`

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `conversationId` _(required)_: Conversation ID
- `messageId` _(required)_: Message ID
- `text` _(required)_: Updated external message text

### DELETE /v2/client/conversations/:conversationId/messages/:messageId

**Delete conversation message**

- Full URL: `https://api.gen-health.app/v2/client/conversations/:conversationId/messages/:messageId`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `conversationId` _(required)_: Conversation ID
- `messageId` _(required)_: Message ID

## Prescriptions

### GET /v2/client/prescriptions

**List prescriptions**

- Full URL: `https://api.gen-health.app/v2/client/prescriptions`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientId`: Filter by patientId or partnerPatientId
- `orderId`: Filter by orderId
- `status`: Filter by prescription status
- `limit`: Maximum returned prescriptions, capped at 500

**Key Details**

- Prescription status and clinical content are read-only through V2. Only notification rules support CRUD.

### GET /v2/client/prescriptions/:prescriptionId

**Get prescription detail**

- Full URL: `https://api.gen-health.app/v2/client/prescriptions/:prescriptionId`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `prescriptionId` _(required)_: Prescription ID

**Key Details**

- No V2 endpoint updates prescription status. Attempts to use PATCH/POST for status changes are unsupported.

### POST /v2/client/prescriptions/:prescriptionId/notification-rules

**Manage prescription notification rules**

- Full URL: `https://api.gen-health.app/v2/client/prescriptions/:prescriptionId/notification-rules`

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `prescriptionId` _(required)_: Prescription ID

**Key Details**

- GET the collection to list rules. PATCH or DELETE /notification-rules/:ruleId updates or removes one rule.

### GET /v2/client/prescriptions/:prescriptionId/notification-rules

**List prescription notification rules**

- Full URL: `https://api.gen-health.app/v2/client/prescriptions/:prescriptionId/notification-rules`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `prescriptionId` _(required)_: Prescription ID

### PATCH /v2/client/prescriptions/:prescriptionId/notification-rules/:ruleId

**Update prescription notification rule**

- Full URL: `https://api.gen-health.app/v2/client/prescriptions/:prescriptionId/notification-rules/:ruleId`

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `prescriptionId` _(required)_: Prescription ID
- `ruleId` _(required)_: Rule ID returned by List prescription notification rules

### DELETE /v2/client/prescriptions/:prescriptionId/notification-rules/:ruleId

**Delete prescription notification rule**

- Full URL: `https://api.gen-health.app/v2/client/prescriptions/:prescriptionId/notification-rules/:ruleId`

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `prescriptionId` _(required)_: Prescription ID
- `ruleId` _(required)_: Rule ID returned by List prescription notification rules

## Payments

### POST /v2/client/payments/affiliate/sessions

**Create affiliate payment session**

- Full URL: `https://api.gen-health.app/v2/client/payments/affiliate/sessions`

Open a short-lived payment session for an affiliate-model client. Use the returned token and processor config to collect payment client-side. For Stripe sessions, redirect to the returned checkout URL; for Authorize.net, tokenize card data client-side and call completeAffiliatePaymentSession.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `clientProductId` _(required)_: clientProductId from List consult products
- `idempotencyKey` _(required)_: Unique per logical checkout attempt. Retrying with the same payload returns the existing session; changing the payload is rejected.
- `patient.email` _(required)_: Patient email
- `patient.firstName`: Patient first name
- `patient.lastName`: Patient last name
- `patient.phone`: Patient phone number
- `patient.partnerPatientId`: External patient reference
- `partnerPatientId`: Alternate top-level external patient reference
- `partnerOrderId`: External order reference stored on the session
- `couponCode`: Coupon code applied to pricing (uppercased server-side)
- `successUrl`: Redirect after successful checkout (Stripe)
- `cancelUrl`: Redirect after cancelled checkout (Stripe)
- `send_email`: Explicit false to suppress welcome email after payment (default true)
- `send_receipt`: Boolean receipt preference. true queues a branded receipt after payment, false suppresses it, omitted follows the client Patient Experience receipt setting.

**Key Details**

- Requires client model "affiliate" with processor credentials configured on the provider network.
- Persist the returned `paymentSessionToken` — it authenticates subsequent calls to `completeAffiliatePaymentSession` and `getAffiliatePaymentSessionStatus`.
- Mode-specific response fields: Stripe returns `publicKey` + `stripeCheckoutSessionId`; Authorize.net returns `apiLoginId` + `clientKey`; Whop returns `whopCheckoutConfigId` + `whopCheckoutUrl`.

**Common Errors And Remediation**

- idempotencyKey already used with a different payload. Remediation: generate a new idempotencyKey for the new payload.
- Client is not affiliate-model. Remediation: use Create consult order or Create lab order for non-affiliate clients.
- Merchant processor credentials are incomplete (HTTP 422). Remediation: configure Stripe or Authorize.net keys on the provider network.

### POST /v2/client/payments/affiliate/session-completions

**Complete affiliate payment session**

- Full URL: `https://api.gen-health.app/v2/client/payments/affiliate/session-completions`

Finalize an Authorize.net or zero-dollar affiliate session after tokenizing card data client-side. Stripe sessions do not use this endpoint — poll getAffiliatePaymentSessionStatus after redirecting to Stripe Checkout.

**Headers**

- `Content-Type`: `application/json`
- `X-Payment-Session-Id`: `<paymentSessionId>`
- `X-Payment-Session-Token`: `<paymentSessionToken>`

**Parameters**

- `paymentSessionId` _(required)_: From createAffiliatePaymentSession. Accepts `sessionId` alias. Can also be sent via X-Payment-Session-Id header.
- `paymentSessionToken` _(required)_: From createAffiliatePaymentSession. Can also be sent via X-Payment-Session-Token header.
- `billingInfo` _(required)_: Object with firstName, lastName, street1, city, state, zip, email, phone.
- `shippingInfo`: Same shape as billingInfo. Required when sameAsBilling is false.
- `sameAsBilling`: Defaults to true — shippingInfo is copied from billingInfo when true.
- `opaqueData`: Authorize.net Accept.js opaque data object. `paymentData` is accepted as an alias.

**Key Details**

- This endpoint does not accept X-API-Key — it authenticates on paymentSessionId + paymentSessionToken.
- Stripe sessions finalize via redirect to Stripe Checkout; call getAffiliatePaymentSessionStatus to confirm payment after return.
- Zero-dollar (fully couponed) sessions accept the same call shape; opaqueData is ignored.

**Common Errors And Remediation**

- Session mode is not authorize (HTTP 422). Remediation: for Stripe sessions, redirect the shopper to the returned checkout URL instead.
- billingInfo incomplete. Remediation: provide firstName, lastName, street1, city, state, zip, email, phone.
- Invalid paymentSessionToken. Remediation: use the token returned by createAffiliatePaymentSession.

### GET /v2/client/payments/affiliate/session-status

**Get affiliate payment session status**

- Full URL: `https://api.gen-health.app/v2/client/payments/affiliate/session-status`

Poll the current status of an affiliate payment session. Stripe sessions self-finalize here on first paid poll.

**Headers**

- `X-Payment-Session-Id`: `<paymentSessionId>`
- `X-Payment-Session-Token`: `<paymentSessionToken>`

**Parameters**

- `paymentSessionId` _(required)_: From createAffiliatePaymentSession. Accepts `sessionId` alias. Can also be sent via X-Payment-Session-Id header or body for POST.
- `paymentSessionToken` _(required)_: From createAffiliatePaymentSession. Can also be sent via X-Payment-Session-Token header or body for POST.

**Key Details**

- Accepts GET or POST. Prefer GET with header credentials for polling.
- Does not accept X-API-Key — authenticates on paymentSessionId + paymentSessionToken.
- Status values: `pending_payment`, `awaiting_completion`, `paid`, `failed`, `expired`.

**Common Errors And Remediation**

- Invalid or expired paymentSessionToken. Remediation: the token is invalid or the session expired — start a new checkout with createAffiliatePaymentSession.

### POST /v2/client/payments/affiliate/session-status

**Get affiliate payment session status with JSON body**

- Full URL: `https://api.gen-health.app/v2/client/payments/affiliate/session-status`

JSON-body variant of the affiliate payment session status endpoint. Prefer GET with session headers for polling; use POST when headers are not available in your environment.

**Headers**

- `Content-Type`: `application/json`

**Parameters**

- `paymentSessionId` _(required)_: Returned by Create affiliate payment session. Alias: sessionId
- `paymentSessionToken` _(required)_: Returned by Create affiliate payment session

## Promocodes

### GET /v2/client/promocodes

**List promocodes**

- Full URL: `https://api.gen-health.app/v2/client/promocodes`

List affiliate-aware promocodes for this client. Supports filtering by status, assignmentType, affiliateId, utmSlug, and cursor pagination on updatedAt. Returns the storefront-mappable shape with discount, applicability scope, validity window, usage counter, and resolved utmSlug for locked codes.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `status`: Filter by status: "active" or "inactive"
- `assignmentType`: Filter by "locked" or "shared"
- `affiliateId`: Return codes assigned to this affiliateId
- `utmSlug`: Return codes whose affiliates list contains this utmSlug
- `limit`: Page size (1-200). When supplied, the response includes pagination metadata.
- `startAfter`: Cursor from the previous page pagination.nextCursor value (promocodeId)
- `sort`: Result ordering. "id" (default) orders by promocodeId so legacy codes without updatedAt are not silently excluded. Use "updatedAt" to sort by most recently updated (only includes codes with an updatedAt field).

**Key Details**

- utmSlug at the top level is derived: it is non-null only when assignmentType is "locked" and exactly one affiliate is assigned. For shared codes inspect the affiliates array.
- applicability.scope can be "all_products", "all_categories", "product_ids", or "category_ids". Legacy codes without applicability fall back to eligibleClientProductIds (treated as "product_ids").
- maxUsage and validity are null when unlimited.
- Default ordering is by promocodeId (sort=id) so legacy codes without an updatedAt field are still returned. Pass sort=updatedAt for time-ordered results, but expect codes missing updatedAt to be excluded.
- affiliateId and utmSlug are post-filtered on the fetched page. When combined with limit, a page may contain fewer matches than the limit; use pagination.nextCursor to keep paging until hasMore is false.

**Common Errors And Remediation**

- 400 Invalid status. Remediation: use one of ["active", "inactive"].
- 400 Invalid assignmentType. Remediation: use one of ["locked", "shared"].
- 400 Invalid sort. Remediation: use one of ["id", "updatedAt"].
- 401 API key required or invalid. Remediation: provide a valid X-API-Key.
- 405 Method not allowed. Remediation: use GET /v2/client/promocodes.

### GET /v2/client/promocodes/:code

**Get promocode by code**

- Full URL: `https://api.gen-health.app/v2/client/promocodes/:code`

Fetch a single promocode by its human-readable code (case-insensitive). Returns the same shape as List promocodes wrapped under data.promocode.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `code` _(required)_: Promocode (case-insensitive). Example: JASON20

**Common Errors And Remediation**

- 404 Promocode '<code>' was not found for this client. Remediation: use GET /v2/client/promocodes to list valid codes.

### PATCH /v2/client/promocodes/:code

**Update promocode (sync utmSlug or affiliate metadata)**

- Full URL: `https://api.gen-health.app/v2/client/promocodes/:code`

Sync affiliate-related metadata onto an existing Gen-Health promocode (the dashboard side remains the system of record for affiliates). Send any combination of name, assignmentType, affiliates, applicability, maxUsage, and validity. As a convenience for locked codes, send utmSlug (with optional affiliateId) and the request will be normalized to a single-affiliate assignment with assignmentType "locked".

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `code` _(required)_: Promocode (case-insensitive). Example: JASON20
- `utmSlug`: Convenience for locked codes. Sets a single-affiliate assignment using this UTM slug.
- `affiliateId`: Optional affiliateId paired with utmSlug for the locked-code shortcut.
- `name`: Human-readable promocode name.
- `assignmentType`: "locked" or "shared". Locked codes can have at most one affiliate.
- `affiliates`: Array of { affiliateId, utmSlug }. Replaces the current assignment list. Use for shared codes.
- `applicability`: Object: { scope: "all_products" | "all_categories" | "product_ids" | "category_ids", productIds?: string[], categoryIds?: string[] }.
- `maxUsage`: Non-negative integer or null for unlimited.
- `validity`: Object: { endsAt?: ISO timestamp }. Send null for unlimited. Only the expiration date is enforced; start dates are ignored.

**Key Details**

- This endpoint never creates a promocode. Codes are created and deleted via the Gen-Health admin UI or the internal product coupon backend route.
- Discount, status, eligibleClientProductIds, code itself, and usage counters are read-only from this endpoint.
- Sending { utmSlug: "" } or { affiliates: [] } clears the affiliate assignment.

**Common Errors And Remediation**

- 400 code is required. Remediation: include the code in the URL.
- 400 No supported promocode fields supplied. Remediation: send any combination of name, assignmentType, affiliates, utmSlug, affiliateId, applicability, maxUsage, validity.
- 400 assignmentType must be "locked" or "shared".
- 400 affiliates must be an array.
- 400 applicability.scope must be one of the allowed values.
- 400 Locked promocodes can only have one affiliate assignment.
- 404 Promocode '<code>' was not found for this client. Remediation: use GET /v2/client/promocodes to list valid codes.
- 405 Method not allowed. Remediation: use PATCH /v2/client/promocodes/:code.

### GET /v2/client/promocodes/validations

**Validate promocode for one or more products (read-only)**

- Full URL: `https://api.gen-health.app/v2/client/promocodes/validations`

Read-only price + applicability check used by external/iframe checkout pages. Supports either single-product input (`clientProductId` / `productId`) or multi-product input (`clientProductIds[]` / `productIds[]`). Single mode returns one validation payload; multi mode returns aggregate bundle flags plus per-item results. No order is created and usage counters are not consumed. Accepts either X-API-Key (server-to-server) or X-Storefront-Key (browser/iframe). The same logic is also exposed under POST /v2/client/promocodes/validations for callers that prefer a JSON body.

**Headers**

- `X-API-Key`: `<your-api-key>`

**Parameters**

- `code` _(required)_: Promocode (case-insensitive). Example: JASON20
- `clientProductId`: Legacy/deterministic clientProductId. Either clientProductId or productId is required.
- `productId`: Product id (used together with the authenticated client). Either clientProductId or productId is required.
- `clientProductIds`: CSV or repeated value list for multi-product validation (example: id1,id2). Use instead of clientProductId/productId.
- `productIds`: CSV or repeated value list for multi-product validation by productId. Use instead of clientProductId/productId.
- `providerNetworkId`: Optional. Disambiguates productId across provider networks.
- `quantity`: Positive integer (default 1). Used to compute lineSubtotal/lineDiscount/lineTotal.
- `currency`: Currency code. Only "usd" is currently supported (default).

**Key Details**

- Read-only. Never creates an order, never increments usageCount, never sends emails or webhooks.
- Returns HTTP 200 with `valid: false` and a `reasonCodes` array for code/product business-rule failures (expired, exhausted, wrong product, etc.). Only auth, transport, or unexpected errors return non-200.
- reasonCode values: code_required, product_required, conflicting_product_inputs, product_not_found, client_mismatch, code_not_found, code_inactive, code_outside_validity, code_exhausted, not_applicable_to_product, invalid_quantity, invalid_currency.
- utmSlug under promocode is non-null only when assignmentType is "locked" and exactly one affiliate is assigned. Use it to drive affiliate attribution from an external/iframe checkout.
- Browser usage: pass X-Storefront-Key (instead of X-API-Key). Origin allow-listing is enforced when the storefront key has allowedOrigins configured.
- POST variant: send the same fields in a JSON body to POST /v2/client/promocodes/validations. For multi mode, send clientProductIds/productIds arrays.
- Do not mix single and multi fields in one request; mixed payloads return `conflicting_product_inputs`.
- Multi mode returns aggregate fields (`valid`, `appliesToAny`, `allValid`) and per-item results in `items[]`.

**Common Errors And Remediation**

- 401 API key required or invalid. Remediation: provide a valid X-API-Key or X-Storefront-Key.
- 403 This origin is not allowed for the provided storefront key. Remediation: add the origin under the storefront key allowlist.
- 405 Method not allowed. Remediation: use GET or POST /v2/client/promocodes/validations.
- 500 Unable to validate promocode. Remediation: retry the request or contact support.

### POST /v2/client/promocodes/validations

**Validate promocode with JSON body**

- Full URL: `https://api.gen-health.app/v2/client/promocodes/validations`

JSON-body variant of the read-only promocode validation endpoint. Use it when validating a bundle with arrays.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `code` _(required)_: Promocode
- `clientProductIds`: Array of clientProductId values for bundle validation
- `clientProductId`: Single clientProductId value
- `quantity`: Positive integer; default 1

## Business

### PATCH /v2/client/business/branding

**Get or update business branding**

- Full URL: `https://api.gen-health.app/v2/client/business/branding`

Authenticated branding management for display name, website, support contact, brand URL slug, colors, header font, and layout theme options. GET the same path to retrieve current values.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `displayName`: Patient-facing business name
- `website`: Business website URL
- `supportEmail`: Support email
- `phoneNumber`: Support phone number
- `brandingSlug`: Lowercase letters, numbers, and dashes; empty string removes slug
- `accentColor`: Primary brand color
- `secondaryColor`: Secondary brand color
- `backgroundColor`: Brand background color
- `layoutOptions.checkoutTheme`: Checkout theme object
- `layoutOptions.loginTheme`: Login theme object
- `layoutOptions.emailTheme`: Email theme object
- `layoutOptions.formTheme`: Form theme object

### GET /v2/client/business/branding

**Get business branding**

- Full URL: `https://api.gen-health.app/v2/client/business/branding`

Retrieve authenticated branding settings, including operational layout options not returned by the public branding endpoint.

**Headers**

- `X-API-Key`: `<your-api-key>`

### PATCH /v2/client/business/payment-processor

**Get or update payment processor**

- Full URL: `https://api.gen-health.app/v2/client/business/payment-processor`

Authenticated payment processor configuration. GET returns processor value, custom instructions, and secret-safe credential field status. PATCH can update processor, custom instructions, and credential fields.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `paymentProcessor` _(required)_: demo, stripe, authorize, nmi, square, whop, or custom_instructions. Aliases: processor, type.
- `customPaymentInstructions`: HTML string or object for custom_instructions
- `credentials`: Processor credential keys. Values are stored but never returned.

**Key Details**

- Credential values are write-only in API responses. Use fieldStatus to confirm whether required fields are present.

### GET /v2/client/business/payment-processor

**Get payment processor**

- Full URL: `https://api.gen-health.app/v2/client/business/payment-processor`

Retrieve the active payment processor, custom instructions, and secret-safe credential field status.

**Headers**

- `X-API-Key`: `<your-api-key>`

### PATCH /v2/client/business/checkout-options

**Get or update checkout options**

- Full URL: `https://api.gen-health.app/v2/client/business/checkout-options`

Authenticated checkout option management for patient checkout sequence, receipt emails, prescription review queueing, post-visit redirect, and default shipping price. GET the same path to retrieve current values.

**Headers**

- `Content-Type`: `application/json`
- `X-API-Key`: `<your-api-key>`

**Parameters**

- `patientCheckout.sequence.products`: intake_before_payment or payment_before_intake
- `patientCheckout.sequence.labs`: intake_before_payment or payment_before_intake
- `patientReceipts.enabled`: Whether paid patient orders queue receipt emails by default
- `queuePrescriptionReview.enabled`: Whether queued prescriptions require client review before payment/add-on prompts
- `postVisitRedirectEnabled`: Enable sync-visit redirect
- `postVisitRedirectUrl`: Redirect URL starting with http:// or https://
- `defaultShippingPrice`: Non-negative default shipping price

### GET /v2/client/business/checkout-options

**Get checkout options**

- Full URL: `https://api.gen-health.app/v2/client/business/checkout-options`

Retrieve patient checkout sequence, receipt, prescription review, post-visit redirect, and shipping defaults.

**Headers**

- `X-API-Key`: `<your-api-key>`

### GET /v2/client/branding

**Get client branding**

- Full URL: `https://api.gen-health.app/v2/client/branding`

Public visual branding payload for a client-scoped docs or checkout page. Operational settings require authenticated Business endpoints.

**Parameters**

- `clientId` _(required)_: Client document id. Alias: client_id

## Important Defaults

- Each API endpoint in this guide is unique. Do not append another endpoint path to that host.
- `send_email` defaults to true. Set it explicitly to false to suppress welcome email delivery.
- `order.sendReceipt` defaults to the client Patient Experience receipt setting, which is off until enabled. Set true or false to override for one order.
- `order.payment_status` accepts only `paid` or `unpaid`. `requestConsult` defaults to `unpaid`; `requestLabs` defaults to `paid`.
- New patient creation requires first name, last name, email, phone, date of birth, and full address.
- Integration-backed lab orders also require the existing patient profile to have complete demographics and address before fulfillment.
- For `requestConsult`, when `order.payment_status` is `paid`, GEN trusts the caller payment status. `order.transactionId` (or `order.transaction_id`) is optional audit/dedupe data.
- Paid provider-backed consults create a canonical Visit and linked ChartReview before the response. Unpaid consults create no Visit.
- Use `clientProductId` as canonical reference. `productId` is accepted for legacy compatibility.
- For returning patients, `requestConsult` and `requestLabs` require top-level `patient_id` or `patientId`. They do not look up existing patients by email alone.
- For returning patients, visit booking also requires top-level `patient_id` or `patientId`.
