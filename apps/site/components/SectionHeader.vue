<script setup lang="ts">
defineProps<{
  eyebrow: string
  title: string
  lead?: string
}>()
</script>

<template>
  <div class="section-header">
    <span class="eyebrow">{{ eyebrow }}</span>
    <h2 v-html="title" />
    <p v-if="lead">{{ lead }}</p>
  </div>
</template>
