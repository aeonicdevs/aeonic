# Aeonic Site

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

Netlify is configured from the repository root with `netlify.toml`.

- Base directory: `apps/site`
- Build command: `npm run generate:netlify`
- Publish directory: `dist`

This keeps the marketing site static and CDN-served. The Netlify build command
generates Nuxt's static output and copies it into `dist/` so Netlify deploys a
plain, explicit publish directory. If the site later needs runtime server
behavior, switch the Netlify command to `npm run build` and let Nuxt/Nitro
deploy the server renderer on Netlify.
