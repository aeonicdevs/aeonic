# Client HTML Reference Assessment

Source reviewed: `app-connect-v2 (1).html`

The HTML file is a broad interactive prototype, not a production-ready page. It combines a clinic/partner portal, a patient/member app shell, login/MFA flows, consent modal, search overlay, notification/export/profile menus, support threads, integrations, protocol resources, Academy content, billing, a clinical workspace overlay, and an AEVA care-package builder wizard.

## Vue/Vuetify Fit

- Standard Vuetify fit: navigation drawer, app bar, cards, tables, tabs, dialogs, steppers, forms, chips, lists, menus, toasts, responsive grids, and modal overlays.
- Best converted to Vue state: role/workspace switching, search overlay results, support thread selection, patient detail drilldowns, Academy filters, builder step validation, onboarding progress, notifications, and file upload state.
- Best kept custom but still straightforward: miniature charts, patient app overlay styling, dashboard progress bars, custom gradient brand treatments, and card hover polish.

## Higher-Risk Areas

- The reference uses large amounts of `innerHTML` string rendering. In Vue this should become components and reactive data to avoid XSS risk, brittle event delegation, and hard-to-test UI.
- The AEVA builder has step gating, signing, route selection, safety-block confirmation, and pricing activation. Vuetify can implement this, but it needs real domain rules and validation copy before it should be treated as more than a demo.
- File uploads and drag/drop protocol manuals are UI-only in the HTML. Production needs upload storage, accepted file validation, processing status, permissions, and error handling.
- HIPAA consent and clinical-data reflection cannot be solved by frontend components alone. They need backend authorization, audit logging, clear data scopes, and integration contracts.
- Patient/clinical workspace overlays behave almost like separate apps inside the page. Vue can do this cleanly, but it should become either routed layouts or separate app sections instead of one giant overlay component.

## Starter Scope

The Nexus starter implements a Vuetify dashboard shell with mock data for the most important visible workflows:

- Workspace switching
- Dashboard KPIs and attention queue
- Onboarding status
- Protocol library
- Academy progress
- Patient/member list
- Integrations grid
- Billing summary
- AEVA builder stepper
