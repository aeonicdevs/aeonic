<script setup lang="ts">
import { marketingPages } from '~/data/marketingPages'

const page = marketingPages['dr-lacey']
</script>

<template>
  <MarketingPage :page="page" />
</template>
