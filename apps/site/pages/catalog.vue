<script setup lang="ts">
import { marketingPages } from '~/data/marketingPages'

const page = marketingPages.catalog
</script>

<template>
  <MarketingPage :page="page" />
</template>
