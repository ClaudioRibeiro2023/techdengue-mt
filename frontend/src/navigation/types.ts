export type NavCategory = 'ANALISE' | 'MAPEAMENTO' | 'INDICADORES' | 'CONTROLE' | 'OPERACIONAL'

export type FunctionItem = {
  id: string
  name: string
  path: string
  category?: NavCategory
  icon?: string
}

export type AppModule = {
  id: string
  name: string
  description?: string
  path: string
  topNav?: boolean
  icon?: string
  functions?: FunctionItem[]
}

export type NavigationMap = {
  modules: AppModule[]
}
