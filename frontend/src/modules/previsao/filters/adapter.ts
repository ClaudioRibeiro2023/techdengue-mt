import { buildQuery } from '@/design-system/filters'

export interface PrevisaoComputed {
  ano?: number
  semanaInicio?: number
  semanaFim?: number
  municipio?: string
  horizonte?: number
  modelo?: string
}

export function previsaoNowcastingParams(values: Pick<PrevisaoComputed, 'ano' | 'semanaInicio' | 'semanaFim' | 'municipio'>) {
  return buildQuery(
    {
      ano: values.ano,
      semanaInicio: values.semanaInicio,
      semanaFim: values.semanaFim,
      municipio: values.municipio,
    },
    {
      ano: 'ano',
      semanaInicio: { to: 'semana_epi_inicio' },
      semanaFim: { to: 'semana_epi_fim' },
      municipio: { to: 'codigo_ibge' },
    }
  )
}

export function previsaoForecastParams(values: Pick<PrevisaoComputed, 'ano' | 'municipio' | 'horizonte' | 'modelo'>) {
  return buildQuery(
    {
      ano: values.ano,
      municipio: values.municipio,
      horizonte: values.horizonte,
      modelo: values.modelo,
    },
    {
      ano: 'ano',
      municipio: { to: 'codigo_ibge' },
      horizonte: { to: 'h' },
      modelo: { to: 'modelo' },
    }
  )
}
