<script setup lang="ts">
const props = defineProps<{
  kind: 'privacy' | 'terms'
}>()

const title = computed(() => (props.kind === 'privacy' ? 'Privacy Policy' : 'Terms of Use'))

useSeoMeta({
  title: () => title.value,
  description: 'Aeonic Health Systems legal information.'
})
</script>

<template>
  <div>
    <SiteNav />

    <main class="content-page legal-page">
      <section class="container legal-page__inner">
        <span class="eyebrow">{{ kind === 'privacy' ? 'Privacy' : 'Terms' }}</span>
        <h1>{{ title }}</h1>
        <p>
          Aeonic Health Systems provides clinical infrastructure and informational materials for qualified partners.
          This Nuxt rebuild keeps the legal route available while final counsel-approved copy is prepared.
        </p>
        <p>
          All clinical decisions and prescriptions are made by licensed providers. This website is informational and
          does not provide medical advice, diagnosis, or treatment.
        </p>
      </section>
    </main>

    <SiteFooter />
  </div>
</template>
