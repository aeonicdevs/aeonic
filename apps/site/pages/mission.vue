<script setup lang="ts">
import { marketingPages } from '~/data/marketingPages'

const page = marketingPages.mission
</script>

<template>
  <MarketingPage :page="page" />
</template>
