<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue';

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

type AroraOrder = {
  orderId: string;
  patientId: string;
  clientProductId: string;
  displayName: string;
  orderType: string;
  orderStatus: string;
  paymentStatus: string;
  amount: number;
  createdAt: string;
  updatedAt: string;
};

type EntityRow = Record<string, unknown>;
type Conversation = {
  conversationId: string;
  patientId: string;
  status: string;
  escalationReason: string | null;
  escalatedAt: string | null;
  messageCount: number;
  lastMessageText: string | null;
  lastMessageAt: string | null;
  updatedAt: string;
  createdAt: string;
};
type ConversationMessage = {
  messageId: string;
  conversationId: string;
  author: 'client' | 'patient';
  senderUserId: string | null;
  senderName: string;
  text: string;
  attachments: PatientAttachment[];
  updatedAt: string;
  createdAt: string;
};
type PatientAttachment = {
  id?: string;
  url: string;
  name?: string;
  mimeType?: string;
  size?: number;
  status?: string;
};

type EntityPageConfig = {
  key: string;
  title: string;
  label: string;
  description: string;
  icon: string;
  path: string;
  endpoint: (params?: Record<string, string>) => string;
  collectionKey: string;
  columns: { key: string; title: string; type?: 'currency' | 'currencyCents' | 'date' | 'status' }[];
};

const queryHost = new URLSearchParams(window.location.search).get('clinicHost');
const resolvedHost = queryHost || window.location.host;
const tokenKey = `aeonic.patient.token.${resolvedHost}`;

const mode = ref<'signup' | 'login'>('signup');
const loading = ref(false);
const productLoading = ref(false);
const error = ref('');
const shipmentMessage = ref('');
const partner = ref<Partner | null>(null);
const patient = ref<Patient | null>(null);
const token = ref(localStorage.getItem(tokenKey) ?? '');
const medicationShipment = ref<MedicationShipment | null>(null);
const medicationShipments = ref<MedicationShipment[]>([]);
const aroraProducts = ref<AroraProduct[]>([]);
const selectedProductId = ref('');
const currentPath = ref(window.location.pathname);
const entityLoading = ref(false);
const entityError = ref('');
const entityRows = ref<EntityRow[]>([]);
const selectedConversationId = ref('');
const conversationMessages = ref<ConversationMessage[]>([]);
const conversationMessageLoading = ref(false);
const savingConversation = ref(false);
const conversationNotice = ref('');
let entityLoadRequestId = 0;
let conversationMessageRequestId = 0;

const entityPages: EntityPageConfig[] = [
  {
    key: 'products',
    title: 'Products',
    label: 'Products',
    description: 'Patient-visible consult products returned through the Arora-shaped catalog.',
    icon: 'mdi-pill',
    path: '/products',
    endpoint: () => '/patients/arora/products',
    collectionKey: 'products',
    columns: [
      { key: 'displayName', title: 'Product' },
      { key: 'clientProductId', title: 'Client product ID' },
      { key: 'customerPrice', title: 'Price', type: 'currency' },
      { key: 'status', title: 'Status', type: 'status' },
    ],
  },
  {
    key: 'orders',
    title: 'Orders',
    label: 'Orders',
    description: 'Orders placed by this patient, normalized toward the Arora v2 order shape.',
    icon: 'mdi-clipboard-pulse-outline',
    path: '/orders',
    endpoint: () => '/patients/arora/orders',
    collectionKey: 'orders',
    columns: [
      { key: 'orderId', title: 'Order ID' },
      { key: 'displayName', title: 'Product' },
      { key: 'orderStatus', title: 'Status', type: 'status' },
      { key: 'paymentStatus', title: 'Payment', type: 'status' },
      { key: 'amount', title: 'Amount', type: 'currencyCents' },
      { key: 'createdAt', title: 'Created', type: 'date' },
    ],
  },
  {
    key: 'labs',
    title: 'Labs',
    label: 'Labs',
    description: 'Lab products available to the patient through the Arora-shaped lab catalog.',
    icon: 'mdi-flask-outline',
    path: '/labs',
    endpoint: () => '/patients/arora/labs',
    collectionKey: 'labs',
    columns: [
      { key: 'displayName', title: 'Lab' },
      { key: 'clientProductId', title: 'Client product ID' },
      { key: 'customerPrice', title: 'Price', type: 'currency' },
      { key: 'status', title: 'Status', type: 'status' },
    ],
  },
  {
    key: 'visits',
    title: 'Visits',
    label: 'Visits',
    description: 'Visit records associated with this patient and their orders.',
    icon: 'mdi-calendar-clock',
    path: '/visits',
    endpoint: () => '/patients/arora/visits',
    collectionKey: 'visits',
    columns: [
      { key: 'visitId', title: 'Visit ID' },
      { key: 'orderId', title: 'Order ID' },
      { key: 'visitType', title: 'Type' },
      { key: 'status', title: 'Status', type: 'status' },
      { key: 'createdAt', title: 'Created', type: 'date' },
    ],
  },
  {
    key: 'conversations',
    title: 'Conversations',
    label: 'Conversations',
    description: 'Patient conversations shaped for the Arora v2 messages surface.',
    icon: 'mdi-message-text-outline',
    path: '/conversations',
    endpoint: () => '/patients/arora/conversations',
    collectionKey: 'conversations',
    columns: [
      { key: 'conversationId', title: 'Conversation ID' },
      { key: 'status', title: 'Status', type: 'status' },
      { key: 'lastMessageText', title: 'Last message' },
      { key: 'updatedAt', title: 'Updated', type: 'date' },
    ],
  },
  {
    key: 'prescriptions',
    title: 'Prescriptions',
    label: 'Prescriptions',
    description: 'Read-only prescription records associated with the patient order timeline.',
    icon: 'mdi-prescription',
    path: '/prescriptions',
    endpoint: () => '/patients/arora/prescriptions',
    collectionKey: 'prescriptions',
    columns: [
      { key: 'prescriptionId', title: 'Prescription ID' },
      { key: 'orderId', title: 'Order ID' },
      { key: 'medicationName', title: 'Medication' },
      { key: 'status', title: 'Status', type: 'status' },
      { key: 'submittedAt', title: 'Submitted', type: 'date' },
    ],
  },
  {
    key: 'payments',
    title: 'Payments',
    label: 'Payments',
    description: 'Payment records derived from patient orders.',
    icon: 'mdi-credit-card-outline',
    path: '/payments',
    endpoint: () => '/patients/arora/payments',
    collectionKey: 'payments',
    columns: [
      { key: 'paymentId', title: 'Payment ID' },
      { key: 'orderId', title: 'Order ID' },
      { key: 'status', title: 'Status', type: 'status' },
      { key: 'amount', title: 'Amount', type: 'currencyCents' },
      { key: 'createdAt', title: 'Created', type: 'date' },
    ],
  },
];

const signup = reactive({
  name: '',
  email: '',
  password: '',
});

const login = reactive({
  email: '',
  password: '',
});

const conversationDraft = reactive({
  text: '',
  files: [] as File[],
});

const conversationMessageDraft = reactive({
  text: '',
  files: [] as File[],
});

const partnerLabel = computed(() => partner.value?.clinicName ?? 'Unconfigured clinic');
const clinicDomainLabel = computed(() => partner.value?.clinicDomain ?? resolvedHost);
const shipmentModeLabel = computed(() => {
  if (!medicationShipment.value) return 'Not started';
  if (medicationShipment.value.aroraOrderId?.startsWith('mock_order_')) return 'Mock order';
  return medicationShipment.value.dryRun ? 'Dry run' : 'Live order';
});
const latestMedicationShipment = computed(() => medicationShipment.value ?? medicationShipments.value[0] ?? null);
const selectedProduct = computed(() => (
  aroraProducts.value.find((product) => product.clientProductId === selectedProductId.value) ?? null
));
const conversationRows = computed(() => (
  entityRows.value.filter((row): row is EntityRow & Conversation => (
    typeof row.conversationId === 'string' && row.conversationId.length > 0
  ))
));
const selectedConversation = computed(() => (
  conversationRows.value.find((conversation) => conversation.conversationId === selectedConversationId.value) ?? null
));
const selectedConversationTitle = computed(() => (
  selectedConversation.value ? formatConversationTitle(selectedConversation.value) : 'Select a conversation'
));
const productItems = computed(() => aroraProducts.value.map((product) => ({
  title: `${product.displayName} - ${formatCurrency(product.customerPrice)}`,
  value: product.clientProductId,
  subtitle: product.displayDescription || product.description || product.clientProductId,
})));
const formsRouteMatch = computed(() => currentPath.value.match(/^\/orders\/([^/]+)\/forms\/?$/));
const currentEntityPage = computed<EntityPageConfig | null>(() => {
  const formsMatch = formsRouteMatch.value;
  if (formsMatch) {
    return {
      key: 'orderForms',
      title: 'Order forms',
      label: 'Forms',
      description: 'Required intake and consent forms for the selected order.',
      icon: 'mdi-form-select',
      path: currentPath.value,
      endpoint: (params = {}) => `/patients/arora/orders/${encodeURIComponent(params.orderId ?? '')}/forms`,
      collectionKey: 'forms',
      columns: [
        { key: 'formKey', title: 'Form key' },
        { key: 'name', title: 'Name' },
        { key: 'formType', title: 'Type' },
        { key: 'completionStatus', title: 'Status', type: 'status' },
        { key: 'version', title: 'Version' },
      ],
    };
  }

  return entityPages.find((page) => page.path === currentPath.value.replace(/\/$/, '') || page.path === currentPath.value) ?? null;
});
const isDashboard = computed(() => currentPath.value === '/' || currentPath.value === '');
const appNavItems = computed(() => [
  { key: 'dashboard', label: 'Dashboard', icon: 'mdi-view-dashboard-outline', path: '/' },
  ...entityPages.map((page) => ({ key: page.key, label: page.label, icon: page.icon, path: page.path })),
]);

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

function formatCurrency(value: number) {
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: 'USD',
  }).format(value);
}

function formatDate(value: unknown) {
  if (!value) return '—';
  const date = new Date(String(value));
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date);
}

function formatTimestamp(value: unknown) {
  if (!value) return 'No activity yet';
  const date = new Date(String(value));
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date);
}

function formatConversationTitle(conversation: Conversation) {
  return `Conversation ${conversation.conversationId.slice(-8)}`;
}

function isCurrentEntityRequest(requestId: number, page: EntityPageConfig) {
  const currentPage = currentEntityPage.value;
  return requestId === entityLoadRequestId && currentPage?.key === page.key && currentPage.path === page.path;
}

function normalizeFiles(value: File[] | File | null | undefined) {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

function formatFileSize(value: number | undefined) {
  if (!value) return '';
  if (value < 1024 * 1024) return `${Math.max(1, Math.round(value / 1024))} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

async function uploadAttachment(file: File) {
  const created = await api<{
    attachment: PatientAttachment;
    upload: { method: 'PUT'; url: string; headers: Record<string, string> };
  }>('/patients/attachments/uploads', {
    method: 'POST',
    body: JSON.stringify({
      file_name: file.name,
      content_type: file.type || 'application/octet-stream',
      size: file.size,
    }),
  });

  const uploadResponse = await fetch(created.upload.url, {
    method: created.upload.method,
    headers: created.upload.headers,
    body: file,
  });
  if (!uploadResponse.ok) {
    throw new Error(`Unable to upload ${file.name}`);
  }

  const completed = await api<{ attachment: PatientAttachment }>(
    `/patients/attachments/${encodeURIComponent(created.attachment.id ?? '')}/complete`,
    { method: 'POST' },
  );
  return completed.attachment;
}

async function uploadDraftAttachments(files: File[]) {
  const attachments: PatientAttachment[] = [];
  for (const file of files) {
    attachments.push(await uploadAttachment(file));
  }
  return attachments;
}

async function openAttachment(attachment: PatientAttachment) {
  if (attachment.id) {
    const body = await api<{ downloadUrl: string }>(`/patients/attachments/${encodeURIComponent(attachment.id)}/open`);
    window.open(body.downloadUrl, '_blank', 'noopener,noreferrer');
    return;
  }

  if (attachment.url.startsWith('http://') || attachment.url.startsWith('https://')) {
    window.open(attachment.url, '_blank', 'noopener,noreferrer');
  }
}

function formatCell(row: EntityRow, column: EntityPageConfig['columns'][number]) {
  const value = row[column.key];
  if (column.type === 'currency') {
    return typeof value === 'number' ? formatCurrency(value) : '—';
  }
  if (column.type === 'currencyCents') {
    return typeof value === 'number' ? formatCurrency(value / 100) : '—';
  }
  if (column.type === 'date') return formatDate(value);
  if (Array.isArray(value)) return `${value.length}`;
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function withClinicHost(path: string) {
  if (!queryHost) return path;
  return `${path}?clinicHost=${encodeURIComponent(queryHost)}`;
}

function navigateTo(path: string) {
  window.history.pushState({}, '', withClinicHost(path));
  currentPath.value = window.location.pathname;
  void loadCurrentEntityPage();
}

function handlePopstate() {
  currentPath.value = window.location.pathname;
  void loadCurrentEntityPage();
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
    await loadPatientProducts();
    await loadMedicationShipments();
  } catch {
    localStorage.removeItem(tokenKey);
    token.value = '';
  }
}

async function loadPatientProducts() {
  if (!token.value) return;

  productLoading.value = true;
  try {
    const body = await api<{ mode: string; products: AroraProduct[] }>('/patients/arora/products');
    aroraProducts.value = body.products;
    if (selectedProductId.value && !body.products.some((product) => product.clientProductId === selectedProductId.value)) {
      selectedProductId.value = '';
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load Arora products';
  } finally {
    productLoading.value = false;
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

async function loadCurrentEntityPage() {
  const page = currentEntityPage.value;
  const requestId = ++entityLoadRequestId;
  if (!token.value || !page) {
    conversationMessageRequestId += 1;
    entityLoading.value = false;
    conversationMessageLoading.value = false;
    entityRows.value = [];
    entityError.value = '';
    conversationMessages.value = [];
    return;
  }

  entityLoading.value = true;
  entityError.value = '';
  try {
    const formsMatch = formsRouteMatch.value;
    const params: Record<string, string> = formsMatch ? { orderId: decodeURIComponent(formsMatch[1]) } : {};
    const body = await api<Record<string, unknown>>(page.endpoint(params));
    if (!isCurrentEntityRequest(requestId, page)) return;

    const rows = body[page.collectionKey];
    entityRows.value = Array.isArray(rows) ? rows as EntityRow[] : [];
    if (page.key === 'conversations') {
      if (!conversationRows.value.some((conversation) => conversation.conversationId === selectedConversationId.value)) {
        selectedConversationId.value = conversationRows.value[0]?.conversationId ?? '';
      }
      if (selectedConversationId.value) {
        await loadConversationMessages(selectedConversationId.value);
      } else {
        conversationMessages.value = [];
      }
    }
  } catch (err) {
    if (!isCurrentEntityRequest(requestId, page)) return;
    entityRows.value = [];
    entityError.value = err instanceof Error ? err.message : `Unable to load ${page.label.toLowerCase()}`;
  } finally {
    if (isCurrentEntityRequest(requestId, page)) {
      entityLoading.value = false;
    }
  }
}

async function loadConversationMessages(conversationId: string) {
  const requestId = ++conversationMessageRequestId;
  if (!conversationId) {
    conversationMessages.value = [];
    return;
  }
  conversationMessageLoading.value = true;
  entityError.value = '';
  try {
    const body = await api<{ mode: string; messages: ConversationMessage[] }>(
      `/patients/arora/conversations/${encodeURIComponent(conversationId)}/messages`,
    );
    if (requestId !== conversationMessageRequestId || selectedConversationId.value !== conversationId) return;
    conversationMessages.value = body.messages;
  } catch (err) {
    if (requestId !== conversationMessageRequestId || selectedConversationId.value !== conversationId) return;
    entityError.value = err instanceof Error ? err.message : 'Unable to load conversation messages';
  } finally {
    if (requestId === conversationMessageRequestId) {
      conversationMessageLoading.value = false;
    }
  }
}

async function selectConversation(conversation: Conversation) {
  selectedConversationId.value = conversation.conversationId;
  await loadConversationMessages(conversation.conversationId);
}

async function createConversation() {
  savingConversation.value = true;
  entityError.value = '';
  conversationNotice.value = '';
  try {
    const body = await api<{ mode: string; conversation: Conversation }>('/patients/arora/conversations', {
      method: 'POST',
      body: JSON.stringify({
        text: conversationDraft.text.trim(),
        attachment_ids: (await uploadDraftAttachments(normalizeFiles(conversationDraft.files)))
          .map((attachment) => attachment.id)
          .filter(Boolean),
      }),
    });
    selectedConversationId.value = body.conversation.conversationId;
    conversationDraft.text = '';
    conversationDraft.files = [];
    await loadCurrentEntityPage();
    conversationNotice.value = 'Conversation started.';
  } catch (err) {
    entityError.value = err instanceof Error ? err.message : 'Unable to start conversation';
  } finally {
    savingConversation.value = false;
  }
}

async function sendConversationMessage() {
  if (!selectedConversationId.value) return;
  savingConversation.value = true;
  entityError.value = '';
  conversationNotice.value = '';
  try {
    const body = await api<{ mode: string; conversation: Conversation; message: ConversationMessage }>(
      `/patients/arora/conversations/${encodeURIComponent(selectedConversationId.value)}/messages`,
      {
        method: 'POST',
        body: JSON.stringify({
          text: conversationMessageDraft.text.trim(),
          attachment_ids: (await uploadDraftAttachments(normalizeFiles(conversationMessageDraft.files)))
            .map((attachment) => attachment.id)
            .filter(Boolean),
        }),
      },
    );
    entityRows.value = conversationRows.value.map((conversation) => (
      conversation.conversationId === body.conversation.conversationId ? body.conversation : conversation
    ));
    conversationMessages.value = [...conversationMessages.value, body.message];
    conversationMessageDraft.text = '';
    conversationMessageDraft.files = [];
    conversationNotice.value = 'Message sent.';
  } catch (err) {
    entityError.value = err instanceof Error ? err.message : 'Unable to send message';
  } finally {
    savingConversation.value = false;
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
    await loadPatientProducts();
    await loadMedicationShipments();
    await loadCurrentEntityPage();
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
    await loadPatientProducts();
    await loadMedicationShipments();
    await loadCurrentEntityPage();
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to log in';
  } finally {
    loading.value = false;
  }
}

function signOut() {
  token.value = '';
  patient.value = null;
  aroraProducts.value = [];
  selectedProductId.value = '';
  entityRows.value = [];
  currentPath.value = '/';
  resetShipmentFeedback();
  localStorage.removeItem(tokenKey);
  window.history.pushState({}, '', withClinicHost('/'));
}

async function requestMedicationShipment() {
  if (!selectedProduct.value) {
    error.value = 'Select a product before placing an order.';
    return;
  }

  loading.value = true;
  error.value = '';
  shipmentMessage.value = '';
  try {
    const body = await api<{ medicationShipment: MedicationShipment }>('/patients/medication-shipments', {
      method: 'POST',
      body: JSON.stringify({
        client_product_id: selectedProduct.value.clientProductId,
        amount: selectedProduct.value.customerPrice.toFixed(2),
      }),
    });
    medicationShipment.value = body.medicationShipment;
    medicationShipments.value = [body.medicationShipment, ...medicationShipments.value];
    await loadCurrentEntityPage();
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
  window.addEventListener('popstate', handlePopstate);
  await loadContext();
  await restoreSession();
  await loadCurrentEntityPage();
});

onUnmounted(() => {
  window.removeEventListener('popstate', handlePopstate);
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
                  Sign in to view the product catalog your clinic has made available through Nexus.
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
              <div class="label mb-3">{{ isDashboard ? 'Dashboard' : 'Arora API' }}</div>
              <h1 class="serif text-h3 mb-2">
                {{ isDashboard ? `Hi, ${patient.name}.` : currentEntityPage?.title }}
              </h1>
              <div class="text-medium-emphasis">{{ partnerLabel }} · {{ patient.email }}</div>
            </div>
          </div>

          <div class="entity-nav mb-6">
            <v-btn
              v-for="item in appNavItems"
              :key="item.key"
              :active="item.path === '/' ? isDashboard : currentPath === item.path"
              :prepend-icon="item.icon"
              size="small"
              variant="tonal"
              @click="navigateTo(item.path)"
            >
              {{ item.label }}
            </v-btn>
          </div>

          <template v-if="isDashboard">
          <v-row>
            <v-col cols="12" md="4">
              <v-card class="nexus-card pa-5 h-100">
                <div class="label mb-3">Account</div>
                <div class="serif text-h5 mb-2">{{ patient.name }}</div>
                <div class="text-body-2 text-medium-emphasis">{{ patient.email }}</div>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card class="nexus-card pa-5 h-100">
                <div class="label mb-3">Clinic domain</div>
                <div class="serif text-h5 mb-2">{{ clinicDomainLabel }}</div>
                <div class="text-body-2 text-medium-emphasis">Resolved by the API before account creation.</div>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card class="nexus-card pa-5 h-100">
                <div class="label mb-3">Orders</div>
                <div class="serif text-h5 mb-2">{{ medicationShipments.length }}</div>
                <div class="text-body-2 text-medium-emphasis">Medication shipment records returned for this patient.</div>
              </v-card>
            </v-col>
          </v-row>

          <v-row class="mt-2">
            <v-col cols="12" md="8">
              <v-card class="nexus-card pa-5">
                <div class="label mb-3">Medication shipment</div>
                <div class="serif text-h5 mb-2">Place order</div>
                <div class="text-body-2 text-medium-emphasis mb-5">
                  Select a patient-visible product from the mock Arora catalog before creating an order.
                </div>

                <v-alert v-if="!productLoading && aroraProducts.length === 0" class="mb-5" type="warning" variant="tonal">
                  No active patient-visible Arora products are available. Add one in the Admin product catalog.
                </v-alert>

                <v-select
                  v-model="selectedProductId"
                  class="mb-2"
                  :items="productItems"
                  item-title="title"
                  item-value="value"
                  label="Product"
                  :loading="productLoading"
                  :disabled="productLoading || aroraProducts.length === 0"
                  persistent-hint
                  hint="Only active products marked visible to patients are shown."
                />

                <div v-if="selectedProduct" class="selected-product mb-5">
                  <div class="d-flex flex-column flex-sm-row align-sm-center ga-2">
                    <div>
                      <div class="text-subtitle-1 font-weight-bold">{{ selectedProduct.displayName }}</div>
                      <div class="text-body-2 text-medium-emphasis">
                        {{ selectedProduct.displayDescription || selectedProduct.description || selectedProduct.clientProductId }}
                      </div>
                    </div>
                    <v-spacer />
                    <v-chip color="primary" variant="tonal">{{ formatCurrency(selectedProduct.customerPrice) }}</v-chip>
                  </div>
                  <div class="product-meta mt-3">
                    <v-chip size="small" variant="tonal">{{ selectedProduct.clientProductId }}</v-chip>
                    <v-chip size="small" variant="tonal">{{ selectedProduct.itemType === 'package' ? 'Package' : 'Product' }}</v-chip>
                    <v-chip v-if="selectedProduct.itemType === 'package'" size="small" variant="tonal">
                      {{ selectedProduct.includedProducts.length }} included
                    </v-chip>
                  </div>
                </div>

                <v-btn
                  color="primary"
                  prepend-icon="mdi-cart-check"
                  :disabled="!selectedProduct"
                  :loading="loading"
                  @click="requestMedicationShipment"
                >
                  Place order
                </v-btn>
                <v-btn class="ml-sm-3 mt-3 mt-sm-0" prepend-icon="mdi-refresh" variant="text" @click="loadPatientProducts">
                  Refresh products
                </v-btn>
                <v-btn class="ml-sm-3 mt-3 mt-sm-0" prepend-icon="mdi-history" variant="text" @click="loadMedicationShipments">
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

          <template v-else-if="currentEntityPage?.key === 'conversations'">
            <v-row align="start">
              <v-col cols="12" lg="4">
                <v-card class="nexus-card pa-5 mb-5">
                  <div class="label mb-3">Start conversation</div>
                  <v-form @submit.prevent="createConversation">
                    <v-textarea
                      v-model="conversationDraft.text"
                      auto-grow
                      label="Message"
                      rows="4"
                      variant="outlined"
                    />
                    <v-file-input
                      v-model="conversationDraft.files"
                      accept="image/*,application/pdf"
                      chips
                      counter
                      multiple
                      prepend-icon="mdi-paperclip"
                      label="Attachments"
                      variant="outlined"
                    />
                    <v-btn color="primary" :loading="savingConversation" prepend-icon="mdi-message-plus-outline" type="submit">
                      Start conversation
                    </v-btn>
                  </v-form>
                </v-card>

                <v-card class="nexus-card pa-5">
                  <div class="d-flex align-center ga-3 mb-4">
                    <v-icon color="primary" icon="mdi-forum-outline" />
                    <div>
                      <div class="label mb-1">Threads</div>
                      <div class="text-body-2 text-medium-emphasis">{{ conversationRows.length }} conversations</div>
                    </div>
                  </div>
                  <div class="conversation-list">
                    <button
                      v-for="conversation in conversationRows"
                      :key="conversation.conversationId"
                      class="conversation-row"
                      :class="{ 'is-selected': conversation.conversationId === selectedConversationId }"
                      type="button"
                      @click="selectConversation(conversation)"
                    >
                      <div class="conversation-title">
                        <strong>{{ formatConversationTitle(conversation) }}</strong>
                        <v-chip size="x-small" variant="tonal">{{ conversation.status }}</v-chip>
                      </div>
                      <div class="text-body-2 text-medium-emphasis">
                        {{ conversation.lastMessageText || 'No messages yet' }}
                      </div>
                      <div class="conversation-meta mt-2">
                        <v-chip size="small" variant="tonal">{{ conversation.messageCount }} messages</v-chip>
                        <span>{{ formatTimestamp(conversation.lastMessageAt || conversation.updatedAt) }}</span>
                      </div>
                    </button>
                  </div>
                  <v-empty-state
                    v-if="!entityLoading && conversationRows.length === 0"
                    icon="mdi-message-text-outline"
                    title="No conversations yet"
                    text="Start a conversation with your care team."
                  />
                </v-card>
              </v-col>

              <v-col cols="12" lg="8">
                <v-card class="nexus-card pa-5">
                  <div class="d-flex flex-column flex-sm-row align-sm-center ga-3 mb-5">
                    <div>
                      <div class="label mb-2">{{ selectedConversation?.status || 'Messages' }}</div>
                      <div class="serif text-h5">{{ selectedConversationTitle }}</div>
                      <div v-if="selectedConversation?.escalatedAt" class="text-body-2 text-medium-emphasis">
                        Escalated {{ formatTimestamp(selectedConversation.escalatedAt) }}
                      </div>
                    </div>
                    <v-spacer />
                    <v-btn color="primary" prepend-icon="mdi-refresh" :loading="entityLoading" variant="tonal" @click="loadCurrentEntityPage">
                      Refresh
                    </v-btn>
                  </div>

                  <v-alert v-if="conversationNotice" class="mb-5" type="success" variant="tonal">
                    {{ conversationNotice }}
                  </v-alert>
                  <v-alert v-if="entityError" class="mb-5" type="error" variant="tonal">
                    {{ entityError }}
                  </v-alert>

                  <div v-if="selectedConversation" class="message-list mb-5">
                    <div
                      v-for="message in conversationMessages"
                      :key="message.messageId"
                      class="message-row"
                      :class="message.author === 'patient' ? 'is-patient' : 'is-client'"
                    >
                      <div class="d-flex justify-space-between ga-3 mb-1">
                        <strong>{{ message.senderName }}</strong>
                        <span class="text-caption text-medium-emphasis">{{ formatTimestamp(message.createdAt) }}</span>
                      </div>
                      <div>{{ message.text }}</div>
                      <div v-if="message.attachments.length" class="attachment-list mt-3">
                        <v-chip
                          v-for="attachment in message.attachments"
                          :key="attachment.url"
                          size="small"
                          prepend-icon="mdi-paperclip"
                          variant="tonal"
                          @click="openAttachment(attachment)"
                        >
                          {{ attachment.name || attachment.url }}
                          <span v-if="attachment.size" class="attachment-size">{{ formatFileSize(attachment.size) }}</span>
                        </v-chip>
                      </div>
                    </div>
                    <v-progress-linear v-if="conversationMessageLoading" color="primary" indeterminate />
                  </div>

                  <v-form v-if="selectedConversation" @submit.prevent="sendConversationMessage">
                    <v-textarea
                      v-model="conversationMessageDraft.text"
                      auto-grow
                      label="Message"
                      rows="3"
                      variant="outlined"
                    />
                    <v-file-input
                      v-model="conversationMessageDraft.files"
                      accept="image/*,application/pdf"
                      chips
                      counter
                      multiple
                      prepend-icon="mdi-paperclip"
                      label="Attachments"
                      variant="outlined"
                    />
                    <v-btn color="primary" :loading="savingConversation" prepend-icon="mdi-send" type="submit">
                      Send message
                    </v-btn>
                  </v-form>

                  <v-empty-state
                    v-if="!selectedConversation"
                    icon="mdi-message-reply-text-outline"
                    title="No thread selected"
                    text="Choose or start a conversation."
                  />
                </v-card>
              </v-col>
            </v-row>
          </template>

          <template v-else-if="currentEntityPage">
            <v-card class="nexus-card pa-5">
              <div class="d-flex flex-column flex-sm-row align-sm-center ga-3 mb-5">
                <div>
                  <div class="label mb-2">{{ currentEntityPage.label }}</div>
                  <div class="text-body-2 text-medium-emphasis">{{ currentEntityPage.description }}</div>
                </div>
                <v-spacer />
                <v-btn
                  color="primary"
                  prepend-icon="mdi-refresh"
                  :loading="entityLoading"
                  variant="tonal"
                  @click="loadCurrentEntityPage"
                >
                  Refresh
                </v-btn>
              </div>

              <v-alert v-if="entityError" class="mb-5" type="error" variant="tonal">
                {{ entityError }}
              </v-alert>

              <v-table class="entity-table">
                <thead>
                  <tr>
                    <th v-for="column in currentEntityPage.columns" :key="column.key">
                      {{ column.title }}
                    </th>
                    <th v-if="currentEntityPage.key === 'orders'">Forms</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in entityRows" :key="String(row.orderId ?? row.clientProductId ?? row.id ?? row.formKey ?? row.paymentId ?? row.prescriptionId ?? row.visitId ?? row.conversationId)">
                    <td v-for="column in currentEntityPage.columns" :key="column.key">
                      <v-chip
                        v-if="column.type === 'status'"
                        size="small"
                        variant="tonal"
                      >
                        {{ formatCell(row, column) }}
                      </v-chip>
                      <span v-else>{{ formatCell(row, column) }}</span>
                    </td>
                    <td v-if="currentEntityPage.key === 'orders'">
                      <v-btn
                        size="small"
                        prepend-icon="mdi-form-select"
                        variant="text"
                        @click="navigateTo(`/orders/${encodeURIComponent(String(row.orderId))}/forms`)"
                      >
                        Forms
                      </v-btn>
                    </td>
                  </tr>
                </tbody>
              </v-table>

              <v-empty-state
                v-if="!entityLoading && entityRows.length === 0"
                icon="mdi-database-search-outline"
                :title="`No ${currentEntityPage.label.toLowerCase()} yet`"
                text="This page is wired to the backend and ready for the next Arora-backed implementation step."
              />
            </v-card>
          </template>

          <template v-else>
            <v-card class="nexus-card pa-6">
              <div class="label mb-3">Not found</div>
              <div class="serif text-h4 mb-2">That Nexus page does not exist.</div>
              <v-btn color="primary" prepend-icon="mdi-view-dashboard-outline" @click="navigateTo('/')">
                Back to dashboard
              </v-btn>
            </v-card>
          </template>
        </template>
      </v-container>
    </v-main>
  </v-app>
</template>
