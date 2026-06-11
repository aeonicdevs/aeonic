<script setup lang="ts">
type FormKind = 'partner-login' | 'member-login' | 'inquiry' | 'contact'

const props = defineProps<{
  kind: FormKind
}>()

const submitted = ref(false)

const isLogin = computed(() => props.kind === 'partner-login' || props.kind === 'member-login')

const formTitle = computed(() => {
  if (props.kind === 'partner-login') return 'Sign in to your practice.'
  if (props.kind === 'member-login') return 'Welcome back.'
  if (props.kind === 'inquiry') return 'Deploy the entire system in your practice.'
  return 'Let’s talk.'
})

const formLead = computed(() => {
  if (props.kind === 'partner-login') {
    return 'Access your protocols, provider console, Academy, compliance, and program analytics.'
  }
  if (props.kind === 'member-login') {
    return 'Sign in to view your protocol, labs, shipments, and messages from your care team.'
  }
  if (props.kind === 'inquiry') {
    return 'Tell us about your practice and we’ll walk you through the console, protocols, and economics of a white-labeled Aeonic program.'
  }
  return 'Send a note to the Aeonic team and we’ll route it to the right person.'
})

const submitLabel = computed(() => {
  if (isLogin.value) return 'Continue'
  if (props.kind === 'inquiry') return 'Request walkthrough'
  return 'Send message'
})

const successMessage = computed(() => {
  if (isLogin.value) return 'Demo sign-in accepted. Authentication can be wired to the backend from here.'
  if (props.kind === 'inquiry') return 'Thanks. The partnership request flow is ready for backend submission.'
  return 'Thanks. The contact flow is ready for backend submission.'
})

useSeoMeta({
  title: () => formTitle.value,
  description: () => formLead.value
})
</script>

<template>
  <div>
    <SiteNav />

    <main class="form-page">
      <section class="container form-shell">
        <div class="form-shell__copy">
          <span class="eyebrow">{{ isLogin ? 'Secure access' : 'Partnerships' }}</span>
          <h1>{{ formTitle }}</h1>
          <p>{{ formLead }}</p>

          <div class="form-proof">
            <div>
              <strong>{{ isLogin ? 'One console' : '30 minutes' }}</strong>
              <span>{{ isLogin ? 'Protocols, patients, labs, and tasks.' : 'A focused walkthrough of the platform and economics.' }}</span>
            </div>
            <div>
              <strong>{{ isLogin ? 'Role aware' : 'Live in days' }}</strong>
              <span>{{ isLogin ? 'Access designed around clinic responsibilities.' : 'White-labeled setup for qualified partners.' }}</span>
            </div>
          </div>
        </div>

        <form class="aeonic-form" @submit.prevent="submitted = true">
          <div v-if="submitted" class="form-success" role="status">
            {{ successMessage }}
          </div>

          <template v-if="isLogin">
            <label>
              Email
              <input type="email" name="email" autocomplete="email" required placeholder="you@clinic.com" />
            </label>
            <label>
              Password
              <input type="password" name="password" autocomplete="current-password" required placeholder="••••••••" />
            </label>
            <div class="form-row">
              <label class="check-label">
                <input type="checkbox" name="remember" />
                Remember this device
              </label>
              <NuxtLink to="/contact">Need help?</NuxtLink>
            </div>
          </template>

          <template v-else>
            <label>
              Name
              <input name="name" autocomplete="name" required placeholder="Your name" />
            </label>
            <label>
              Work email
              <input type="email" name="email" autocomplete="email" required placeholder="you@clinic.com" />
            </label>
            <label>
              Practice or company
              <input name="company" autocomplete="organization" placeholder="Clinic name" />
            </label>
            <label>
              What are you building?
              <textarea name="message" rows="5" placeholder="Tell us about your clinic, brand, or program goals." />
            </label>
          </template>

          <button class="btn btn--primary" type="submit">{{ submitLabel }}</button>
        </form>
      </section>
    </main>

    <SiteFooter />
  </div>
</template>
