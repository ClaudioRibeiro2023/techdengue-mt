export type NavCategory = 'ANALISE' | 'MAPEAMENTO' | 'INDICADORES' | 'CONTROLE' | 'OPERACIONAL'

export type FunctionItem = {
  id: string
  name: string
  path: string
  category?: NavCategory
}

export type AppModule = {
  id: string
  name: string
  description?: string
  path: string
  topNav?: boolean
  functions?: FunctionItem[]
}

export type NavigationMap = {
  modules: AppModule[]
}
