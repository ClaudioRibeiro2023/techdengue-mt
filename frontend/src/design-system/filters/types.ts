// Design System de Filtros - Tipos e Schemas Universais

export enum FilterOperator {
  EQ = 'eq',
  NE = 'ne',
  GT = 'gt',
  GTE = 'gte',
  LT = 'lt',
  LTE = 'lte',
  CONTAINS = 'contains',
  STARTS_WITH = 'startsWith',
  ENDS_WITH = 'endsWith',
  IN = 'in',
  NOT_IN = 'notIn',
  BETWEEN = 'between',
  IS_NULL = 'isNull',
  IS_NOT_NULL = 'isNotNull',
  IS_EMPTY = 'isEmpty',
  IS_NOT_EMPTY = 'isNotEmpty',
  BEFORE = 'before',
  AFTER = 'after',
  DATE_RANGE = 'dateRange',
  CUSTOM = 'custom',
}

export enum DataType {
  STRING = 'string',
  NUMBER = 'number',
  BOOLEAN = 'boolean',
  DATE = 'date',
  DATETIME = 'datetime',
  ARRAY = 'array',
  OBJECT = 'object',
  ENUM = 'enum',
}

export enum FilterComponent {
  TEXT_INPUT = 'textInput',
  NUMBER_INPUT = 'numberInput',
  SELECT = 'select',
  MULTI_SELECT = 'multiSelect',
  DATE_RANGE = 'dateRange',
  SEARCHABLE_SELECT = 'searchableSelect',
  NUMBER_RANGE = 'numberRange',
}

export type FilterValue = unknown
export type FilterState = Record<string, FilterValue>

export interface FilterOption {
  value: unknown
  label: string
  icon?: string
  disabled?: boolean
  metadata?: Record<string, unknown>
  children?: FilterOption[]
}

export interface OptionsSource {
  type: 'static' | 'api' | 'function'
  data?: FilterOption[]
  endpoint?: string
  method?: 'GET' | 'POST'
  params?: Record<string, unknown>
  transform?: (response: unknown) => FilterOption[]
  fetch?: () => Promise<FilterOption[]> | FilterOption[]
  cache?: boolean
  cacheTTL?: number
}

export interface ValidationRule {
  message: string
  validate: (value: unknown) => boolean
}

export interface FilterDependency {
  field: string
  operator: FilterOperator
  value: unknown
  action: 'show' | 'hide' | 'enable' | 'disable' | 'setOptions'
}

export interface FilterSchema {
  id: string
  field: string
  label: string
  dataType: DataType
  operator: FilterOperator
  allowedOperators?: FilterOperator[]
  defaultValue?: unknown
  value?: unknown
  component?: FilterComponent
  placeholder?: string
  helpText?: string
  icon?: string
  required?: boolean
  validation?: ValidationRule[]
  options?: FilterOption[]
  optionsSource?: OptionsSource
  dependsOn?: FilterDependency[]
  metadata?: Record<string, unknown>
  disabled?: boolean
  hidden?: boolean
}

export interface FilterGroup {
  id: string
  label: string
  icon?: string
  collapsed?: boolean
  filters: FilterSchema[]
  order?: number
}

export interface PersistConfig {
  strategy?: 'url' | 'localStorage'
  key?: string
}

export interface FilterConfig {
  groups: FilterGroup[]
  layout?: 'panel' | 'drawer'
  position?: 'left' | 'right'
  collapsible?: boolean
  mode?: 'instant' | 'apply'
  resetButton?: boolean
  clearButton?: boolean
  persist?: PersistConfig | boolean
  presets?: Array<{ id: string; label: string; values: FilterState }>
  onChange?: (filters: FilterState) => void
  onApply?: (filters: FilterState) => void
  onReset?: () => void
}
