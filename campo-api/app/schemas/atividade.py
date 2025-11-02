"""
Atividade - Schemas for field activities
"""
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from pydantic_settings import SettingsConfigDict


class AtividadeStatus(str, Enum):
    """Status possíveis de uma atividade"""
    CRIADA = "CRIADA"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"


class AtividadeOrigem(str, Enum):
    """Origem da atividade"""
    MANUAL = "MANUAL"
    IMPORTACAO = "IMPORTACAO"
    ALERTA = "ALERTA"


class AtividadeTipo(str, Enum):
    """Tipos de atividade de campo"""
    VISTORIA = "VISTORIA"
    LIRAA = "LIRAA"  # Levantamento de Índice Rápido de Aedes aegypti
    NEBULIZACAO = "NEBULIZACAO"
    ARMADILHA = "ARMADILHA"  # Instalação/manutenção de armadilhas
    PESQUISA_LARVARIA = "PESQUISA_LARVARIA"
    EDUCACAO = "EDUCACAO"  # Educação em saúde
    BLOQUEIO = "BLOQUEIO"  # Bloqueio de transmissão
    OUTROS = "OUTROS"


class GeoPoint(BaseModel):
    """GeoJSON Point representation"""
    type: str = Field(default="Point", pattern=r"^Point$")
    coordinates: list[float] = Field(
        ..., 
        min_length=2, 
        max_length=3,
        description="[longitude, latitude] or [longitude, latitude, altitude]"
    )
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        """Validate longitude and latitude ranges"""
        if len(v) < 2:
            raise ValueError("coordinates must have at least [longitude, latitude]")
        
        lon, lat = v[0], v[1]
        
        # Validate longitude (-180 to 180)
        if not -180 <= lon <= 180:
            raise ValueError(f"longitude must be between -180 and 180, got {lon}")
        
        # Validate latitude (-90 to 90)
        if not -90 <= lat <= 90:
            raise ValueError(f"latitude must be between -90 and 90, got {lat}")
        
        # Validate MT bounds (approximate)
        # MT: lon [-61, -50], lat [-18, -7]
        if not (-61 <= lon <= -50):
            raise ValueError(f"longitude outside Mato Grosso bounds: {lon}")
        if not (-18 <= lat <= -7):
            raise ValueError(f"latitude outside Mato Grosso bounds: {lat}")
        
        return v
    
    model_config = SettingsConfigDict(json_schema_extra={
        "example": {
            "type": "Point",
            "coordinates": [-56.0967, -15.6014]  # Cuiabá
        }
    })


class AtividadeBase(BaseModel):
    """Base schema for Atividade"""
    tipo: AtividadeTipo = Field(..., description="Tipo da atividade")
    municipio_cod_ibge: str = Field(
        ..., 
        min_length=7, 
        max_length=7,
        pattern=r"^51\d{5}$",
        description="Código IBGE do município (MT: 51xxxxx)"
    )
    localizacao: Optional[GeoPoint] = Field(None, description="Localização geográfica da atividade")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição da atividade")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Metadados customizáveis (JSONB)"
    )


class AtividadeCreate(AtividadeBase):
    """Schema for creating a new Atividade"""
    origem: AtividadeOrigem = Field(default=AtividadeOrigem.MANUAL, description="Origem da atividade")


class AtividadeUpdate(BaseModel):
    """Schema for updating an Atividade"""
    status: Optional[AtividadeStatus] = Field(None, description="Novo status")
    descricao: Optional[str] = Field(None, max_length=1000)
    localizacao: Optional[GeoPoint] = None
    metadata: Optional[Dict[str, Any]] = None


class AtividadeResponse(AtividadeBase):
    """Schema for Atividade response"""
    id: int
    status: AtividadeStatus
    origem: AtividadeOrigem
    criado_em: datetime
    iniciado_em: Optional[datetime] = None
    encerrado_em: Optional[datetime] = None
    usuario_criacao: Optional[str] = None
    usuario_responsavel: Optional[str] = None
    
    model_config = SettingsConfigDict(from_attributes=True)


class AtividadeList(BaseModel):
    """Schema for paginated list of Atividades"""
    items: list[AtividadeResponse]
    total: int
    page: int = 1
    page_size: int = 50


class AtividadeStats(BaseModel):
    """Statistics for activities"""
    total: int
    por_status: Dict[str, int]
    por_tipo: Dict[str, int]
    por_municipio: Dict[str, int]
