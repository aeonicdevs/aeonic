import { existsSync } from 'node:fs'
import { cp, rm } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'

const nitroOutput = fileURLToPath(new URL('../.output/public', import.meta.url))
const target = fileURLToPath(new URL('../dist', import.meta.url))
const targetIndex = fileURLToPath(new URL('../dist/index.html', import.meta.url))

if (existsSync(nitroOutput)) {
  await rm(target, { recursive: true, force: true })
  await cp(nitroOutput, target, { recursive: true })
  console.log('Copied Nuxt static output from .output/public to dist.')
} else if (existsSync(targetIndex)) {
  console.log('Nuxt static output already exists in dist.')
} else {
  throw new Error('Nuxt static output was not found. Checked .output/public and dist.')
}
