<script setup lang="ts">
const route = useRoute()
const slug = computed(() => {
  const value = route.params.slug
  return Array.isArray(value) ? value.join(' / ') : String(value || '')
})

const title = computed(() =>
  slug.value
    .split(/[/-]/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
)

useSeoMeta({
  title: () => title.value || 'Page',
  description: 'This Aeonic marketing page is being rebuilt from the client reference material.'
})
</script>

<template>
  <div>
    <SiteNav />
    <main class="placeholder-page">
      <div class="container">
        <span class="eyebrow">In progress</span>
        <h1>{{ title }}</h1>
        <p>This page is queued for the structured Nuxt rebuild from the client reference material.</p>
        <NuxtLink class="btn btn--primary" to="/">Back to the system overview</NuxtLink>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>
