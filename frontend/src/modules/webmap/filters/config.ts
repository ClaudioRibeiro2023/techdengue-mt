import { FilterComponent, FilterConfig, FilterOperator, DataType } from '@/design-system/filters'

const currentYear = new Date().getFullYear()

export const webmapFilterConfig: FilterConfig = {
  groups: [
    {
      id: 'periodo',
      label: 'Período',
      icon: 'Calendar',
      filters: [
        {
          id: 'ano',
          field: 'ano',
          label: 'Ano',
          dataType: DataType.NUMBER,
          operator: FilterOperator.EQ,
          component: FilterComponent.SELECT,
          options: [
            { value: String(currentYear), label: String(currentYear) },
            { value: String(currentYear - 1), label: String(currentYear - 1) },
            { value: String(currentYear - 2), label: String(currentYear - 2) },
          ],
          defaultValue: String(currentYear),
        },
        {
          id: 'semanaInicio',
          field: 'semanaInicio',
          label: 'Semana inicial',
          dataType: DataType.NUMBER,
          operator: FilterOperator.GTE,
          component: FilterComponent.NUMBER_INPUT,
          placeholder: '1',
        },
        {
          id: 'semanaFim',
          field: 'semanaFim',
          label: 'Semana final',
          dataType: DataType.NUMBER,
          operator: FilterOperator.LTE,
          component: FilterComponent.NUMBER_INPUT,
          placeholder: '53',
        },
      ],
    },
    {
      id: 'escopo',
      label: 'Escopo',
      icon: 'Target',
      filters: [
        {
          id: 'doenca',
          field: 'doenca',
          label: 'Doença',
          dataType: DataType.ENUM,
          operator: FilterOperator.EQ,
          component: FilterComponent.SELECT,
          options: [
            { value: '', label: 'Todas' },
            { value: 'DENGUE', label: 'Dengue' },
            { value: 'ZIKA', label: 'Zika' },
            { value: 'CHIKUNGUNYA', label: 'Chikungunya' },
          ],
          defaultValue: '',
        },
        {
          id: 'tipoCamada',
          field: 'tipoCamada',
          label: 'Camada',
          dataType: DataType.STRING,
          operator: FilterOperator.EQ,
          component: FilterComponent.SELECT,
          options: [
            { value: 'INCIDENCIA', label: 'Incidência' },
            { value: 'IPO', label: 'IPO (Pendências)' },
            { value: 'IDO', label: 'IDO (Depósitos)' },
          ],
          defaultValue: 'INCIDENCIA',
        },
      ],
    },
  ],
  layout: 'drawer',
  position: 'right',
  persist: { strategy: 'url', key: 'webmap-filters' },
}
