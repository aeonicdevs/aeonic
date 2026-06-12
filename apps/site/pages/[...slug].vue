<script setup lang="ts">
import { mockPages } from '~/data/mockPages'

const route = useRoute()

const slug = computed(() => {
  const value = route.params.slug
  return Array.isArray(value) ? value.join('/') : String(value || '')
})

const pageSource = computed(() => mockPages[slug.value.replace(/\/$/, '').replace(/\.html$/, '')])

if (import.meta.server && !pageSource.value) {
  throw createError({
    statusCode: 404,
    statusMessage: 'Mockup page not found'
  })
}
</script>

<template>
  <MockHtmlPage v-if="pageSource" :source="pageSource" />
</template>
