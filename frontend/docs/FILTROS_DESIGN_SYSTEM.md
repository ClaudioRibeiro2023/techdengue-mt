# Design System de Filtros (Universal)

Este guia descreve como usar o sistema de filtros schema‑driven, agnóstico de domínio, criado em `src/design-system/filters`.

## Objetivos

- Padrão único de UX para filtros em toda a plataforma
- Configuração via schema TypeScript (sem duplicação)
- Motor de filtros (client-side) + serialização para URL/LocalStorage
- Layouts prontos (Painel lateral e Drawer mobile)
- Extensível: novos tipos/operadores e fontes dinâmicas de opções

## Estrutura de Pastas

```
frontend/src/design-system/filters
  ├─ types.ts                 # Tipos/schemas universais
  ├─ core/FilterEngine.ts     # Motor (apply, toURL, fromURL)
  ├─ hooks/
  │   ├─ useFilters.ts        # Hook principal
  │   └─ useFilterPersist.ts  # Persistência (URL/LocalStorage)
  ├─ components/
  │   ├─ layouts/
  │   │   ├─ FilterPanel.tsx  # Painel lateral (desktop)
  │   │   └─ FilterDrawer.tsx # Drawer (mobile)
  │   └─ primitives/
  │       ├─ TextFilter.tsx
  │       ├─ NumberFilter.tsx
  │       ├─ SelectFilter.tsx (suporta múltipla seleção)
  │       └─ DateRangeFilter.tsx
  └─ index.ts                 # Barrel export
```

## Instalação de Dependências

- Não há dependências externas obrigatórias (usa inputs nativos).
- Futuro (opcional): integrar datepicker avançado ou select virtualizado sem alterar o contrato do schema.

## Conceitos Rápidos

- `FilterConfig` define grupos, filtros, layout, persistência e callbacks.
- `FilterSchema` descreve cada filtro (campo, tipo de dado, operador, componente, opções, validações).
- `useFilters` gerencia estado, aplica filtros (quando há dados client‑side) e persiste valores.

## Exemplo Mínimo de Uso

```tsx
import { 
  FilterPanel, useFilters, 
  FilterComponent, FilterOperator, DataType, FilterConfig 
} from '@/design-system/filters'

const config: FilterConfig = {
  groups: [
    {
      id: 'periodo', label: 'Período', icon: 'Calendar',
      filters: [
        { id: 'dt', field: 'data', label: 'Data', dataType: DataType.DATE, operator: FilterOperator.DATE_RANGE, component: FilterComponent.DATE_RANGE },
      ]
    },
    {
      id: 'local', label: 'Localização', icon: 'MapPin',
      filters: [
        { id: 'mun', field: 'municipio', label: 'Município', dataType: DataType.ENUM, operator: FilterOperator.IN, component: FilterComponent.MULTI_SELECT, options: [{ value: '5103403', label: 'Cuiabá' }] }
      ]
    }
  ],
  layout: 'panel',
  position: 'right',
  persist: { strategy: 'localStorage', key: 'exemplo-filtros' }
}

export default function Page() {
  const { filters, setFilter, reset, filteredData } = useFilters({ config, data: [] })
  return (
    <div className="flex">
      <div className="flex-1">{/* conteúdo */}</div>
      <FilterPanel config={config} values={filters} onChange={setFilter} onReset={reset} />
    </div>
  )
}
```

## API (resumo)

- Tipos base: `DataType`, `FilterOperator`, `FilterComponent`.
- `FilterSchema`:
  - `field`: caminho do dado (ex. `customer.email`), `dataType`: STRING|NUMBER|DATE|...,
  - `operator`: eq, contains, in, between, dateRange...
  - `options`/`optionsSource`: opções estáticas ou dinâmicas
  - `dependsOn`: dependências entre filtros
- `FilterConfig`:
  - `groups`: grupos e ícones
  - `layout`: 'panel' | 'drawer'
  - `persist`: { strategy: 'localStorage' | 'url', key }
  - `mode`: 'instant' | 'apply' (integrar botão Aplicar via prop do painel)
- `useFilters({ config, data })` retorna:
  - `filters`, `filteredData`, `setFilter(field, value)`, `reset()`, `clear(field)`

## Boas Práticas

- Campos caros (listas grandes): usar `optionsSource` com cache/TTL.
- Usar `mode: 'apply'` quando a consulta aciona backend pesado.
- Serializar filtros em URL para compartilhamento de tela.
- Validar contraste/acessibilidade (labels e `htmlFor` já implementados nos primitivos).
- Versionar schemas se salvar presets por usuário.

## Integração por Módulo

1. Criar arquivo `filters/config.ts` no módulo com um `FilterConfig`.
2. No container/página do módulo, usar `useFilters` e renderizar `FilterPanel` ou `FilterDrawer`.
3. Se o módulo usa backend, traduza `filters` para query da API (adapter/DSL).

## Roadmap Sugerido

- `SearchableSelect` com virtualização e busca remota
- `NumberRange` com slider
- `Cascade/Tree Select` para hierarquias (UF → Município → Bairro)
- Presets nomeados por usuário
- Adapter/DSL para construir queries no backend
