<template>
  <footer class="site-footer">
    <div class="container site-footer__inner">
      <div class="site-footer__brand">
        <NuxtLink class="brand" to="/">
          <img class="brand__mark" src="/assets/aeonic-mark.png" alt="" />
          <span class="brand__word">Aeonic</span>
        </NuxtLink>
        <p>The clinical infrastructure for functional, performance, and precision longevity medicine.</p>
      </div>

      <div class="site-footer__nav">
        <div>
          <h3>Company</h3>
          <NuxtLink to="/our-story">Our story</NuxtLink>
          <NuxtLink to="/#science">Science</NuxtLink>
          <NuxtLink to="/contact">Contact</NuxtLink>
        </div>
        <div>
          <h3>System</h3>
          <NuxtLink to="/programs">Aeonic Continuum</NuxtLink>
          <NuxtLink to="/nexus">Aeonic Nexus</NuxtLink>
          <NuxtLink to="/#capabilities">Capabilities</NuxtLink>
        </div>
      </div>
    </div>

    <div class="container site-footer__bottom">
      <span>© 2026 Aeonic Health Systems</span>
      <p>All clinical decisions and prescriptions are made by licensed providers. This site is informational and not medical advice.</p>
      <div>
        <NuxtLink to="/privacy">Privacy</NuxtLink>
        <NuxtLink to="/terms">Terms</NuxtLink>
      </div>
    </div>
  </footer>
</template>
