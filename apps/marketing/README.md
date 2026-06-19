# Aeonic Marketing

Public marketing site for Aeonic.

This Nuxt app currently serves the client-provided mockup port as the source of
truth for the public marketing site.

The messy `AEONIC (28)/` folder at the repo root is client-provided reference
material, not production source. The active implementation lives in
`pages/index.vue` and loads the mockup stylesheet, script, and assets from
`public/mock/`. Once the mockup match is acceptable, extract stable shared
styles/components from that implementation deliberately.

## Local development

```sh
npm install
npm run dev
```

## Static build

```sh
npm run generate:netlify
```

Configure the marketing Netlify site with:

- Base directory: `apps/marketing`
- Build command: `npm run build`
- Publish directory: `.output/public`

This keeps the marketing site static and CDN-served. The Netlify build command
forces Nitro's generic static preset so Nuxt writes static output to
`.output/public`, matching the Netlify publish directory. If the site later
needs runtime server behavior, switch the build script to `nuxt build` and let
Nuxt/Nitro deploy the server renderer on Netlify.
