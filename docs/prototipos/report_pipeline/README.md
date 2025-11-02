# Pipeline de Relatórios — TechDengue

Este pacote gera relatórios a partir de **templates DOCX** (com placeholders `{{chave}}`) e insere imagens onde encontrar tokens no formato:
```
[IMG:key:width_in_inches:align]
```
Ex.: `[IMG:chart_tendencia:5:CENTER]`

## Pré-requisitos
- Python 3.10+
- `pip install python-docx matplotlib pillow`
- (Opcional) **LibreOffice** (`soffice`) para converter DOCX→PDF
- (Opcional) **Ghostscript** (`gs`) para PDF/A-1

## Arquivos
- `merge_reports.py` — script principal
- `data_epi01.json` — exemplo de dados (EPI01)
- `images_epi01.json` — exemplo de mapeamento de imagens
- `chart_tendencia.png` — exemplo de gráfico
- `map_thematic.png` — placeholder de mapa

## Uso
1) Gere/edite seu template, por exemplo `template_RPT_EPI01.docx` (criado na Etapa 2).
   - No corpo, você pode inserir:
     - Placeholders: `{municipio_nome}`, `{competencia}`, etc.
     - Tokens de imagem, por exemplo na seção "Tendência Temporal":
       ```
       [IMG:chart_tendencia:5:CENTER]
       ```
     - Na seção "Mapa Temático":
       ```
       [IMG:map_temat:6:CENTER]
       ```

2) Rode o merge (substitua paths conforme seu ambiente):
```bash
python3 merge_reports.py   --template "/mnt/data/template_RPT_EPI01.docx"   --data "/mnt/data/report_pipeline/data_epi01.json"   --images "/mnt/data/report_pipeline/images_epi01.json"   --out "/mnt/data/report_pipeline/RPT_EPI01_preenchido.docx"   --pdf --pdfa
```

- Se **LibreOffice** estiver instalado, o PDF será gerado ao lado do DOCX.
- Se **Ghostscript** estiver instalado, o **PDF/A-1** também será gerado.

## Dicas
- Para EVD01, crie um mapeamento de imagens para as evidências (miniaturas) e use o token `[IMG:evid_1:3:LEFT]` etc.
- O hash (sha256) do PDF final pode ser calculado após a geração e reinserido em um rodapé se desejar a "dupla conferência".
- Padronize as versões dos relatórios e mantenha um **catálogo JSON** com os campos/tipos.

