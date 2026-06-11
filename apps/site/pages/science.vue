<script setup lang="ts">
import { marketingPages } from '~/data/marketingPages'

const page = marketingPages.science
</script>

<template>
  <MarketingPage :page="page" />
</template>
