<script setup lang="ts">
import type { MarketingPageData } from '~/data/marketingPages'

const props = defineProps<{
  page: MarketingPageData
}>()

useSeoMeta({
  title: () => props.page.title,
  description: () => props.page.lead
})
</script>

<template>
  <div>
    <SiteNav />

    <main class="content-page">
      <section class="page-hero" :class="{ 'page-hero--image': page.heroImage }">
        <img v-if="page.heroImage" class="page-hero__image" :src="page.heroImage" alt="" />
        <div class="page-hero__shade" />
        <div class="container page-hero__inner">
          <div>
            <span class="eyebrow">{{ page.eyebrow }}</span>
            <h1>{{ page.title }}</h1>
            <p>{{ page.lead }}</p>
            <div v-if="page.primaryAction || page.secondaryAction" class="hero__actions">
              <NuxtLink v-if="page.primaryAction" class="btn btn--primary" :to="page.primaryAction[1]">
                {{ page.primaryAction[0] }}
              </NuxtLink>
              <NuxtLink v-if="page.secondaryAction" class="btn btn--secondary" :to="page.secondaryAction[1]">
                {{ page.secondaryAction[0] }}
              </NuxtLink>
            </div>
          </div>

          <div v-if="page.metrics?.length" class="hero-stats">
            <div v-for="metric in page.metrics" :key="metric.value">
              <strong>{{ metric.value }}</strong>
              <span>{{ metric.label }}</span>
            </div>
          </div>
        </div>
      </section>

      <section v-for="section in page.sections" :key="section.eyebrow" class="section">
        <div class="container">
          <SectionHeader :eyebrow="section.eyebrow" :title="section.title" :lead="section.lead" />
          <div class="ruled-grid" :class="{ 'ruled-grid--three': section.features.length >= 3 }">
            <article v-for="feature in section.features" :key="feature.title">
              <span>{{ feature.label }}</span>
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.text }}</p>
            </article>
          </div>
        </div>
      </section>

      <section v-if="page.note" class="section section--band page-note">
        <div class="container">
          <p>{{ page.note }}</p>
        </div>
      </section>
    </main>

    <SiteFooter />
  </div>
</template>
