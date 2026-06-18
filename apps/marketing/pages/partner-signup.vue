<script setup lang="ts">
const config = useRuntimeConfig()
const partnerAppUrl = config.public.partnerAppUrl

useSeoMeta({
  title: 'Create Partner Account',
  description: 'Create an Aeonic Partner account.'
})
</script>

<template>
  <main class="bridge">
    <section class="bridge__inner">
      <div class="bridge__eyebrow">Partner onboarding</div>
      <h1>Create your clinic account.</h1>
      <p>The Partner app handles account creation and the first domain setting for the patient-facing Nexus app.</p>
      <div class="bridge__actions">
        <a class="bridge__primary" :href="partnerAppUrl">Start onboarding</a>
        <NuxtLink class="bridge__secondary" to="/partner-login">Log in instead</NuxtLink>
      </div>
    </section>
  </main>
</template>

<style scoped>
.bridge {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px;
  background: #f7f5ef;
  color: #171512;
  font-family: 'Hanken Grotesk', ui-sans-serif, system-ui, sans-serif;
}

.bridge__inner {
  width: min(100%, 760px);
}

.bridge__eyebrow {
  margin-bottom: 18px;
  color: #63706a;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  max-width: 680px;
  margin: 0;
  font-family: Georgia, serif;
  font-size: clamp(42px, 7vw, 72px);
  font-weight: 500;
  line-height: 0.98;
}

p {
  max-width: 560px;
  margin: 24px 0 0;
  color: #63706a;
  font-size: 18px;
  line-height: 1.55;
}

.bridge__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 32px;
}

.bridge__primary,
.bridge__secondary {
  min-height: 46px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  padding: 0 18px;
  font-weight: 700;
  text-decoration: none;
}

.bridge__primary {
  background: #0f8f83;
  color: #101411;
}

.bridge__secondary {
  border: 1px solid #d8d1c4;
  color: #171512;
}
</style>
