<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';
const TOKEN_KEY = 'aeonic.partner.token';

type Partner = {
  id: string;
  ownerName: string;
  email: string;
  clinicName: string;
  clinicDomain: string | null;
};

const mode = ref<'signup' | 'login'>('signup');
const loading = ref(false);
const error = ref('');
const notice = ref('');
const token = ref(localStorage.getItem(TOKEN_KEY) ?? '');
const partner = ref<Partner | null>(null);
const domainDraft = ref('');

const signup = reactive({
  owner_name: '',
  email: '',
  password: '',
  clinic_name: '',
});

const login = reactive({
  email: '',
  password: '',
});

const nexusUrl = computed(() => {
  const host = partner.value?.clinicDomain || 'app.demo.localhost';
  return `http://127.0.0.1:5173/?clinicHost=${encodeURIComponent(host)}`;
});

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
    throw new Error(body.detail ?? 'Something went wrong');
  }

  return body as T;
}

function setSession(nextToken: string, nextPartner: Partner) {
  token.value = nextToken;
  partner.value = nextPartner;
  domainDraft.value = nextPartner.clinicDomain ?? '';
  localStorage.setItem(TOKEN_KEY, nextToken);
}

async function submitSignup() {
  loading.value = true;
  error.value = '';
  notice.value = '';
  try {
    const body = await api<{ token: string; partner: Partner }>('/partners/signup', {
      method: 'POST',
      body: JSON.stringify(signup),
    });
    setSession(body.token, body.partner);
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to create partner account';
  } finally {
    loading.value = false;
  }
}

async function submitLogin() {
  loading.value = true;
  error.value = '';
  notice.value = '';
  try {
    const body = await api<{ token: string; partner: Partner }>('/partners/login', {
      method: 'POST',
      body: JSON.stringify(login),
    });
    setSession(body.token, body.partner);
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to log in';
  } finally {
    loading.value = false;
  }
}

async function saveDomain() {
  loading.value = true;
  error.value = '';
  notice.value = '';
  try {
    const body = await api<{ partner: Partner }>('/partners/settings', {
      method: 'PATCH',
      body: JSON.stringify({ clinic_domain: domainDraft.value }),
    });
    partner.value = body.partner;
    domainDraft.value = body.partner.clinicDomain ?? '';
    notice.value = 'Domain saved. Nexus will resolve this host to your clinic.';
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to save domain';
  } finally {
    loading.value = false;
  }
}

async function restoreSession() {
  if (!token.value) return;

  try {
    const body = await api<{ partner: Partner }>('/partners/me');
    partner.value = body.partner;
    domainDraft.value = body.partner.clinicDomain ?? '';
  } catch {
    localStorage.removeItem(TOKEN_KEY);
    token.value = '';
  }
}

function signOut() {
  token.value = '';
  partner.value = null;
  localStorage.removeItem(TOKEN_KEY);
}

onMounted(restoreSession);
</script>

<template>
  <v-app class="partner-shell">
    <v-app-bar class="topline" flat height="72">
      <v-container class="d-flex align-center" fluid>
        <div class="d-flex align-center ga-3">
          <v-avatar color="primary" rounded="lg" size="40">
            <span class="font-weight-bold">A</span>
          </v-avatar>
          <div>
            <div class="serif text-h6">Aeonic Partner</div>
            <div class="text-caption text-medium-emphasis">Clinic owner console</div>
          </div>
        </div>
        <v-spacer />
        <v-btn v-if="partner" prepend-icon="mdi-logout" variant="text" @click="signOut">Sign out</v-btn>
      </v-container>
    </v-app-bar>

    <v-main>
      <v-container class="py-8 py-md-12" style="max-width: 1160px">
        <template v-if="!partner">
          <v-row align="stretch">
            <v-col cols="12" md="6">
              <div class="pr-md-8">
                <div class="label mb-4">Partner onboarding</div>
                <h1 class="serif text-h3 text-md-h2 mb-5">Create a clinic account and connect your patient domain.</h1>
                <p class="text-body-1 text-medium-emphasis mb-6">
                  This skeleton creates a partner session, then drops you into the dashboard where the clinic domain can be mapped to Nexus.
                </p>
                <div class="domain-preview pa-4">
                  <div class="label mb-2">Local patient app preview</div>
                  <div class="text-body-2">After saving a domain, open Nexus with a simulated host query string.</div>
                </div>
              </div>
            </v-col>

            <v-col cols="12" md="6">
              <v-card class="panel pa-5 pa-md-6">
                <v-btn-toggle v-model="mode" mandatory class="mb-6" color="primary" density="comfortable">
                  <v-btn value="signup" prepend-icon="mdi-account-plus">Create account</v-btn>
                  <v-btn value="login" prepend-icon="mdi-login">Log in</v-btn>
                </v-btn-toggle>

                <v-alert v-if="error" class="mb-4" type="error" variant="tonal">{{ error }}</v-alert>

                <v-form v-if="mode === 'signup'" @submit.prevent="submitSignup">
                  <v-text-field v-model="signup.owner_name" label="Owner name" autocomplete="name" />
                  <v-text-field v-model="signup.clinic_name" label="Clinic name" />
                  <v-text-field v-model="signup.email" label="Email" type="email" autocomplete="email" />
                  <v-text-field v-model="signup.password" label="Password" type="password" autocomplete="new-password" />
                  <v-btn block color="primary" :loading="loading" size="large" type="submit">Create partner account</v-btn>
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
              <h1 class="serif text-h3 mb-2">{{ partner.clinicName }}</h1>
              <div class="text-medium-emphasis">Signed in as {{ partner.ownerName }} · {{ partner.email }}</div>
            </div>
            <v-spacer />
            <v-btn color="primary" prepend-icon="mdi-open-in-new" :href="nexusUrl" target="_blank">Open Nexus preview</v-btn>
          </div>

          <v-row>
            <v-col cols="12" md="4">
              <div class="stat">
                <div class="label mb-2">Patients</div>
                <div class="serif text-h4">0</div>
                <div class="text-caption text-medium-emphasis mt-1">Ready for real data.</div>
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="stat">
                <div class="label mb-2">Domain</div>
                <div class="serif text-h5">{{ partner.clinicDomain || 'Not configured' }}</div>
                <div class="text-caption text-medium-emphasis mt-1">Used by Nexus host detection.</div>
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="stat">
                <div class="label mb-2">Status</div>
                <div class="serif text-h5">Skeleton live</div>
                <div class="text-caption text-medium-emphasis mt-1">Auth and routing are wired.</div>
              </div>
            </v-col>
          </v-row>

          <v-card class="panel pa-5 pa-md-6 mt-6">
            <div class="d-flex align-center ga-3 mb-4">
              <v-icon color="primary" icon="mdi-web" />
              <div>
                <h2 class="text-h6 mb-0">Patient-facing domain</h2>
                <div class="text-body-2 text-medium-emphasis">Enter the host that will point to Nexus, for example patients.yourclinic.com.</div>
              </div>
            </div>

            <v-alert v-if="notice" class="mb-4" type="success" variant="tonal">{{ notice }}</v-alert>
            <v-alert v-if="error" class="mb-4" type="error" variant="tonal">{{ error }}</v-alert>

            <v-row align="center">
              <v-col cols="12" md="8">
                <v-text-field v-model="domainDraft" hide-details label="Clinic patient domain" placeholder="patients.yourclinic.com" />
              </v-col>
              <v-col cols="12" md="4">
                <v-btn block color="primary" :loading="loading" prepend-icon="mdi-content-save" size="large" @click="saveDomain">
                  Save domain
                </v-btn>
              </v-col>
            </v-row>
          </v-card>
        </template>
      </v-container>
    </v-main>
  </v-app>
</template>
