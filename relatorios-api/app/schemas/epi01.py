"""
EPI01 Report - Schemas for epidemiological report generation
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class FormatoRelatorio(str, Enum):
    """Formatos de saída do relatório"""
    PDF = "pdf"
    CSV = "csv"
    BOTH = "both"


class StatusRelatorio(str, Enum):
    """Status de geração do relatório"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DoencaTipo(str, Enum):
    """Tipos de doença"""
    DENGUE = "DENGUE"
    ZIKA = "ZIKA"
    CHIKUNGUNYA = "CHIKUNGUNYA"
    FEBRE_AMARELA = "FEBRE_AMARELA"
    TODAS = "TODAS"


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class EPI01Request(BaseModel):
    """Request para geração de relatório EPI01"""
    # Filtros temporais
    ano: int = Field(..., ge=2000, le=2100, description="Ano de referência")
    semana_epi_inicio: Optional[int] = Field(None, ge=1, le=53, description="Semana epidemiológica início")
    semana_epi_fim: Optional[int] = Field(None, ge=1, le=53, description="Semana epidemiológica fim")
    
    # Filtros espaciais
    codigo_ibge: Optional[str] = Field(None, min_length=7, max_length=7, description="Filtro por município")
    regional_saude: Optional[str] = Field(None, description="Filtro por regional de saúde")
    
    # Filtros de doença
    doenca_tipo: DoencaTipo = Field(DoencaTipo.DENGUE, description="Tipo de doença")
    
    # Opções de formatação
    formato: FormatoRelatorio = Field(FormatoRelatorio.PDF, description="Formato de saída")
    incluir_graficos: bool = Field(True, description="Incluir gráficos no PDF")
    incluir_tabelas_detalhadas: bool = Field(True, description="Incluir tabelas detalhadas")
    
    # Metadados
    titulo_customizado: Optional[str] = Field(None, max_length=200, description="Título customizado do relatório")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações adicionais")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ano": 2024,
                "semana_epi_inicio": 1,
                "semana_epi_fim": 44,
                "doenca_tipo": "DENGUE",
                "formato": "pdf",
                "incluir_graficos": True,
                "incluir_tabelas_detalhadas": True
            }
        }


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class EPI01Response(BaseModel):
    """Response inicial após solicitação de relatório"""
    relatorio_id: str = Field(..., description="ID único do relatório")
    status: StatusRelatorio
    mensagem: str
    formato: FormatoRelatorio
    estimativa_tempo_segundos: Optional[int] = Field(None, description="Estimativa de tempo para conclusão")
    criado_em: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "relatorio_id": "epi01-2024-44-dengue-abc123",
                "status": "processing",
                "mensagem": "Relatório EPI01 em geração...",
                "formato": "pdf",
                "estimativa_tempo_segundos": 30,
                "criado_em": "2024-11-02T17:00:00Z"
            }
        }


class ArquivoRelatorio(BaseModel):
    """Metadados de arquivo gerado"""
    formato: str = Field(..., description="pdf ou csv")
    tamanho_bytes: int = Field(..., ge=0)
    hash_sha256: str = Field(..., min_length=64, max_length=64, description="Hash SHA-256 do arquivo")
    url_download: str = Field(..., description="URL para download")
    nome_arquivo: str = Field(..., description="Nome do arquivo gerado")


class EPI01StatusResponse(BaseModel):
    """Response com status detalhado do relatório"""
    relatorio_id: str
    status: StatusRelatorio
    formato: FormatoRelatorio
    
    # Timestamps
    criado_em: datetime
    atualizado_em: datetime
    concluido_em: Optional[datetime] = None
    
    # Metadados de geração
    total_registros: Optional[int] = Field(None, description="Total de registros processados")
    tempo_processamento_segundos: Optional[float] = None
    
    # Arquivos gerados
    arquivos: List[ArquivoRelatorio] = Field(default_factory=list)
    
    # Erros
    erro_mensagem: Optional[str] = None
    erro_detalhes: Optional[Dict[str, Any]] = None
    
    # Request original
    parametros: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Parâmetros da solicitação")
    
    class Config:
        json_schema_extra = {
            "example": {
                "relatorio_id": "epi01-2024-44-dengue-abc123",
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
                        "url_download": "/api/relatorios/epi01/download/epi01-2024-44-dengue-abc123/pdf",
                        "nome_arquivo": "EPI01_DENGUE_2024_W01-W44.pdf"
                    }
                ],
                "parametros": {
                    "ano": 2024,
                    "semana_epi_inicio": 1,
                    "semana_epi_fim": 44,
                    "doenca_tipo": "DENGUE"
                }
            }
        }


# ============================================================================
# DATA SCHEMAS (para conteúdo do relatório)
# ============================================================================

class DadosResumo(BaseModel):
    """Resumo executivo dos dados"""
    total_casos: int = Field(..., ge=0)
    total_obitos: int = Field(..., ge=0)
    taxa_letalidade: float = Field(..., ge=0, le=100, description="%")
    incidencia_media: float = Field(..., ge=0, description="/100k hab")
    municipios_afetados: int = Field(..., ge=0)
    casos_graves: int = Field(..., ge=0)
    
    # Comparativo com período anterior
    variacao_casos_percentual: Optional[float] = None
    variacao_obitos_percentual: Optional[float] = None


class DadosMunicipio(BaseModel):
    """Dados por município"""
    codigo_ibge: str
    nome: str
    populacao: int
    casos: int
    obitos: int
    incidencia: float
    taxa_letalidade: float
    nivel_risco: str


class DadosSemana(BaseModel):
    """Dados por semana epidemiológica"""
    ano: int
    semana_epi: int
    data_inicio: str
    data_fim: str
    casos: int
    obitos: int
    casos_graves: int


class ConteudoRelatorioEPI01(BaseModel):
    """Conteúdo completo do relatório EPI01"""
    # Cabeçalho
    titulo: str
    periodo: str
    data_geracao: datetime
    doenca_tipo: str
    
    # Resumo executivo
    resumo: DadosResumo
    
    # Dados por município (top N)
    municipios: List[DadosMunicipio]
    
    # Série temporal
    serie_temporal: List[DadosSemana]
    
    # Distribuições
    distribuicao_faixa_etaria: Optional[Dict[str, int]] = Field(default_factory=dict)
    distribuicao_sexo: Optional[Dict[str, int]] = Field(default_factory=dict)
    
    # Observações
    observacoes: Optional[str] = None
    
    # Assinatura digital
    hash_conteudo: Optional[str] = Field(None, description="Hash SHA-256 do conteúdo")


# ============================================================================
# VALIDATION SCHEMAS
# ============================================================================

class ValidacaoRelatorio(BaseModel):
    """Resultado de validação de relatório"""
    valido: bool
    erros: List[str] = Field(default_factory=list)
    avisos: List[str] = Field(default_factory=list)
    hash_verificado: Optional[bool] = None
    tamanho_bytes: Optional[int] = None
    formato_conforme: Optional[bool] = None  # PDF/A-1 compliance
