"""
Schemas para Índices LIRAa (Levantamento Rápido de Índices)
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum


class TipoIndice(str, Enum):
    """Tipos de índices LIRAa"""
    IPO = "IPO"  # Índice de Pendências
    IDO = "IDO"  # Índice de Depósitos
    IVO = "IVO"  # Índice de Vetores
    IMO = "IMO"  # Índice de Mosquitos


class ClassificacaoRisco(str, Enum):
    """Classificação de risco baseada nos índices"""
    SATISFATORIO = "SATISFATORIO"  # < 1%
    ALERTA = "ALERTA"              # 1% a 3.9%
    RISCO = "RISCO"                 # ≥ 4%


# ============================================================================
# REQUEST/RESPONSE
# ============================================================================

class LiraaFiltros(BaseModel):
    """Filtros para consulta de índices LIRAa"""
    ano: int = Field(..., ge=2000, le=2100, description="Ano do levantamento")
    semana_epi_inicio: Optional[int] = Field(None, ge=1, le=53, description="Semana epidemiológica início")
    semana_epi_fim: Optional[int] = Field(None, ge=1, le=53, description="Semana epidemiológica fim")
    codigo_ibge: Optional[str] = Field(None, min_length=7, max_length=7, description="Código IBGE do município")
    tipo_indice: Optional[TipoIndice] = Field(None, description="Tipo de índice (IPO, IDO, IVO, IMO)")


class IndiceLiraa(BaseModel):
    """Índice LIRAa individual"""
    codigo_ibge: str = Field(..., description="Código IBGE do município")
    municipio: str = Field(..., description="Nome do município")
    tipo_indice: TipoIndice = Field(..., description="Tipo de índice")
    valor: float = Field(..., ge=0, le=100, description="Valor do índice (%)")
    classificacao: ClassificacaoRisco = Field(..., description="Classificação de risco")
    imoveis_inspecionados: int = Field(..., ge=0, description="Total de imóveis inspecionados")
    imoveis_positivos: int = Field(..., ge=0, description="Imóveis com focos/positivos")
    data_levantamento: date = Field(..., description="Data do levantamento")
    semana_epi: int = Field(..., ge=1, le=53, description="Semana epidemiológica")


class LiraaResponse(BaseModel):
    """Response com índices LIRAa"""
    ano: int
    total_municipios: int
    indices: list[IndiceLiraa]


# ============================================================================
# SÉRIE TEMPORAL
# ============================================================================

class IndiceTemporal(BaseModel):
    """Índice LIRAa em um ponto no tempo"""
    ano: int
    semana_epi: int
    data_inicio: date
    data_fim: date
    valor_ipo: Optional[float] = Field(None, description="Índice de Pendências (%)")
    valor_ido: Optional[float] = Field(None, description="Índice de Depósitos (%)")
    valor_ivo: Optional[float] = Field(None, description="Índice de Vetores (%)")
    valor_imo: Optional[float] = Field(None, description="Índice de Mosquitos (%)")
    imoveis_inspecionados: int
    classificacao_geral: ClassificacaoRisco


class SerieLiraa(BaseModel):
    """Série temporal de índices LIRAa"""
    codigo_ibge: str
    municipio: str
    pontos: list[IndiceTemporal]


class SerieTemporalLiraaResponse(BaseModel):
    """Response com séries temporais LIRAa"""
    ano: int
    tipo_indice: Optional[TipoIndice]
    series: list[SerieLiraa]


# ============================================================================
# RANKING
# ============================================================================

class RankingLiraa(BaseModel):
    """Item do ranking de municípios por índice"""
    posicao: int
    codigo_ibge: str
    municipio: str
    populacao: int
    valor_indice: float
    classificacao: ClassificacaoRisco
    imoveis_inspecionados: int
    imoveis_positivos: int
    data_levantamento: date


class RankingLiraaResponse(BaseModel):
    """Response com ranking de municípios"""
    ano: int
    tipo_indice: TipoIndice
    total_municipios: int
    ranking: list[RankingLiraa]


# ============================================================================
# COMPARATIVO
# ============================================================================

class ComparativoLiraa(BaseModel):
    """Comparativo de índices entre dois períodos"""
    codigo_ibge: str
    municipio: str
    tipo_indice: TipoIndice
    
    # Período 1
    periodo1_ano: int
    periodo1_semana: int
    periodo1_valor: float
    periodo1_classificacao: ClassificacaoRisco
    
    # Período 2
    periodo2_ano: int
    periodo2_semana: int
    periodo2_valor: float
    periodo2_classificacao: ClassificacaoRisco
    
    # Variação
    variacao_absoluta: float = Field(..., description="Variação em pontos percentuais")
    variacao_percentual: float = Field(..., description="Variação percentual")
    tendencia: str = Field(..., description="MELHORA, PIORA ou ESTAVEL")


class ComparativoLiraaResponse(BaseModel):
    """Response com comparativo temporal"""
    tipo_indice: TipoIndice
    total_municipios: int
    comparativos: list[ComparativoLiraa]


# ============================================================================
# MAPA
# ============================================================================

class MunicipioLiraaProperties(BaseModel):
    """Propriedades de município para mapa"""
    codigo_ibge: str
    nome: str
    populacao: int
    valor_ipo: Optional[float]
    valor_ido: Optional[float]
    valor_ivo: Optional[float]
    valor_imo: Optional[float]
    classificacao_geral: ClassificacaoRisco
    imoveis_inspecionados: int
    data_levantamento: date


class MapaLiraaResponse(BaseModel):
    """Response para camada de mapa com índices LIRAa"""
    type: str = "FeatureCollection"
    ano: int
    tipo_indice: TipoIndice
    features: list[dict]  # GeoJSON features


# ============================================================================
# HELPERS
# ============================================================================

def classificar_risco(valor: float) -> ClassificacaoRisco:
    """
    Classifica risco baseado no valor do índice
    
    Referência: MS - Diretrizes Nacionais para Prevenção e Controle de Epidemias de Dengue
    """
    if valor < 1.0:
        return ClassificacaoRisco.SATISFATORIO
    elif valor < 4.0:
        return ClassificacaoRisco.ALERTA
    else:
        return ClassificacaoRisco.RISCO
