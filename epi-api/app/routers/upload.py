"""
Router para Upload de Arquivos (Fotos de Denúncias)
Usa MinIO (S3-compatible) configurado no docker-compose
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import os
import uuid
from datetime import datetime
import mimetypes
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/upload",
    tags=["Upload"]
)

# Configuração MinIO (S3-compatible)
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "denuncias")
MINIO_USE_SSL = os.getenv("MINIO_USE_SSL", "false").lower() == "true"

# Lazy import do boto3/minio client
_s3_client = None

def get_s3_client():
    """Retorna cliente S3 (boto3) para MinIO"""
    global _s3_client
    if _s3_client is None:
        try:
            import boto3
            from botocore.client import Config
            
            _s3_client = boto3.client(
                's3',
                endpoint_url=f"http{'s' if MINIO_USE_SSL else ''}://{MINIO_ENDPOINT}",
                aws_access_key_id=MINIO_ACCESS_KEY,
                aws_secret_access_key=MINIO_SECRET_KEY,
                config=Config(signature_version='s3v4'),
                region_name='us-east-1'
            )
            
            # Garantir que o bucket existe
            try:
                _s3_client.head_bucket(Bucket=MINIO_BUCKET)
            except Exception:
                _s3_client.create_bucket(Bucket=MINIO_BUCKET)
                logger.info(f"Bucket '{MINIO_BUCKET}' criado no MinIO")
                
        except ImportError:
            logger.error("boto3 não instalado. Execute: pip install boto3")
            raise HTTPException(status_code=500, detail="Serviço de upload indisponível")
        except Exception as e:
            logger.error(f"Erro ao conectar no MinIO: {e}")
            raise HTTPException(status_code=500, detail="Erro ao conectar no armazenamento")
    
    return _s3_client

# Tipos MIME aceitos para fotos
ALLOWED_MIMETYPES = {
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/webp',
    'image/heic',
    'image/heif'
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@router.post("/foto", response_model=dict)
async def upload_foto(
    file: UploadFile = File(...)
):
    """
    Faz upload de foto de denúncia para MinIO.
    
    Retorna:
    - `url`: caminho relativo do arquivo no bucket (para salvar no DB)
    - `public_url`: URL pública (se MinIO configurado com acesso público)
    """
    
    # Validar tipo MIME
    content_type = file.content_type
    if content_type not in ALLOWED_MIMETYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não permitido: {content_type}. Use JPG, PNG, WEBP ou HEIC."
        )
    
    # Ler arquivo
    try:
        contents = await file.read()
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar arquivo")
    
    # Validar tamanho
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo muito grande: {len(contents)} bytes. Máximo: {MAX_FILE_SIZE} bytes (5MB)."
        )
    
    # Gerar nome único
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_id = str(uuid.uuid4())[:8]
    ext = mimetypes.guess_extension(content_type) or '.jpg'
    filename = f"denuncias/{timestamp}_{file_id}{ext}"
    
    # Upload para MinIO
    try:
        s3 = get_s3_client()
        s3.put_object(
            Bucket=MINIO_BUCKET,
            Key=filename,
            Body=contents,
            ContentType=content_type
        )
        logger.info(f"Foto uploaded: {filename}")
    except Exception as e:
        logger.error(f"Erro ao fazer upload para MinIO: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar arquivo")
    
    # Montar URL pública (se MinIO exposto)
    public_url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{filename}"
    
    return {
        "url": filename,  # Para salvar no DB
        "public_url": public_url,
        "size": len(contents),
        "content_type": content_type
    }


@router.get("/foto/{path:path}")
async def get_foto(path: str):
    """
    Retorna foto do MinIO (proxy).
    Útil se MinIO não estiver exposto publicamente.
    """
    try:
        s3 = get_s3_client()
        obj = s3.get_object(Bucket=MINIO_BUCKET, Key=path)
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            obj['Body'],
            media_type=obj.get('ContentType', 'image/jpeg')
        )
    except Exception as e:
        logger.error(f"Erro ao buscar foto: {e}")
        raise HTTPException(status_code=404, detail="Foto não encontrada")
