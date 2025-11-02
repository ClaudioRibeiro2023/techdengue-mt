"""
EPI01 Router - Endpoints for epidemiological report generation
"""
import os
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from datetime import datetime

from app.schemas.epi01 import (
    EPI01Request,
    EPI01Response,
    EPI01StatusResponse,
    ArquivoRelatorio,
    StatusRelatorio,
    FormatoRelatorio
)
from app.services.epi01_service import EPI01Service

router = APIRouter(prefix="/relatorios/epi01", tags=["Relatórios EPI01"])

# Database connection
DB_CONN_STR = os.getenv(
    "DATABASE_URL",
    "postgresql://techdengue:techdengue@localhost:5432/techdengue"
).replace("postgresql+asyncpg://", "postgresql://")

# Storage path
STORAGE_PATH = os.getenv("REPORTS_STORAGE_PATH", "/tmp/relatorios")

# In-memory job tracker (produção: usar Redis ou banco)
relatorios_status: dict = {}


def processar_relatorio_background(relatorio_id: str, request: EPI01Request):
    """
    Processa relatório em background
    
    Em produção, usar Celery task
    """
    try:
        # Atualizar status para PROCESSING
        relatorios_status[relatorio_id]['status'] = StatusRelatorio.PROCESSING
        relatorios_status[relatorio_id]['atualizado_em'] = datetime.now()
        
        service = EPI01Service(DB_CONN_STR, STORAGE_PATH)
        
        # Gerar relatório
        inicio = datetime.now()
        arquivos, tamanhos, hashes = service.gerar_relatorio(relatorio_id, request)
        fim = datetime.now()
        
        tempo_processamento = (fim - inicio).total_seconds()
        
        # Construir metadados de arquivos
        arquivos_metadata = []
        for i, (arquivo, tamanho, hash_sha) in enumerate(zip(arquivos, tamanhos, hashes)):
            formato = "pdf" if arquivo.endswith('.pdf') else "csv"
            nome_arquivo = os.path.basename(arquivo)
            
            arquivos_metadata.append(ArquivoRelatorio(
                formato=formato,
                tamanho_bytes=tamanho,
                hash_sha256=hash_sha,
                url_download=f"/api/relatorios/epi01/download/{relatorio_id}/{formato}",
                nome_arquivo=nome_arquivo
            ))
        
        # Atualizar status para COMPLETED
        relatorios_status[relatorio_id].update({
            'status': StatusRelatorio.COMPLETED,
            'concluido_em': fim,
            'atualizado_em': fim,
            'tempo_processamento_segundos': tempo_processamento,
            'arquivos': arquivos_metadata
        })
        
    except Exception as e:
        # Atualizar status para FAILED
        relatorios_status[relatorio_id].update({
            'status': StatusRelatorio.FAILED,
            'atualizado_em': datetime.now(),
            'erro_mensagem': str(e),
            'erro_detalhes': {'type': type(e).__name__}
        })


@router.post("", response_model=EPI01Response, status_code=202)
async def gerar_epi01(
    request: EPI01Request,
    background_tasks: BackgroundTasks
):
    """
    Solicita geração de relatório EPI01
    
    **Fluxo**:
    1. Recebe solicitação e retorna `relatorio_id` imediatamente (202 Accepted)
    2. Processa relatório em background
    3. Cliente deve consultar status via GET /relatorios/epi01/{relatorio_id}
    4. Quando completo (status=completed), fazer download via GET /relatorios/epi01/download/{relatorio_id}/{formato}
    
    **Formatos disponíveis**:
    - `pdf`: Relatório formatado PDF/A-1 com gráficos (padrão)
    - `csv`: Dados tabulares em CSV
    - `both`: Ambos os formatos
    
    **Filtros temporais**:
    - `ano`: Obrigatório (2000-2100)
    - `semana_epi_inicio` / `semana_epi_fim`: Opcional (1-53)
    
    **Filtros espaciais**:
    - `codigo_ibge`: Opcional (7 dígitos) - filtrar por município
    - `regional_saude`: Opcional - filtrar por regional
    
    **Filtros de doença**:
    - `doenca_tipo`: DENGUE | ZIKA | CHIKUNGUNYA | FEBRE_AMARELA | TODAS (default: DENGUE)
    
    **Opções**:
    - `incluir_graficos`: true | false (default: true) - incluir gráficos no PDF
    - `incluir_tabelas_detalhadas`: true | false (default: true)
    - `titulo_customizado`: Opcional - título personalizado
    - `observacoes`: Opcional - observações adicionais
    
    **Exemplo**:
    ```bash
    curl -X POST "http://localhost:8000/api/relatorios/epi01" \\
      -H "Content-Type: application/json" \\
      -H "Authorization: Bearer $TOKEN" \\
      -d '{
        "ano": 2024,
        "semana_epi_inicio": 1,
        "semana_epi_fim": 44,
        "doenca_tipo": "DENGUE",
        "formato": "pdf",
        "incluir_graficos": true
      }'
    ```
    
    **Response (202 Accepted)**:
    ```json
    {
      "relatorio_id": "epi01-2024-44-dengue-abc123",
      "status": "pending",
      "mensagem": "Relatório EPI01 solicitado. Processamento iniciado.",
      "formato": "pdf",
      "estimativa_tempo_segundos": 30,
      "criado_em": "2024-11-02T17:00:00Z"
    }
    ```
    
    **Próximos passos**:
    1. Aguarde alguns segundos (conforme estimativa)
    2. Consulte status: `GET /relatorios/epi01/{relatorio_id}`
    3. Quando `status=completed`, faça download: `GET /relatorios/epi01/download/{relatorio_id}/pdf`
    
    **Performance**:
    - Tempo médio: 20-40 segundos para ano completo
    - Depende do volume de dados e formato escolhido
    """
    # Gerar ID único
    relatorio_id = f"epi01-{request.ano}-{request.doenca_tipo.value.lower()}-{uuid.uuid4().hex[:8]}"
    
    # Estimar tempo de processamento
    estimativa_tempo = 30  # segundos (pode ser ajustado baseado em histórico)
    if request.formato == FormatoRelatorio.BOTH:
        estimativa_tempo = 45
    if request.incluir_graficos:
        estimativa_tempo += 10
    
    # Registrar job
    relatorios_status[relatorio_id] = {
        'relatorio_id': relatorio_id,
        'status': StatusRelatorio.PENDING,
        'formato': request.formato,
        'criado_em': datetime.now(),
        'atualizado_em': datetime.now(),
        'concluido_em': None,
        'total_registros': None,
        'tempo_processamento_segundos': None,
        'arquivos': [],
        'erro_mensagem': None,
        'erro_detalhes': None,
        'parametros': request.model_dump()
    }
    
    # Agendar processamento em background
    background_tasks.add_task(processar_relatorio_background, relatorio_id, request)
    
    return EPI01Response(
        relatorio_id=relatorio_id,
        status=StatusRelatorio.PENDING,
        mensagem="Relatório EPI01 solicitado. Processamento iniciado.",
        formato=request.formato,
        estimativa_tempo_segundos=estimativa_tempo,
        criado_em=datetime.now()
    )


@router.get("/{relatorio_id}", response_model=EPI01StatusResponse)
async def obter_status_epi01(relatorio_id: str):
    """
    Consulta status de geração do relatório EPI01
    
    **Status possíveis**:
    - `pending`: Aguardando processamento
    - `processing`: Em processamento
    - `completed`: Concluído (pronto para download)
    - `failed`: Falha no processamento
    
    **Exemplo**:
    ```bash
    curl "http://localhost:8000/api/relatorios/epi01/epi01-2024-dengue-abc123" \\
      -H "Authorization: Bearer $TOKEN"
    ```
    
    **Response (processing)**:
    ```json
    {
      "relatorio_id": "epi01-2024-dengue-abc123",
      "status": "processing",
      "formato": "pdf",
      "criado_em": "2024-11-02T17:00:00Z",
      "atualizado_em": "2024-11-02T17:00:15Z",
      "arquivos": []
    }
    ```
    
    **Response (completed)**:
    ```json
    {
      "relatorio_id": "epi01-2024-dengue-abc123",
      "status": "completed",
      "formato": "pdf",
      "criado_em": "2024-11-02T17:00:00Z",
      "atualizado_em": "2024-11-02T17:00:30Z",
      "concluido_em": "2024-11-02T17:00:30Z",
      "total_registros": 15234,
      "tempo_processamento_segundos": 28.5,
      "arquivos": [
        {
          "formato": "pdf",
          "tamanho_bytes": 524288,
          "hash_sha256": "a1b2c3d4e5f6...",
          "url_download": "/api/relatorios/epi01/download/epi01-2024-dengue-abc123/pdf",
          "nome_arquivo": "epi01-2024-dengue-abc123.pdf"
        }
      ]
    }
    ```
    
    **Polling recomendado**:
    - Consultar a cada 5-10 segundos
    - Timeout após 5 minutos
    """
    if relatorio_id not in relatorios_status:
        raise HTTPException(
            status_code=404,
            detail=f"Relatório {relatorio_id} não encontrado"
        )
    
    job_data = relatorios_status[relatorio_id]
    
    return EPI01StatusResponse(**job_data)


@router.get("/download/{relatorio_id}/{formato}")
async def download_epi01(
    relatorio_id: str,
    formato: str = Query(..., pattern=r"^(pdf|csv)$", description="pdf ou csv")
):
    """
    Download de relatório EPI01 gerado
    
    **Pré-requisitos**:
    1. Relatório deve estar com `status=completed`
    2. Formato solicitado deve ter sido gerado
    
    **Validação de integridade**:
    - Hash SHA-256 incluído nos metadados do arquivo
    - Cliente pode verificar integridade após download
    
    **Exemplo**:
    ```bash
    # Download PDF
    curl -O "http://localhost:8000/api/relatorios/epi01/download/epi01-2024-dengue-abc123/pdf" \\
      -H "Authorization: Bearer $TOKEN"
    
    # Verificar hash
    sha256sum epi01-2024-dengue-abc123.pdf
    ```
    
    **Response**:
    - Status 200: Arquivo binário (PDF ou CSV)
    - Headers:
      - `Content-Type`: application/pdf ou text/csv
      - `Content-Disposition`: attachment; filename="..."
      - `X-File-Hash`: SHA-256 do arquivo
      - `X-File-Size`: Tamanho em bytes
    
    **Erros**:
    - 404: Relatório não encontrado ou formato não disponível
    - 400: Relatório ainda não concluído
    """
    if relatorio_id not in relatorios_status:
        raise HTTPException(
            status_code=404,
            detail=f"Relatório {relatorio_id} não encontrado"
        )
    
    job_data = relatorios_status[relatorio_id]
    
    # Verificar se concluído
    if job_data['status'] != StatusRelatorio.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Relatório ainda não concluído. Status atual: {job_data['status']}"
        )
    
    # Buscar arquivo do formato solicitado
    arquivo_metadata = None
    for arq in job_data['arquivos']:
        if arq.formato == formato:
            arquivo_metadata = arq
            break
    
    if not arquivo_metadata:
        raise HTTPException(
            status_code=404,
            detail=f"Formato '{formato}' não disponível para este relatório"
        )
    
    # Caminho do arquivo
    filepath = os.path.join(STORAGE_PATH, arquivo_metadata.nome_arquivo)
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail="Arquivo não encontrado no storage"
        )
    
    # Definir media type
    media_type = "application/pdf" if formato == "pdf" else "text/csv"
    
    # Retornar arquivo
    return FileResponse(
        path=filepath,
        media_type=media_type,
        filename=arquivo_metadata.nome_arquivo,
        headers={
            "X-File-Hash": arquivo_metadata.hash_sha256,
            "X-File-Size": str(arquivo_metadata.tamanho_bytes)
        }
    )
