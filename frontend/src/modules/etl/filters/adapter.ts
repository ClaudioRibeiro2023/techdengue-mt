import { buildQuery } from '@/design-system/filters'

export interface ETLComputed {
  src?: 'sinan' | 'liraa' | 'ovitrampas' | 'ibge'
  ano?: number
  competencia?: string
  municipio?: string
}

export function etlListarImportsParams(values: Pick<ETLComputed, 'src' | 'ano' | 'competencia' | 'municipio'>) {
  return buildQuery(
    {
      src: values.src,
      ano: values.ano,
      competencia: values.competencia,
      municipio: values.municipio,
    },
    {
      src: 'src',
      ano: 'ano',
      competencia: 'competencia',
      municipio: { to: 'codigo_ibge' },
    }
  )
}

export function etlReprocessoParams(values: Pick<ETLComputed, 'src' | 'competencia'>) {
  return buildQuery(
    {
      src: values.src,
      competencia: values.competencia,
    },
    {
      src: 'src',
      competencia: 'competencia',
    }
  )
}
