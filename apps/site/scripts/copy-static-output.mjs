import { existsSync } from 'node:fs'
import { cp, rm } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'

const source = fileURLToPath(new URL('../.output/public', import.meta.url))
const target = fileURLToPath(new URL('../dist', import.meta.url))

if (!existsSync(source)) {
  throw new Error('Nuxt static output was not found at .output/public')
}

await rm(target, { recursive: true, force: true })
await cp(source, target, { recursive: true })
