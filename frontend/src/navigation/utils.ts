import { NAVIGATION } from './map'
import type { AppModule } from './types'

export function getModuleById(id?: string): AppModule | undefined {
  if (!id) return undefined
  return NAVIGATION.modules.find(m => m.id === id)
}

export function getModuleByPath(path: string): AppModule | undefined {
  return NAVIGATION.modules.find(m => path.startsWith(m.path))
}
