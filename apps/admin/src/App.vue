<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';
const ORDERS_KEY = 'aeonic.admin.mock-orders';

type ApiStatus = 'checking' | 'online' | 'offline';
type OrderStage =
  | 'intake_received'
  | 'clinical_review'
  | 'prescription_approved'
  | 'pharmacy_submitted'
  | 'fulfilled'
  | 'exception';

type MockOrder = {
  id: string;
  patientName: string;
  partnerName: string;
  product: string;
  stage: OrderStage;
  aroraOrderId: string;
  updatedAt: string;
};

const stages: Array<{ value: OrderStage; label: string; icon: string; color: string }> = [
  { value: 'intake_received', label: 'Intake received', icon: 'mdi-clipboard-text-clock', color: 'info' },
  { value: 'clinical_review', label: 'Clinical review', icon: 'mdi-stethoscope', color: 'primary' },
  { value: 'prescription_approved', label: 'Prescription approved', icon: 'mdi-prescription', color: 'success' },
  { value: 'pharmacy_submitted', label: 'Pharmacy submitted', icon: 'mdi-pharmacy', color: 'accent' },
  { value: 'fulfilled', label: 'Fulfilled', icon: 'mdi-package-variant-closed-check', color: 'success' },
  { value: 'exception', label: 'Exception', icon: 'mdi-alert-circle', color: 'warning' },
];

const apiStatus = ref<ApiStatus>('checking');
const apiMessage = ref('Checking API connection');
const orders = ref<MockOrder[]>([]);
const selectedStage = ref<OrderStage | 'all'>('all');
const notice = ref('');

const draft = reactive({
  patientName: 'Jordan Ellis',
  partnerName: 'Demo Longevity Clinic',
  product: 'Foundational peptide protocol',
});

const stageItems = computed(() => stages.map((stage) => ({ title: stage.label, value: stage.value })));

const filteredOrders = computed(() => {
  if (selectedStage.value === 'all') return orders.value;
  return orders.value.filter((order) => order.stage === selectedStage.value);
});

const activeOrders = computed(() => orders.value.filter((order) => !['fulfilled', 'exception'].includes(order.stage)));
const completedOrders = computed(() => orders.value.filter((order) => order.stage === 'fulfilled'));
const exceptionOrders = computed(() => orders.value.filter((order) => order.stage === 'exception'));

const statusCopy = computed(() => {
  if (apiStatus.value === 'online') {
    return { color: 'success', icon: 'mdi-check-circle', label: 'API online' };
  }
  if (apiStatus.value === 'offline') {
    return { color: 'warning', icon: 'mdi-alert-circle', label: 'API unavailable' };
  }
  return { color: 'info', icon: 'mdi-progress-clock', label: 'Checking API' };
});

function stageFor(value: OrderStage) {
  return stages.find((stage) => stage.value === value) ?? stages[0];
}

function saveOrders() {
  localStorage.setItem(ORDERS_KEY, JSON.stringify(orders.value));
}

function loadOrders() {
  const raw = localStorage.getItem(ORDERS_KEY);
  if (!raw) {
    orders.value = [
      {
        id: 'mock-1007',
        patientName: 'Maya Chen',
        partnerName: 'Demo Longevity Clinic',
        product: 'Metabolic optimization kit',
        stage: 'clinical_review',
        aroraOrderId: 'ARORA-MOCK-1007',
        updatedAt: new Date().toISOString(),
      },
      {
        id: 'mock-1008',
        patientName: 'Alex Rivera',
        partnerName: 'Viper Dental Wellness',
        product: 'Sleep support protocol',
        stage: 'pharmacy_submitted',
        aroraOrderId: 'ARORA-MOCK-1008',
        updatedAt: new Date().toISOString(),
      },
    ];
    saveOrders();
    return;
  }

  try {
    orders.value = JSON.parse(raw) as MockOrder[];
  } catch {
    orders.value = [];
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

function createOrder() {
  const nextNumber = orders.value.length + 1009;
  const now = new Date().toISOString();
  orders.value = [
    {
      id: `mock-${nextNumber}`,
      patientName: draft.patientName.trim() || 'Test Patient',
      partnerName: draft.partnerName.trim() || 'Demo Clinic',
      product: draft.product.trim() || 'Mock protocol',
      stage: 'intake_received',
      aroraOrderId: `ARORA-MOCK-${nextNumber}`,
      updatedAt: now,
    },
    ...orders.value,
  ];
  notice.value = 'Mock order created.';
  saveOrders();
}

function moveOrder(order: MockOrder, stage: OrderStage) {
  orders.value = orders.value.map((item) => (
    item.id === order.id ? { ...item, stage, updatedAt: new Date().toISOString() } : item
  ));
  notice.value = `${order.aroraOrderId} moved to ${stageFor(stage).label}.`;
  saveOrders();
}

function moveOrderTo(order: MockOrder, stage: unknown) {
  if (!stages.some((item) => item.value === stage)) return;
  moveOrder(order, stage as OrderStage);
}

function resetOrders() {
  localStorage.removeItem(ORDERS_KEY);
  loadOrders();
  notice.value = 'Mock queue reset.';
}

function formatTimestamp(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value));
}

onMounted(() => {
  loadOrders();
  void checkApi();
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
            <h1 class="serif text-h3 mb-2">Order and prescription simulator</h1>
            <div class="text-medium-emphasis">
              Create local mock orders and move them through the external states Aeonic will receive from Arora.
            </div>
          </div>
          <v-spacer />
          <v-btn color="primary" prepend-icon="mdi-refresh" variant="flat" @click="checkApi">Check API</v-btn>
        </div>

        <v-alert class="mb-5" :color="statusCopy.color" :icon="statusCopy.icon" variant="tonal">
          <strong>{{ API_BASE }}</strong> - {{ apiMessage }}
        </v-alert>

        <v-alert v-if="notice" class="mb-5" type="success" variant="tonal" closable @click:close="notice = ''">
          {{ notice }}
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
              <div class="label mb-2">Fulfilled</div>
              <div class="serif text-h4">{{ completedOrders.length }}</div>
              <div class="text-caption text-medium-emphasis mt-1">Completed simulations.</div>
            </div>
          </v-col>
          <v-col cols="12" md="4">
            <div class="stat">
              <div class="label mb-2">Exceptions</div>
              <div class="serif text-h4">{{ exceptionOrders.length }}</div>
              <div class="text-caption text-medium-emphasis mt-1">Needs operator attention.</div>
            </div>
          </v-col>
        </v-row>

        <v-row align="start">
          <v-col cols="12" lg="4">
            <v-card class="panel pa-5">
              <div class="d-flex align-center ga-3 mb-5">
                <v-icon color="primary" icon="mdi-plus-circle" />
                <div>
                  <h2 class="text-h6 mb-0">Create mock order</h2>
                  <div class="text-body-2 text-medium-emphasis">Stored locally until backend admin endpoints exist.</div>
                </div>
              </div>

              <v-text-field v-model="draft.patientName" label="Patient name" />
              <v-text-field v-model="draft.partnerName" label="Partner clinic" />
              <v-text-field v-model="draft.product" label="Protocol or product" />

              <v-btn block color="primary" prepend-icon="mdi-playlist-plus" size="large" @click="createOrder">
                Add to simulator
              </v-btn>
            </v-card>
          </v-col>

          <v-col cols="12" lg="8">
            <v-card class="panel pa-5">
              <div class="d-flex flex-column flex-sm-row align-sm-center ga-3 mb-5">
                <div>
                  <h2 class="text-h6 mb-0">Mock Arora queue</h2>
                  <div class="text-body-2 text-medium-emphasis">Use the stage menu on each row to simulate an external update.</div>
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
                <v-btn icon="mdi-restore" variant="text" @click="resetOrders" />
              </div>

              <div class="order-list">
                <div v-for="order in filteredOrders" :key="order.id" class="order-row">
                  <div class="order-main">
                    <div class="d-flex align-center ga-2 mb-2">
                      <v-icon :color="stageFor(order.stage).color" :icon="stageFor(order.stage).icon" size="20" />
                      <strong>{{ order.patientName }}</strong>
                    </div>
                    <div class="text-body-2 text-medium-emphasis">
                      {{ order.partnerName }} - {{ order.product }}
                    </div>
                    <div class="order-meta mt-3">
                      <v-chip size="small" variant="tonal">{{ order.aroraOrderId }}</v-chip>
                      <span>{{ formatTimestamp(order.updatedAt) }}</span>
                    </div>
                  </div>

                  <div class="order-actions">
                    <v-select
                      density="compact"
                      hide-details
                      :items="stageItems"
                      label="Stage"
                      :model-value="order.stage"
                      @update:model-value="moveOrderTo(order, $event)"
                    />
                  </div>
                </div>

                <v-empty-state
                  v-if="filteredOrders.length === 0"
                  icon="mdi-clipboard-search"
                  title="No orders match this stage"
                />
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>
