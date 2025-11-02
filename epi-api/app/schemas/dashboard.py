"""
Dashboard EPI - Schemas for KPIs, charts and drill-down
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import date
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class DoencaTipo(str, Enum):
    """Tipos de doença"""
    DENGUE = "DENGUE"
    ZIKA = "ZIKA"
    CHIKUNGUNYA = "CHIKUNGUNYA"
    FEBRE_AMARELA = "FEBRE_AMARELA"


class PeriodoAgregacao(str, Enum):
    """Período de agregação para séries temporais"""
    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSAL = "mensal"
    ANUAL = "anual"


class TendenciaDirecao(str, Enum):
    """Direção da tendência"""
    ALTA = "alta"
    BAIXA = "baixa"
    ESTAVEL = "estavel"


# ============================================================================
# KPIs - KEY PERFORMANCE INDICATORS
# ============================================================================

class KPIVariacao(BaseModel):
    """Variação de KPI comparado ao período anterior"""
    valor_atual: float = Field(..., description="Valor no período atual")
    valor_anterior: float = Field(..., description="Valor no período anterior")
    variacao_absoluta: float = Field(..., description="Diferença absoluta")
    variacao_percentual: float = Field(..., description="Variação % (positivo = aumento)")
    tendencia: TendenciaDirecao = Field(..., description="Tendência (alta/baixa/estavel)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "valor_atual": 1523.0,
                "valor_anterior": 1240.0,
                "variacao_absoluta": 283.0,
                "variacao_percentual": 22.82,
                "tendencia": "alta"
            }
        }


class KPICard(BaseModel):
    """Card individual de KPI"""
    titulo: str = Field(..., description="Título do KPI")
    valor: float = Field(..., description="Valor principal")
    unidade: str = Field(..., description="Unidade (casos, %, /100k hab, etc)")
    variacao: Optional[KPIVariacao] = Field(None, description="Variação vs período anterior")
    icone: Optional[str] = Field(None, description="Nome do ícone (lucide-react)")
    cor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor hex")
    descricao: Optional[str] = Field(None, description="Descrição adicional")
    
    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Total de Casos",
                "valor": 15234.0,
                "unidade": "casos",
                "variacao": {
                    "valor_atual": 15234.0,
                    "valor_anterior": 12450.0,
                    "variacao_absoluta": 2784.0,
                    "variacao_percentual": 22.36,
                    "tendencia": "alta"
                },
                "icone": "Activity",
                "cor": "#FF6B6B",
                "descricao": "Casos confirmados de dengue em 2024"
            }
        }


class DashboardKPIs(BaseModel):
    """Conjunto completo de KPIs do dashboard"""
    # KPIs principais
    total_casos: KPICard
    total_obitos: KPICard
    taxa_letalidade: KPICard
    incidencia_media: KPICard
    
    # KPIs secundários
    municipios_risco_alto: Optional[KPICard] = None
    casos_graves: Optional[KPICard] = None
    tempo_medio_notificacao: Optional[KPICard] = None
    
    # Metadados
    periodo_inicio: str = Field(..., description="Data início YYYY-MM-DD")
    periodo_fim: str = Field(..., description="Data fim YYYY-MM-DD")
    ultima_atualizacao: str = Field(..., description="Timestamp última atualização")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_casos": {
                    "titulo": "Total de Casos",
                    "valor": 15234.0,
                    "unidade": "casos",
                    "icone": "Activity",
                    "cor": "#FF6B6B"
                },
                "total_obitos": {
                    "titulo": "Óbitos",
                    "valor": 45.0,
                    "unidade": "óbitos",
                    "icone": "AlertTriangle",
                    "cor": "#F44336"
                },
                "taxa_letalidade": {
                    "titulo": "Letalidade",
                    "valor": 0.30,
                    "unidade": "%",
                    "icone": "TrendingUp",
                    "cor": "#FFC107"
                },
                "incidencia_media": {
                    "titulo": "Incidência Média",
                    "valor": 125.5,
                    "unidade": "/100k hab",
                    "icone": "Users",
                    "cor": "#2196F3"
                },
                "periodo_inicio": "2024-01-01",
                "periodo_fim": "2024-10-31",
                "ultima_atualizacao": "2024-11-02T16:30:00Z"
            }
        }


# ============================================================================
# SERIES TEMPORAIS
# ============================================================================

class PontoSerie(BaseModel):
    """Ponto individual em série temporal"""
    data: str = Field(..., description="Data no formato YYYY-MM-DD ou YYYY-Www")
    valor: float = Field(..., ge=0, description="Valor do indicador")
    label: Optional[str] = Field(None, description="Label customizado")
    metadados: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SerieTemporal(BaseModel):
    """Série temporal de indicador"""
    nome: str = Field(..., description="Nome da série (ex: Dengue 2024)")
    tipo: str = Field(..., description="Tipo de indicador (casos, incidencia, obitos)")
    unidade: str = Field(..., description="Unidade (casos, /100k hab, %)")
    dados: List[PontoSerie] = Field(..., description="Pontos da série")
    cor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Dengue 2024",
                "tipo": "incidencia",
                "unidade": "/100k hab",
                "dados": [
                    {"data": "2024-W01", "valor": 125.5},
                    {"data": "2024-W02", "valor": 134.2},
                    {"data": "2024-W03", "valor": 142.8}
                ],
                "cor": "#FF6B6B"
            }
        }


class SeriesTemporaisResponse(BaseModel):
    """Response para endpoint de séries temporais"""
    series: List[SerieTemporal] = Field(..., description="Lista de séries")
    periodo_agregacao: PeriodoAgregacao
    periodo_inicio: str
    periodo_fim: str
    total_pontos: int = Field(..., description="Total de pontos em todas as séries")
    
    class Config:
        json_schema_extra = {
            "example": {
                "series": [
                    {
                        "nome": "Dengue 2024",
                        "tipo": "casos",
                        "unidade": "casos",
                        "dados": [
                            {"data": "2024-01", "valor": 1523.0},
                            {"data": "2024-02", "valor": 1687.0}
                        ],
                        "cor": "#FF6B6B"
                    }
                ],
                "periodo_agregacao": "mensal",
                "periodo_inicio": "2024-01-01",
                "periodo_fim": "2024-10-31",
                "total_pontos": 10
            }
        }


# ============================================================================
# TOP N (RANKINGS)
# ============================================================================

class ItemRanking(BaseModel):
    """Item individual em ranking"""
    posicao: int = Field(..., ge=1, description="Posição no ranking")
    codigo_ibge: str = Field(..., min_length=7, max_length=7)
    nome: str = Field(..., description="Nome do município")
    valor: float = Field(..., ge=0, description="Valor do indicador")
    valor_secundario: Optional[float] = Field(None, description="Valor adicional (ex: população)")
    percentual: Optional[float] = Field(None, ge=0, le=100, description="% do total")
    nivel_risco: Optional[str] = Field(None, description="BAIXO, MEDIO, ALTO, MUITO_ALTO")
    cor_hex: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "posicao": 1,
                "codigo_ibge": "5103403",
                "nome": "Cuiabá",
                "valor": 3845.0,
                "valor_secundario": 618124.0,
                "percentual": 25.23,
                "nivel_risco": "MUITO_ALTO",
                "cor_hex": "#F44336"
            }
        }


class TopNResponse(BaseModel):
    """Response para endpoint top N"""
    ranking: List[ItemRanking] = Field(..., description="Lista ordenada por valor")
    tipo_indicador: str = Field(..., description="casos, incidencia, obitos")
    unidade: str
    total_items: int = Field(..., description="Total de itens no ranking completo")
    limite: int = Field(..., description="Limite solicitado (top N)")
    periodo_inicio: str
    periodo_fim: str
    agregacao: Optional[str] = Field(None, description="Tipo de agregação (municipio, regional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ranking": [
                    {
                        "posicao": 1,
                        "codigo_ibge": "5103403",
                        "nome": "Cuiabá",
                        "valor": 3845.0,
                        "percentual": 25.23,
                        "nivel_risco": "MUITO_ALTO"
                    },
                    {
                        "posicao": 2,
                        "codigo_ibge": "5105606",
                        "nome": "Várzea Grande",
                        "valor": 2134.0,
                        "percentual": 14.01,
                        "nivel_risco": "ALTO"
                    }
                ],
                "tipo_indicador": "casos",
                "unidade": "casos",
                "total_items": 141,
                "limite": 10,
                "periodo_inicio": "2024-01-01",
                "periodo_fim": "2024-10-31",
                "agregacao": "municipio"
            }
        }


# ============================================================================
# DRILL-DOWN
# ============================================================================

class DrillDownFiltro(BaseModel):
    """Filtros para drill-down"""
    codigo_ibge: Optional[str] = Field(None, min_length=7, max_length=7)
    doenca_tipo: Optional[DoencaTipo] = None
    faixa_etaria: Optional[str] = Field(None, description="0-10, 11-20, 21-30, etc")
    sexo: Optional[str] = Field(None, pattern=r"^(M|F|I)$")
    classificacao: Optional[str] = Field(None, description="confirmado, suspeito, descartado")


class DrillDownDados(BaseModel):
    """Dados detalhados para drill-down"""
    titulo: str
    descricao: Optional[str] = None
    
    # Dados agregados
    total_casos: int
    total_obitos: int
    incidencia: float
    taxa_letalidade: float
    
    # Distribuições
    distribuicao_idade: Dict[str, int] = Field(default_factory=dict)
    distribuicao_sexo: Dict[str, int] = Field(default_factory=dict)
    distribuicao_classificacao: Dict[str, int] = Field(default_factory=dict)
    
    # Série temporal
    serie_temporal: Optional[SerieTemporal] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Cuiabá - Dengue 2024",
                "total_casos": 3845,
                "total_obitos": 12,
                "incidencia": 622.04,
                "taxa_letalidade": 0.31,
                "distribuicao_idade": {
                    "0-10": 234,
                    "11-20": 567,
                    "21-30": 789
                },
                "distribuicao_sexo": {
                    "M": 1823,
                    "F": 2022
                },
                "distribuicao_classificacao": {
                    "confirmado": 3456,
                    "suspeito": 389
                }
            }
        }


# ============================================================================
# COMPARATIVOS
# ============================================================================

class ComparativoMunicipio(BaseModel):
    """Comparativo entre municípios"""
    municipios: List[str] = Field(..., description="Nomes dos municípios")
    indicador: str = Field(..., description="casos, incidencia, obitos")
    valores: List[float] = Field(..., description="Valores correspondentes")
    cores: Optional[List[str]] = Field(None, description="Cores para cada município")
    
    class Config:
        json_schema_extra = {
            "example": {
                "municipios": ["Cuiabá", "Várzea Grande", "Rondonópolis"],
                "indicador": "incidencia",
                "valores": [622.04, 450.23, 385.67],
                "cores": ["#F44336", "#FF9800", "#FFC107"]
            }
        }
