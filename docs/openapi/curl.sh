#!/usr/bin/env bash
BASE=${BASE:-http://localhost:8080/v1}
TOKEN=${TOKEN:-"REPLACE_ME"}

auth() { echo "Authorization: Bearer $TOKEN"; }

echo "== /auth/me =="
curl -s -H "$(auth)" "$BASE/auth/me" | jq .

echo "== Upload ETL =="
curl -s -H "$(auth)" -F "arquivo=@indicadores.csv" "$BASE/etl/epi/upload" | jq .

echo "== Qualidade carga =="
curl -s -H "$(auth)" "$BASE/etl/epi/qualidade/CARGA123" | jq .

echo "== Indicadores =="
curl -s -H "$(auth)" "$BASE/indicadores?municipio_cod_ibge=3106200&competencia=2025-09-30" | jq .

echo "== Criar atividade =="
curl -s -H "$(auth)" -H "Content-Type: application/json" -d '{"municipio_cod_ibge":"3106200","status":"CRIADA"}' "$BASE/atividades" | jq .

echo "== Presign evidência =="
curl -s -H "$(auth)" -H "Content-Type: application/json" -d '{"atividade_id":"UUID_ATV","filename":"foto.jpg","contentType":"image/jpeg"}' "$BASE/evidencias/presign" | jq .

echo "== Registrar evidência =="
curl -s -H "$(auth)" -H "Content-Type: application/json" -d '{"atividade_id":"UUID_ATV","uri":"s3://.../foto.jpg","hash_sha256":"sha256:...","tipo":"FOTO","capturado_em":"2025-10-31T10:00:00-03:00"}' "$BASE/evidencias" | jq .

echo "== EPI01 =="
curl -s -H "$(auth)" "$BASE/relatorios/epi01?municipio_cod_ibge=3106200&competencia=2025-09-30&formato=pdf" | jq .
