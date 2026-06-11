<script setup lang="ts">
import { marketingPages } from '~/data/marketingPages'

const page = marketingPages.nexus
</script>

<template>
  <MarketingPage :page="page" />
</template>
