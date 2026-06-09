export type Workspace = {
  id: string;
  name: string;
  scope: string;
  initials: string;
  tier: 'Build' | 'Connect' | 'Grow';
};

export type NavItem = {
  id: string;
  label: string;
  icon: string;
  badge?: string;
};

export const workspaces: Workspace[] = [
  { id: 'downtown', name: 'Downtown Clinic', scope: 'Hybrid prescribing', initials: 'DC', tier: 'Connect' },
  { id: 'acme', name: 'Acme Wellness Partners', scope: '4 clinics', initials: 'AW', tier: 'Grow' },
  { id: 'platform', name: 'Aeonic Operations', scope: 'Platform admin', initials: 'AO', tier: 'Grow' },
];

export const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: 'mdi-view-dashboard-outline' },
  { id: 'patients', label: 'Patients', icon: 'mdi-account-heart-outline', badge: '486' },
  { id: 'protocols', label: 'Protocols', icon: 'mdi-file-document-outline' },
  { id: 'academy', label: 'Academy', icon: 'mdi-school-outline', badge: '6' },
  { id: 'connect', label: 'Integrations', icon: 'mdi-connection' },
  { id: 'billing', label: 'Billing', icon: 'mdi-credit-card-outline' },
  { id: 'builder', label: 'AEVA Builder', icon: 'mdi-auto-fix' },
];

export const kpis = [
  { label: 'Active members', value: '486', detail: '+22 this month', icon: 'mdi-account-group-outline' },
  { label: 'Revenue MTD', value: '$214k', detail: '+11% month over month', icon: 'mdi-chart-line' },
  { label: 'Active protocols', value: '8', detail: '2 due for review', icon: 'mdi-clipboard-pulse-outline' },
  { label: 'Avg engagement', value: '68%', detail: 'From patient app activity', icon: 'mdi-heart-pulse' },
];

export const attentionItems = [
  { title: '4 scripts to review', detail: 'Prescribing queue has pending approvals', icon: 'mdi-prescription' },
  { title: '2 protocols need updates', detail: 'Semaglutide and recovery plans', icon: 'mdi-alert-circle-outline' },
  { title: '3 members need outreach', detail: 'AEVA flagged adherence changes', icon: 'mdi-message-alert-outline' },
];

export const onboardingSteps = [
  { title: 'Welcome & account setup', detail: 'Confirm account and set password', done: true },
  { title: 'Complete clinic profile', detail: 'Locations, services, and team', done: true },
  { title: 'Connect clinical backend', detail: 'Reflect data into Nexus', done: true },
  { title: 'Review core protocols', detail: 'Approve baseline care pathways', done: false },
  { title: 'Invite providers', detail: 'Add clinicians and support staff', done: false },
];

export const protocols = [
  { name: 'Semaglutide Weight Loss', version: 'v3.2', category: 'Weight', members: 148, status: 'Review due' },
  { name: 'Testosterone Optimization', version: 'v2.4', category: 'Hormones', members: 96, status: 'Current' },
  { name: 'BPC-157 Recovery', version: 'v1.8', category: 'Peptides', members: 34, status: 'Current' },
  { name: 'Sleep Restoration Stack', version: 'v1.3', category: 'Sleep', members: 58, status: 'Draft update' },
];

export const courses = [
  { title: 'Foundations of Protocol Design', type: 'Masterclass', duration: '48 min', progress: 35 },
  { title: 'Clinical Protocol Foundations', type: 'Core', duration: '9 lessons', progress: 45 },
  { title: 'Compliance & Documentation', type: 'Required', duration: '5 lessons', progress: 20 },
  { title: 'Supplement Stacking 101', type: 'Video', duration: '22 min', progress: 0 },
];

export const patients = [
  { name: 'Maya Chen', program: 'Semaglutide', adherence: '97%', status: 'On track', last: 'Today' },
  { name: 'Devin Park', program: 'Recovery peptide', adherence: '82%', status: 'Needs review', last: 'Yesterday' },
  { name: 'Tom Reed', program: 'Hormone optimization', adherence: '88%', status: 'Labs due', last: '2 days ago' },
  { name: 'Sara Lopez', program: 'Maintenance taper', adherence: '94%', status: 'On track', last: 'Today' },
];

export const integrations = [
  { name: 'Clinical platform', category: 'EMR', status: 'Connected', color: '#0f9d8e' },
  { name: 'GoHighLevel', category: 'CRM', status: 'Reflecting leads', color: '#3a5a86' },
  { name: 'Stripe', category: 'Payments', status: 'Connected', color: '#635bff' },
  { name: 'Quest / LabCorp', category: 'Labs', status: 'Available', color: '#b9743a' },
  { name: 'Pharmacy network', category: 'Fulfillment', status: 'Connected', color: '#2f8f6b' },
  { name: 'Analytics', category: 'Reporting', status: 'Demo data', color: '#7b5ea7' },
];

export const builderSteps = [
  'Package basics',
  'Titration',
  'Safety checks',
  'Labs guidance',
  'Pricing & activation',
  'Clinician sign-off',
];
