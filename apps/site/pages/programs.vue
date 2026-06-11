<script setup lang="ts">
import { marketingPages } from '~/data/marketingPages'

const page = marketingPages.programs
</script>

<template>
  <MarketingPage :page="page" />
</template>
