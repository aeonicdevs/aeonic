<script setup lang="ts">
useHead({
  bodyAttrs: { 'data-prop': 'systems' },
  link: [
    {
      rel: 'stylesheet',
      href:
        'https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400;1,6..72,500&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;1,9..144,400;1,9..144,500&family=Spectral:ital,wght@0,400;0,500;1,400;1,500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;1,8..60,400&family=Libre+Caslon+Text:ital,wght@0,400;1,400&family=Hanken+Grotesk:wght@400;500;600;700&family=Schibsted+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=Manrope:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Mona+Sans:wght@400;500;600;700&display=swap'
    },
    { rel: 'stylesheet', href: '/mock/aeonic.css' }
  ],
  script: [{ src: '/mock/aeonic.js' }]
})

useSeoMeta({
  title: 'The System Behind Precision Longevity Medicine',
  description:
    'Aeonic is the complete operating system for longevity medicine: protocols, platform, intelligence, and clinical governance.'
})
</script>

<template>
  <div class="mock-home">
    <header class="nav nav--in">
      <div class="wrap nav__in">
        <NuxtLink class="brand" to="/">
          <span class="brand__mark"></span>
          <span class="brand__word">Aeonic</span>
        </NuxtLink>
        <nav class="nav__links">
          <div class="nav__item">
            <span class="nav__trigger">The Programs <span class="car"></span></span>
            <div class="nav__dd nav__dd--wide">
              <div class="dd-head">The forward-facing layer · Aeonic Continuum</div>
              <NuxtLink to="/programs"><span class="dt">Aeonic Continuum overview</span><span class="ds">The clinical program we deploy</span></NuxtLink>
              <NuxtLink to="/treatments"><span class="dt">The protocols</span><span class="ds">Ten care lines — proven & customizable</span></NuxtLink>
              <NuxtLink to="/catalog"><span class="dt">The catalog</span><span class="ds">The formulary, by clinical area</span></NuxtLink>
              <NuxtLink to="/member-login"><span class="dt">The member experience</span><span class="ds">What patients get in the portal</span></NuxtLink>
            </div>
          </div>
          <div class="nav__item">
            <span class="nav__trigger">The Platform <span class="car"></span></span>
            <div class="nav__dd nav__dd--wide">
              <div class="dd-head">The platform layer · Aeonic Nexus</div>
              <NuxtLink to="/nexus"><span class="dt">Aeonic Nexus overview</span><span class="ds">The platform behind the practice</span></NuxtLink>
              <NuxtLink to="/#capabilities"><span class="dt">The console & capabilities</span><span class="ds">Everything the platform runs, one screen</span></NuxtLink>
              <NuxtLink to="/partner-login"><span class="dt">Partner login</span><span class="ds">Enter the provider console</span></NuxtLink>
            </div>
          </div>
          <div class="nav__item">
            <span class="nav__trigger">About <span class="car"></span></span>
            <div class="nav__dd nav__mega">
              <div class="mega">
                <div class="mega-main">
                  <div class="mega-cols mega-cols--plain">
                    <div>
                      <div class="mega-coltitle">Company</div>
                      <NuxtLink class="mega-link" to="/our-story">Our story</NuxtLink>
                      <NuxtLink class="mega-link" to="/mission">Mission & the system</NuxtLink>
                      <NuxtLink class="mega-link" to="/dr-lacey">Dr. Lacey & the team</NuxtLink>
                      <NuxtLink class="mega-link" to="/partners">Partners</NuxtLink>
                    </div>
                    <div>
                      <div class="mega-coltitle">Newsroom</div>
                      <NuxtLink class="mega-link" to="/press">Press & media</NuxtLink>
                      <NuxtLink class="mega-link" to="/announcements">Announcements</NuxtLink>
                      <NuxtLink class="mega-link" to="/contact">Contact</NuxtLink>
                    </div>
                  </div>
                </div>
                <NuxtLink class="mega-feat" to="/announcements">
                  <div class="brandtile"></div>
                  <div class="mega-feat-cap">
                    <div class="fe">Announcement</div>
                    <div class="fn">One system, now open to practices via Aeonic Nexus</div>
                  </div>
                </NuxtLink>
              </div>
            </div>
          </div>
        </nav>
        <div class="nav__cta">
          <NuxtLink class="btn btn--ghost nav-getstarted" to="/connect-inquiry">Get started</NuxtLink>
          <button class="burger" aria-label="Menu"><span></span><span></span><span></span></button>
        </div>
      </div>
    </header>

    <main>
      <section class="hero bleed has-bg hero--left">
        <div class="hero__bg">
          <img src="/mock/assets/hero-systems.avif" alt="" style="width:100%;height:100%;object-fit:cover;object-position:center;display:block" />
        </div>
        <div class="hero__scrim"></div>
        <div class="wrap">
          <div class="hero__grid">
            <div class="reveal force-in">
              <h1 class="disp" style="margin-top:0;font-size:clamp(42px,7vw,65px)">The complete <em>operating system</em> for longevity protocols.</h1>
              <p class="lead lead--lg" style="margin-top:28px">Aeonic is the complete operating system for longevity medicine — plug it into your existing clinic or brand, or build a new one on it.</p>
              <div class="stack gap-s mt-l">
                <div id="sys-hero-cta" class="btn-row btn-row--full">
                  <NuxtLink class="btn btn--primary btn--lg" to="/connect-inquiry">Get started <span class="arw">→</span></NuxtLink>
                  <NuxtLink class="btn btn--ghost btn--lg" to="/ways">How it works <span class="arw">→</span></NuxtLink>
                </div>
              </div>
            </div>
          </div>
          <div class="hero-stats reveal force-in">
            <div class="hs"><b>Aeonic Health Systems</b><span>The complete system for longevity medicine</span></div>
            <div class="hs"><b>Physician-led</b><span>Licensed oversight</span></div>
            <div class="hs"><b>50-State</b><span>Compliance</span></div>
          </div>
        </div>
      </section>

      <section id="doors" class="section">
        <div class="wrap">
          <div class="sec-head center reveal force-in" style="margin-bottom:48px">
            <span class="eyebrow eyebrow--center">One system, front to back</span>
            <h2 class="h-lg">One system: the <em>front end</em> patients feel, and the <em>back end</em> behind it.</h2>
            <p class="lead" style="margin-inline:auto">Aeonic is one system. <strong style="color:var(--fg)">Health</strong> is the medicine — the protocols and treatments. <strong style="color:var(--fg)">Connect</strong> is the platform that runs it.</p>
          </div>
          <div class="doors">
            <NuxtLink class="door reveal force-in" to="/programs">
              <span class="door__k">The forward-facing layer</span>
              <span class="door__t">
                <span class="brand-lockup">
                  <img class="brand-lockup__mark" src="/mock/assets/aeonic-mark.png" alt="" />
                  <span class="brand-lockup__type"><span class="bl-aeonic" style="font-family: Spectral">AEONIC</span><span class="bl-div"></span><span class="bl-sub">Health</span></span>
                </span>
              </span>
              <p class="muted">The protocols, programming, and treatment systems — the clinical care patients actually experience.</p>
              <div class="spacer"></div>
              <span class="btn--link">Explore Aeonic Continuum</span>
            </NuxtLink>
            <NuxtLink class="door reveal force-in" to="/nexus">
              <span class="door__k">The platform layer</span>
              <span class="door__t">
                <span class="brand-lockup">
                  <img class="brand-lockup__mark" src="/mock/assets/aeonic-mark.png" alt="" />
                  <span class="brand-lockup__type"><span class="bl-aeonic" style="font-family: Spectral">AEONIC</span><span class="bl-div"></span><span class="bl-sub">Connect</span></span>
                </span>
              </span>
              <p class="muted">The software and rails that run Health — prescribing, pharmacy, labs, compliance, and billing in one clinical backend.</p>
              <div class="spacer"></div>
              <span class="btn--link">Explore Aeonic Nexus</span>
            </NuxtLink>
          </div>
        </div>
      </section>

      <section id="health-overview" class="section">
        <div class="wrap">
          <div class="overlay-band reveal force-in" style="margin-bottom:clamp(28px,3.6vw,48px)">
            <img class="overlay-band__img" src="/mock/assets/hero-health.webp" alt="" />
            <div class="overlay-band__scrim"></div>
            <div class="overlay-band__inner">
              <span class="eyebrow">The Programs · Aeonic Continuum</span>
              <h2 class="overlay-band__h">Health is the program — the <em>protocols patients experience</em>.</h2>
              <p class="overlay-band__sub">A deployable, scalable program on the Aeonic back-end: physician-led, lab-guided protocols for weight, hormones, energy, performance, and recovery.</p>
              <NuxtLink class="btn btn--primary" to="/contact" style="margin-top:22px">Bring the program to your practice <span class="arw">→</span></NuxtLink>
            </div>
          </div>
          <div class="ruledgrid ruledgrid--3 reveal force-in">
            <div class="rg-cell"><span class="rg-cell__k">The programs</span><h3>Pre-built, lab-guided</h3><p>Dosing, titration, biomarker targets, and screening — refined over 20 years and built around each patient's bloodwork, not a template.</p></div>
            <div class="rg-cell"><span class="rg-cell__k">The treatments</span><h3>Twelve care lines</h3><p>Weight, hormones, peptides, sexual health, cognitive, longevity, immune, skin, sleep, gut, energy, and performance — each a complete protocol.</p></div>
            <div class="rg-cell"><span class="rg-cell__k">The experience</span><h3>Ongoing, not one-off</h3><p>Labs, dosing, supplements, nutrition, and Aeva in one member portal — monitored and adjusted as biomarkers move over time.</p></div>
          </div>
          <div class="btn-row mt-l reveal force-in">
            <NuxtLink class="btn btn--ghost btn--lg" to="/programs">Explore Aeonic Continuum <span class="arw">→</span></NuxtLink>
            <NuxtLink class="btn--link" to="/treatments" style="align-self:center">View all treatments →</NuxtLink>
          </div>
        </div>
      </section>

      <section id="connect-overview" class="section band">
        <div class="wrap">
          <div class="overlay-band reveal force-in" style="margin-bottom:clamp(28px,3.6vw,48px)">
            <img class="overlay-band__img" src="/mock/assets/hero-connect.avif" alt="" />
            <div class="overlay-band__scrim"></div>
            <div class="overlay-band__inner">
              <span class="eyebrow">The Platform · Aeonic Nexus</span>
              <h2 class="overlay-band__h">Nexus is the platform — the <em>rails that run it</em>.</h2>
              <p class="overlay-band__sub">The software behind the protocols: a provider console on one side, a branded patient portal on the other — wired to prescribing, pharmacy, labs, and billing.</p>
              <NuxtLink class="btn btn--primary" to="/contact" style="margin-top:22px">Deploy the platform in your clinic <span class="arw">→</span></NuxtLink>
            </div>
          </div>
          <div class="ruledgrid ruledgrid--3 reveal force-in">
            <div class="rg-cell"><span class="rg-cell__k">The clinic side</span><h3>The provider console</h3><p>Patients, protocols in flight, scripts, labs, tasks, and revenue — the whole program on one screen, with Aeva drafting and flagging alongside.</p></div>
            <div class="rg-cell"><span class="rg-cell__k">The patient side</span><h3>The branded portal</h3><p>A polished member app — protocol, labs, shipments, messaging, store, and Aeva — fully white-labeled to the practice.</p></div>
            <div class="rg-cell"><span class="rg-cell__k">How it connects</span><h3>Wired end to end</h3><p>e-Prescribing into a 503A pharmacy network with tracked fulfillment, labs and biomarkers, payments and billing, and state-by-state compliance — integrated, not stitched together.</p></div>
          </div>
          <div class="btn-row mt-l reveal force-in"><NuxtLink class="btn btn--ghost btn--lg" to="/nexus">Explore Aeonic Nexus <span class="arw">→</span></NuxtLink></div>
        </div>
      </section>

      <section id="howitworks" class="section">
        <div class="wrap">
          <div class="sec-head center reveal force-in" style="margin-bottom:48px">
            <span class="eyebrow eyebrow--center">How it works</span>
            <h2 class="h-lg">From pre-built protocols to a <em>running program</em>.</h2>
            <p class="lead">The same flow powers every Aeonic deployment — your own clinic or your brand, stood up in weeks, not quarters.</p>
          </div>
          <div class="howflow howflow--3 reveal force-in">
            <div v-for="step in [
              ['1','Codify','Twenty years of protocols — dosing, titration, biomarker targets, contraindication screening — pre-built into the platform as the clinical standard.'],
              ['2','Brand & deploy','Spin up a white-labeled DTC brand, a clinic program, or both. Your domain, your logo, your member experience — live in days.'],
              ['3','Acquire & intake','Funnels and guided intake screen and convert members; eligibility and consent are captured before anyone reaches a prescriber.'],
              ['4','Prescribe — three ways','Prescribe in-house with your own licensed providers, in-house through the Aeonic physician network, or prescribe nationwide across all 50 states.'],
              ['5','Engage & retain','Members live in the portal — labs, dosing, messaging, Academy, missions, store and Aeva — driving adherence and recurring revenue.'],
              ['6','Scale','Add providers, locations and care lines on shared protocols and one source of truth. The standard holds as you grow.']
            ]" :key="step[0]" class="howstep2">
              <div class="howstep2__top"><span class="howstep2__n">{{ step[0] }}</span><span class="howstep-ic howstep-ic--pulse"></span></div>
              <h3 class="h-sm">{{ step[1] }}</h3>
              <p>{{ step[2] }}</p>
            </div>
          </div>
        </div>
      </section>

      <section id="capabilities" class="section band">
        <div class="wrap">
          <div class="sec-head center reveal force-in" style="margin-bottom:48px">
            <span class="eyebrow eyebrow--center">Full capabilities</span>
            <h2 class="h-lg">Everything to run longevity medicine — <em>clinically and commercially</em>.</h2>
          </div>
          <div class="ruledgrid ruledgrid--3 reveal force-in">
            <div class="rg-cell"><span class="rg-cell__k">Protocols & prescribing</span><h3>Clinical engine</h3><p>Peptides, hormones, GLP-1, regenerative & longevity — with e-prescribing and a vetted pharmacy network.</p></div>
            <div class="rg-cell"><span class="rg-cell__k">Labs & biomarkers</span><h3>Function-style results</h3><p>Order panels, auto-digitize results, trend markers, and trigger protocol adjustments with clinician summaries.</p></div>
            <div class="rg-cell"><span class="rg-cell__k">Membership & commerce</span><h3>Recurring by design</h3><p>Tiered memberships, billing, and a rewards wallet — plus a clinician-formulated catalog sold at your margin and shipped to the door.</p></div>
            <div class="rg-cell"><span class="rg-cell__k">Academy & missions</span><h3>Education that engages</h3><p>Workouts, nutrition, courses, and rewarded missions that keep members active and adherent.</p></div>
            <div class="rg-cell"><span class="rg-cell__k">Aeva intelligence</span><h3>Woven throughout</h3><p>A member companion and a clinical co-pilot — explaining labs, drafting protocols, and surfacing insight.</p></div>
            <div class="rg-cell"><span class="rg-cell__k">Compliance & governance</span><h3>Built in, not bolted on</h3><p>HIPAA-compliant, state-by-state, with consent, audit trail and role-based access.</p></div>
            <div class="rg-cell"><span class="rg-cell__k">Integrations & build-outs</span><h3>Front end & back end</h3><p>Website and landing-page build-outs, plus HIPAA-compliant CRM setup and support — the program launched complete.</p></div>
            <div class="rg-cell"><span class="rg-cell__k">Growth</span><h3>We help fill it</h3><p>Paid acquisition and territory-level demand, plus retention programs engineered for longevity conversion — patients in, and kept on protocol.</p></div>
            <div class="rg-cell"><span class="rg-cell__k">White-label & scale</span><h3>Your brand, any size</h3><p>One platform across brands, clinics and locations — deploy fast and grow without rebuilding.</p></div>
          </div>
        </div>
      </section>

      <section id="aura" class="section">
        <div class="wrap">
          <div class="sec-head center reveal force-in" style="margin-bottom:48px">
            <span class="eyebrow eyebrow--center">Aeva · Intelligence layer</span>
            <h2 class="h-lg">Aeva is the <em>intelligence</em> woven through the system.</h2>
            <p class="lead">One intelligence layer across everything Aeonic does — reading data, surfacing insight, and accelerating clinicians on both sides of the system. Always in service of a licensed provider, never instead of one.</p>
          </div>
          <div class="reveal force-in" style="margin-bottom:18px;aspect-ratio:21/9;border:1px solid var(--line-2);border-radius:10px;overflow:hidden;background:#f5f3ec">
            <img src="/mock/assets/aura-patient-2.png" alt="Aeva — intelligence across the system" style="width:100%;height:100%;object-fit:cover;object-position:top left;display:block" />
          </div>
          <div class="grid cols-3">
            <div class="card reveal force-in"><span class="num">For members</span><h3 class="h-md">Understands your plan</h3><p>Explains labs in plain language, answers questions any time, and keeps the protocol moving — inside the Aeonic Continuum portal.</p></div>
            <div class="card reveal force-in"><span class="num">For practices</span><h3 class="h-md">A clinical co-pilot</h3><p>Drafts protocols, flags interactions, and summarizes patients in the provider console — so partner clinics run to standard, faster.</p></div>
            <div class="card reveal force-in"><span class="num">For the system</span><h3 class="h-md">Sharper over time</h3><p>Learns from outcomes across the network to refine protocols and surface what works — under clinical governance.</p></div>
          </div>
          <p class="note" style="margin-top:24px">Aeva supports clinical decisions; it never makes them. Every protocol and prescription is reviewed and signed by a licensed provider.</p>
        </div>
      </section>

      <section id="close" class="section band section--deep">
        <div class="wrap">
          <div class="sec-head center reveal force-in maxw-md" style="gap:28px">
            <span class="eyebrow eyebrow--center">Get started</span>
            <h2 class="disp" style="font-size:clamp(36px,5.2vw,72px)">Add Aeonic to your <em>practice — today.</em></h2>
            <p class="lead" style="margin-inline:auto">Plug the complete system into your clinic or brand, or launch a new one on it. We'll have you live in days.</p>
            <div class="btn-row" style="justify-content:center">
              <NuxtLink class="btn btn--primary btn--lg" to="/connect-inquiry">Book a demo <span class="arw">→</span></NuxtLink>
              <NuxtLink class="btn btn--ghost btn--lg" to="/contact">Get started <span class="arw">→</span></NuxtLink>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
