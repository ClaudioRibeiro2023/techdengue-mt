"""
Mapa - Schemas for map layers and indicators
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TipoCamada(str, Enum):
    """Tipos de camadas disponíveis no mapa"""
    INCIDENCIA = "incidencia"  # Incidência/100k habitantes
    IPO = "ipo"  # Índice de Positividade de Ovos
    IDO = "ido"  # Índice de Densidade de Ovos
    IVO = "ivo"  # Índice de Vigilância de Ovos
    IMO = "imo"  # Índice de Mosquitos por Ovitrampa


class GeoJSONGeometry(BaseModel):
    """GeoJSON Geometry (simplified for Point)"""
    type: str = Field(..., pattern=r"^Point$")
    coordinates: List[float] = Field(..., min_length=2, max_length=2, description="[longitude, latitude]")


class MunicipioProperties(BaseModel):
    """Properties for municipality feature"""
    municipio_cod_ibge: str = Field(..., min_length=7, max_length=7)
    municipio_nome: str
    populacao: int = Field(..., ge=0, description="População estimada")
    casos: int = Field(..., ge=0, description="Número de casos no período")
    incidencia: float = Field(..., ge=0.0, description="Incidência por 100k hab")
    obitos: int = Field(..., ge=0, description="Número de óbitos")
    letalidade: float = Field(..., ge=0.0, le=100.0, description="Taxa de letalidade (%)")
    # Classification for color coding
    classe_risco: str = Field(..., description="baixo, medio, alto, muito_alto")
    cor_hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor para visualização")


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature"""
    type: str = Field(default="Feature")
    geometry: GeoJSONGeometry
    properties: MunicipioProperties


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection"""
    type: str = Field(default="FeatureCollection")
    features: List[GeoJSONFeature]
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [-56.0967, -15.6014]},
                        "properties": {
                            "municipio_cod_ibge": "5103403",
                            "municipio_nome": "Cuiabá",
                            "populacao": 618124,
                            "casos": 1234,
                            "incidencia": 199.65,
                            "obitos": 3,
                            "letalidade": 0.24,
                            "classe_risco": "alto",
                            "cor_hex": "#FF6B6B"
                        }
                    }
                ]
            }
        }


class IndiceEntomologico(BaseModel):
    """Índices entomológicos (IPO, IDO, IVO, IMO)"""
    municipio_cod_ibge: str
    municipio_nome: str
    ipo: Optional[float] = Field(None, ge=0.0, le=100.0, description="Índice de Positividade de Ovos (%)")
    ido: Optional[float] = Field(None, ge=0.0, description="Índice de Densidade de Ovos")
    ivo: Optional[float] = Field(None, ge=0.0, description="Índice de Vigilância de Ovos")
    imo: Optional[float] = Field(None, ge=0.0, description="Índice de Mosquitos por Ovitrampa")
    # Risk classification based on indices
    classe_risco_ipo: Optional[str] = Field(None, description="satisfatorio, alerta, risco")
    cor_hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")


class MapaCamadasRequest(BaseModel):
    """Request parameters for map layers"""
    tipo_camada: TipoCamada
    competencia_inicio: str = Field(..., pattern=r"^\d{6}$", description="YYYYMM início do período")
    competencia_fim: str = Field(..., pattern=r"^\d{6}$", description="YYYYMM fim do período")
    municipios: Optional[List[str]] = Field(None, description="Filtrar por códigos IBGE específicos")
    cluster: bool = Field(default=False, description="Se True, aplica clustering para reduzir features")
    max_features: int = Field(default=10000, ge=1, le=50000, description="Máximo de features retornadas")


class MapaCamadasResponse(BaseModel):
    """Response for map layers endpoint"""
    tipo_camada: TipoCamada
    competencia_inicio: str
    competencia_fim: str
    total_municipios: int
    total_casos: int
    total_obitos: int
    incidencia_media: float
    data: GeoJSONFeatureCollection
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais (clustering, etc)")


# ============================================================================
# HEATMAP SCHEMAS
# ============================================================================

class HeatmapPoint(BaseModel):
    """Ponto individual para heatmap"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    intensity: float = Field(..., ge=0, description="Intensidade (casos, incidência, etc)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": -15.6014,
                "lng": -56.0967,
                "intensity": 150.5
            }
        }


class HeatmapData(BaseModel):
    """Dados para camada heatmap"""
    points: List[HeatmapPoint] = Field(..., description="Lista de pontos com intensidade")
    max_intensity: float = Field(..., description="Intensidade máxima para normalização")
    total_points: int = Field(..., description="Total de pontos")
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# CHOROPLETH SCHEMAS (Polygon-based)
# ============================================================================

class ChoroplethMunicipioProperties(BaseModel):
    """Properties para choropleth de município (polígono)"""
    codigo_ibge: str = Field(..., min_length=7, max_length=7)
    nome: str
    casos: int = Field(..., ge=0)
    populacao: int = Field(..., ge=0)
    incidencia: float = Field(..., ge=0)
    obitos: int = Field(0, ge=0)
    nivel_risco: str = Field(..., description="BAIXO, MEDIO, ALTO, MUITO_ALTO")
    cor_hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    # Índices LIRAa (se disponível)
    iip: Optional[float] = Field(None, ge=0, le=100)
    ib: Optional[float] = Field(None, ge=0)
    idc: Optional[float] = Field(None, ge=0, le=100)


class PolygonCoordinates(BaseModel):
    """Coordenadas de polígono (exterior ring)"""
    type: str = Field(default="Polygon")
    coordinates: List[List[List[float]]] = Field(..., description="[[[lng, lat], ...]]")


class ChoroplethFeature(BaseModel):
    """Feature GeoJSON para choropleth (polígono)"""
    type: str = Field(default="Feature")
    id: str = Field(..., description="Código IBGE")
    geometry: PolygonCoordinates
    properties: ChoroplethMunicipioProperties


class ChoroplethFeatureCollection(BaseModel):
    """FeatureCollection para choropleth"""
    type: str = Field(default="FeatureCollection")
    features: List[ChoroplethFeature]
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "id": "5103403",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[-56.1, -15.6], [-56.0, -15.6], [-56.0, -15.5], [-56.1, -15.5], [-56.1, -15.6]]]
                    },
                    "properties": {
                        "codigo_ibge": "5103403",
                        "nome": "Cuiabá",
                        "casos": 1234,
                        "populacao": 618124,
                        "incidencia": 199.65,
                        "obitos": 3,
                        "nivel_risco": "ALTO",
                        "cor_hex": "#FF6B6B"
                    }
                }]
            }
        }


# ============================================================================
# FILTROS DINÂMICOS
# ============================================================================

class FiltroMapa(BaseModel):
    """Filtros para consulta do mapa"""
    # Temporal
    data_inicio: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")
    data_fim: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")
    semana_epi_inicio: Optional[int] = Field(None, ge=1, le=53)
    semana_epi_fim: Optional[int] = Field(None, ge=1, le=53)
    ano: Optional[int] = Field(None, ge=2000, le=2100)
    
    # Espacial
    municipios: Optional[List[str]] = Field(None, description="Códigos IBGE")
    bbox: Optional[List[float]] = Field(None, min_length=4, max_length=4, description="[minLng, minLat, maxLng, maxLat]")
    
    # Doença
    doenca_tipo: Optional[str] = Field(None, description="DENGUE, ZIKA, CHIKUNGUNYA, FEBRE_AMARELA")
    
    # Risco
    nivel_risco_min: Optional[str] = Field(None, description="BAIXO, MEDIO, ALTO, MUITO_ALTO")
    incidencia_min: Optional[float] = Field(None, ge=0)
    incidencia_max: Optional[float] = Field(None, ge=0)


# ============================================================================
# CLUSTERING
# ============================================================================

class ClusterProperties(BaseModel):
    """Properties de um cluster de municípios"""
    cluster_id: int
    point_count: int = Field(..., ge=1, description="Número de municípios no cluster")
    casos_total: int = Field(..., ge=0)
    obitos_total: int = Field(0, ge=0)
    incidencia_media: float = Field(..., ge=0)
    nivel_risco_predominante: str
    cor_hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")


class ClusterFeature(BaseModel):
    """Feature GeoJSON para cluster"""
    type: str = Field(default="Feature")
    geometry: GeoJSONGeometry
    properties: ClusterProperties


# ============================================================================
# ESTATÍSTICAS AGREGADAS
# ============================================================================

class EstatisticasMapa(BaseModel):
    """Estatísticas agregadas para o mapa"""
    total_municipios: int
    total_casos: int
    total_obitos: int
    taxa_letalidade: float = Field(..., ge=0, le=100, description="%")
    incidencia_media: float
    incidencia_maxima: float
    municipio_max_casos: Optional[str] = None
    
    # Distribuição por risco
    distribuicao_risco: Dict[str, int] = Field(
        default_factory=dict,
        description="{'BAIXO': 10, 'MEDIO': 20, 'ALTO': 15, 'MUITO_ALTO': 5}"
    )
    
    # Temporal
    periodo_inicio: str
    periodo_fim: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_municipios": 141,
                "total_casos": 15234,
                "total_obitos": 45,
                "taxa_letalidade": 0.30,
                "incidencia_media": 125.5,
                "incidencia_maxima": 450.2,
                "municipio_max_casos": "Cuiabá",
                "distribuicao_risco": {
                    "BAIXO": 50,
                    "MEDIO": 60,
                    "ALTO": 25,
                    "MUITO_ALTO": 6
                },
                "periodo_inicio": "2024-01-01",
                "periodo_fim": "2024-10-31"
            }
        }


# ============================================================================
# SERIES TEMPORAIS PARA MAPA
# ============================================================================

class SerieTemporal(BaseModel):
    """Série temporal de indicador"""
    data: str = Field(..., description="YYYY-MM-DD ou YYYY-Www (semana epi)")
    valor: float = Field(..., ge=0)


class SerieTemporalMunicipio(BaseModel):
    """Série temporal por município"""
    codigo_ibge: str
    nome: str
    serie: List[SerieTemporal]
    
    class Config:
        json_schema_extra = {
            "example": {
                "codigo_ibge": "5103403",
                "nome": "Cuiabá",
                "serie": [
                    {"data": "2024-W01", "valor": 125.5},
                    {"data": "2024-W02", "valor": 134.2}
                ]
            }
        }
