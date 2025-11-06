import type { UserRole } from '@/config/auth'

export type NavCategory = 'ANALISE' | 'MAPEAMENTO' | 'INDICADORES' | 'CONTROLE' | 'OPERACIONAL'

export type FunctionItem = {
  id: string
  name: string
  path: string
  category?: NavCategory
  icon?: string
  subtitle?: string
  roles?: UserRole[]
}

export type AppModule = {
  id: string
  name: string
  description?: string
  path: string
  topNav?: boolean
  icon?: string
  badge?: string
  group?: string
  functions?: FunctionItem[]
  roles?: UserRole[]
}

export type NavigationMap = {
  modules: AppModule[]
}
