<script setup lang="ts">
useSeoMeta({
  title: 'The System Behind Precision Longevity Medicine',
  description:
    'Aeonic is the complete operating system for longevity medicine: protocols, platform, intelligence, and clinical governance.'
})

const programCards = [
  {
    label: 'The programs',
    title: 'Pre-built, lab-guided',
    text: 'Dosing, titration, biomarker targets, and screening logic built around each patient’s bloodwork.'
  },
  {
    label: 'The treatments',
    title: 'Twelve care lines',
    text: 'Weight, hormones, peptides, sexual health, cognitive, longevity, immune, skin, sleep, gut, energy, and performance.'
  },
  {
    label: 'The experience',
    title: 'Ongoing, not one-off',
    text: 'Labs, dosing, supplements, nutrition, messaging, and Aeva in one member portal.'
  }
]

const platformCards = [
  {
    label: 'The clinic side',
    title: 'The provider console',
    text: 'Patients, protocols, prescriptions, labs, tasks, and revenue on one operating screen.'
  },
  {
    label: 'The patient side',
    title: 'The branded portal',
    text: 'A polished member app for protocols, labs, shipments, messaging, store, and Aeva.'
  },
  {
    label: 'The rails',
    title: 'Wired end to end',
    text: 'Prescribing, pharmacy, labs, billing, compliance, and role-based access integrated into the workflow.'
  }
]

const flow = [
  ['01', 'Codify', 'Protocols, biomarker ranges, contraindication checks, and dosing standards become executable clinical workflows.'],
  ['02', 'Brand & deploy', 'Launch a white-labeled clinic program, DTC brand, or both with a coherent member experience.'],
  ['03', 'Acquire & intake', 'Funnels and guided intake screen, consent, and route members before a provider review.'],
  ['04', 'Prescribe — three ways', 'Licensed providers review, sign, and oversee treatment across the supported deployment model.'],
  ['05', 'Engage & retain', 'Members return for labs, education, messaging, missions, refills, and protocol evolution.'],
  ['06', 'Scale', 'Add providers, locations, care lines, and brands while keeping one clinical standard.']
]

const capabilities = [
  ['Protocols and prescribing', 'Clinical engine', 'Peptides, hormones, GLP-1, regenerative and longevity care lines with prescribing workflows.'],
  ['Labs and biomarkers', 'Functional results', 'Order panels, trend markers, and trigger protocol adjustments from one source of truth.'],
  ['Membership and commerce', 'Recurring by design', 'Tiered memberships, billing, rewards, and clinician-formulated products.'],
  ['Academy and missions', 'Education that engages', 'Programs that keep members active, informed, and adherent.'],
  ['Aeva intelligence', 'Woven throughout', 'Member companion and clinical co-pilot for labs, plans, summaries, and insight.'],
  ['Compliance and governance', 'Built in', 'Consent, audit trail, permissions, and state-aware operating practices.'],
  ['Integrations', 'Front end and back end', 'Landing pages, CRM, labs, pharmacy, telehealth, and billing setup.'],
  ['Growth', 'Demand and retention', 'Acquisition and lifecycle programs engineered around recurring longevity care.'],
  ['White label', 'Your brand, any size', 'One platform across brands, clinics, and locations without rebuilding the system.']
]
</script>

<template>
  <div>
    <SiteNav />

    <main>
      <section class="hero">
        <img class="hero__image" src="/assets/hero-systems.avif" alt="" />
        <div class="hero__shade" />
        <div class="container hero__content">
          <div class="hero__copy">
            <h1>The complete operating system for longevity protocols.</h1>
            <p>
              Aeonic is the complete operating system for longevity medicine — plug it into your existing clinic or
              brand, or build a new one on it.
            </p>
            <div class="hero__actions">
              <NuxtLink class="btn btn--primary" to="/connect-inquiry">Get started <span aria-hidden="true">→</span></NuxtLink>
              <NuxtLink class="btn btn--secondary" to="#how-it-works">How it works <span aria-hidden="true">→</span></NuxtLink>
            </div>
          </div>
          <div class="hero-stats" aria-label="Aeonic summary">
            <div>
              <strong>Aeonic Health Systems</strong>
              <span>The complete system for longevity medicine</span>
            </div>
            <div>
              <strong>Physician-led</strong>
              <span>Licensed oversight</span>
            </div>
            <div>
              <strong>50-State</strong>
              <span>Compliance</span>
            </div>
          </div>
        </div>
      </section>

      <section class="section section--doors">
        <div class="container">
          <SectionHeader
            eyebrow="One system, front to back"
            title="One system: the front end patients feel, and the back end behind it."
            lead="Aeonic is one system. Health is the medicine — the protocols and treatments. Connect is the platform that runs it."
          />

          <div class="door-grid">
            <NuxtLink class="door-card" to="/programs">
              <span>The forward-facing layer</span>
              <h3><img src="/assets/aeonic-mark.png" alt="" />AEONIC <small>HEALTH</small></h3>
              <p>The protocols, programming, and treatment systems — the clinical care patients actually experience.</p>
              <strong>Explore Aeonic Continuum <span aria-hidden="true">→</span></strong>
            </NuxtLink>
            <NuxtLink class="door-card" to="/nexus">
              <span>The platform layer</span>
              <h3><img src="/assets/aeonic-mark.png" alt="" />AEONIC <small>CONNECT</small></h3>
              <p>The software and rails that run Health — prescribing, pharmacy, labs, compliance, and billing in one clinical backend.</p>
              <strong>Explore Aeonic Nexus <span aria-hidden="true">→</span></strong>
            </NuxtLink>
          </div>
        </div>
      </section>

      <section class="section section--band">
        <div class="container">
          <article class="image-band">
            <img src="/assets/hero-health.webp" alt="" />
            <div>
              <span class="eyebrow">The Programs · Aeonic Continuum</span>
              <h2>Health is the program — the protocols patients experience.</h2>
              <p>A deployable, scalable program on the Aeonic back end: physician-led, lab-guided protocols for weight, hormones, energy, performance, and recovery.</p>
              <NuxtLink class="btn btn--primary" to="/programs">Bring the program to your practice <span aria-hidden="true">→</span></NuxtLink>
            </div>
          </article>

          <div class="ruled-grid">
            <article v-for="card in programCards" :key="card.title">
              <span>{{ card.label }}</span>
              <h3>{{ card.title }}</h3>
              <p>{{ card.text }}</p>
            </article>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="container">
          <article class="image-band image-band--right">
            <img src="/assets/hero-nexus.avif" alt="" />
            <div>
              <span class="eyebrow">The Platform · Aeonic Nexus</span>
              <h2>Nexus is the platform — the rails that run it.</h2>
              <p>The software behind the protocols: a provider console on one side, a branded patient portal on the other, wired to prescribing, pharmacy, labs, and billing.</p>
              <NuxtLink class="btn btn--primary" to="/nexus">Deploy the platform in your clinic <span aria-hidden="true">→</span></NuxtLink>
            </div>
          </article>

          <div class="ruled-grid">
            <article v-for="card in platformCards" :key="card.title">
              <span>{{ card.label }}</span>
              <h3>{{ card.title }}</h3>
              <p>{{ card.text }}</p>
            </article>
          </div>
        </div>
      </section>

      <section id="how-it-works" class="section section--how">
        <div class="container">
          <SectionHeader
            eyebrow="How it works"
            title="From pre-built protocols to a <em>running program</em>."
            lead="The same flow powers every Aeonic deployment: clinic, brand, or hybrid."
          />

          <div class="flow-grid">
            <article v-for="[step, title, text] in flow" :key="step">
              <span>{{ step }}</span>
              <h3>{{ title }}</h3>
              <p>{{ text }}</p>
            </article>
          </div>
        </div>
      </section>

      <section id="capabilities" class="section">
        <div class="container">
          <SectionHeader
            eyebrow="Full capabilities"
            title="Everything to run longevity medicine: <em>clinically and commercially</em>."
          />

          <div class="ruled-grid ruled-grid--three">
            <article v-for="[label, title, text] in capabilities" :key="title">
              <span>{{ label }}</span>
              <h3>{{ title }}</h3>
              <p>{{ text }}</p>
            </article>
          </div>
        </div>
      </section>

      <section class="section section--band">
        <div class="container aeva-layout">
          <div>
            <span class="eyebrow">Aeva · Intelligence layer</span>
            <h2>Aeva is the <em>intelligence</em> woven through the system.</h2>
            <p>
              One intelligence layer across the member portal and provider console: explaining labs, drafting summaries,
              surfacing risk, and accelerating licensed clinicians without replacing them.
            </p>
            <p class="clinical-note">Aeva supports clinical decisions; it never makes them.</p>
          </div>
          <img src="/assets/aeva-patient.png" alt="Aeva patient interface mockup" />
        </div>
      </section>

      <section id="science" class="section">
        <div class="container founder">
          <img src="/assets/dr-lacey.webp" alt="Dr. Lacey" />
          <div>
            <span class="eyebrow">The science and authority</span>
            <h2>Two decades of clinical practice, <em>built into a system</em>.</h2>
            <p>
              Aeonic translates root-cause, functional, and performance medicine into repeatable protocols,
              clinical governance, and a deployable software platform.
            </p>
            <blockquote>Root-cause medicine, refined patient by patient, then made repeatable at scale.</blockquote>
          </div>
        </div>
      </section>

      <section class="closing-cta">
        <div class="container">
          <span class="eyebrow">Get started</span>
          <h2>Add Aeonic to your <em>practice</em>.</h2>
          <p>Plug the complete system into your clinic or brand, or launch a new one on it.</p>
          <div>
            <NuxtLink class="btn btn--primary" to="/connect-inquiry">Book a demo</NuxtLink>
            <NuxtLink class="btn btn--secondary" to="/nexus">See Nexus</NuxtLink>
          </div>
        </div>
      </section>
    </main>

    <SiteFooter />
  </div>
</template>
