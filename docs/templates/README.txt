Etapa 2 entregue. Aqui estão os templates DOCX prontos:

Baixar template_RPT_EPI01.docx

Baixar template_RPT_EVD01.docx

Baixar template_RPT_OP01.docx

Como usar (renderização e PDF/A-1)

Preenchimento de placeholders
No backend de relatórios, substitua os campos {{...}} por valores reais (ex.: {{municipio_nome}}, {{hash_sha256}}, {{root_hash}} etc.).

Sugestão: usar docx-template/python-docx (merge) ou pipeline seu (Jinja sobre XML do DOCX).

Assinatura/Hash no rodapé
Já deixei o rodapé com report_code, versao, build_id e hash_sha256. Gere o hash do PDF final e reabra o DOCX para imprimir também o hash do pacote (se quiser a dupla conferência).

Converter para PDF e padronizar em PDF/A-1

Conversão: LibreOffice headless

soffice --headless --convert-to pdf "/caminho/RPT_EPI01_preenchido.docx" --outdir "/saida"


Padronizar em PDF/A-1 (Ghostscript):

gs -dPDFA=1 -dBATCH -dNOPAUSE -sProcessColorModel=DeviceRGB \
   -sDEVICE=pdfwrite -sOutputFile="/saida/RPT_EPI01_PDFA.pdf" \
   -sPDFACompatibilityPolicy=1 "/saida/RPT_EPI01_preenchido.pdf"


Inserir gráficos/mapas

Nos pontos marcados com [Inserir ...], seu pipeline pode:
a) gerar imagens (PNG/SVG) e injetar no DOCX antes da conversão, ou
b) renderizar um PDF parcial (gráficos) e mesclar.

Lembre-se de adicionar alt-text nas imagens (acessibilidade).

Dicionário de dados e CSVs

Garanta que o CSV exportado bata com os campos das tabelas do DOCX (EPI01 e OP01).