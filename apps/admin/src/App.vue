<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

type ApiStatus = 'checking' | 'online' | 'offline';

type OrderStage = {
  value: string;
  label: string;
  description: string;
};

type MedicationShipment = {
  id: string;
  patientId: string;
  partnerId: string;
  patientName: string;
  patientEmail: string;
  partnerName: string;
  partnerEmail: string;
  partnerClinicDomain: string | null;
  clientProductId: string;
  aroraPatientId: string | null;
  aroraOrderId: string | null;
  status: string;
  dryRun: boolean;
  response: { message?: string; expectedOutcome?: string } | null;
  updatedAt: string;
  createdAt: string;
};

const fallbackStages: OrderStage[] = [
  {
    value: 'pending_review',
    label: 'Pending review',
    description: 'Arora has accepted the paid product order and it is waiting for clinical review.',
  },
];

const stageVisuals: Record<string, { icon: string; color: string }> = {
  pending_review: { icon: 'mdi-clipboard-text-clock', color: 'info' },
  action_required: { icon: 'mdi-alert-circle', color: 'warning' },
  prescription_approved: { icon: 'mdi-prescription', color: 'success' },
  prescription_rejected: { icon: 'mdi-close-octagon', color: 'error' },
  pharmacy_submitted: { icon: 'mdi-pharmacy', color: 'accent' },
  shipped: { icon: 'mdi-truck-delivery', color: 'primary' },
  delivered: { icon: 'mdi-package-variant-closed-check', color: 'success' },
  canceled: { icon: 'mdi-cancel', color: 'error' },
};

const apiStatus = ref<ApiStatus>('checking');
const apiMessage = ref('Checking API connection');
const orders = ref<MedicationShipment[]>([]);
const stages = ref<OrderStage[]>(fallbackStages);
const selectedStage = ref('all');
const notice = ref('');
const error = ref('');
const loading = ref(false);
const updatingOrderId = ref('');

const stageItems = computed(() => stages.value.map((stage) => ({ title: stage.label, value: stage.value })));

const filteredOrders = computed(() => {
  if (selectedStage.value === 'all') return orders.value;
  return orders.value.filter((order) => order.status === selectedStage.value);
});

const terminalStatuses = new Set(['delivered', 'canceled', 'prescription_rejected']);
const activeOrders = computed(() => orders.value.filter((order) => !terminalStatuses.has(order.status)));
const completedOrders = computed(() => orders.value.filter((order) => order.status === 'delivered'));
const exceptionOrders = computed(() => orders.value.filter((order) => (
  order.status === 'action_required'
  || order.status === 'canceled'
  || order.status === 'prescription_rejected'
)));

const statusCopy = computed(() => {
  if (apiStatus.value === 'online') {
    return { color: 'success', icon: 'mdi-check-circle', label: 'API online' };
  }
  if (apiStatus.value === 'offline') {
    return { color: 'warning', icon: 'mdi-alert-circle', label: 'API unavailable' };
  }
  return { color: 'info', icon: 'mdi-progress-clock', label: 'Checking API' };
});

function stageFor(value: string) {
  const metadata = stages.value.find((stage) => stage.value === value) ?? {
    value,
    label: value.replace(/_/g, ' '),
    description: 'Unrecognized order stage.',
  };
  const visual = stageVisuals[value] ?? { icon: 'mdi-progress-question', color: 'default' };
  return { ...metadata, ...visual };
}

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail ?? 'Something went wrong');
  }

  return body as T;
}

async function loadOrders() {
  loading.value = true;
  error.value = '';
  try {
    const body = await api<{ stages: OrderStage[]; medicationShipments: MedicationShipment[] }>(
      '/admin/medication-shipments',
    );
    stages.value = body.stages.length ? body.stages : fallbackStages;
    orders.value = body.medicationShipments;
    apiStatus.value = 'online';
    apiMessage.value = 'Backend API returned the admin medication queue.';
  } catch (err) {
    apiStatus.value = 'offline';
    apiMessage.value = err instanceof Error ? err.message : 'Unable to reach backend API.';
    error.value = 'Unable to load the admin order queue.';
  } finally {
    loading.value = false;
  }
}

async function checkApi() {
  apiStatus.value = 'checking';
  apiMessage.value = `Checking ${API_BASE}/health`;
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const body = await response.json().catch(() => ({}));
    apiStatus.value = 'online';
    apiMessage.value = body.status === 'ok' ? 'Backend API health check passed.' : 'Backend API responded.';
  } catch (err) {
    apiStatus.value = 'offline';
    apiMessage.value = err instanceof Error ? err.message : 'Unable to reach backend API.';
  }
}

async function moveOrderTo(order: MedicationShipment, status: unknown) {
  if (typeof status !== 'string' || !stages.value.some((stage) => stage.value === status)) return;

  updatingOrderId.value = order.id;
  notice.value = '';
  error.value = '';
  try {
    const body = await api<{ medicationShipment: MedicationShipment }>(
      `/admin/medication-shipments/${order.id}`,
      {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      },
    );
    orders.value = orders.value.map((item) => (
      item.id === order.id ? body.medicationShipment : item
    ));
    notice.value = `${order.aroraOrderId ?? order.id} moved to ${stageFor(status).label}.`;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to update order status.';
  } finally {
    updatingOrderId.value = '';
  }
}

function formatTimestamp(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value));
}

onMounted(async () => {
  await checkApi();
  await loadOrders();
});
</script>

<template>
  <v-app class="admin-shell">
    <v-app-bar class="topline" flat height="72">
      <v-container class="d-flex align-center" fluid>
        <div class="d-flex align-center ga-3">
          <v-avatar color="primary" rounded="lg" size="40">
            <span class="font-weight-bold">A</span>
          </v-avatar>
          <div>
            <div class="serif text-h6">Aeonic Admin</div>
            <div class="text-caption text-medium-emphasis">Operations console</div>
          </div>
        </div>
        <v-spacer />
        <v-chip :color="statusCopy.color" :prepend-icon="statusCopy.icon" variant="tonal">
          {{ statusCopy.label }}
        </v-chip>
      </v-container>
    </v-app-bar>

    <v-main>
      <v-container class="py-6 py-md-8" style="max-width: 1280px">
        <div class="d-flex flex-column flex-md-row align-md-end ga-4 mb-6">
          <div>
            <div class="label mb-3">Manual testing</div>
            <h1 class="serif text-h3 mb-2">Order and prescription queue</h1>
            <div class="text-medium-emphasis">
              Orders placed in a local partner Nexus app appear here for Arora stage simulation.
            </div>
          </div>
          <v-spacer />
          <v-btn color="primary" prepend-icon="mdi-refresh" :loading="loading" variant="flat" @click="loadOrders">
            Refresh queue
          </v-btn>
        </div>

        <v-alert class="mb-5" :color="statusCopy.color" :icon="statusCopy.icon" variant="tonal">
          <strong>{{ API_BASE }}</strong> - {{ apiMessage }}
        </v-alert>

        <v-alert v-if="notice" class="mb-5" type="success" variant="tonal" closable @click:close="notice = ''">
          {{ notice }}
        </v-alert>
        <v-alert v-if="error" class="mb-5" type="error" variant="tonal" closable @click:close="error = ''">
          {{ error }}
        </v-alert>

        <v-row class="mb-5">
          <v-col cols="12" md="4">
            <div class="stat">
              <div class="label mb-2">Active queue</div>
              <div class="serif text-h4">{{ activeOrders.length }}</div>
              <div class="text-caption text-medium-emphasis mt-1">Orders still moving.</div>
            </div>
          </v-col>
          <v-col cols="12" md="4">
            <div class="stat">
              <div class="label mb-2">Delivered</div>
              <div class="serif text-h4">{{ completedOrders.length }}</div>
              <div class="text-caption text-medium-emphasis mt-1">Completed simulations.</div>
            </div>
          </v-col>
          <v-col cols="12" md="4">
            <div class="stat">
              <div class="label mb-2">Needs attention</div>
              <div class="serif text-h4">{{ exceptionOrders.length }}</div>
              <div class="text-caption text-medium-emphasis mt-1">Action required, canceled, or rejected.</div>
            </div>
          </v-col>
        </v-row>

        <v-card class="panel pa-5">
          <div class="d-flex flex-column flex-sm-row align-sm-center ga-3 mb-5">
            <div>
              <h2 class="text-h6 mb-0">Medication shipments</h2>
              <div class="text-body-2 text-medium-emphasis">Advance a row to simulate the next Arora API state.</div>
            </div>
            <v-spacer />
            <v-select
              v-model="selectedStage"
              class="stage-filter"
              density="compact"
              hide-details
              :items="[{ title: 'All stages', value: 'all' }, ...stageItems]"
              label="Stage"
            />
          </div>

          <div class="order-list">
            <div v-for="order in filteredOrders" :key="order.id" class="order-row">
              <div class="order-main">
                <div class="d-flex align-center ga-2 mb-2">
                  <v-icon :color="stageFor(order.status).color" :icon="stageFor(order.status).icon" size="20" />
                  <strong>{{ order.patientName }}</strong>
                  <v-chip :color="stageFor(order.status).color" size="small" variant="tonal">
                    {{ stageFor(order.status).label }}
                  </v-chip>
                </div>
                <div class="text-body-2 text-medium-emphasis">
                  {{ order.partnerName }} - {{ order.clientProductId }}
                </div>
                <div class="order-meta mt-3">
                  <v-chip size="small" variant="tonal">{{ order.aroraOrderId ?? 'Pending Arora order' }}</v-chip>
                  <span>{{ order.patientEmail }}</span>
                  <span>{{ formatTimestamp(order.updatedAt) }}</span>
                </div>
              </div>

              <div class="order-actions">
                <v-select
                  density="compact"
                  hide-details
                  :items="stageItems"
                  label="Stage"
                  :loading="updatingOrderId === order.id"
                  :model-value="order.status"
                  @update:model-value="moveOrderTo(order, $event)"
                />
              </div>
            </div>

            <v-empty-state
              v-if="filteredOrders.length === 0"
              icon="mdi-clipboard-search"
              title="No orders yet"
              text="Place an order from a local Nexus patient account, then refresh this queue."
            />
          </div>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>
