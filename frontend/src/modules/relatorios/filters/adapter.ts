import { buildQuery } from '@/design-system/filters'

export interface ReportsComputed {
  ano?: number
  semanaInicio?: number
  semanaFim?: number
  doencaTipo?: string
  municipio?: string
  fonte?: 'sinan' | 'liraa' | 'ovitrampas' | 'ibge'
}

export function epiRelatoriosParams(values: Pick<ReportsComputed, 'ano' | 'semanaInicio' | 'semanaFim' | 'doencaTipo' | 'municipio'>) {
  return buildQuery(
    {
      ano: values.ano,
      semanaInicio: values.semanaInicio,
      semanaFim: values.semanaFim,
      doencaTipo: values.doencaTipo,
      municipio: values.municipio,
    },
    {
      ano: 'ano',
      semanaInicio: { to: 'semana_epi_inicio' },
      semanaFim: { to: 'semana_epi_fim' },
      doencaTipo: { to: 'doenca_tipo' },
      municipio: { to: 'codigo_ibge' },
    }
  )
}

export function exportacoesParams(values: Pick<ReportsComputed, 'fonte' | 'ano' | 'municipio'>) {
  return buildQuery(
    {
      fonte: values.fonte,
      ano: values.ano,
      municipio: values.municipio,
    },
    {
      fonte: { to: 'fonte_dados' },
      ano: 'ano',
      municipio: { to: 'codigo_ibge' },
    }
  )
}
