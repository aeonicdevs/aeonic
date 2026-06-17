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

type DomainStatus = 'not_configured' | 'pending_dns' | 'connected' | 'needs_attention';
type CloudflareProvisioningStatus =
  | 'not_configured'
  | 'dns_not_ready'
  | 'not_available'
  | 'skipped'
  | 'pending'
  | 'active'
  | 'needs_attention';

type DomainVerification = {
  domain: string | null;
  recordType: 'CNAME';
  recordName: string | null;
  recordValue: string;
  status: DomainStatus;
  message: string;
  checkedAt: string;
};

type DomainSetup = {
  recordType: 'CNAME';
  recordValue: string;
};

type CloudflareCustomHostname = {
  domain: string | null;
  status: CloudflareProvisioningStatus;
  message: string;
  id: string | null;
  hostname: string | null;
  hostnameStatus: string | null;
  sslStatus: string | null;
  sslValidationMethod: string | null;
  syncedAt: string | null;
  error: string | null;
};

const mode = ref<'signup' | 'login'>('signup');
const loading = ref(false);
const verifyingDomain = ref(false);
const provisioningCloudflare = ref(false);
const error = ref('');
const notice = ref('');
const token = ref(localStorage.getItem(TOKEN_KEY) ?? '');
const partner = ref<Partner | null>(null);
const baseDomainDraft = ref('');
const subdomainDraft = ref('app');
const domainSetup = ref<DomainSetup>({
  recordType: 'CNAME',
  recordValue: 'nexus.aeonichealthsystems.com',
});
const domainVerification = ref<DomainVerification | null>(null);
const cloudflareHostname = ref<CloudflareCustomHostname | null>(null);

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

const hostnamePreview = computed(() => {
  const baseDomain = normalizeHostInput(baseDomainDraft.value);
  const subdomain = normalizeSubdomain(subdomainDraft.value);
  if (!baseDomain || !subdomain) return '';
  return `${subdomain}.${baseDomain}`;
});

const dnsRecord = computed(() => {
  const domain = partner.value?.clinicDomain || hostnamePreview.value || null;
  return {
    type: domainVerification.value?.recordType ?? domainSetup.value.recordType,
    name: domainVerification.value?.recordName ?? domain,
    value: domainVerification.value?.recordValue ?? domainSetup.value.recordValue,
  };
});

const domainStatus = computed<DomainStatus>(() => {
  if (!partner.value?.clinicDomain) return 'not_configured';
  return domainVerification.value?.status ?? 'pending_dns';
});

const domainStatusCopy = computed(() => {
  switch (domainStatus.value) {
    case 'connected':
      return {
        color: 'success',
        icon: 'mdi-check-circle',
        label: 'Connected',
        message: domainVerification.value?.message ?? 'DNS is connected.',
      };
    case 'needs_attention':
      return {
        color: 'warning',
        icon: 'mdi-alert-circle',
        label: 'Needs attention',
        message: domainVerification.value?.message ?? 'DNS is resolving, but not to the expected Nexus target.',
      };
    case 'not_configured':
      return {
        color: 'default',
        icon: 'mdi-web-off',
        label: 'Not configured',
        message: 'Save a patient-facing domain to generate DNS instructions.',
      };
    default:
      return {
        color: 'info',
        icon: 'mdi-progress-clock',
        label: 'Pending DNS setup',
        message: domainVerification.value?.message ?? 'Create this CNAME record with your DNS provider, then verify it.',
      };
  }
});

const cloudflareStatusCopy = computed(() => {
  const status = cloudflareHostname.value?.status ?? (partner.value?.clinicDomain ? 'pending' : 'not_configured');
  switch (status) {
    case 'active':
      return {
        color: 'success',
        icon: 'mdi-cloud-check',
        label: 'Active',
        message: cloudflareHostname.value?.message ?? 'Cloudflare SSL is active for this hostname.',
      };
    case 'needs_attention':
      return {
        color: 'warning',
        icon: 'mdi-cloud-alert',
        label: 'Needs attention',
        message: cloudflareHostname.value?.message ?? 'Cloudflare needs attention before this hostname can go live.',
      };
    case 'dns_not_ready':
      return {
        color: 'info',
        icon: 'mdi-cloud-clock',
        label: 'Waiting for DNS',
        message: cloudflareHostname.value?.message ?? 'Verify the CNAME before creating the Cloudflare hostname.',
      };
    case 'not_available':
      return {
        color: 'warning',
        icon: 'mdi-cloud-off-outline',
        label: 'Not configured',
        message: cloudflareHostname.value?.message ?? 'Cloudflare is not configured for this environment.',
      };
    case 'skipped':
      return {
        color: 'default',
        icon: 'mdi-cloud-off-outline',
        label: 'Skipped',
        message: cloudflareHostname.value?.message ?? 'Local development domains do not need Cloudflare.',
      };
    case 'not_configured':
      return {
        color: 'default',
        icon: 'mdi-cloud-outline',
        label: 'Not configured',
        message: 'Save a domain before creating a Cloudflare hostname.',
      };
    default:
      return {
        color: 'info',
        icon: 'mdi-cloud-sync',
        label: 'Ready to create',
        message: cloudflareHostname.value?.message ?? 'Create the Cloudflare custom hostname after DNS is connected.',
      };
  }
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
  domainVerification.value = null;
  cloudflareHostname.value = null;
  hydrateDomainDrafts(nextPartner.clinicDomain);
  localStorage.setItem(TOKEN_KEY, nextToken);
  void loadDomainSetup();
}

function normalizeHostInput(value: string) {
  let normalized = value.trim().toLowerCase();
  if (normalized.includes('://')) {
    normalized = normalized.split('://', 2)[1];
  }
  normalized = normalized.split('/', 1)[0];
  if (normalized.includes(':') && !normalized.startsWith('[')) {
    normalized = normalized.split(':', 1)[0];
  }
  return normalized.replace(/\.+$/, '');
}

function normalizeSubdomain(value: string) {
  return value.trim().toLowerCase().replace(/^\.+|\.+$/g, '');
}

function isValidBaseDomain(value: string) {
  const labels = value.split('.');
  return labels.every((label) => /^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(label));
}

function isValidSubdomain(value: string) {
  return /^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(value);
}

function hydrateDomainDrafts(clinicDomain: string | null) {
  if (!clinicDomain) {
    subdomainDraft.value = 'app';
    baseDomainDraft.value = '';
    return;
  }

  const normalizedDomain = normalizeHostInput(clinicDomain);
  const parts = normalizedDomain.split('.');
  subdomainDraft.value = parts.length >= 3 ? parts[0] : 'app';
  baseDomainDraft.value = parts.length >= 3 ? parts.slice(1).join('.') : normalizedDomain;
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
    const baseDomain = normalizeHostInput(baseDomainDraft.value);
    const subdomain = normalizeSubdomain(subdomainDraft.value);

    if (!baseDomain) {
      throw new Error('Domain is required');
    }
    if (!isValidBaseDomain(baseDomain)) {
      throw new Error('Enter a valid domain, for example yourclinic.com');
    }
    if (!isValidSubdomain(subdomain)) {
      throw new Error('Subdomain can use only letters, numbers, and hyphens');
    }

    const clinicDomain = `${subdomain}.${baseDomain}`;
    const body = await api<{ partner: Partner }>('/partners/settings', {
      method: 'PATCH',
      body: JSON.stringify({ clinic_domain: clinicDomain }),
    });
    partner.value = body.partner;
    hydrateDomainDrafts(body.partner.clinicDomain);
    domainVerification.value = null;
    cloudflareHostname.value = null;
    notice.value = 'Domain saved. Add the DNS record below, then verify the connection.';
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to save domain';
  } finally {
    loading.value = false;
  }
}

async function verifyDomain() {
  verifyingDomain.value = true;
  error.value = '';
  notice.value = '';
  try {
    const body = await api<{ verification: DomainVerification }>('/partners/domain/verify', {
      method: 'POST',
    });
    domainVerification.value = body.verification;
    notice.value = body.verification.status === 'connected'
      ? 'Domain connected. Create the Cloudflare hostname to finish SSL provisioning.'
      : '';
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to verify domain';
  } finally {
    verifyingDomain.value = false;
  }
}

async function loadCloudflareHostname() {
  if (!partner.value?.clinicDomain) {
    cloudflareHostname.value = null;
    return;
  }

  try {
    const body = await api<{ cloudflare: CloudflareCustomHostname }>('/partners/domain/cloudflare-custom-hostname');
    cloudflareHostname.value = body.cloudflare;
  } catch {
    cloudflareHostname.value = null;
  }
}

async function loadDomainSetup() {
  if (!partner.value) return;

  try {
    const body = await api<{ dns: DomainSetup }>('/partners/domain/setup');
    domainSetup.value = body.dns;
  } catch {
    domainSetup.value = {
      recordType: 'CNAME',
      recordValue: 'nexus.aeonichealthsystems.com',
    };
  }
}

async function provisionCloudflareHostname() {
  provisioningCloudflare.value = true;
  error.value = '';
  notice.value = '';
  try {
    const body = await api<{ verification: DomainVerification; cloudflare: CloudflareCustomHostname }>(
      '/partners/domain/cloudflare-custom-hostname',
      { method: 'POST' },
    );
    domainVerification.value = body.verification;
    cloudflareHostname.value = body.cloudflare;
    notice.value = body.cloudflare.status === 'active'
      ? 'Cloudflare custom hostname is active.'
      : body.cloudflare.message;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to create Cloudflare hostname';
  } finally {
    provisioningCloudflare.value = false;
  }
}

async function copyDnsValue(value: string | null) {
  if (!value) return;

  try {
    await navigator.clipboard.writeText(value);
    notice.value = 'Copied DNS value.';
  } catch {
    error.value = 'Unable to copy. Select the value and copy it manually.';
  }
}

async function restoreSession() {
  if (!token.value) return;

  try {
    const body = await api<{ partner: Partner }>('/partners/me');
    partner.value = body.partner;
    domainVerification.value = null;
    hydrateDomainDrafts(body.partner.clinicDomain);
    await loadDomainSetup();
    await loadCloudflareHostname();
  } catch {
    localStorage.removeItem(TOKEN_KEY);
    token.value = '';
  }
}

function signOut() {
  token.value = '';
  partner.value = null;
  domainVerification.value = null;
  cloudflareHostname.value = null;
  hydrateDomainDrafts(null);
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
                <div class="d-flex align-center ga-2">
                  <v-icon :color="domainStatusCopy.color" :icon="domainStatusCopy.icon" size="20" />
                  <div class="serif text-h5">{{ domainStatusCopy.label }}</div>
                </div>
                <div class="text-caption text-medium-emphasis mt-1">{{ domainStatusCopy.message }}</div>
              </div>
            </v-col>
          </v-row>

          <v-card class="panel pa-5 pa-md-6 mt-6">
            <div class="d-flex align-center ga-3 mb-4">
              <v-icon color="primary" icon="mdi-web" />
              <div>
                <h2 class="text-h6 mb-0">Patient-facing domain</h2>
                <div class="text-body-2 text-medium-emphasis">Connect a partner-owned hostname, then let Aeonic provision it in Cloudflare.</div>
              </div>
            </div>

            <v-alert v-if="notice" class="mb-4" type="success" variant="tonal">{{ notice }}</v-alert>
            <v-alert v-if="error" class="mb-4" type="error" variant="tonal">{{ error }}</v-alert>

            <div class="setup-step">
              <div class="step-marker">1</div>
              <div class="step-body">
                <div class="label mb-2">Hostname</div>
                <v-row align="start">
                  <v-col cols="12" md="4">
                    <v-text-field v-model="subdomainDraft" hide-details label="Subdomain" placeholder="app" />
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field v-model="baseDomainDraft" hide-details label="Clinic domain" placeholder="yourclinic.com" />
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-btn block color="primary" :loading="loading" prepend-icon="mdi-content-save" size="large" @click="saveDomain">
                      Save domain
                    </v-btn>
                  </v-col>
                </v-row>
                <div class="domain-final mt-4">
                  <span class="label">Nexus host</span>
                  <span>{{ hostnamePreview || 'app.yourclinic.com' }}</span>
                </div>
              </div>
            </div>

            <div class="setup-step mt-5">
              <div class="step-marker">2</div>
              <div class="step-body">
              <div class="d-flex flex-column flex-md-row align-md-center ga-3 mb-4">
                <div>
                  <div class="label mb-2">DNS setup</div>
                  <h3 class="text-h6 mb-1">Create this record with your DNS provider</h3>
                  <div class="text-body-2 text-medium-emphasis">
                    DNS changes can take a few minutes to propagate. Verify again after your provider saves the record.
                  </div>
                </div>
                <v-spacer />
                <v-chip :color="domainStatusCopy.color" :prepend-icon="domainStatusCopy.icon" variant="tonal">
                  {{ domainStatusCopy.label }}
                </v-chip>
              </div>

              <div class="dns-record-grid">
                <div class="dns-record-cell">
                  <span class="label">Type</span>
                  <strong>{{ dnsRecord.type }}</strong>
                </div>
                <div class="dns-record-cell">
                  <span class="label">Name</span>
                  <div class="dns-record-value">
                    <strong>{{ dnsRecord.name || 'Save a domain first' }}</strong>
                    <v-btn
                      :disabled="!dnsRecord.name"
                      icon="mdi-content-copy"
                      size="small"
                      title="Copy DNS record name"
                      variant="text"
                      @click="copyDnsValue(dnsRecord.name)"
                    />
                  </div>
                </div>
                <div class="dns-record-cell">
                  <span class="label">Value</span>
                  <div class="dns-record-value">
                    <strong>{{ dnsRecord.value }}</strong>
                    <v-btn
                      icon="mdi-content-copy"
                      size="small"
                      title="Copy DNS record value"
                      variant="text"
                      @click="copyDnsValue(dnsRecord.value)"
                    />
                  </div>
                </div>
              </div>

              <div class="d-flex flex-column flex-md-row align-md-center ga-3 mt-4">
                <div class="text-body-2 text-medium-emphasis">
                  {{ domainStatusCopy.message }}
                </div>
                <v-spacer />
                <v-btn
                  color="primary"
                  :disabled="!partner.clinicDomain"
                  :loading="verifyingDomain"
                  prepend-icon="mdi-shield-check"
                  @click="verifyDomain"
                >
                  Verify connection
                </v-btn>
              </div>
              </div>
            </div>

            <div class="setup-step mt-5">
              <div class="step-marker">3</div>
              <div class="step-body">
                <div class="d-flex flex-column flex-md-row align-md-center ga-3 mb-4">
                  <div>
                    <div class="label mb-2">Cloudflare for SaaS</div>
                    <h3 class="text-h6 mb-1">Create the custom hostname</h3>
                    <div class="text-body-2 text-medium-emphasis">
                      Once DNS is connected, Aeonic asks Cloudflare to create the SaaS hostname and issue SSL.
                    </div>
                  </div>
                  <v-spacer />
                  <v-chip :color="cloudflareStatusCopy.color" :prepend-icon="cloudflareStatusCopy.icon" variant="tonal">
                    {{ cloudflareStatusCopy.label }}
                  </v-chip>
                </div>

                <div class="cloudflare-grid">
                  <div class="dns-record-cell">
                    <span class="label">Hostname ID</span>
                    <strong>{{ cloudflareHostname?.id || 'Not created yet' }}</strong>
                  </div>
                  <div class="dns-record-cell">
                    <span class="label">Hostname status</span>
                    <strong>{{ cloudflareHostname?.hostnameStatus || cloudflareStatusCopy.label }}</strong>
                  </div>
                  <div class="dns-record-cell">
                    <span class="label">SSL status</span>
                    <strong>{{ cloudflareHostname?.sslStatus || 'Pending creation' }}</strong>
                  </div>
                </div>

                <div class="d-flex flex-column flex-md-row align-md-center ga-3 mt-4">
                  <div class="text-body-2 text-medium-emphasis">
                    {{ cloudflareStatusCopy.message }}
                  </div>
                  <v-spacer />
                  <v-btn
                    color="primary"
                    :disabled="!partner.clinicDomain || cloudflareHostname?.status === 'skipped'"
                    :loading="provisioningCloudflare"
                    prepend-icon="mdi-cloud-upload"
                    @click="provisionCloudflareHostname"
                  >
                    Confirm CNAME and create
                  </v-btn>
                </div>
              </div>
            </div>
          </v-card>
        </template>
      </v-container>
    </v-main>
  </v-app>
</template>
