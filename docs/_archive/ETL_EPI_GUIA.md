# Guia de Upload ETL EPI

## Visão Geral

O endpoint `/api/etl/epi/upload` permite o upload de arquivos CSV no formato SINAN/SIVEP-DDA contendo casos de dengue para persistência no banco de dados TimescaleDB.

## Formato do CSV

### Especificação

- **Separador**: ponto-e-vírgula (`;`)
- **Encoding**: UTF-8
- **Header**: Obrigatório na primeira linha
- **Formato de datas**: `YYYY-MM-DD`

### Colunas Obrigatórias

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `dt_notificacao` | date | Data da notificação | 2024-01-15 |
| `dt_sintomas` | date | Data dos primeiros sintomas | 2024-01-13 |
| `municipio_cod_ibge` | string(7) | Código IBGE do município (MT) | 5103403 |
| `sexo` | char(1) | Sexo: M, F ou I | F |
| `idade` | int | Idade em anos (0-120) | 28 |
| `gestante` | char(1) | 1-3T, 4-idade ign, 8-NÃO, 9-ign, N-NA | N |
| `classificacao_final` | enum | DENGUE, DENGUE_GRAVE, DENGUE_SINAIS_ALARME, DESCARTADO, INCONCLUSIVO | DENGUE |
| `criterio_confirmacao` | enum | LABORATORIAL, CLINICO_EPIDEMIOLOGICO, EM_INVESTIGACAO | LABORATORIAL |
| `febre` | int(0/1) | Presença de febre | 1 |
| `cefaleia` | int(0/1) | Presença de cefaleia | 1 |
| `dor_retroocular` | int(0/1) | Dor retroocular | 1 |
| `mialgia` | int(0/1) | Mialgia | 1 |
| `artralgia` | int(0/1) | Artralgia | 1 |
| `exantema` | int(0/1) | Exantema | 0 |
| `vomito` | int(0/1) | Vômito | 0 |
| `nausea` | int(0/1) | Náusea | 0 |
| `dor_abdominal` | int(0/1) | Dor abdominal | 0 |
| `plaquetas_baixas` | int(0/1) | Plaquetopenia (<100k) | 0 |
| `hemorragia` | int(0/1) | Manifestações hemorrágicas | 0 |
| `hepatomegalia` | int(0/1) | Hepatomegalia | 0 |
| `acumulo_liquidos` | int(0/1) | Acúmulo de líquidos | 0 |
| `diabetes` | int(0/1) | Diabetes | 0 |
| `hipertensao` | int(0/1) | Hipertensão | 0 |
| `evolucao` | enum | CURA, OBITO, OBITO_OUTRA_CAUSA, IGNORADO | CURA |
| `dt_obito` | date | Data do óbito (opcional) | |
| `dt_encerramento` | date | Data de encerramento (opcional) | 2024-01-30 |

## Regras de Validação

### Validações de Campo

1. **Código IBGE**:
   - Deve ter exatamente 7 dígitos
   - Deve iniciar com `51` (estado de Mato Grosso)
   
2. **Datas**:
   - Não podem ser futuras
   - `dt_sintomas` deve ser ≤ `dt_notificacao`
   - `dt_obito` obrigatória se `evolucao = OBITO`

3. **Demografia**:
   - Idade entre 0 e 120 anos
   - Campo `gestante` relevante apenas para mulheres (10-49 anos)

4. **Flags clínicos**:
   - Todos os campos de sintomas/sinais devem ser 0 ou 1

### Validações Cruzadas

- Caso com `evolucao=OBITO` deve ter `dt_obito` informada (aviso se ausente)
- Caso `DESCARTADO` com critério `LABORATORIAL` gera aviso
- Gestante informada para sexo != F gera aviso

### Critérios de Aprovação

Para o arquivo ser aprovado para carga:
- **Taxa de qualidade ≥ 95%** (linhas válidas / total)
- **Erros bloqueantes < 5%** do total de linhas

## Uso via API

### Autenticação

Todos os endpoints ETL requerem autenticação Bearer token (OIDC):

```bash
export TOKEN="seu_token_aqui"
```

### Upload de Arquivo

**Endpoint**: `POST /api/etl/epi/upload`

**Parâmetros**:
- `file` (form-data): Arquivo CSV
- `competencia` (form-data): YYYYMM (ex: 202401 para Jan/2024)
- `sobrescrever` (form-data): true/false (padrão: false)

**Exemplo com curl**:

```bash
curl -X POST "http://localhost:8000/api/etl/epi/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@dados_dengue_202401.csv" \
  -F "competencia=202401" \
  -F "sobrescrever=false"
```

**Exemplo com httpie**:

```bash
http --form POST localhost:8000/api/etl/epi/upload \
  Authorization:"Bearer $TOKEN" \
  file@dados_dengue_202401.csv \
  competencia=202401 \
  sobrescrever=false
```

**Exemplo com Python**:

```python
import requests

url = "http://localhost:8000/api/etl/epi/upload"
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("dados_dengue_202401.csv", "rb")}
data = {"competencia": "202401", "sobrescrever": "false"}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

### Resposta de Sucesso (200)

```json
{
  "mensagem": "Upload concluído com sucesso. 1543 casos inseridos na competência 202401.",
  "relatorio": {
    "arquivo": "dados_dengue_202401.csv",
    "dt_processamento": "2024-01-15T10:30:00Z",
    "total_linhas": 1543,
    "linhas_validas": 1543,
    "linhas_com_erro": 0,
    "linhas_com_aviso": 2,
    "erros": [],
    "avisos": [
      {
        "linha": 45,
        "campo": "dt_obito",
        "valor": "null",
        "aviso": "Evolução = OBITO mas dt_obito não informada"
      }
    ],
    "periodo_inicio": "2024-01-01",
    "periodo_fim": "2024-01-31",
    "municipios_unicos": 12,
    "total_casos_confirmados": 1421,
    "total_obitos": 2,
    "taxa_qualidade": 100.0,
    "aprovado_para_carga": true
  },
  "casos_inseridos": 1543
}
```

### Resposta de Erro (400)

```json
{
  "mensagem": "Arquivo não aprovado para carga. Taxa de qualidade: 87.3%. Corrija os 45 erros e tente novamente.",
  "relatorio": {
    "arquivo": "dados_dengue_202401.csv",
    "dt_processamento": "2024-01-15T10:30:00Z",
    "total_linhas": 1543,
    "linhas_validas": 1347,
    "linhas_com_erro": 45,
    "linhas_com_aviso": 5,
    "erros": [
      {
        "linha": 23,
        "campo": "municipio_cod_ibge",
        "valor": "3550308",
        "erro": "Código IBGE deve ser de município de MT (inicia com 51)",
        "severidade": "ERRO"
      },
      {
        "linha": 67,
        "campo": "dt_sintomas",
        "valor": "2024-02-15",
        "erro": "Data de sintomas posterior à data de notificação",
        "severidade": "ERRO"
      }
    ],
    "avisos": [],
    "periodo_inicio": null,
    "periodo_fim": null,
    "municipios_unicos": 0,
    "total_casos_confirmados": 0,
    "total_obitos": 0,
    "taxa_qualidade": 87.3,
    "aprovado_para_carga": false
  },
  "casos_inseridos": 0
}
```

## Outros Endpoints

### Listar Competências Carregadas

```bash
curl "http://localhost:8000/api/etl/epi/competencias" \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta**:
```json
{
  "competencias": ["202401", "202312", "202311"],
  "total": 3
}
```

### Estatísticas de Competência

```bash
curl "http://localhost:8000/api/etl/epi/competencias/202401/stats" \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta**:
```json
{
  "competencia": "202401",
  "total_casos": 1543,
  "casos_confirmados": 1421,
  "obitos": 2
}
```

## Fluxo de Trabalho Recomendado

1. **Preparar CSV**: Exportar dados do SINAN/SIVEP no formato especificado
2. **Testar localmente**: Validar estrutura e conteúdo antes do upload
3. **Upload inicial**: Enviar com `sobrescrever=false` para primeira carga
4. **Revisar relatório**: Analisar erros e avisos retornados
5. **Corrigir dados**: Se necessário, corrigir CSV e reenviar
6. **Atualizar competência**: Se precisar substituir, usar `sobrescrever=true`

## Exemplo de CSV Válido

```csv
dt_notificacao;dt_sintomas;municipio_cod_ibge;sexo;idade;gestante;classificacao_final;criterio_confirmacao;febre;cefaleia;dor_retroocular;mialgia;artralgia;exantema;vomito;nausea;dor_abdominal;plaquetas_baixas;hemorragia;hepatomegalia;acumulo_liquidos;diabetes;hipertensao;evolucao;dt_obito;dt_encerramento
2024-01-15;2024-01-13;5103403;F;28;N;DENGUE;LABORATORIAL;1;1;1;1;1;0;0;0;0;0;0;0;0;0;0;CURA;;2024-01-30
2024-01-16;2024-01-14;5103403;M;45;;DENGUE;CLINICO_EPIDEMIOLOGICO;1;1;0;1;1;1;0;0;0;0;0;0;0;1;1;CURA;;2024-01-31
```

## Troubleshooting

### Erro "Colunas obrigatórias ausentes"
- Verifique que todas as 26 colunas estão presentes no header
- Confirme que os nomes das colunas estão exatamente como especificado

### Erro "Código IBGE deve ser de município de MT"
- Códigos de municípios de MT começam com `51`
- Verifique na tabela de municípios do IBGE

### Taxa de qualidade baixa
- Revise os erros mais frequentes no relatório
- Corrija em lote no CSV antes de reenviar
- Use ferramentas de validação pré-upload (ex: pandas)

### Competência já existe
- Use `sobrescrever=true` para substituir dados
- Ou escolha outra competência se for upload novo

## Contato e Suporte

Para dúvidas ou problemas:
- Consulte a documentação completa em `docs/`
- Abra uma issue no repositório do projeto
- Entre em contato com a equipe de desenvolvimento
