<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

type ApiStatus = 'checking' | 'online' | 'offline';
type AdminRoute = 'orders' | 'products' | 'mockArora' | 'mockAroraConversations';
type MockAuthor = 'client' | 'patient';

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

type AroraProduct = {
  clientProductId: string;
  name: string;
  displayName: string;
  customerPrice: number;
  itemType: 'package' | null;
  includedProducts: { clientProductId: string }[];
  description: string;
  displayDescription: string;
  displayCategoryIds?: string[];
  showPatient: boolean;
  status: 'active' | 'inactive';
  updatedAt: string;
  createdAt: string;
};

type MockConversation = {
  conversationId: string;
  patientId: string;
  partnerId: string;
  partnerName: string;
  patientName: string;
  patientEmail: string;
  status: string;
  subject: string;
  messageCount: number;
  lastMessageText: string | null;
  lastMessageAt: string | null;
  updatedAt: string;
  createdAt: string;
};

type MockConversationMessage = {
  messageId: string;
  conversationId: string;
  author: MockAuthor;
  senderName: string;
  text: string;
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

const routeItems: { key: AdminRoute; path: string; label: string; icon: string }[] = [
  { key: 'orders', path: '/orders', label: 'Orders', icon: 'mdi-clipboard-pulse' },
  { key: 'products', path: '/products', label: 'Products', icon: 'mdi-pill' },
  { key: 'mockArora', path: '/mock/arora', label: 'Mock Arora', icon: 'mdi-flask-outline' },
  {
    key: 'mockAroraConversations',
    path: '/mock/arora/conversations',
    label: 'Conversations',
    icon: 'mdi-message-text-outline',
  },
];

const routeCopy: Record<AdminRoute, { eyebrow: string; title: string; description: string }> = {
  orders: {
    eyebrow: 'Operations',
    title: 'Order and prescription queue',
    description: 'Orders placed through partner Nexus sites appear here for stage review.',
  },
  products: {
    eyebrow: 'Catalog',
    title: 'Products and packages',
    description: 'Create and edit products and packages available through the mock Arora catalog.',
  },
  mockArora: {
    eyebrow: 'Mock Arora',
    title: 'Mock Arora simulator',
    description: 'Simulation surfaces for the local mock Arora adapter.',
  },
  mockAroraConversations: {
    eyebrow: 'Mock Arora',
    title: 'Mock conversations',
    description: 'Initiate and reply to patient conversations through backend-backed mock Arora records.',
  },
};

const apiStatus = ref<ApiStatus>('checking');
const apiMessage = ref('Checking API connection');
const currentPath = ref(window.location.pathname);
const orders = ref<MedicationShipment[]>([]);
const products = ref<AroraProduct[]>([]);
const mockConversations = ref<MockConversation[]>([]);
const mockMessages = ref<MockConversationMessage[]>([]);
const stages = ref<OrderStage[]>(fallbackStages);
const selectedStage = ref('all');
const selectedConversationId = ref('');
const notice = ref('');
const error = ref('');
const loading = ref(false);
const productLoading = ref(false);
const conversationLoading = ref(false);
const messageLoading = ref(false);
const updatingOrderId = ref('');
const savingProduct = ref(false);
const savingConversation = ref(false);
const savingMessage = ref(false);
const editingProductId = ref('');

const productDraft = reactive({
  item_kind: 'product',
  name: '',
  displayName: '',
  customerPrice: 199,
  showPatient: true,
  description: '',
  displayDescription: '',
  includedProductIds: [] as string[],
  status: 'active',
});

const conversationDraft = reactive({
  patientId: '',
  subject: 'Care team',
  text: '',
  author: 'client' as MockAuthor,
  senderName: 'Care Team',
});

const messageDraft = reactive({
  author: 'client' as MockAuthor,
  senderName: 'Care Team',
  text: '',
});

const authorItems = [
  { title: 'Care team', value: 'client' },
  { title: 'Patient', value: 'patient' },
];

const currentRoute = computed<AdminRoute>(() => {
  const path = currentPath.value.replace(/\/+$/, '') || '/orders';
  if (path === '/products') return 'products';
  if (path === '/mock/arora') return 'mockArora';
  if (path === '/mock/arora/conversations') return 'mockAroraConversations';
  return 'orders';
});
const currentRouteCopy = computed(() => routeCopy[currentRoute.value]);
const stageItems = computed(() => stages.value.map((stage) => ({ title: stage.label, value: stage.value })));
const productStatusItems = [
  { title: 'Active', value: 'active' },
  { title: 'Inactive', value: 'inactive' },
];
const availablePackageProductItems = computed(() => products.value
  .filter((product) => product.status === 'active' && product.itemType !== 'package')
  .map((product) => ({
    title: `${product.displayName} (${product.clientProductId})`,
    value: product.clientProductId,
  })));

const filteredOrders = computed(() => {
  if (selectedStage.value === 'all') return orders.value;
  return orders.value.filter((order) => order.status === selectedStage.value);
});

const patientItems = computed(() => {
  const byId = new Map<string, { title: string; value: string; subtitle: string }>();
  for (const order of orders.value) {
    if (!byId.has(order.patientId)) {
      byId.set(order.patientId, {
        title: order.patientName,
        value: order.patientId,
        subtitle: order.patientEmail,
      });
    }
  }
  return Array.from(byId.values()).sort((a, b) => a.title.localeCompare(b.title));
});

const selectedConversation = computed(() => (
  mockConversations.value.find((conversation) => conversation.conversationId === selectedConversationId.value) ?? null
));

const terminalStatuses = new Set(['delivered', 'canceled', 'prescription_rejected']);
const activeOrders = computed(() => orders.value.filter((order) => !terminalStatuses.has(order.status)));
const completedOrders = computed(() => orders.value.filter((order) => order.status === 'delivered'));
const exceptionOrders = computed(() => orders.value.filter((order) => (
  order.status === 'action_required'
  || order.status === 'canceled'
  || order.status === 'prescription_rejected'
)));
const activeProducts = computed(() => products.value.filter((product) => product.status === 'active'));
const inactiveProducts = computed(() => products.value.filter((product) => product.status === 'inactive'));

const statusCopy = computed(() => {
  if (apiStatus.value === 'online') {
    return { color: 'success', icon: 'mdi-check-circle', label: 'API online' };
  }
  if (apiStatus.value === 'offline') {
    return { color: 'warning', icon: 'mdi-alert-circle', label: 'API unavailable' };
  }
  return { color: 'info', icon: 'mdi-progress-clock', label: 'Checking API' };
});

const refreshCopy = computed(() => {
  if (currentRoute.value === 'products') return { label: 'Refresh products', loading: productLoading.value };
  if (currentRoute.value === 'mockAroraConversations') {
    return { label: 'Refresh conversations', loading: conversationLoading.value };
  }
  if (currentRoute.value === 'mockArora') return { label: 'Refresh mock data', loading: loading.value || productLoading.value || conversationLoading.value };
  return { label: 'Refresh queue', loading: loading.value };
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

function nextStageFor(value: string) {
  const currentIndex = stages.value.findIndex((stage) => stage.value === value);
  if (currentIndex < 0) return stages.value[0] ?? null;
  return stages.value[currentIndex + 1] ?? null;
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

function navigateTo(path: string) {
  if (window.location.pathname === path) return;
  window.history.pushState({}, '', path);
  currentPath.value = window.location.pathname;
  notice.value = '';
  error.value = '';
}

function handlePopstate() {
  currentPath.value = window.location.pathname;
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
    if (!conversationDraft.patientId && patientItems.value.length) {
      conversationDraft.patientId = patientItems.value[0].value;
    }
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

async function loadProducts() {
  productLoading.value = true;
  error.value = '';
  try {
    const body = await api<{ mode: string; products: AroraProduct[] }>('/admin/arora/products');
    products.value = body.products;
    apiStatus.value = 'online';
    apiMessage.value = 'Backend API returned the product catalog.';
  } catch (err) {
    apiStatus.value = 'offline';
    apiMessage.value = err instanceof Error ? err.message : 'Unable to reach backend API.';
    error.value = 'Unable to load products.';
  } finally {
    productLoading.value = false;
  }
}

async function loadMockConversationMessages(conversationId: string) {
  if (!conversationId) {
    mockMessages.value = [];
    return;
  }
  messageLoading.value = true;
  error.value = '';
  try {
    const body = await api<{ mode: string; messages: MockConversationMessage[] }>(
      `/admin/mock/arora/conversations/${encodeURIComponent(conversationId)}/messages`,
    );
    mockMessages.value = body.messages;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load conversation messages.';
  } finally {
    messageLoading.value = false;
  }
}

async function loadMockConversations() {
  conversationLoading.value = true;
  error.value = '';
  try {
    const body = await api<{ mode: string; conversations: MockConversation[] }>('/admin/mock/arora/conversations');
    mockConversations.value = body.conversations;
    if (!mockConversations.value.some((conversation) => conversation.conversationId === selectedConversationId.value)) {
      selectedConversationId.value = mockConversations.value[0]?.conversationId ?? '';
    }
    if (selectedConversationId.value) {
      await loadMockConversationMessages(selectedConversationId.value);
    } else {
      mockMessages.value = [];
    }
    apiStatus.value = 'online';
    apiMessage.value = 'Backend API returned mock Arora conversations.';
  } catch (err) {
    apiStatus.value = 'offline';
    apiMessage.value = err instanceof Error ? err.message : 'Unable to reach backend API.';
    error.value = 'Unable to load mock conversations.';
  } finally {
    conversationLoading.value = false;
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

async function refreshCurrentView() {
  if (currentRoute.value === 'products') {
    await loadProducts();
    return;
  }
  if (currentRoute.value === 'mockAroraConversations') {
    await Promise.all([loadOrders(), loadMockConversations()]);
    return;
  }
  if (currentRoute.value === 'mockArora') {
    await Promise.all([loadOrders(), loadProducts(), loadMockConversations()]);
    return;
  }
  await loadOrders();
}

function resetProductForm() {
  editingProductId.value = '';
  Object.assign(productDraft, {
    item_kind: 'product',
    name: '',
    displayName: '',
    customerPrice: 199,
    showPatient: true,
    description: '',
    displayDescription: '',
    includedProductIds: [],
    status: 'active',
  });
}

function editProduct(product: AroraProduct) {
  navigateTo('/products');
  editingProductId.value = product.clientProductId;
  Object.assign(productDraft, {
    item_kind: product.itemType === 'package' ? 'package' : 'product',
    name: product.name,
    displayName: product.displayName,
    customerPrice: product.customerPrice,
    showPatient: product.showPatient,
    description: product.description,
    displayDescription: product.displayDescription,
    includedProductIds: product.includedProducts.map((includedProduct) => includedProduct.clientProductId),
    status: product.status,
  });
}

async function saveProduct() {
  savingProduct.value = true;
  notice.value = '';
  error.value = '';
  try {
    const payload = {
      name: productDraft.name.trim(),
      displayName: productDraft.displayName.trim() || undefined,
      customerPrice: Number.isFinite(Number(productDraft.customerPrice)) ? Number(productDraft.customerPrice) : undefined,
      itemType: productDraft.item_kind === 'package' ? 'package' : undefined,
      includedProducts: productDraft.item_kind === 'package'
        ? productDraft.includedProductIds.map((clientProductId) => ({ clientProductId }))
        : undefined,
      description: productDraft.description.trim() || undefined,
      displayDescription: productDraft.displayDescription.trim() || undefined,
      showPatient: productDraft.showPatient,
      status: productDraft.status,
    };
    const path = editingProductId.value
      ? `/admin/arora/products/${encodeURIComponent(editingProductId.value)}`
      : '/admin/arora/products';
    const method = editingProductId.value ? 'PATCH' : 'POST';
    const body = await api<{ mode: string; product: AroraProduct }>(path, {
      method,
      body: JSON.stringify(payload),
    });
    products.value = editingProductId.value
      ? products.value.map((product) => (
        product.clientProductId === body.product.clientProductId ? body.product : product
      ))
      : [...products.value, body.product].sort((a, b) => a.displayName.localeCompare(b.displayName));
    notice.value = `${body.product.displayName} saved.`;
    resetProductForm();
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to save product.';
  } finally {
    savingProduct.value = false;
  }
}

async function deleteProduct(product: AroraProduct) {
  savingProduct.value = true;
  notice.value = '';
  error.value = '';
  try {
    await api<{ deleted: boolean }>(`/admin/arora/products/${encodeURIComponent(product.clientProductId)}`, {
      method: 'DELETE',
    });
    products.value = products.value.filter((item) => item.clientProductId !== product.clientProductId);
    if (editingProductId.value === product.clientProductId) resetProductForm();
    notice.value = `${product.displayName} removed.`;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to delete product.';
  } finally {
    savingProduct.value = false;
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

async function createMockConversation() {
  savingConversation.value = true;
  notice.value = '';
  error.value = '';
  try {
    const body = await api<{ mode: string; conversation: MockConversation }>('/admin/mock/arora/conversations', {
      method: 'POST',
      body: JSON.stringify({
        patient_id: conversationDraft.patientId,
        subject: conversationDraft.subject.trim() || 'Care team',
        text: conversationDraft.text.trim(),
        author: conversationDraft.author,
        sender_name: conversationDraft.senderName.trim() || 'Care Team',
      }),
    });
    conversationDraft.text = '';
    selectedConversationId.value = body.conversation.conversationId;
    await loadMockConversations();
    notice.value = `Conversation started with ${body.conversation.patientName}.`;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to create mock conversation.';
  } finally {
    savingConversation.value = false;
  }
}

async function selectConversation(conversation: MockConversation) {
  selectedConversationId.value = conversation.conversationId;
  await loadMockConversationMessages(conversation.conversationId);
}

async function sendMockConversationMessage() {
  if (!selectedConversationId.value) return;
  savingMessage.value = true;
  notice.value = '';
  error.value = '';
  try {
    const body = await api<{ mode: string; conversation: MockConversation; message: MockConversationMessage }>(
      `/admin/mock/arora/conversations/${encodeURIComponent(selectedConversationId.value)}/messages`,
      {
        method: 'POST',
        body: JSON.stringify({
          author: messageDraft.author,
          sender_name: messageDraft.senderName.trim() || (messageDraft.author === 'patient' ? 'Patient' : 'Care Team'),
          text: messageDraft.text.trim(),
        }),
      },
    );
    mockConversations.value = mockConversations.value.map((conversation) => (
      conversation.conversationId === body.conversation.conversationId ? body.conversation : conversation
    ));
    mockMessages.value = [...mockMessages.value, body.message];
    messageDraft.text = '';
    notice.value = 'Message added to the mock conversation.';
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to add message.';
  } finally {
    savingMessage.value = false;
  }
}

function formatCurrency(value: number | null) {
  if (value === null) return 'No price';
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: 'USD',
  }).format(value);
}

function formatTimestamp(value: string | null) {
  if (!value) return 'No activity yet';
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value));
}

onMounted(async () => {
  window.addEventListener('popstate', handlePopstate);
  if (window.location.pathname === '/') {
    window.history.replaceState({}, '', '/orders');
    currentPath.value = '/orders';
  }
  await checkApi();
  await Promise.all([loadOrders(), loadProducts(), loadMockConversations()]);
});

onUnmounted(() => {
  window.removeEventListener('popstate', handlePopstate);
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
            <div class="label mb-3">{{ currentRouteCopy.eyebrow }}</div>
            <h1 class="serif text-h3 mb-2">{{ currentRouteCopy.title }}</h1>
            <div class="text-medium-emphasis">{{ currentRouteCopy.description }}</div>
          </div>
          <v-spacer />
          <v-btn
            color="primary"
            prepend-icon="mdi-refresh"
            :loading="refreshCopy.loading"
            variant="flat"
            @click="refreshCurrentView"
          >
            {{ refreshCopy.label }}
          </v-btn>
        </div>

        <nav class="admin-nav mb-5" aria-label="Admin sections">
          <v-btn
            v-for="item in routeItems"
            :key="item.key"
            :active="currentRoute === item.key"
            :color="currentRoute === item.key ? 'primary' : undefined"
            :prepend-icon="item.icon"
            :variant="currentRoute === item.key ? 'flat' : 'tonal'"
            @click="navigateTo(item.path)"
          >
            {{ item.label }}
          </v-btn>
        </nav>

        <v-alert class="mb-5" :color="statusCopy.color" :icon="statusCopy.icon" variant="tonal">
          <strong>{{ API_BASE }}</strong> - {{ apiMessage }}
        </v-alert>

        <v-alert v-if="notice" class="mb-5" type="success" variant="tonal" closable @click:close="notice = ''">
          {{ notice }}
        </v-alert>
        <v-alert v-if="error" class="mb-5" type="error" variant="tonal" closable @click:close="error = ''">
          {{ error }}
        </v-alert>

        <template v-if="currentRoute === 'orders'">
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
                <div class="text-caption text-medium-emphasis mt-1">Completed orders.</div>
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
                <div class="text-body-2 text-medium-emphasis">Advance a row through the available order stages.</div>
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
                  <v-btn
                    block
                    class="mt-3"
                    color="primary"
                    :disabled="!nextStageFor(order.status)"
                    prepend-icon="mdi-debug-step-over"
                    :loading="updatingOrderId === order.id"
                    @click="moveOrderTo(order, nextStageFor(order.status)?.value)"
                  >
                    Advance to next stage
                  </v-btn>
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
        </template>

        <template v-else-if="currentRoute === 'products'">
          <v-row class="mb-5">
            <v-col cols="12" md="4">
              <div class="stat">
                <div class="label mb-2">Catalog records</div>
                <div class="serif text-h4">{{ products.length }}</div>
                <div class="text-caption text-medium-emphasis mt-1">Products and packages.</div>
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="stat">
                <div class="label mb-2">Active</div>
                <div class="serif text-h4">{{ activeProducts.length }}</div>
                <div class="text-caption text-medium-emphasis mt-1">Available in the catalog.</div>
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="stat">
                <div class="label mb-2">Inactive</div>
                <div class="serif text-h4">{{ inactiveProducts.length }}</div>
                <div class="text-caption text-medium-emphasis mt-1">Retained but hidden from active lists.</div>
              </div>
            </v-col>
          </v-row>

          <v-row align="start">
            <v-col cols="12" lg="4">
              <v-card class="panel pa-5">
                <div class="d-flex align-center ga-3 mb-5">
                  <v-icon color="primary" icon="mdi-database-edit" />
                  <div>
                    <h2 class="text-h6 mb-0">{{ editingProductId ? 'Edit product' : 'Create product' }}</h2>
                    <div class="text-body-2 text-medium-emphasis">Manage catalog availability and patient-facing copy.</div>
                  </div>
                </div>

                <v-form @submit.prevent="saveProduct">
                  <v-btn-toggle
                    v-model="productDraft.item_kind"
                    class="mb-4"
                    color="primary"
                    density="comfortable"
                    divided
                    mandatory
                  >
                    <v-btn value="product" prepend-icon="mdi-pill">Product</v-btn>
                    <v-btn value="package" prepend-icon="mdi-package-variant">Package</v-btn>
                  </v-btn-toggle>
                  <v-text-field v-model="productDraft.name" label="Internal name" />
                  <v-text-field v-model="productDraft.displayName" label="Patient-facing name" />
                  <v-row>
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model.number="productDraft.customerPrice"
                        label="Customer price"
                        min="0"
                        prefix="$"
                        step="0.01"
                        type="number"
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-select v-model="productDraft.status" :items="productStatusItems" label="Status" />
                    </v-col>
                  </v-row>
                  <v-switch
                    v-model="productDraft.showPatient"
                    color="primary"
                    hide-details
                    inset
                    label="Show to patients"
                  />
                  <v-select
                    v-if="productDraft.item_kind === 'package'"
                    v-model="productDraft.includedProductIds"
                    :items="availablePackageProductItems"
                    chips
                    closable-chips
                    label="Included products"
                    multiple
                  />
                  <v-textarea
                    v-model="productDraft.description"
                    auto-grow
                    label="Internal description"
                    rows="3"
                    variant="outlined"
                  />
                  <v-textarea
                    v-model="productDraft.displayDescription"
                    auto-grow
                    label="Patient-facing description"
                    rows="3"
                    variant="outlined"
                  />
                  <div class="d-flex ga-3">
                    <v-btn color="primary" :loading="savingProduct" prepend-icon="mdi-content-save" type="submit">
                      {{ editingProductId ? 'Save changes' : 'Create product' }}
                    </v-btn>
                    <v-btn variant="text" @click="resetProductForm">Clear</v-btn>
                  </div>
                </v-form>
              </v-card>
            </v-col>

            <v-col cols="12" lg="8">
              <v-card class="panel pa-5">
                <div class="d-flex flex-column flex-sm-row align-sm-center ga-3 mb-5">
                  <div>
                    <h2 class="text-h6 mb-0">Product catalog</h2>
                    <div class="text-body-2 text-medium-emphasis">Products and packages available for patient ordering.</div>
                  </div>
                </div>

                <div class="product-list">
                  <div v-for="product in products" :key="product.clientProductId" class="product-row">
                    <div class="product-main">
                      <div class="d-flex align-center ga-2 mb-2">
                        <strong>{{ product.displayName }}</strong>
                        <v-chip :color="product.status === 'active' ? 'success' : 'default'" size="small" variant="tonal">
                          {{ product.status }}
                        </v-chip>
                        <v-chip size="small" variant="tonal">{{ product.itemType === 'package' ? 'package' : 'product' }}</v-chip>
                        <v-chip :color="product.showPatient ? 'primary' : 'default'" size="small" variant="tonal">
                          {{ product.showPatient ? 'patient visible' : 'hidden' }}
                        </v-chip>
                      </div>
                      <div class="text-body-2 text-medium-emphasis">
                        {{ product.displayDescription || product.description || 'No description' }}
                      </div>
                      <div class="order-meta mt-3">
                        <v-chip size="small" variant="tonal">{{ product.clientProductId }}</v-chip>
                        <span>{{ formatCurrency(product.customerPrice) }}</span>
                        <span v-if="product.itemType === 'package'">
                          {{ product.includedProducts.length }} included
                        </span>
                      </div>
                    </div>

                    <div class="product-actions">
                      <v-btn block prepend-icon="mdi-pencil" variant="tonal" @click="editProduct(product)">
                        Edit
                      </v-btn>
                      <v-btn
                        block
                        class="mt-3"
                        color="error"
                        prepend-icon="mdi-delete"
                        variant="text"
                        @click="deleteProduct(product)"
                      >
                        Delete
                      </v-btn>
                    </div>
                  </div>

                  <v-empty-state
                    v-if="products.length === 0"
                    icon="mdi-package-variant"
                    title="No products yet"
                    text="Create the first product or package from the form."
                  />
                </div>
              </v-card>
            </v-col>
          </v-row>
        </template>

        <template v-else-if="currentRoute === 'mockArora'">
          <v-row class="mb-5">
            <v-col cols="12" md="4">
              <div class="stat">
                <div class="label mb-2">Mock products</div>
                <div class="serif text-h4">{{ products.length }}</div>
                <div class="text-caption text-medium-emphasis mt-1">Records in the mock catalog.</div>
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="stat">
                <div class="label mb-2">Mock orders</div>
                <div class="serif text-h4">{{ orders.length }}</div>
                <div class="text-caption text-medium-emphasis mt-1">Medication shipments backed by Arora order flow.</div>
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="stat">
                <div class="label mb-2">Conversations</div>
                <div class="serif text-h4">{{ mockConversations.length }}</div>
                <div class="text-caption text-medium-emphasis mt-1">Patient conversation simulations.</div>
              </div>
            </v-col>
          </v-row>

          <div class="mock-grid">
            <v-card class="panel pa-5">
              <div class="d-flex align-center ga-3 mb-4">
                <v-icon color="primary" icon="mdi-message-text-outline" />
                <div>
                  <h2 class="text-h6 mb-0">Conversations</h2>
                  <div class="text-body-2 text-medium-emphasis">Start and reply to mock Arora patient threads.</div>
                </div>
              </div>
              <v-btn color="primary" prepend-icon="mdi-arrow-right" @click="navigateTo('/mock/arora/conversations')">
                Open conversations
              </v-btn>
            </v-card>

            <v-card class="panel pa-5">
              <div class="d-flex align-center ga-3 mb-4">
                <v-icon color="primary" icon="mdi-pill" />
                <div>
                  <h2 class="text-h6 mb-0">Products</h2>
                  <div class="text-body-2 text-medium-emphasis">Edit the mock Arora catalog used by patient ordering.</div>
                </div>
              </div>
              <v-btn variant="tonal" prepend-icon="mdi-arrow-right" @click="navigateTo('/products')">
                Open products
              </v-btn>
            </v-card>
          </div>
        </template>

        <template v-else>
          <v-row align="start">
            <v-col cols="12" lg="4">
              <v-card class="panel pa-5">
                <div class="d-flex align-center ga-3 mb-5">
                  <v-icon color="primary" icon="mdi-message-plus-outline" />
                  <div>
                    <h2 class="text-h6 mb-0">Start conversation</h2>
                    <div class="text-body-2 text-medium-emphasis">Use a patient from the current admin order queue.</div>
                  </div>
                </div>

                <v-form @submit.prevent="createMockConversation">
                  <v-select
                    v-model="conversationDraft.patientId"
                    :disabled="patientItems.length === 0"
                    :items="patientItems"
                    item-title="title"
                    item-value="value"
                    label="Patient"
                  >
                    <template #item="{ props, item }">
                      <v-list-item v-bind="props" :subtitle="item.raw.subtitle" />
                    </template>
                  </v-select>
                  <v-text-field v-model="conversationDraft.subject" label="Subject" />
                  <v-select v-model="conversationDraft.author" :items="authorItems" label="Initial author" />
                  <v-text-field v-model="conversationDraft.senderName" label="Sender name" />
                  <v-textarea
                    v-model="conversationDraft.text"
                    auto-grow
                    label="Initial message"
                    rows="4"
                    variant="outlined"
                  />
                  <v-btn
                    color="primary"
                    :disabled="patientItems.length === 0"
                    :loading="savingConversation"
                    prepend-icon="mdi-message-plus-outline"
                    type="submit"
                  >
                    Start conversation
                  </v-btn>
                </v-form>
              </v-card>
            </v-col>

            <v-col cols="12" lg="8">
              <div class="conversation-layout">
                <v-card class="panel pa-5">
                  <div class="d-flex align-center ga-3 mb-5">
                    <v-icon color="primary" icon="mdi-forum-outline" />
                    <div>
                      <h2 class="text-h6 mb-0">Conversation list</h2>
                      <div class="text-body-2 text-medium-emphasis">Mock threads stored by the backend.</div>
                    </div>
                  </div>

                  <div class="conversation-list">
                    <button
                      v-for="conversation in mockConversations"
                      :key="conversation.conversationId"
                      class="conversation-row"
                      :class="{ 'is-selected': conversation.conversationId === selectedConversationId }"
                      type="button"
                      @click="selectConversation(conversation)"
                    >
                      <div>
                        <div class="conversation-title">
                          <strong>{{ conversation.subject }}</strong>
                          <span>{{ conversation.patientName }}</span>
                        </div>
                        <div class="text-body-2 text-medium-emphasis">
                          {{ conversation.lastMessageText || 'No messages yet' }}
                        </div>
                      </div>
                      <div class="conversation-meta">
                        <v-chip size="small" variant="tonal">{{ conversation.messageCount }} messages</v-chip>
                        <span>{{ formatTimestamp(conversation.lastMessageAt || conversation.updatedAt) }}</span>
                      </div>
                    </button>

                    <v-empty-state
                      v-if="mockConversations.length === 0"
                      icon="mdi-message-text-outline"
                      title="No mock conversations yet"
                      text="Start a conversation with a patient from the admin order queue."
                    />
                  </div>
                </v-card>

                <v-card class="panel pa-5">
                  <div class="d-flex align-center ga-3 mb-5">
                    <v-icon color="primary" icon="mdi-message-reply-text-outline" />
                    <div>
                      <h2 class="text-h6 mb-0">{{ selectedConversation?.subject || 'Messages' }}</h2>
                      <div class="text-body-2 text-medium-emphasis">
                        {{ selectedConversation ? selectedConversation.patientEmail : 'Select a conversation to view messages.' }}
                      </div>
                    </div>
                  </div>

                  <div v-if="selectedConversation" class="message-list mb-5">
                    <div
                      v-for="message in mockMessages"
                      :key="message.messageId"
                      class="message-row"
                      :class="message.author === 'patient' ? 'is-patient' : 'is-client'"
                    >
                      <div class="d-flex justify-space-between ga-3 mb-1">
                        <strong>{{ message.senderName }}</strong>
                        <span class="text-caption text-medium-emphasis">{{ formatTimestamp(message.createdAt) }}</span>
                      </div>
                      <div>{{ message.text }}</div>
                    </div>
                    <v-progress-linear v-if="messageLoading" color="primary" indeterminate />
                  </div>

                  <v-form v-if="selectedConversation" @submit.prevent="sendMockConversationMessage">
                    <v-row>
                      <v-col cols="12" sm="6">
                        <v-select v-model="messageDraft.author" :items="authorItems" label="Reply as" />
                      </v-col>
                      <v-col cols="12" sm="6">
                        <v-text-field v-model="messageDraft.senderName" label="Sender name" />
                      </v-col>
                    </v-row>
                    <v-textarea
                      v-model="messageDraft.text"
                      auto-grow
                      label="Reply"
                      rows="3"
                      variant="outlined"
                    />
                    <v-btn color="primary" :loading="savingMessage" prepend-icon="mdi-send" type="submit">
                      Send reply
                    </v-btn>
                  </v-form>
                </v-card>
              </div>
            </v-col>
          </v-row>
        </template>
      </v-container>
    </v-main>
  </v-app>
</template>
