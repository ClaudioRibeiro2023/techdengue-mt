# Protótipos e Exemplos de Referência

Este diretório contém códigos de referência, protótipos e exemplos que foram criados durante o planejamento do TechDengue.

**⚠️ Atenção**: Estes NÃO são códigos de produção. São exemplos/mockups para demonstrar conceitos técnicos mencionados no plano de implementação.

---

## Conteúdo

### 1. pwa_offline/

**Descrição**: Exemplos TypeScript de implementação PWA offline-first.

**Arquivos**:
- `indexeddb.ts`: Schema e operações IndexedDB para atividades, evidências, fila de sync
- `sw.js`: Service Worker com cache strategies (cache-first assets, network-first data)
- `syncQueue.ts`: Fila de sincronização idempotente (LWW, exponential backoff)
- `hooks.ts`: React hooks customizados (`useOfflineSync`, `useNetworkStatus`)
- `types.ts`: TypeScript types compartilhados
- `manifest.webmanifest`: Web App Manifest (PWA)

**Referência no Plano**: ADR-003, ADR-009, Seção 3.3 (Campo e Evidências)

**Status**: Exemplo de referência (não implementado)

---

### 2. windsurf_skeleton/

**Descrição**: Componentes React skeleton para demonstrar estrutura do frontend.

**Arquivos principais**:
- `App.tsx`: App principal com rotas e contexto de auth
- `Mapa.tsx`, `MapView.tsx`: Componentes de mapa (Leaflet)
- `Agenda.tsx`, `Atividade.tsx`: Gestão de atividades campo
- `ETL.tsx`, `UploadETL.tsx`: Interface upload CSV EPI
- `Admin.tsx`: Painel administrativo
- `Operacional.tsx`: Dashboard operacional
- `Relatorios.tsx`: Geração de relatórios
- `Layout.tsx`, `Navbar.tsx`, `Sidebar.tsx`: Estrutura de layout
- `KPI.tsx`, `DataTable.tsx`: Componentes reutilizáveis
- `api.ts`, `auth.ts`, `format.ts`: Utilitários
- `routes.tsx`: Definição de rotas React Router
- `index.html`, `main.tsx`, `index.css`: Entry points

**Referência no Plano**: ADR-006, ADR-007, Seção 3.2 (Mapa Vivo)

**Status**: Skeleton de referência (não implementado)

---

### 3. report_pipeline/

**Descrição**: Pipeline Python para geração de relatórios (exemplo).

**Arquivos**:
- `merge_reports.py`: Script Python que mescla dados + imagens → HTML → PDF
- `data_epi01.json`: Exemplo de dados epidemiológicos estruturados
- `images_epi01.json`: Mapeamento de imagens (gráficos, mapas)
- `chart_tendencia.png`, `map_thematic.png`: Imagens de exemplo
- `README.md`: Documentação do pipeline

**Referência no Plano**: Seção 3.4 (Relatórios EPI01/EVD01)

**Status**: Exemplo de referência (não implementado)

---

## Uso

Estes arquivos servem como:

1. **Documentação técnica** de padrões e decisões arquiteturais (ADRs)
2. **Referência de implementação** para o time de desenvolvimento
3. **Prova de conceito** de viabilidade técnica

**NÃO devem ser copiados diretamente para produção.** Servem apenas como guia.

---

## Próximos Passos

Quando a estrutura monorepo for criada:

- `/frontend` → Implementação real dos componentes (baseado em windsurf_skeleton/)
- `/epi-api`, `/campo-api`, `/relatorios-api` → Implementação real das APIs (FastAPI)
- `/db/flyway` → Migrações reais (baseado em `docs/1_Fundacoes.md`)

Os protótipos permanecerão aqui como referência histórica.

---

**Data**: 2025-11-01  
**Status**: Arquivos de referência (pré-implementação)
