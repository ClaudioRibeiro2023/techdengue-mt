"""
Router para Índices LIRAa (IPO, IDO, IVO, IMO)
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from app.schemas.liraa import (
    TipoIndice,
    LiraaResponse,
    SerieTemporalLiraaResponse,
    RankingLiraaResponse,
    ComparativoLiraaResponse,
    MapaLiraaResponse,
)

router = APIRouter(prefix="/liraa", tags=["LIRAa - Índices Entomológicos"])


# ============================================================================
# GET ÍNDICES
# ============================================================================

@router.get("/indices", response_model=LiraaResponse)
async def get_indices_liraa(
    ano: int = Query(..., ge=2000, le=2100, description="Ano do levantamento"),
    tipo_indice: Optional[TipoIndice] = Query(None, description="Tipo de índice (IPO/IDO/IVO/IMO)"),
    codigo_ibge: Optional[str] = Query(None, min_length=7, max_length=7, description="Código IBGE do município"),
    semana_epi_inicio: Optional[int] = Query(None, ge=1, le=53),
    semana_epi_fim: Optional[int] = Query(None, ge=1, le=53),
):
    """
    **Retorna índices LIRAa agregados por município**
    
    Os índices LIRAa (Levantamento Rápido de Índices para Aedes aegypti) são:
    
    - **IPO** (Índice de Pendências): % de imóveis com pendências
    - **IDO** (Índice de Depósitos): % de depósitos com larvas
    - **IVO** (Índice de Vetores): % de imóveis com vetores
    - **IMO** (Índice de Mosquitos): % de imóveis com mosquitos adultos
    
    **Classificação de Risco**:
    - Satisfatório: < 1%
    - Alerta: 1% a 3.9%
    - Risco: ≥ 4%
    
    **Exemplo**:
    ```bash
    curl "http://localhost:8000/api/liraa/indices?ano=2024&tipo_indice=IPO"
    ```
    
    **Nota**: Dados serão disponibilizados quando os datasets LIRAa estiverem carregados.
    """
    
    # TODO: Implementar quando dados LIRAa estiverem disponíveis
    raise HTTPException(
        status_code=503,
        detail="Dados LIRAa não disponíveis. Aguardando carregamento de datasets."
    )


# ============================================================================
# SÉRIE TEMPORAL
# ============================================================================

@router.get("/series-temporais", response_model=SerieTemporalLiraaResponse)
async def get_series_temporais_liraa(
    ano: int = Query(..., ge=2000, le=2100),
    tipo_indice: TipoIndice = Query(..., description="Tipo de índice"),
    codigo_ibge: Optional[str] = Query(None, min_length=7, max_length=7),
):
    """
    **Retorna série temporal de índices LIRAa**
    
    Evolução dos índices ao longo do ano, agrupados por semana epidemiológica.
    
    Útil para:
    - Visualizar tendências temporais
    - Identificar períodos críticos
    - Avaliar eficácia de intervenções
    
    **Exemplo**:
    ```bash
    curl "http://localhost:8000/api/liraa/series-temporais?ano=2024&tipo_indice=IPO&codigo_ibge=5103403"
    ```
    """
    
    raise HTTPException(
        status_code=503,
        detail="Dados LIRAa não disponíveis. Aguardando carregamento de datasets."
    )


# ============================================================================
# RANKING
# ============================================================================

@router.get("/ranking", response_model=RankingLiraaResponse)
async def get_ranking_liraa(
    ano: int = Query(..., ge=2000, le=2100),
    tipo_indice: TipoIndice = Query(..., description="Tipo de índice para ranking"),
    limite: int = Query(20, ge=1, le=100, description="Número de municípios no ranking"),
    ordem: str = Query("desc", regex="^(asc|desc)$", description="Ordem (asc/desc)"),
):
    """
    **Retorna ranking de municípios por índice LIRAa**
    
    Ordena municípios por valor do índice selecionado.
    
    **Parâmetros**:
    - `ordem=desc`: Municípios com índices mais altos (piores)
    - `ordem=asc`: Municípios com índices mais baixos (melhores)
    
    **Exemplo**:
    ```bash
    curl "http://localhost:8000/api/liraa/ranking?ano=2024&tipo_indice=IPO&limite=10&ordem=desc"
    ```
    """
    
    raise HTTPException(
        status_code=503,
        detail="Dados LIRAa não disponíveis. Aguardando carregamento de datasets."
    )


# ============================================================================
# COMPARATIVO TEMPORAL
# ============================================================================

@router.get("/comparativo", response_model=ComparativoLiraaResponse)
async def get_comparativo_liraa(
    tipo_indice: TipoIndice = Query(..., description="Tipo de índice"),
    ano1: int = Query(..., ge=2000, le=2100, description="Ano do período 1"),
    semana1: int = Query(..., ge=1, le=53, description="Semana do período 1"),
    ano2: int = Query(..., ge=2000, le=2100, description="Ano do período 2"),
    semana2: int = Query(..., ge=1, le=53, description="Semana do período 2"),
    codigo_ibge: Optional[str] = Query(None, min_length=7, max_length=7),
):
    """
    **Compara índices LIRAa entre dois períodos**
    
    Analisa variação temporal para identificar melhoras ou pioras.
    
    **Métricas retornadas**:
    - Variação absoluta (pontos percentuais)
    - Variação percentual
    - Tendência (MELHORA/PIORA/ESTAVEL)
    
    **Exemplo**:
    ```bash
    curl "http://localhost:8000/api/liraa/comparativo?\
tipo_indice=IPO&ano1=2023&semana1=1&ano2=2024&semana2=1"
    ```
    """
    
    raise HTTPException(
        status_code=503,
        detail="Dados LIRAa não disponíveis. Aguardando carregamento de datasets."
    )


# ============================================================================
# MAPA
# ============================================================================

@router.get("/mapa", response_model=MapaLiraaResponse)
async def get_mapa_liraa(
    ano: int = Query(..., ge=2000, le=2100),
    tipo_indice: TipoIndice = Query(..., description="Tipo de índice para visualização"),
    semana_epi: Optional[int] = Query(None, ge=1, le=53),
):
    """
    **Retorna GeoJSON para visualização de índices LIRAa no mapa**
    
    Formato FeatureCollection com polígonos de municípios e propriedades:
    - Valores de todos os índices (IPO, IDO, IVO, IMO)
    - Classificação de risco
    - Dados do levantamento
    
    **Integração com frontend**:
    ```javascript
    // Leaflet/React-Leaflet
    const response = await fetch('/api/liraa/mapa?ano=2024&tipo_indice=IPO');
    const geojson = await response.json();
    
    <GeoJSON data={geojson} style={styleByRisk} />
    ```
    
    **Exemplo**:
    ```bash
    curl "http://localhost:8000/api/liraa/mapa?ano=2024&tipo_indice=IPO"
    ```
    """
    
    raise HTTPException(
        status_code=503,
        detail="Dados LIRAa não disponíveis. Aguardando carregamento de datasets."
    )


# ============================================================================
# ESTATÍSTICAS
# ============================================================================

@router.get("/estatisticas")
async def get_estatisticas_liraa(
    ano: int = Query(..., ge=2000, le=2100),
    tipo_indice: Optional[TipoIndice] = Query(None),
):
    """
    **Retorna estatísticas descritivas dos índices LIRAa**
    
    **Métricas**:
    - Média, mediana, desvio padrão
    - Mínimo e máximo
    - Percentis (p25, p50, p75, p95)
    - Distribuição por classificação de risco
    - Total de imóveis inspecionados
    
    **Exemplo**:
    ```bash
    curl "http://localhost:8000/api/liraa/estatisticas?ano=2024&tipo_indice=IPO"
    ```
    """
    
    raise HTTPException(
        status_code=503,
        detail="Dados LIRAa não disponíveis. Aguardando carregamento de datasets."
    )
