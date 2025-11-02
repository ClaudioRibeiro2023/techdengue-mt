"""
Relatórios Router - Endpoints for report generation
"""
import os
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse

from app.schemas.relatorio import (
    FormatoRelatorio,
    RelatorioEPI01Response
)
from app.services.relatorio_service import RelatorioService

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

# Database connection
DB_CONN_STR = os.getenv(
    "DATABASE_URL",
    "postgresql://techdengue:techdengue@localhost:5432/techdengue"
).replace("postgresql+asyncpg://", "postgresql://")

REPORTS_DIR = os.getenv("REPORTS_DIR", "/tmp/relatorios")


@router.get("/epi01", response_model=RelatorioEPI01Response)
async def gerar_relatorio_epi01(
    competencia_inicio: str = Query(..., pattern=r"^\d{6}$", description="Período início YYYYMM"),
    competencia_fim: str = Query(..., pattern=r"^\d{6}$", description="Período fim YYYYMM"),
    municipios: Optional[str] = Query(None, description="Códigos IBGE separados por vírgula"),
    formato: FormatoRelatorio = Query(FormatoRelatorio.PDF, description="Formato: pdf ou csv"),
    incluir_grafico: bool = Query(True, description="Incluir gráficos no PDF")
):
    """
    Gera relatório epidemiológico EPI01 com indicadores de dengue.
    
    **Relatório EPI01:**
    - Resumo geral: total de casos, óbitos, incidência, letalidade
    - Detalhamento por município: casos, óbitos, incidência/100k, letalidade
    - Formato PDF/A-1 com hash SHA-256 no rodapé
    - Exportação CSV com todos os indicadores
    
    **Formatos Disponíveis:**
    - `pdf`: Relatório formatado em PDF/A-1 (padrão de arquivamento)
    - `csv`: Exportação em CSV (separador ;) para análise
    
    **Hash SHA-256:**
    - Calculado sobre o conteúdo completo do arquivo
    - Incluído nos metadados da resposta
    - Garante integridade e autenticidade do documento
    
    **Exemplo de uso (curl):**
    ```bash
    # Gerar PDF
    curl "http://localhost:8002/api/relatorios/epi01?competencia_inicio=202401&competencia_fim=202401&formato=pdf" \\
      -H "Authorization: Bearer $TOKEN" \\
      -o relatorio.json
    
    # Baixar arquivo
    curl "http://localhost:8002/api/relatorios/download/epi01_202401_202401_20240215_103045.pdf" \\
      -H "Authorization: Bearer $TOKEN" \\
      -o epi01.pdf
    
    # Gerar CSV
    curl "http://localhost:8002/api/relatorios/epi01?competencia_inicio=202401&competencia_fim=202401&formato=csv" \\
      -H "Authorization: Bearer $TOKEN"
    ```
    
    **Resposta:**
    ```json
    {
      "metadata": {
        "competencia_inicio": "202401",
        "competencia_fim": "202401",
        "dt_geracao": "2024-02-15T10:30:45Z",
        "total_municipios": 10,
        "total_casos": 5432,
        "total_obitos": 12,
        "incidencia_media": 245.67,
        "hash_sha256": "a3f5...",
        "formato": "pdf"
      },
      "arquivo": "epi01_202401_202401_20240215_103045.pdf",
      "tamanho_bytes": 125467,
      "url_download": "/api/relatorios/download/epi01_..."
    }
    ```
    
    **Performance:**
    - Geração de PDF: ~2-5s para 100 municípios
    - Geração de CSV: ~1s para 100 municípios
    - Cache recomendado para relatórios frequentes
    """
    
    # Parse municipalities filter
    municipios_list = None
    if municipios:
        municipios_list = [m.strip() for m in municipios.split(',') if m.strip()]
        for cod in municipios_list:
            if len(cod) != 7 or not cod.isdigit():
                raise HTTPException(
                    status_code=400,
                    detail=f"Código IBGE inválido: {cod}"
                )
    
    # Validate period
    if competencia_inicio > competencia_fim:
        raise HTTPException(
            status_code=400,
            detail="competencia_inicio deve ser menor ou igual a competencia_fim"
        )
    
    service = RelatorioService(DB_CONN_STR, REPORTS_DIR)
    
    try:
        return service.generate_epi01(
            competencia_inicio=competencia_inicio,
            competencia_fim=competencia_fim,
            municipios_filter=municipios_list,
            formato=formato,
            incluir_grafico=incluir_grafico
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_relatorio(filename: str):
    """
    Download de arquivo de relatório gerado.
    
    **Segurança:**
    - Apenas arquivos do diretório de relatórios são acessíveis
    - Path traversal bloqueado
    - Autenticação requerida
    
    **Exemplo:**
    ```bash
    curl "http://localhost:8002/api/relatorios/download/epi01_202401_202401_20240215_103045.pdf" \\
      -H "Authorization: Bearer $TOKEN" \\
      -o relatorio.pdf
    ```
    """
    # Security: prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=400,
            detail="Nome de arquivo inválido"
        )
    
    filepath = os.path.join(REPORTS_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail="Arquivo não encontrado"
        )
    
    # Determine media type
    if filename.endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.endswith(".csv"):
        media_type = "text/csv"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        filepath,
        media_type=media_type,
        filename=filename
    )


@router.get("/list", response_model=dict)
async def listar_relatorios(
    formato: Optional[FormatoRelatorio] = Query(None, description="Filtrar por formato")
):
    """
    Lista relatórios disponíveis para download.
    
    **Retorna:**
    ```json
    {
      "relatorios": [
        {
          "arquivo": "epi01_202401_202401_20240215_103045.pdf",
          "tamanho_bytes": 125467,
          "dt_criacao": "2024-02-15T10:30:45Z",
          "formato": "pdf"
        }
      ],
      "total": 1
    }
    ```
    """
    try:
        files = []
        for filename in os.listdir(REPORTS_DIR):
            filepath = os.path.join(REPORTS_DIR, filename)
            if not os.path.isfile(filepath):
                continue
            
            # Filter by format if specified
            if formato:
                if formato == FormatoRelatorio.PDF and not filename.endswith('.pdf'):
                    continue
                if formato == FormatoRelatorio.CSV and not filename.endswith('.csv'):
                    continue
            
            stat = os.stat(filepath)
            files.append({
                "arquivo": filename,
                "tamanho_bytes": stat.st_size,
                "dt_criacao": None,  # TODO: parse from filename
                "formato": "pdf" if filename.endswith('.pdf') else "csv"
            })
        
        # Sort by name (descending, most recent first)
        files.sort(key=lambda x: x['arquivo'], reverse=True)
        
        return {
            "relatorios": files,
            "total": len(files)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar relatórios: {str(e)}"
        )
