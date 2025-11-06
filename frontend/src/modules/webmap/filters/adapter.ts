import { buildQuery } from '@/design-system/filters'

export interface WebmapComputed {
  ano: number
  semanaInicio?: number
  semanaFim?: number
  doenca?: string
  tipoCamada: string
}

export function webmapHeatmapParams(values: Pick<WebmapComputed, 'ano' | 'semanaInicio' | 'semanaFim' | 'doenca'>) {
  return buildQuery(
    {
      ano: values.ano,
      semanaInicio: values.semanaInicio,
      semanaFim: values.semanaFim,
      doenca: values.doenca,
    },
    {
      ano: 'ano',
      semanaInicio: { to: 'semana_epi_inicio' },
      semanaFim: { to: 'semana_epi_fim' },
      doenca: { to: 'doenca_tipo' },
    }
  )
}

export function webmapCamadasParams(values: Pick<WebmapComputed, 'ano' | 'tipoCamada' | 'doenca'>) {
  const tipo = (values.tipoCamada || 'incidencia').toLowerCase()
  const competenciaInicio = `${values.ano}01`
  const competenciaFim = `${values.ano}12`
  const base = buildQuery({ doenca: values.doenca }, { doenca: { to: 'doenca_tipo' } })
  base.set('tipo_camada', tipo)
  base.set('competencia_inicio', competenciaInicio)
  base.set('competencia_fim', competenciaFim)
  return base
}
