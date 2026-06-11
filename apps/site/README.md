# Aeonic Site

Public marketing site for Aeonic.

This Nuxt app serves the main public website, product positioning, company
pages, and other unauthenticated marketing pages.

The messy `AEONIC (28)/` folder at the repo root is client-provided reference
material, not production source. Recreate useful pages here as structured Vue
components and copy only curated assets into `public/assets/`.

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
