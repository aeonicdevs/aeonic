<script setup lang="ts">
import { marketingPages } from '~/data/marketingPages'

const page = marketingPages.partners
</script>

<template>
  <MarketingPage :page="page" />
</template>
