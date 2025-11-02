# OpenAPI v1 — TechDengue

Arquivos principais:

- `openapi-v1.yaml`: contrato **OpenAPI 3.0.3** das rotas do Edital-Core++
- `tests/curl.sh`: exemplos de chamadas cURL
- `tests/httpie.http`: coleção para HTTPie/VSCode REST Client

## Fonte da verdade

- O arquivo de referência é `openapi-v1.yaml` nesta pasta.
- O arquivo duplicado `../openapi-v1.yaml.txt` está descontinuado e permanecerá apenas para consulta histórica até migração completa.

## Como validar

- Use o **Stoplight/Prism** para mock:

  ```bash
  npx @stoplight/prism-cli mock openapi-v1.yaml
  ```

- Use **Swagger UI** (qualquer hospedagem) para ler o YAML.

## Segurança

- Todas as rotas exigem **Bearer JWT** (OIDC). Ajuste o host base conforme o seu ambiente.
