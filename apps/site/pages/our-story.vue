<script setup lang="ts">
import { marketingPages } from '~/data/marketingPages'

const page = marketingPages['our-story']
</script>

<template>
  <MarketingPage :page="page" />
</template>
