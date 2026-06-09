<script setup lang="ts">
import { computed, ref } from 'vue';
import {
  attentionItems,
  builderSteps,
  courses,
  integrations,
  kpis,
  navItems,
  onboardingSteps,
  patients,
  protocols,
  workspaces,
  type NavItem,
  type Workspace,
} from './data/mock';

const drawer = ref(true);
const activeView = ref('dashboard');
const selectedWorkspace = ref<Workspace>(workspaces[0]);
const search = ref('');
const builderStep = ref(2);
const safetyConfirmed = ref(false);
const routeMode = ref('inhouse');

const pageTitle = computed(() => navItems.find((item) => item.id === activeView.value)?.label ?? 'Dashboard');
const completedSteps = computed(() => onboardingSteps.filter((step) => step.done).length);
const onboardingPercent = computed(() => Math.round((completedSteps.value / onboardingSteps.length) * 100));
const protocolNeedsReview = computed(() => protocols.filter((protocol) => protocol.status !== 'Current').length);

const navGroups: { label: string; items: NavItem[] }[] = [
  { label: 'Operate', items: navItems.slice(0, 3) },
  { label: 'Grow', items: navItems.slice(3, 6) },
  { label: 'Build', items: navItems.slice(6) },
];

const filteredPatients = computed(() => {
  const term = search.value.trim().toLowerCase();
  if (!term) return patients;

  return patients.filter((patient) =>
    [patient.name, patient.program, patient.status].some((value) => value.toLowerCase().includes(term)),
  );
});

const setView = (id: string) => {
  activeView.value = id;
};
</script>

<template>
  <v-app class="nexus-shell">
    <v-navigation-drawer
      v-model="drawer"
      class="app-rail"
      :temporary="$vuetify.display.mdAndDown"
      width="268"
    >
      <div class="pa-5">
        <div class="d-flex align-center ga-3 mb-6">
          <v-avatar color="primary" rounded="lg" size="42">
            <span class="font-weight-bold text-secondary">A</span>
          </v-avatar>
          <div>
            <div class="serif rail-brand text-white text-h6">Aeonic</div>
            <div class="text-caption text-uppercase text-medium-emphasis">Nexus</div>
          </div>
        </div>

        <v-select
          v-model="selectedWorkspace"
          :items="workspaces"
          item-title="name"
          item-value="id"
          return-object
          density="compact"
          variant="solo-filled"
          hide-details
          class="mb-5"
        >
          <template #selection="{ item }">
            <div class="d-flex align-center ga-2">
              <v-avatar color="primary" rounded="lg" size="28">{{ item.raw.initials }}</v-avatar>
              <div class="text-truncate">
                <div class="text-body-2 font-weight-bold">{{ item.raw.name }}</div>
                <div class="text-caption text-medium-emphasis">{{ item.raw.scope }}</div>
              </div>
            </div>
          </template>
          <template #item="{ props, item }">
            <v-list-item v-bind="props" :subtitle="item.raw.scope">
              <template #prepend>
                <v-avatar color="primary" rounded="lg" size="30">{{ item.raw.initials }}</v-avatar>
              </template>
            </v-list-item>
          </template>
        </v-select>

        <div v-for="group in navGroups" :key="group.label" class="mb-5">
          <div class="text-caption text-uppercase text-disabled font-weight-bold px-2 mb-2">{{ group.label }}</div>
          <v-btn
            v-for="item in group.items"
            :key="item.id"
            :active="activeView === item.id"
            :prepend-icon="item.icon"
            class="rail-link mb-1"
            block
            variant="text"
            @click="setView(item.id)"
          >
            <span class="text-none">{{ item.label }}</span>
            <v-spacer />
            <v-chip v-if="item.badge" size="x-small" variant="tonal">{{ item.badge }}</v-chip>
          </v-btn>
        </div>
      </div>
    </v-navigation-drawer>

    <v-app-bar class="topbar" color="rgba(245,243,236,.82)" flat height="76">
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <div class="min-w-0">
        <div class="page-title">{{ pageTitle }}</div>
        <div class="text-caption muted text-truncate">
          {{ selectedWorkspace.name }} · {{ selectedWorkspace.scope }} · {{ selectedWorkspace.tier }} tier
        </div>
      </div>
      <v-spacer />
      <v-text-field
        v-model="search"
        class="d-none d-md-block"
        density="compact"
        prepend-inner-icon="mdi-magnify"
        placeholder="Search patients, protocols, files..."
        hide-details
        max-width="320"
      />
      <v-btn class="ml-3 d-none d-sm-inline-flex" color="primary" prepend-icon="mdi-auto-fix">
        Ask AEVA
      </v-btn>
      <v-btn class="ml-2" icon="mdi-bell-outline" variant="tonal" aria-label="Notifications" />
      <v-avatar class="ml-2" color="secondary" rounded="lg">DR</v-avatar>
    </v-app-bar>

    <v-main>
      <v-container fluid class="pa-4 pa-md-8">
        <section v-show="activeView === 'dashboard'">
          <v-row>
            <v-col v-for="kpi in kpis" :key="kpi.label" cols="12" sm="6" lg="3">
              <v-card class="nexus-card h-100 pa-5">
                <div class="d-flex align-center ga-2 muted text-caption font-weight-bold text-uppercase">
                  <v-icon :icon="kpi.icon" color="primary" />
                  {{ kpi.label }}
                </div>
                <div class="kpi-value mt-4">{{ kpi.value }}</div>
                <div class="text-body-2 muted mt-2">{{ kpi.detail }}</div>
              </v-card>
            </v-col>
          </v-row>

          <v-row class="mt-1">
            <v-col cols="12" lg="8">
              <v-card class="nexus-card">
                <v-card-title class="d-flex align-center">
                  Performance
                  <v-chip class="ml-auto" color="primary" size="small" variant="tonal">Reflected live</v-chip>
                </v-card-title>
                <v-divider />
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="5">
                      <v-row dense>
                        <v-col cols="6">
                          <div class="metric-value">$48.2k</div>
                          <div class="text-caption muted">Revenue · 30d</div>
                        </v-col>
                        <v-col cols="6">
                          <div class="metric-value">312</div>
                          <div class="text-caption muted">Orders</div>
                        </v-col>
                        <v-col cols="6">
                          <div class="metric-value">$154</div>
                          <div class="text-caption muted">Avg order</div>
                        </v-col>
                        <v-col cols="6">
                          <div class="metric-value">+18%</div>
                          <div class="text-caption muted">Prior 30d</div>
                        </v-col>
                      </v-row>
                    </v-col>
                    <v-col cols="12" md="7">
                      <div class="chart-bars">
                        <div
                          v-for="height in [42, 50, 46, 58, 54, 68, 76, 84]"
                          :key="height"
                          class="chart-bar"
                          :style="{ height: `${height}%` }"
                        />
                      </div>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" lg="4">
              <v-card class="nexus-card h-100">
                <v-card-title>Needs Attention</v-card-title>
                <v-divider />
                <v-list lines="two">
                  <v-list-item v-for="item in attentionItems" :key="item.title" :title="item.title" :subtitle="item.detail">
                    <template #prepend>
                      <v-avatar color="primary" variant="tonal" rounded="lg">
                        <v-icon :icon="item.icon" />
                      </v-avatar>
                    </template>
                    <template #append>
                      <v-icon icon="mdi-chevron-right" />
                    </template>
                  </v-list-item>
                </v-list>
              </v-card>
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="6">
              <v-card class="nexus-card h-100">
                <v-card-title class="d-flex align-center">
                  Onboarding
                  <v-chip class="ml-auto" color="primary" size="small" variant="tonal">{{ onboardingPercent }}%</v-chip>
                </v-card-title>
                <v-card-text>
                  <v-progress-linear :model-value="onboardingPercent" color="primary" height="8" rounded />
                  <v-list class="mt-3" lines="two">
                    <v-list-item v-for="step in onboardingSteps" :key="step.title" :title="step.title" :subtitle="step.detail">
                      <template #prepend>
                        <v-icon :color="step.done ? 'primary' : 'grey'" :icon="step.done ? 'mdi-check-circle' : 'mdi-circle-outline'" />
                      </template>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" md="6">
              <v-card class="nexus-card h-100">
                <v-card-title>Patient Engagement</v-card-title>
                <v-card-text>
                  <div class="d-flex ga-4 mb-4">
                    <div class="soft-panel rounded-lg pa-4 flex-1-1">
                      <div class="metric-value">486</div>
                      <div class="text-caption muted">Enrolled members</div>
                    </div>
                    <div class="soft-panel rounded-lg pa-4 flex-1-1">
                      <div class="metric-value">154</div>
                      <div class="text-caption muted">Active today</div>
                    </div>
                  </div>
                  <v-alert color="primary" variant="tonal" icon="mdi-heart-pulse">
                    Top education item: Welcome to your care journey
                  </v-alert>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </section>

        <section v-show="activeView === 'patients'">
          <v-card class="nexus-card">
            <v-card-title class="d-flex align-center">
              Member Panel
              <v-chip class="ml-3" color="primary" variant="tonal">{{ filteredPatients.length }} shown</v-chip>
              <v-spacer />
              <v-btn color="primary" prepend-icon="mdi-account-plus-outline">Add member</v-btn>
            </v-card-title>
            <v-divider />
            <v-table>
              <thead>
                <tr>
                  <th>Member</th>
                  <th>Program</th>
                  <th>Adherence</th>
                  <th>Status</th>
                  <th>Last Activity</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="patient in filteredPatients" :key="patient.name">
                  <td class="font-weight-bold">{{ patient.name }}</td>
                  <td>{{ patient.program }}</td>
                  <td>{{ patient.adherence }}</td>
                  <td>
                    <v-chip
                      class="status-chip"
                      :color="patient.status === 'On track' ? 'success' : patient.status === 'Labs due' ? 'info' : 'warning'"
                      size="small"
                      variant="tonal"
                    >
                      {{ patient.status }}
                    </v-chip>
                  </td>
                  <td>{{ patient.last }}</td>
                </tr>
              </tbody>
            </v-table>
          </v-card>
        </section>

        <section v-show="activeView === 'protocols'">
          <v-alert class="mb-4" color="primary" variant="tonal" icon="mdi-shield-check-outline">
            Clinical-data reflection and protocol uploads need backend authorization, audit logging, and file processing before production.
          </v-alert>
          <v-row>
            <v-col v-for="protocol in protocols" :key="protocol.name" cols="12" md="6" xl="3">
              <v-card class="nexus-card h-100 pa-5">
                <div class="d-flex align-start ga-3">
                  <v-avatar color="primary" variant="tonal" rounded="lg">
                    <v-icon icon="mdi-file-document-outline" />
                  </v-avatar>
                  <div class="min-w-0">
                    <div class="font-weight-bold text-body-1">{{ protocol.name }}</div>
                    <div class="text-caption muted">{{ protocol.category }} · {{ protocol.version }}</div>
                  </div>
                </div>
                <v-divider class="my-4" />
                <div class="d-flex align-center">
                  <span class="muted">Members on protocol</span>
                  <strong class="ml-auto">{{ protocol.members }}</strong>
                </div>
                <v-chip
                  class="mt-4 status-chip"
                  :color="protocol.status === 'Current' ? 'success' : 'warning'"
                  variant="tonal"
                >
                  {{ protocol.status }}
                </v-chip>
              </v-card>
            </v-col>
          </v-row>
        </section>

        <section v-show="activeView === 'academy'">
          <v-card class="nexus-card mb-4 overflow-hidden">
            <div class="pa-6 pa-md-8 text-white" style="background: linear-gradient(135deg, #201c13, #0f9d8e)">
              <div class="text-caption text-uppercase font-weight-bold">Academy</div>
              <h2 class="serif text-h4 mt-2">Keep providers aligned to the Aeonic standard.</h2>
              <p class="mt-3 mb-0" style="max-width: 760px">
                Courses, certifications, reading, and protocol training from the reference can map cleanly to Vuetify tabs and cards.
              </p>
            </div>
          </v-card>
          <v-row>
            <v-col v-for="course in courses" :key="course.title" cols="12" md="6" xl="3">
              <v-card class="nexus-card h-100 pa-5">
                <v-chip color="primary" size="small" variant="tonal">{{ course.type }}</v-chip>
                <div class="font-weight-bold text-body-1 mt-4">{{ course.title }}</div>
                <div class="text-caption muted mt-1">{{ course.duration }}</div>
                <v-progress-linear class="mt-5" :model-value="course.progress" color="primary" height="8" rounded />
                <div class="text-caption muted mt-2">{{ course.progress }}% complete</div>
              </v-card>
            </v-col>
          </v-row>
        </section>

        <section v-show="activeView === 'connect'">
          <v-row>
            <v-col v-for="integration in integrations" :key="integration.name" cols="12" sm="6" lg="4">
              <v-card class="nexus-card h-100 pa-5">
                <div class="d-flex align-center ga-3">
                  <v-avatar :style="{ background: integration.color }" rounded="lg">
                    <v-icon color="white" icon="mdi-connection" />
                  </v-avatar>
                  <div>
                    <div class="font-weight-bold">{{ integration.name }}</div>
                    <div class="text-caption muted">{{ integration.category }}</div>
                  </div>
                  <v-chip class="ml-auto status-chip" color="success" size="small" variant="tonal">{{ integration.status }}</v-chip>
                </div>
              </v-card>
            </v-col>
          </v-row>
        </section>

        <section v-show="activeView === 'billing'">
          <v-row>
            <v-col cols="12" md="5">
              <v-card class="nexus-card pa-6 h-100">
                <div class="text-caption muted text-uppercase font-weight-bold">Current Plan</div>
                <div class="serif text-h4 mt-2">{{ selectedWorkspace.tier }}</div>
                <p class="muted mt-3">Portal, Academy, integrations, protocol library, and billing workflows from the reference are represented here as starter surfaces.</p>
                <v-btn color="primary" prepend-icon="mdi-credit-card-outline">Manage billing</v-btn>
              </v-card>
            </v-col>
            <v-col cols="12" md="7">
              <v-card class="nexus-card">
                <v-card-title>Monthly Snapshot</v-card-title>
                <v-divider />
                <v-list lines="one">
                  <v-list-item title="Membership MRR" subtitle="Recurring member subscriptions">
                    <template #append><strong>$42.1k</strong></template>
                  </v-list-item>
                  <v-list-item title="Program revenue" subtitle="Cash-pay packages and visits">
                    <template #append><strong>$126k</strong></template>
                  </v-list-item>
                  <v-list-item title="Store orders" subtitle="Supplements and care bundles">
                    <template #append><strong>$45.9k</strong></template>
                  </v-list-item>
                </v-list>
              </v-card>
            </v-col>
          </v-row>
        </section>

        <section v-show="activeView === 'builder'">
          <v-row>
            <v-col cols="12" lg="4">
              <v-card class="nexus-card pa-4">
                <v-list>
                  <v-list-item
                    v-for="(step, index) in builderSteps"
                    :key="step"
                    :class="['builder-step rounded-lg mb-2', { 'is-active': builderStep === index, 'is-done': builderStep > index }]"
                    :title="step"
                    @click="builderStep = index"
                  >
                    <template #prepend>
                      <v-avatar :color="builderStep > index ? 'primary' : undefined" rounded="circle" size="28">
                        <v-icon v-if="builderStep > index" icon="mdi-check" size="16" />
                        <span v-else class="text-caption">{{ index + 1 }}</span>
                      </v-avatar>
                    </template>
                  </v-list-item>
                </v-list>
              </v-card>
            </v-col>
            <v-col cols="12" lg="8">
              <v-card class="nexus-card">
                <v-card-title>{{ builderSteps[builderStep] }}</v-card-title>
                <v-divider />
                <v-card-text>
                  <template v-if="builderStep === 2">
                    <v-alert color="warning" variant="tonal" icon="mdi-alert-outline" title="ICD chart diagnosis required">
                      Confirm diagnosis and contraindication checks before this protocol can activate.
                    </v-alert>
                    <v-checkbox
                      v-model="safetyConfirmed"
                      color="primary"
                      label="ICD diagnosis and safety checks confirmed"
                    />
                  </template>
                  <template v-else-if="builderStep === 4">
                    <v-radio-group v-model="routeMode" color="primary" label="Activation route">
                      <v-radio label="In-house · Dr. Lacey Hart" value="inhouse" />
                      <v-radio label="Route to Aeonic network" value="network" />
                    </v-radio-group>
                    <v-alert color="primary" variant="tonal">
                      Pricing, fulfillment, prescribing rules, and nationwide routing should come from backend policy configuration.
                    </v-alert>
                  </template>
                  <template v-else>
                    <v-alert color="primary" variant="tonal" icon="mdi-auto-fix">
                      This starter represents the wizard structure. The original reference includes richer domain-specific copy and validation per step.
                    </v-alert>
                  </template>
                </v-card-text>
                <v-divider />
                <v-card-actions class="pa-4">
                  <v-btn :disabled="builderStep === 0" variant="tonal" @click="builderStep--">Back</v-btn>
                  <v-spacer />
                  <v-btn
                    color="primary"
                    :disabled="builderStep === 2 && !safetyConfirmed"
                    @click="builderStep = Math.min(builderStep + 1, builderSteps.length - 1)"
                  >
                    Continue
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </section>
      </v-container>
    </v-main>
  </v-app>
</template>
