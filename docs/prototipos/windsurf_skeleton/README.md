# Skeleton Windsurf — TechDengue (Edital-Core++)

Esqueleto React + Tailwind minimalista para iniciar as telas:
- **/mapa**: visualização de indicadores (EPI)
- **/etl**: upload e qualidade de dados
- **/operacional**: KPIs e produtividade (Operação)
- **/relatorios**: gatilhos de geração/baixa (EPI01/EVD01/OP01)
- **/admin**: usuários, territórios, parâmetros
- **PWA**: **/agenda**, **/atividade/:id** (quando integrar Etapa 3)

## Como usar no Windsurf
1. Crie um projeto React + Vite (ou similar).
2. Copie a pasta `src/` e `public/` para o projeto.
3. Garanta que o Tailwind esteja habilitado (as diretivas já estão em `src/index.css`).
4. Ajuste `API_BASE` em `src/lib/api.ts` para apontar ao seu backend.

## Navegação
- `App.tsx` define o layout e usa `routes.tsx` para trocar de página.
- Navbar/Sidebar simples com links.
