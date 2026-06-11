<script setup lang="ts">
import { marketingPages } from '~/data/marketingPages'

const page = marketingPages.treatments
</script>

<template>
  <MarketingPage :page="page" />
</template>
