"""
Modelos Pydantic para Denúncias Públicas (e-Denúncia)
Módulo PoC - Fase P (ELIMINATÓRIA)
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class DenunciaStatus(str, Enum):
    """Status do workflow de denúncia"""
    PENDENTE = "PENDENTE"
    EM_ANALISE = "EM_ANALISE"
    ATIVIDADE_CRIADA = "ATIVIDADE_CRIADA"
    DESCARTADA = "DESCARTADA"
    DUPLICADA = "DUPLICADA"


class DenunciaPrioridade(str, Enum):
    """Classificação de prioridade pelo chatbot FSM"""
    BAIXO = "BAIXO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"


class ChatbotResposta(BaseModel):
    """Resposta individual do chatbot"""
    pergunta: str
    resposta: str
    timestamp: datetime


class CoordenadasGPS(BaseModel):
    """Coordenadas GPS capturadas"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    precisao: Optional[float] = Field(None, ge=0, description="Precisão em metros")
    
    @validator('latitude', 'longitude')
    def validar_coordenadas(cls, v):
        if v == 0:
            raise ValueError("Coordenadas (0,0) não são válidas para MT")
        return v


class DenunciaCreate(BaseModel):
    """Schema para criação de denúncia (POST)"""
    # Localização (obrigatórios)
    endereco: str = Field(..., min_length=5, max_length=500)
    bairro: str = Field(..., min_length=2, max_length=200)
    municipio_codigo: str = Field(..., pattern=r"^51\d{5}$", description="Código IBGE 7 dígitos MT")
    
    # GPS
    coordenadas: CoordenadasGPS
    
    # Descrição
    descricao: str = Field(..., min_length=10, max_length=500)
    foto_url: Optional[str] = None
    
    # Chatbot
    chatbot_classificacao: DenunciaPrioridade
    chatbot_respostas: List[ChatbotResposta]
    chatbot_duracao_segundos: Optional[int] = Field(None, ge=0, le=600)
    
    # Contato (opcional)
    contato_nome: Optional[str] = Field(None, max_length=200)
    contato_telefone: Optional[str] = Field(None, pattern=r"^\+?[\d\s\-\(\)]{8,20}$")
    contato_email: Optional[str] = Field(None, max_length=200)
    contato_anonimo: bool = False
    
    # Metadata
    origem: str = Field(default="WEB", pattern=r"^(WEB|PWA|APP)$")
    user_agent: Optional[str] = None
    
    @validator('chatbot_respostas')
    def validar_chatbot_respostas(cls, v):
        if len(v) < 1:
            raise ValueError("Chatbot deve ter pelo menos 1 resposta")
        if len(v) > 10:
            raise ValueError("Chatbot não pode ter mais de 10 respostas")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "endereco": "Rua das Flores, 123",
                "bairro": "Centro",
                "municipio_codigo": "5103403",
                "coordenadas": {
                    "latitude": -15.601411,
                    "longitude": -56.097892,
                    "precisao": 10.5
                },
                "descricao": "Há um pneu com água parada há mais de uma semana no terreno baldio ao lado da casa.",
                "chatbot_classificacao": "ALTO",
                "chatbot_respostas": [
                    {
                        "pergunta": "Você viu água parada no local?",
                        "resposta": "Sim",
                        "timestamp": "2025-01-15T10:30:00Z"
                    },
                    {
                        "pergunta": "Há larvas visíveis na água?",
                        "resposta": "Sim",
                        "timestamp": "2025-01-15T10:30:15Z"
                    }
                ],
                "chatbot_duracao_segundos": 45,
                "contato_nome": "Maria Silva",
                "contato_telefone": "+55 65 98765-4321",
                "contato_anonimo": False,
                "origem": "WEB"
            }
        }


class DenunciaResponse(BaseModel):
    """Schema para resposta de denúncia (GET)"""
    id: str
    numero_protocolo: str
    
    # Localização
    endereco: str
    bairro: str
    municipio_codigo: str
    municipio_nome: Optional[str]
    coordenadas: Optional[CoordenadasGPS]
    
    # Descrição
    descricao: str
    foto_url: Optional[str]
    
    # Chatbot
    chatbot_classificacao: DenunciaPrioridade
    chatbot_duracao_segundos: Optional[int]
    
    # Contato (masked se anônimo)
    contato_nome: Optional[str]
    contato_telefone: Optional[str]
    contato_anonimo: bool
    
    # Status
    status: DenunciaStatus
    atividade_id: Optional[str]
    
    # Timestamps
    criado_em: datetime
    atualizado_em: datetime
    sincronizado_em: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class DenunciaUpdate(BaseModel):
    """Schema para atualização de status (PATCH)"""
    status: Optional[DenunciaStatus]
    motivo_descarte: Optional[str] = Field(None, max_length=500)
    atividade_id: Optional[str]


class DenunciaListResponse(BaseModel):
    """Schema para listagem paginada"""
    items: List[DenunciaResponse]
    total: int
    page: int
    per_page: int
    has_next: bool


class DenunciaStatsResponse(BaseModel):
    """Schema para estatísticas de denúncias"""
    total_denuncias: int
    por_prioridade: dict[str, int]
    por_status: dict[str, int]
    por_municipio: List[dict]
    tempo_medio_chatbot: Optional[float]
    taxa_conversao_atividade: Optional[float]
