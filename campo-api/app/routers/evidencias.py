"""
Evidencias Router - Endpoints for evidence/media management
"""
import os
from typing import List, Optional, Annotated
from fastapi import APIRouter, HTTPException, Path, Query, status

from app.schemas.evidencia import (
    PresignedURLRequest,
    PresignedURLResponse,
    EvidenciaCreate,
    EvidenciaResponse,
    EvidenciaList
)
from app.services.s3_service import S3Service
from app.services.evidencia_service import EvidenciaService
from app.services.atividade_service import AtividadeService

router = APIRouter(tags=["Evidências"])

# Database connection
DB_CONN_STR = os.getenv(
    "DATABASE_URL",
    "postgresql://techdengue:techdengue@localhost:5432/techdengue"
).replace("postgresql+asyncpg://", "postgresql://")

# S3 service
s3_service = S3Service()


@router.post(
    "/atividades/{atividade_id}/evidencias/presigned-url",
    response_model=PresignedURLResponse,
    status_code=status.HTTP_200_OK
)
async def generate_presigned_upload_url(
    atividade_id: Annotated[int, Path(gt=0, description="ID da atividade")],
    request: PresignedURLRequest
):
    """
    Gerar URL pré-assinada para upload direto ao S3.
    
    **Fluxo:**
    1. Cliente solicita presigned URL com metadata do arquivo
    2. Servidor valida e retorna URL temporária (5min)
    3. Cliente faz PUT direto ao S3 com o arquivo
    4. Cliente chama POST /evidencias para registrar no banco
    
    **Content-Types Permitidos:**
    - `image/jpeg`, `image/png`, `image/webp` (Fotos)
    - `video/mp4`, `video/quicktime` (Vídeos)
    - `application/pdf` (Documentos)
    - `audio/mpeg`, `audio/wav` (Áudio)
    
    **Limites:**
    - Tamanho máximo: 50MB
    - Validade da URL: 5 minutos
    
    **Exemplo de uso:**
    ```bash
    # 1. Obter presigned URL
    RESPONSE=$(curl -X POST "http://localhost:8001/api/atividades/123/evidencias/presigned-url" \\
      -H "Content-Type: application/json" \\
      -d '{
        "filename": "foto_fachada.jpg",
        "content_type": "image/jpeg",
        "tamanho_bytes": 2048576
      }')
    
    # 2. Extrair URL
    UPLOAD_URL=$(echo $RESPONSE | jq -r '.upload_url')
    UPLOAD_ID=$(echo $RESPONSE | jq -r '.upload_id')
    
    # 3. Upload direto ao S3
    curl -X PUT "$UPLOAD_URL" \\
      -H "Content-Type: image/jpeg" \\
      --upload-file foto_fachada.jpg
    
    # 4. Registrar no banco
    curl -X POST "http://localhost:8001/api/atividades/123/evidencias" \\
      -H "Content-Type: application/json" \\
      -d '{
        "atividade_id": 123,
        "tipo": "FOTO",
        "upload_id": "'$UPLOAD_ID'",
        "hash_sha256": "abc123...",
        "tamanho_bytes": 2048576,
        "url_s3": "atividades/123/uuid_foto_fachada.jpg"
      }'
    ```
    
    **Retorna:**
    - 200: Presigned URL gerada
    - 404: Atividade não encontrada
    - 400: Parâmetros inválidos
    """
    # Verify activity exists
    atividade_service = AtividadeService(DB_CONN_STR)
    atividade = atividade_service.get_by_id(atividade_id)
    
    if not atividade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atividade {atividade_id} não encontrada"
        )
    
    try:
        # Generate presigned URL
        result = s3_service.generate_presigned_upload_url(
            atividade_id=atividade_id,
            filename=request.filename,
            content_type=request.content_type,
            expires_in=300  # 5 minutes
        )
        
        return PresignedURLResponse(
            upload_url=result["upload_url"],
            upload_id=result["upload_id"],
            expires_in=result["expires_in"],
            fields={"key": result["object_key"]}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar presigned URL: {str(e)}"
        )


@router.post(
    "/atividades/{atividade_id}/evidencias",
    response_model=EvidenciaResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_evidencia(
    atividade_id: Annotated[int, Path(gt=0)],
    evidencia: EvidenciaCreate
):
    """
    Registrar evidência após upload bem-sucedido ao S3.
    
    **Pré-requisitos:**
    1. Ter obtido presigned URL via `/presigned-url`
    2. Upload concluído com sucesso no S3
    3. Hash SHA-256 calculado no cliente
    
    **Validações:**
    - Atividade deve existir
    - upload_id deve corresponder à presigned URL gerada
    - hash_sha256 deve ter 64 caracteres hexadecimais
    - url_s3 deve corresponder ao object_key retornado
    
    **Metadata Esperado (opcional):**
    ```json
    {
      "exif": {
        "make": "Apple",
        "model": "iPhone 13",
        "datetime_original": "2024-01-15T14:30:00",
        "gps_latitude": -15.6014,
        "gps_longitude": -56.0967,
        "image_width": 4032,
        "image_height": 3024
      },
      "watermark": {
        "timestamp": "15/01/2024 14:30",
        "usuario": "agente_campo_01",
        "coordinates": [-56.0967, -15.6014]
      }
    }
    ```
    
    **Exemplo:**
    ```bash
    curl -X POST "http://localhost:8001/api/atividades/123/evidencias" \\
      -H "Content-Type: application/json" \\
      -d '{
        "atividade_id": 123,
        "tipo": "FOTO",
        "upload_id": "550e8400-e29b-41d4-a716-446655440000",
        "hash_sha256": "abc123def456...",
        "tamanho_bytes": 2048576,
        "url_s3": "atividades/123/uuid_foto.jpg",
        "descricao": "Fachada do imóvel",
        "metadata": {
          "exif": {...},
          "watermark": {...}
        }
      }'
    ```
    
    **Retorna:**
    - 201: Evidência registrada com sucesso
    - 400: Dados inválidos
    - 404: Atividade não encontrada
    """
    # Verify atividade_id matches
    if evidencia.atividade_id != atividade_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="atividade_id no path não corresponde ao body"
        )
    
    evidencia_service = EvidenciaService(DB_CONN_STR)
    
    try:
        # Create evidence record
        created = evidencia_service.create(evidencia)
        
        # Generate download URL
        created.url_download = s3_service.generate_presigned_download_url(
            created.url_s3,
            expires_in=3600  # 1 hour
        )
        
        return created
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar evidência: {str(e)}"
        )


@router.get(
    "/atividades/{atividade_id}/evidencias",
    response_model=EvidenciaList
)
async def list_evidencias(
    atividade_id: Annotated[int, Path(gt=0)],
    tipo: Annotated[Optional[List[str]], Query()] = []
):
    """
    Listar evidências de uma atividade.
    
    **Filtros:**
    - `tipo`: Filtrar por tipo (FOTO, VIDEO, DOCUMENTO, AUDIO)
    
    **Exemplos:**
    ```bash
    # Todas evidências
    curl "http://localhost:8001/api/atividades/123/evidencias"
    
    # Apenas fotos
    curl "http://localhost:8001/api/atividades/123/evidencias?tipo=FOTO"
    
    # Fotos e vídeos
    curl "http://localhost:8001/api/atividades/123/evidencias?tipo=FOTO&tipo=VIDEO"
    ```
    
    **Retorna:**
    ```json
    {
      "items": [
        {
          "id": 1,
          "atividade_id": 123,
          "tipo": "FOTO",
          "status": "CONCLUIDA",
          "hash_sha256": "abc123...",
          "tamanho_bytes": 2048576,
          "url_s3": "atividades/123/uuid_foto.jpg",
          "url_download": "https://s3.../presigned-url...",
          "descricao": "Fachada",
          "metadata": {...},
          "criado_em": "2024-01-15T14:30:00Z",
          "atualizado_em": "2024-01-15T14:30:00Z"
        }
      ],
      "total": 1
    }
    ```
    
    **Notas:**
    - `url_download` é gerada on-demand e válida por 1 hora
    - Evidências deletadas não aparecem na listagem
    """
    # Verify activity exists
    atividade_service = AtividadeService(DB_CONN_STR)
    atividade = atividade_service.get_by_id(atividade_id)
    
    if not atividade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atividade {atividade_id} não encontrada"
        )
    
    evidencia_service = EvidenciaService(DB_CONN_STR)
    
    try:
        result = evidencia_service.list_by_atividade(
            atividade_id,
            tipo=tipo if tipo and len(tipo) > 0 else None
        )
        
        # Generate download URLs for all items
        for item in result.items:
            item.url_download = s3_service.generate_presigned_download_url(
                item.url_s3,
                expires_in=3600
            )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar evidências: {str(e)}"
        )


@router.delete(
    "/evidencias/{evidencia_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_evidencia(
    evidencia_id: Annotated[int, Path(gt=0)]
):
    """
    Remover evidência (soft delete).
    
    **Comportamento:**
    - Define status como DELETADA
    - Não remove fisicamente do S3 (pode ser feito por job de limpeza)
    - Não aparece mais em listagens
    
    **Permissões:**
    - CAMPO: Apenas evidências de atividades próprias
    - GESTOR/ADMIN: Qualquer evidência
    
    **Exemplo:**
    ```bash
    curl -X DELETE "http://localhost:8001/api/evidencias/456"
    ```
    
    **Retorna:**
    - 204: Evidência removida com sucesso
    - 404: Evidência não encontrada
    """
    evidencia_service = EvidenciaService(DB_CONN_STR)
    
    deleted = evidencia_service.delete(evidencia_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidência {evidencia_id} não encontrada"
        )
    
    # TODO: Optionally delete from S3 here or via background job
    # s3_service.delete_object(evidencia.url_s3)
    
    return None
