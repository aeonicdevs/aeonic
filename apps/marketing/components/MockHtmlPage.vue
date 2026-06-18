<script setup lang="ts">
type MockScript = {
  src?: string
  code?: string
  type?: string
}

const props = defineProps<{
  source: string
}>()

const fontHref =
  'https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400;1,6..72,500&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;1,9..144,400;1,9..144,500&family=Spectral:ital,wght@0,400;0,500;1,400;1,500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;1,8..60,400&family=Libre+Caslon+Text:ital,wght@0,400;1,400&family=Hanken+Grotesk:wght@400;500;600;700&family=Schibsted+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=Manrope:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Mona+Sans:wght@400;500;600;700&display=swap'

const routeMap: Record<string, string> = {
  'aeonic-systems.html': '/',
  'index.html': '/',
  'system.html': '/',
  'systems-next.html': '/',
  'aeonic-health.html': '/programs',
  'health-start.html': '/programs',
  'programs-next.html': '/programs',
  'aeonic-connect.html': '/nexus',
  'platform.html': '/nexus',
  'aeonic-store.html': '/catalog',
  'aeonic-health-login.html': '/member-login',
  'aeonic-systems-login.html': '/member-login',
  'aeonic-connect-login.html': '/partner-login',
  'connect-inquiry.html': '/connect-inquiry',
  'get-started.html': '/connect-inquiry',
  'how-it-works.html': '/ways',
  'ways.html': '/ways'
}

function normalizeUrl(url: string) {
  if (/^(https?:|mailto:|tel:|#|\/|data:)/.test(url)) return url

  if (url.startsWith('assets/')) return `/mock/${url}`

  const [path, hash = ''] = url.split('#')
  if (!path) return hash ? `#${hash}` : url

  const mapped = routeMap[path]
  if (mapped) return `${mapped}${hash ? `#${hash}` : ''}`

  if (path.endsWith('.html')) return `/${path.replace(/\.html$/, '')}${hash ? `#${hash}` : ''}`

  return url
}

function normalizeMarkup(markup: string) {
  return markup.replace(/\b(href|src)=["']([^"']+)["']/g, (_match, attr: string, value: string) => {
    return `${attr}="${normalizeUrl(value)}"`
  })
}

function parseSource(source: string) {
  const title = source.match(/<title>([\s\S]*?)<\/title>/i)?.[1]?.replace(/&amp;/g, '&') || 'Aeonic'
  const bodyOpen = source.match(/<body([^>]*)>/i)?.[1] || ''
  const bodyProp = bodyOpen.match(/data-prop=["']([^"']+)["']/i)?.[1] || 'systems'
  const rawBody = source.match(/<body[^>]*>([\s\S]*?)<\/body>/i)?.[1] || source
  const scripts: MockScript[] = []

  const bodyWithoutScripts = rawBody.replace(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi, (_match, attrs: string, code: string) => {
    const src = attrs.match(/\bsrc=["']([^"']+)["']/i)?.[1]
    const type = attrs.match(/\btype=["']([^"']+)["']/i)?.[1]

    if (src && /^(aeonic\.js|image-slot\.js|tweaks-panel\.jsx|aeonic-tweaks\.jsx)$/.test(src)) return ''
    if (src && /^https:\/\/unpkg\.com\//.test(src)) return ''
    if (src) scripts.push({ src: normalizeUrl(src), type })
    if (!src && code.trim()) scripts.push({ code, type })
    return ''
  })

  return {
    title,
    bodyProp,
    html: normalizeMarkup(bodyWithoutScripts),
    scripts
  }
}

const parsed = computed(() => parseSource(props.source))

useHead(() => ({
  title: parsed.value.title,
  bodyAttrs: { 'data-prop': parsed.value.bodyProp },
  link: [
    { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
    { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
    { rel: 'stylesheet', href: fontHref },
    { rel: 'stylesheet', href: '/mock/aeonic.css' }
  ],
  script: [{ src: '/mock/aeonic.js' }]
}))

async function runPageScripts() {
  await nextTick()

  for (const script of parsed.value.scripts) {
    if (script.type === 'text/babel') continue

    if (script.src) {
      await new Promise<void>((resolve, reject) => {
        const el = document.createElement('script')
        el.src = script.src
        el.onload = () => resolve()
        el.onerror = () => reject(new Error(`Unable to load ${script.src}`))
        document.body.appendChild(el)
      })
    } else if (script.code) {
      window.setTimeout(() => {
        try {
          Function(script.code || '')()
        } catch (error) {
          console.warn('Mock page script failed', error)
        }
      }, 0)
    }
  }
}

onMounted(runPageScripts)
watch(() => props.source, runPageScripts)
</script>

<template>
  <div class="mock-page" v-html="parsed.html"></div>
</template>
