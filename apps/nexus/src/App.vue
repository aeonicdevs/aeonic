<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

type Partner = {
  id: string;
  ownerName: string;
  email: string;
  clinicName: string;
  clinicDomain: string | null;
};

type Patient = {
  id: string;
  partnerId: string;
  name: string;
  email: string;
};

type MedicationShipment = {
  id: string;
  clientProductId: string;
  aroraPatientId: string | null;
  aroraOrderId: string | null;
  status: string;
  dryRun: boolean;
  response: { message?: string; expectedOutcome?: string } | null;
  updatedAt: string;
  createdAt: string;
};

const queryHost = new URLSearchParams(window.location.search).get('clinicHost');
const resolvedHost = queryHost || window.location.host;
const tokenKey = `aeonic.patient.token.${resolvedHost}`;

const mode = ref<'signup' | 'login'>('signup');
const loading = ref(false);
const error = ref('');
const shipmentMessage = ref('');
const partner = ref<Partner | null>(null);
const patient = ref<Patient | null>(null);
const token = ref(localStorage.getItem(tokenKey) ?? '');
const medicationShipment = ref<MedicationShipment | null>(null);
const medicationShipments = ref<MedicationShipment[]>([]);

const signup = reactive({
  name: '',
  email: '',
  password: '',
});

const login = reactive({
  email: '',
  password: '',
});

const partnerLabel = computed(() => partner.value?.clinicName ?? 'Unconfigured clinic');
const activeProtocol = computed(() => (patient.value ? 'New patient onboarding' : 'Awaiting sign in'));
const clinicDomainLabel = computed(() => partner.value?.clinicDomain ?? resolvedHost);
const shipmentModeLabel = computed(() => {
  if (!medicationShipment.value) return 'Not started';
  if (medicationShipment.value.aroraOrderId?.startsWith('mock_order_')) return 'Mock order';
  return medicationShipment.value.dryRun ? 'Dry run' : 'Live order';
});
const latestMedicationShipment = computed(() => medicationShipment.value ?? medicationShipments.value[0] ?? null);

function formatApiDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail;

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === 'string') return item;
        if (item && typeof item === 'object') {
          const record = item as { loc?: unknown; msg?: unknown };
          const field = Array.isArray(record.loc) ? record.loc.filter(Boolean).slice(1).join('.') : '';
          const message = typeof record.msg === 'string' ? record.msg : '';
          if (field && message) return `${field}: ${message}`;
          if (message) return message;
        }
        return '';
      })
      .filter(Boolean);
    if (messages.length) return messages.join('; ');
  }

  if (detail && typeof detail === 'object') {
    const record = detail as { message?: unknown; msg?: unknown; error?: unknown };
    for (const value of [record.message, record.msg, record.error]) {
      if (typeof value === 'string' && value.trim()) return value;
    }
  }

  return 'Something went wrong';
}

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token.value ? { Authorization: `Bearer ${token.value}` } : {}),
      ...options.headers,
    },
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(formatApiDetail(body.detail));
  }

  return body as T;
}

function setSession(nextToken: string, nextPatient: Patient, nextPartner: Partner) {
  token.value = nextToken;
  patient.value = nextPatient;
  partner.value = nextPartner;
  localStorage.setItem(tokenKey, nextToken);
}

function resetShipmentFeedback() {
  shipmentMessage.value = '';
  medicationShipment.value = null;
}

function formatShipmentStatus(status: string) {
  return status.replace(/_/g, ' ');
}

async function loadContext() {
  loading.value = true;
  error.value = '';
  try {
    const body = await api<{ host: string; partner: Partner | null }>(
      `/nexus/context?host=${encodeURIComponent(resolvedHost)}`,
    );
    partner.value = body.partner;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to resolve clinic';
  } finally {
    loading.value = false;
  }
}

async function restoreSession() {
  if (!token.value) return;

  try {
    const body = await api<{ patient: Patient; partner: Partner }>('/patients/me');
    patient.value = body.patient;
    partner.value = body.partner;
    await loadMedicationShipments();
  } catch {
    localStorage.removeItem(tokenKey);
    token.value = '';
  }
}

async function loadMedicationShipments() {
  if (!token.value) return;

  try {
    const body = await api<{ medicationShipments: MedicationShipment[] }>('/patients/medication-shipments');
    medicationShipments.value = body.medicationShipments;
    medicationShipment.value = body.medicationShipments[0] ?? null;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load medication shipments';
  }
}

async function submitSignup() {
  loading.value = true;
  error.value = '';
  resetShipmentFeedback();
  try {
    const body = await api<{ token: string; patient: Patient; partner: Partner }>('/patients/signup', {
      method: 'POST',
      body: JSON.stringify({ ...signup, host: resolvedHost }),
    });
    setSession(body.token, body.patient, body.partner);
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to create patient account';
  } finally {
    loading.value = false;
  }
}

async function submitLogin() {
  loading.value = true;
  error.value = '';
  resetShipmentFeedback();
  try {
    const body = await api<{ token: string; patient: Patient; partner: Partner }>('/patients/login', {
      method: 'POST',
      body: JSON.stringify({ ...login, host: resolvedHost }),
    });
    setSession(body.token, body.patient, body.partner);
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to log in';
  } finally {
    loading.value = false;
  }
}

function signOut() {
  token.value = '';
  patient.value = null;
  resetShipmentFeedback();
  localStorage.removeItem(tokenKey);
}

async function requestMedicationShipment() {
  loading.value = true;
  error.value = '';
  shipmentMessage.value = '';
  try {
    const body = await api<{ medicationShipment: MedicationShipment }>('/patients/medication-shipments', {
      method: 'POST',
      body: JSON.stringify({}),
    });
    medicationShipment.value = body.medicationShipment;
    medicationShipments.value = [body.medicationShipment, ...medicationShipments.value];
    if (body.medicationShipment.aroraOrderId?.startsWith('mock_order_')) {
      shipmentMessage.value = 'Mock order created. No Arora request was sent.';
    } else if (body.medicationShipment.dryRun) {
      shipmentMessage.value = 'Dry run ready. Configure Arora credentials to place the paid product order.';
    } else {
      shipmentMessage.value = 'Arora order created. Provider review and pharmacy submission are now the next external steps.';
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to request medication shipment';
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await loadContext();
  await restoreSession();
});
</script>

<template>
  <v-app class="patient-shell">
    <v-app-bar class="patient-topbar" flat height="72">
      <v-container class="d-flex align-center" fluid>
        <div class="d-flex align-center ga-3">
          <v-avatar color="primary" rounded="lg" size="40">
            <span class="font-weight-bold text-secondary">A</span>
          </v-avatar>
          <div>
            <div class="serif text-h6">{{ partnerLabel }}</div>
            <div class="text-caption text-medium-emphasis">Aeonic Nexus</div>
          </div>
        </div>
        <v-spacer />
        <v-chip class="d-none d-sm-inline-flex mr-3" color="primary" size="small" variant="tonal">
          {{ resolvedHost }}
        </v-chip>
        <v-btn v-if="patient" prepend-icon="mdi-logout" variant="text" @click="signOut">Sign out</v-btn>
      </v-container>
    </v-app-bar>

    <v-main>
      <v-container class="py-8 py-md-12" style="max-width: 1120px">
        <v-alert v-if="error" class="mb-5" type="error" variant="tonal">{{ error }}</v-alert>

        <template v-if="!partner && !loading">
          <v-card class="nexus-card pa-6 pa-md-8">
            <div class="label mb-3">Host not mapped</div>
            <h1 class="serif text-h3 mb-3">No clinic is configured for {{ resolvedHost }}.</h1>
            <p class="text-medium-emphasis mb-0">
              Save this domain in the Partner app first, then reload Nexus from the clinic host or with the local preview query string.
            </p>
          </v-card>
        </template>

        <template v-else-if="!patient">
          <v-row align="stretch">
            <v-col cols="12" md="6">
              <div class="pr-md-8">
                <div class="label mb-4">Patient portal</div>
                <h1 class="serif text-h3 text-md-h2 mb-5">Welcome to {{ partnerLabel }}.</h1>
                <p class="text-body-1 text-medium-emphasis mb-6">
                  This first-pass Nexus shell proves the white-labeled host flow: the same app resolves the clinic from the domain, then scopes the patient account to that clinic.
                </p>
                <div class="patient-preview pa-4">
                  <div class="label mb-2">Detected host</div>
                  <div class="text-body-1">{{ resolvedHost }}</div>
                </div>
              </div>
            </v-col>

            <v-col cols="12" md="6">
              <v-card class="nexus-card pa-5 pa-md-6">
                <v-btn-toggle v-model="mode" mandatory class="mb-6" color="primary" density="comfortable">
                  <v-btn value="signup" prepend-icon="mdi-account-plus">Create account</v-btn>
                  <v-btn value="login" prepend-icon="mdi-login">Log in</v-btn>
                </v-btn-toggle>

                <v-form v-if="mode === 'signup'" @submit.prevent="submitSignup">
                  <v-text-field v-model="signup.name" label="Full name" autocomplete="name" />
                  <v-text-field v-model="signup.email" label="Email" type="email" autocomplete="email" />
                  <v-text-field v-model="signup.password" label="Password" type="password" autocomplete="new-password" />
                  <v-btn block color="primary" :loading="loading" size="large" type="submit">Create patient account</v-btn>
                </v-form>

                <v-form v-else @submit.prevent="submitLogin">
                  <v-text-field v-model="login.email" label="Email" type="email" autocomplete="email" />
                  <v-text-field v-model="login.password" label="Password" type="password" autocomplete="current-password" />
                  <v-btn block color="primary" :loading="loading" size="large" type="submit">Log in</v-btn>
                </v-form>
              </v-card>
            </v-col>
          </v-row>
        </template>

        <template v-else>
          <div class="d-flex flex-column flex-md-row align-md-end ga-4 mb-6">
            <div>
              <div class="label mb-3">Dashboard</div>
              <h1 class="serif text-h3 mb-2">Hi, {{ patient.name }}.</h1>
              <div class="text-medium-emphasis">{{ partnerLabel }} · {{ patient.email }}</div>
            </div>
            <v-spacer />
            <v-btn color="primary" prepend-icon="mdi-message-text-outline">Message care team</v-btn>
          </div>

          <v-row>
            <v-col cols="12" md="4">
              <v-card class="nexus-card pa-5 h-100">
                <div class="label mb-3">Program</div>
                <div class="serif text-h5 mb-2">{{ activeProtocol }}</div>
                <div class="text-body-2 text-medium-emphasis">Intake, eligibility, protocols, and tasks will hang from this card.</div>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card class="nexus-card pa-5 h-100">
                <div class="label mb-3">Next step</div>
                <div class="serif text-h5 mb-2">Complete intake</div>
                <div class="text-body-2 text-medium-emphasis">This is the first patient workflow to replace with real forms.</div>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card class="nexus-card pa-5 h-100">
                <div class="label mb-3">Clinic domain</div>
                <div class="serif text-h5 mb-2">{{ clinicDomainLabel }}</div>
                <div class="text-body-2 text-medium-emphasis">Resolved by the API before account creation.</div>
              </v-card>
            </v-col>
          </v-row>

          <v-row class="mt-2">
            <v-col cols="12" md="8">
              <v-card class="nexus-card pa-5">
                <div class="label mb-3">Medication shipment</div>
                <div class="serif text-h5 mb-2">Place order</div>
                <div class="text-body-2 text-medium-emphasis mb-5">
                  This creates the first mocked Arora product order for the signed-in patient.
                </div>

                <v-btn color="primary" prepend-icon="mdi-cart-check" :loading="loading" @click="requestMedicationShipment">
                  Place order
                </v-btn>
                <v-btn class="ml-sm-3 mt-3 mt-sm-0" prepend-icon="mdi-refresh" variant="text" @click="loadMedicationShipments">
                  Refresh status
                </v-btn>

                <v-alert v-if="shipmentMessage" class="mt-5" type="success" variant="tonal">
                  {{ shipmentMessage }}
                </v-alert>
              </v-card>
            </v-col>

            <v-col cols="12" md="4">
              <v-card class="nexus-card pa-5 h-100">
                <div class="label mb-3">Arora status</div>
                <template v-if="latestMedicationShipment">
                  <div class="serif text-h5 mb-2">{{ formatShipmentStatus(latestMedicationShipment.status) }}</div>
                  <div class="text-body-2 text-medium-emphasis mb-3">
                    {{ shipmentModeLabel }} · {{ latestMedicationShipment.clientProductId }}
                  </div>
                  <v-list density="compact" class="pa-0 bg-transparent">
                    <v-list-item title="Order ID" :subtitle="latestMedicationShipment.aroraOrderId ?? 'Pending'" />
                    <v-list-item title="Patient ID" :subtitle="latestMedicationShipment.aroraPatientId ?? 'Pending'" />
                  </v-list>
                </template>
                <template v-else>
                  <div class="serif text-h5 mb-2">Not requested</div>
                  <div class="text-body-2 text-medium-emphasis">
                    The first shipment attempt will appear here after the request is submitted.
                  </div>
                </template>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </v-container>
    </v-main>
  </v-app>
</template>
