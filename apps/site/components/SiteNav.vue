<script setup lang="ts">
const isOpen = ref(false)

const menuGroups = [
  {
    label: 'The Programs',
    items: [
      ['Aeonic Continuum', '/programs', 'The clinical program patients experience'],
      ['Protocols', '/treatments', 'Care lines, dosing logic, and guided treatment'],
      ['Catalog', '/catalog', 'Formulary, supplements, and clinical commerce']
    ]
  },
  {
    label: 'The Platform',
    items: [
      ['Aeonic Nexus', '/nexus', 'The platform behind the practice'],
      ['Capabilities', '/#capabilities', 'The operating layer end to end'],
      ['Partner login', '/partner-login', 'Console access for clinical teams']
    ]
  },
  {
    label: 'About',
    items: [
      ['Our Story', '/our-story', 'Why Aeonic exists'],
      ['Science', '/#science', 'Clinical foundation and authority'],
      ['Contact', '/contact', 'Talk with the Aeonic team']
    ]
  }
]
</script>

<template>
  <header class="site-nav">
    <div class="site-nav__inner container">
      <NuxtLink class="brand" to="/" aria-label="Aeonic home">
        <img class="brand__mark" src="/assets/aeonic-mark.png" alt="" />
        <span class="brand__word">AEONIC</span>
      </NuxtLink>

      <nav class="site-nav__links" aria-label="Main navigation">
        <div v-for="group in menuGroups" :key="group.label" class="nav-menu">
          <button class="nav-menu__trigger" type="button">
            {{ group.label }}
          </button>
          <div class="nav-menu__panel">
            <NuxtLink v-for="[title, href, text] in group.items" :key="title" class="nav-menu__link" :to="href">
              <strong>{{ title }}</strong>
              <span>{{ text }}</span>
            </NuxtLink>
          </div>
        </div>
      </nav>

      <div class="site-nav__actions">
        <NuxtLink class="btn btn--small btn--secondary nav-getstarted" to="/connect-inquiry">Get started</NuxtLink>
        <button class="menu-toggle" type="button" :aria-expanded="isOpen" aria-controls="mobile-menu" @click="isOpen = !isOpen">
          <span />
          <span />
          <span />
        </button>
      </div>
    </div>

    <div id="mobile-menu" class="mobile-menu" :class="{ 'mobile-menu--open': isOpen }">
      <NuxtLink to="/programs" @click="isOpen = false">Programs</NuxtLink>
      <NuxtLink to="/nexus" @click="isOpen = false">Nexus</NuxtLink>
      <NuxtLink to="/#capabilities" @click="isOpen = false">Capabilities</NuxtLink>
      <NuxtLink to="/partner-login" @click="isOpen = false">Partner login</NuxtLink>
      <NuxtLink to="/connect-inquiry" @click="isOpen = false">Get started</NuxtLink>
    </div>
  </header>
</template>
