"""
Relatórios EVD01 Router - Endpoints for evidence reports
"""
import os
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse

from app.schemas.relatorio_evd01 import (
    EVD01Request,
    EVD01Response,
    EVD01Metadata,
    FormatoRelatorio,
    TamanhoPagina,
    OrientacaoPagina,
    MerkleTree as MerkleTreeSchema
)
from app.services.atividade_service import AtividadeService
from app.services.evidencia_service import EvidenciaService
from app.services.evd01_generator import EVD01Generator

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

# Database connection
DB_CONN_STR = os.getenv(
    "DATABASE_URL",
    "postgresql://techdengue:techdengue@localhost:5432/techdengue"
).replace("postgresql+asyncpg://", "postgresql://")

# Reports output directory
REPORTS_DIR = os.getenv("REPORTS_DIR", "/tmp/reports")


@router.get("/evd01", response_model=EVD01Response)
async def generate_evd01(
    atividade_id: Annotated[int, Query(gt=0, description="ID da atividade")],
    tamanho_pagina: Annotated[TamanhoPagina, Query()] = TamanhoPagina.A4,
    orientacao: Annotated[OrientacaoPagina, Query()] = OrientacaoPagina.RETRATO,
    formato: Annotated[FormatoRelatorio, Query()] = FormatoRelatorio.PDF,
    incluir_miniaturas: Annotated[bool, Query()] = True,
    incluir_qrcode: Annotated[bool, Query()] = True
):
    """
    Gerar relatório EVD01 de evidências.
    
    **Relatório EVD01:**
    - Relatório oficial de evidências coletadas em campo
    - Formato PDF/A-1 para arquivamento de longo prazo
    - Inclui Merkle Tree para verificação de integridade
    - Suporta múltiplos tamanhos de página (A1, A4)
    - QR Code para verificação digital
    
    **Tamanhos de Página:**
    - **A4** (210x297mm): Uso geral, impressão padrão
      - Retrato: Grid 4x4 (16 miniaturas/página)
      - Paisagem: Grid 5x3 (15 miniaturas/página)
    - **A1** (594x841mm): Apresentações, painéis
      - Retrato: Grid 8x8 (64 miniaturas/página)
      - Paisagem: Grid 10x6 (60 miniaturas/página)
    
    **Conteúdo do Relatório:**
    1. Cabeçalho com dados da atividade
    2. Merkle Tree Root Hash
    3. Lista de evidências com hashes individuais
    4. Grid de miniaturas (se incluir_miniaturas=true)
    5. QR Code de verificação (se incluir_qrcode=true)
    6. Footer com metadata e timestamp
    
    **Merkle Tree:**
    - Árvore binária de hashes SHA-256
    - Root hash representa todo o conjunto
    - Qualquer alteração invalida o hash
    - Verificação individual de evidências
    
    **Exemplos:**
    ```bash
    # Relatório A4 padrão
    curl "http://localhost:8001/api/relatorios/evd01?atividade_id=123"
    
    # Relatório A1 paisagem para painel
    curl "http://localhost:8001/api/relatorios/evd01?atividade_id=123&tamanho_pagina=A1&orientacao=paisagem"
    
    # Apenas JSON (sem PDF)
    curl "http://localhost:8001/api/relatorios/evd01?atividade_id=123&formato=json"
    ```
    
    **Retorna:**
    - 200: Relatório gerado com sucesso
    - 404: Atividade não encontrada
    - 400: Nenhuma evidência encontrada
    
    **Response:**
    ```json
    {
      "metadata": {
        "atividade_id": 123,
        "atividade_tipo": "VISTORIA",
        "municipio_cod_ibge": "5103403",
        "dt_geracao": "2024-01-15T14:30:00Z",
        "total_evidencias": 5,
        "merkle_root_hash": "abc123...",
        "formato": "pdf",
        "tamanho_pagina": "A4",
        "orientacao": "portrait"
      },
      "arquivo": "EVD01_Atividade_123_20240115_143000.pdf",
      "tamanho_bytes": 524288,
      "url_download": "/relatorios/download/EVD01_Atividade_123_20240115_143000.pdf",
      "qrcode_url": "data:image/png;base64,...",
      "merkle_tree": {
        "root_hash": "abc123...",
        "leaf_count": 5,
        "tree_depth": 3,
        "leaves": [
          {
            "evidencia_id": 456,
            "hash": "def456..."
          }
        ]
      }
    }
    ```
    """
    atividade_service = AtividadeService(DB_CONN_STR)
    evidencia_service = EvidenciaService(DB_CONN_STR)
    
    # Get activity
    atividade = atividade_service.get_by_id(atividade_id)
    if not atividade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atividade {atividade_id} não encontrada"
        )
    
    # Get evidences
    evidencias_list = evidencia_service.list_by_atividade(atividade_id)
    if evidencias_list.total == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Atividade {atividade_id} não possui evidências"
        )
    
    # Convert to dict for PDF generation
    atividade_dict = {
        "id": atividade.id,
        "tipo": atividade.tipo.value,
        "status": atividade.status.value,
        "municipio_cod_ibge": atividade.municipio_cod_ibge,
        "criado_em": atividade.criado_em.isoformat()
    }
    
    evidencias_dict = [
        {
            "id": ev.id,
            "tipo": ev.tipo.value,
            "hash_sha256": ev.hash_sha256,
            "tamanho_bytes": ev.tamanho_bytes,
            "criado_em": ev.criado_em.isoformat()
        }
        for ev in evidencias_list.items
    ]
    
    try:
        # Generate PDF
        generator = EVD01Generator(output_dir=REPORTS_DIR)
        filepath, filename, merkle_dict = generator.generate(
            atividade=atividade_dict,
            evidencias=evidencias_dict,
            tamanho_pagina=tamanho_pagina,
            orientacao=orientacao,
            incluir_miniaturas=incluir_miniaturas,
            incluir_qrcode=incluir_qrcode
        )
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Build response
        metadata = EVD01Metadata(
            atividade_id=atividade.id,
            atividade_tipo=atividade.tipo.value,
            municipio_cod_ibge=atividade.municipio_cod_ibge,
            municipio_nome="",  # TODO: lookup municipality name
            dt_geracao=atividade.criado_em,
            total_evidencias=len(evidencias_dict),
            merkle_root_hash=merkle_dict["root_hash"],
            formato=formato,
            tamanho_pagina=tamanho_pagina,
            orientacao=orientacao
        )
        
        # Convert merkle dict to schema
        merkle_tree = MerkleTreeSchema(
            root_hash=merkle_dict["root_hash"],
            leaf_count=merkle_dict["leaf_count"],
            tree_depth=merkle_dict["tree_depth"],
            leaves=[
                {"evidencia_id": leaf["evidencia_id"], "filename": "", 
                 "hash_sha256": leaf["hash"], "tamanho_bytes": 0, "tipo": ""}
                for leaf in merkle_dict["leaves"]
            ]
        )
        
        return EVD01Response(
            metadata=metadata,
            arquivo=filename,
            tamanho_bytes=file_size,
            url_download=f"/relatorios/download/{filename}",
            qrcode_url=None,  # TODO: generate QR code data URL
            merkle_tree=merkle_tree
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_report(filename: str):
    """
    Download relatório gerado.
    
    **Segurança:**
    - Path traversal protection
    - Apenas arquivos do diretório de relatórios
    - Verificação de existência
    
    **Exemplo:**
    ```bash
    curl -O "http://localhost:8001/api/relatorios/download/EVD01_Atividade_123_20240115_143000.pdf"
    ```
    
    **Retorna:**
    - 200: Arquivo PDF
    - 404: Arquivo não encontrado
    - 400: Nome de arquivo inválido
    """
    # Sanitize filename (path traversal protection)
    filename = os.path.basename(filename)
    
    if not filename.startswith("EVD01_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de arquivo inválido"
        )
    
    filepath = os.path.join(REPORTS_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    return FileResponse(
        path=filepath,
        media_type="application/pdf",
        filename=filename
    )
