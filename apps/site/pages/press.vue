<script setup lang="ts">
import { marketingPages } from '~/data/marketingPages'

const page = marketingPages.press
</script>

<template>
  <MarketingPage :page="page" />
</template>
