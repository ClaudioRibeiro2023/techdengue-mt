"""
Evidencia - Schemas for evidence/media attached to activities
"""
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from pydantic_settings import SettingsConfigDict


class EvidenciaTipo(str, Enum):
    """Tipos de evidência"""
    FOTO = "FOTO"
    VIDEO = "VIDEO"
    DOCUMENTO = "DOCUMENTO"
    AUDIO = "AUDIO"


class EvidenciaStatus(str, Enum):
    """Status do processo de upload"""
    PENDENTE = "PENDENTE"  # Awaiting upload
    UPLOADING = "UPLOADING"  # Upload in progress
    CONCLUIDA = "CONCLUIDA"  # Upload complete
    ERRO = "ERRO"  # Upload failed
    DELETADA = "DELETADA"  # Soft deleted


class EvidenciaBase(BaseModel):
    """Base schema for Evidencia"""
    tipo: EvidenciaTipo = Field(..., description="Tipo de evidência")
    descricao: Optional[str] = Field(None, max_length=500, description="Descrição da evidência")


class PresignedURLRequest(BaseModel):
    """Request for presigned S3 URL"""
    filename: str = Field(..., max_length=255, description="Nome do arquivo")
    content_type: str = Field(..., description="MIME type (image/jpeg, video/mp4, etc)")
    tamanho_bytes: int = Field(..., gt=0, le=52428800, description="Tamanho em bytes (max 50MB)")
    
    @validator('content_type')
    def validate_content_type(cls, v):
        """Validate allowed content types"""
        allowed = [
            'image/jpeg',
            'image/png',
            'image/webp',
            'video/mp4',
            'video/quicktime',
            'application/pdf',
            'audio/mpeg',
            'audio/wav'
        ]
        if v not in allowed:
            raise ValueError(f"content_type {v} not allowed. Allowed: {', '.join(allowed)}")
        return v


class PresignedURLResponse(BaseModel):
    """Response with presigned URL for upload"""
    upload_url: str = Field(..., description="Presigned URL for PUT request")
    upload_id: str = Field(..., description="Unique upload ID")
    expires_in: int = Field(default=300, description="URL validity in seconds")
    fields: Dict[str, str] = Field(default_factory=dict, description="Additional fields for multipart upload")


class EvidenciaCreate(EvidenciaBase):
    """Schema for creating Evidencia after successful upload"""
    atividade_id: int = Field(..., gt=0, description="ID da atividade associada")
    upload_id: str = Field(..., description="Upload ID from presigned URL request")
    hash_sha256: str = Field(
        ..., 
        min_length=64,
        max_length=64,
        pattern=r"^[a-f0-9]{64}$",
        description="SHA-256 hash of file content"
    )
    tamanho_bytes: int = Field(..., gt=0)
    url_s3: str = Field(..., description="S3 object key/path")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="EXIF, geotag, camera info, etc"
    )


class EvidenciaResponse(EvidenciaBase):
    """Schema for Evidencia response"""
    id: int
    atividade_id: int
    status: EvidenciaStatus
    hash_sha256: str
    tamanho_bytes: int
    url_s3: str
    url_download: Optional[str] = Field(None, description="Temporary signed download URL")
    metadata: Dict[str, Any]
    criado_em: datetime
    atualizado_em: datetime
    
    model_config = SettingsConfigDict(from_attributes=True)


class EvidenciaList(BaseModel):
    """Schema for list of Evidencias"""
    items: list[EvidenciaResponse]
    total: int


class WatermarkInfo(BaseModel):
    """Information for watermark overlay"""
    timestamp: str = Field(..., description="Timestamp to embed")
    usuario: str = Field(..., description="Username")
    coordinates: Optional[list[float]] = Field(None, description="[lon, lat]")
    
    def format_watermark(self) -> str:
        """Format watermark text"""
        parts = [self.timestamp, f"@{self.usuario}"]
        if self.coordinates and len(self.coordinates) >= 2:
            parts.append(f"[{self.coordinates[0]:.4f}, {self.coordinates[1]:.4f}]")
        return " ".join(parts)


class EXIFData(BaseModel):
    """EXIF metadata extracted from image"""
    make: Optional[str] = None  # Camera manufacturer
    model: Optional[str] = None  # Camera model
    datetime_original: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_altitude: Optional[float] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    orientation: Optional[int] = None
