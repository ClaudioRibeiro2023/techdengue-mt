import { buildQuery } from '@/design-system/filters'

export interface DashboardComputed {
  ano: number
  semanaInicio?: number
  semanaFim?: number
  doencaTipo?: string
}

export function dashboardEstatisticasParams(values: Pick<DashboardComputed, 'ano' | 'semanaInicio' | 'semanaFim'>) {
  return buildQuery(
    {
      ano: values.ano,
      semanaInicio: values.semanaInicio,
      semanaFim: values.semanaFim,
    },
    {
      ano: 'ano',
      semanaInicio: { to: 'semana_epi_inicio' },
      semanaFim: { to: 'semana_epi_fim' },
    }
  )
}

export function dashboardTopNParams(values: Pick<DashboardComputed, 'ano' | 'semanaInicio' | 'semanaFim'>) {
  // Hoje o TopN usa o endpoint de heatmap; mapeamento igual ao de estatísticas
  return dashboardEstatisticasParams(values)
}
