# Flyway Migrations - TechDengue

Este diretório contém as migrações SQL do banco de dados, gerenciadas pelo Flyway.

## Estrutura

```
migrations/
├── V1__create_extensions_and_enums.sql
├── V2__create_tables.sql
├── V3__create_indexes.sql
└── V4__insert_seeds.sql
```

## Como criar as migrações

As migrações devem ser baseadas no DDL completo documentado em `docs/1_Fundacoes.md`.

### V1 — Extensões e Enums

```sql
-- PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Timescale
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Enums
CREATE TYPE papel AS ENUM ('GESTOR', 'VIGILANCIA', 'CAMPO', 'ADMIN');
CREATE TYPE atividade_status AS ENUM ('CRIADA', 'EM_ANDAMENTO', 'ENCERRADA');
CREATE TYPE atividade_origem AS ENUM ('MANUAL', 'DENUNCIA', 'ALERTA');
-- ...outros enums conforme docs/1_Fundacoes.md
```

### V2 — Tabelas

Criar todas as tabelas conforme `docs/1_Fundacoes.md`:
- `usuario` (com RLS habilitado)
- `municipio`, `distrito`, `setor`, `quadra`
- `indicador_epi` (hypertable Timescale por `competencia`)
- `atividade`, `evidencia`, `insumo`
- `relatorio`
- `audit_log`

### V3 — Índices

```sql
-- Índices espaciais (GiST)
CREATE INDEX idx_municipio_geom ON municipio USING GIST (geom);
CREATE INDEX idx_atividade_localizacao ON atividade USING GIST (localizacao);

-- Índices temporais
CREATE INDEX idx_indicador_epi_competencia ON indicador_epi (competencia DESC);
CREATE INDEX idx_atividade_criado_em ON atividade (criado_em DESC);

-- Índices compostos
CREATE INDEX idx_atividade_status_municipio ON atividade (status, municipio_cod_ibge);
-- ...outros índices conforme docs/1_Fundacoes.md
```

### V4 — Seeds

```sql
-- Municípios MT (exemplo)
INSERT INTO municipio (cod_ibge, nome, uf, geom) VALUES
  ('5103403', 'Cuiabá', 'MT', ST_GeomFromText('POINT(...)', 4326)),
  ('5107040', 'Várzea Grande', 'MT', ST_GeomFromText('POINT(...)', 4326));
-- ...outros seeds
```

## Execução

### Local (docker-compose)

```bash
cd infra
docker-compose up flyway
```

### Manual

```bash
flyway -url=jdbc:postgresql://localhost:5432/techdengue \
       -user=techdengue \
       -password=techdengue \
       -locations=filesystem:./migrations \
       migrate
```

## Convenções

- Prefixo `V` + número sequencial + `__` + descrição snake_case
- Ordem numérica estrita (V1, V2, V3...)
- Idempotência: usar `IF NOT EXISTS`, `IF EXISTS`, etc.
- Uma transação por arquivo (padrão Flyway)
- Rollback manual (criar `U{version}__description.sql` se necessário)

## Referência

- DDL completo: `docs/1_Fundacoes.md`
- Flyway docs: https://flywaydb.org/documentation/
