import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const staticOutput = fileURLToPath(new URL('../.output/public/index.html', import.meta.url))

if (!existsSync(staticOutput)) {
  throw new Error('Expected Nuxt static output at .output/public/index.html after `nuxt generate`.')
}

console.log('Verified Nuxt static output at .output/public.')
