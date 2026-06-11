<script setup lang="ts">
import { legacyAliases, marketingPages } from '~/data/marketingPages'

const route = useRoute()

const rawSlug = computed(() => {
  const value = route.params.slug
  return Array.isArray(value) ? value.join('/') : String(value || '')
})

const normalizedSlug = computed(() => rawSlug.value.replace(/\/$/, '').replace(/\.html$/, ''))
const targetKey = computed(() => legacyAliases[normalizedSlug.value] || normalizedSlug.value)
const page = computed(() => marketingPages[targetKey.value])

const generatedTitle = computed(() =>
  normalizedSlug.value
    .split(/[/-]/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
)

const formKind = computed(() => {
  if (targetKey.value === 'partner-login') return 'partner-login'
  if (targetKey.value === 'member-login') return 'member-login'
  if (targetKey.value === 'inquiry') return 'inquiry'
  return null
})

useSeoMeta({
  title: () => page.value?.title || generatedTitle.value || 'Page',
  description: () => page.value?.lead || 'Aeonic Health Systems'
})
</script>

<template>
  <MarketingPage v-if="page" :page="page" />
  <FormPage v-else-if="formKind" :kind="formKind" />

  <div v-else>
    <SiteNav />
    <main class="placeholder-page">
      <div class="container">
        <span class="eyebrow">In progress</span>
        <h1>{{ generatedTitle }}</h1>
        <p>This page is queued for the structured Nuxt rebuild from the client reference material.</p>
        <NuxtLink class="btn btn--primary" to="/">Back to the system overview</NuxtLink>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>
