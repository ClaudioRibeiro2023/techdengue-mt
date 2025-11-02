"""
Mapa Router - Endpoints for map visualization layers
"""
import os
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException

from app.schemas.mapa import (
    TipoCamada,
    MapaCamadasResponse,
    HeatmapData,
    EstatisticasMapa,
    FiltroMapa,
    SerieTemporalMunicipio
)
from app.services.mapa_service import MapaService

router = APIRouter(prefix="/mapa", tags=["Mapa"])

# Database connection
DB_CONN_STR = os.getenv(
    "DATABASE_URL",
    "postgresql://techdengue:techdengue@localhost:5432/techdengue"
).replace("postgresql+asyncpg://", "postgresql://")


@router.get("/camadas", response_model=MapaCamadasResponse)
async def obter_camadas_mapa(
    tipo_camada: TipoCamada = Query(..., description="Tipo de camada: incidencia, ipo, ido, ivo, imo"),
    competencia_inicio: str = Query(..., pattern=r"^\d{6}$", description="Período início YYYYMM"),
    competencia_fim: str = Query(..., pattern=r"^\d{6}$", description="Período fim YYYYMM"),
    municipios: Optional[str] = Query(None, description="Códigos IBGE separados por vírgula (ex: 5103403,5105606)"),
    cluster: bool = Query(False, description="Aplicar clustering para reduzir features"),
    max_features: int = Query(10000, ge=1, le=50000, description="Máximo de features retornadas")
):
    """
    Retorna camadas do mapa em formato GeoJSON para visualização.
    
    **Tipos de Camada:**
    - `incidencia`: Incidência de dengue por 100k habitantes
    - `ipo`: Índice de Positividade de Ovos (LIRAa)
    - `ido`: Índice de Densidade de Ovos (LIRAa)
    - `ivo`: Índice de Vigilância de Ovos
    - `imo`: Índice de Mosquitos por Ovitrampa
    
    **Período:**
    - Define o intervalo de competências para agregação dos dados
    - Formato: YYYYMM (ex: 202401 para Janeiro/2024)
    
    **Filtros:**
    - `municipios`: Lista de códigos IBGE para filtrar municípios específicos
    - `cluster`: Reduz o número de features através de clustering espacial
    - `max_features`: Limite de features retornadas (performance)
    
    **Classificação de Risco (Incidência):**
    - **Baixo** (<100 casos/100k): Verde
    - **Médio** (100-300): Amarelo
    - **Alto** (300-500): Laranja
    - **Muito Alto** (>500): Vermelho
    
    **Exemplo de uso (curl):**
    ```bash
    curl "http://localhost:8000/api/mapa/camadas?tipo_camada=incidencia&competencia_inicio=202401&competencia_fim=202401" \\
      -H "Authorization: Bearer $TOKEN"
    ```
    
    **Resposta:**
    ```json
    {
      "tipo_camada": "incidencia",
      "competencia_inicio": "202401",
      "competencia_fim": "202401",
      "total_municipios": 10,
      "total_casos": 5432,
      "total_obitos": 12,
      "incidencia_media": 245.67,
      "data": {
        "type": "FeatureCollection",
        "features": [...]
      },
      "metadata": {}
    }
    ```
    
    **Performance:**
    - Objetivo: p95 ≤ 4s para ≤10k features
    - Recomendado: Usar `cluster=true` para grandes volumes
    - Cache: Considere cache em produção para períodos fixos
    """
    
    # Parse municipalities filter
    municipios_list = None
    if municipios:
        municipios_list = [m.strip() for m in municipios.split(',') if m.strip()]
        # Validate IBGE codes
        for cod in municipios_list:
            if len(cod) != 7 or not cod.isdigit():
                raise HTTPException(
                    status_code=400,
                    detail=f"Código IBGE inválido: {cod}. Deve ter 7 dígitos numéricos."
                )
    
    # Validate period
    if competencia_inicio > competencia_fim:
        raise HTTPException(
            status_code=400,
            detail="competencia_inicio deve ser menor ou igual a competencia_fim"
        )
    
    service = MapaService(DB_CONN_STR)
    
    try:
        if tipo_camada == TipoCamada.INCIDENCIA:
            return service.get_camada_incidencia(
                competencia_inicio=competencia_inicio,
                competencia_fim=competencia_fim,
                municipios=municipios_list,
                cluster=cluster,
                max_features=max_features
            )
        else:
            # TODO: Implement other layer types (IPO, IDO, IVO, IMO)
            raise HTTPException(
                status_code=501,
                detail=f"Tipo de camada '{tipo_camada}' ainda não implementado. Disponível: incidencia"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar camada do mapa: {str(e)}"
        )


@router.get("/municipios", response_model=dict)
async def listar_municipios():
    """
    Lista municípios disponíveis com suas informações básicas.
    
    **Retorna:**
    ```json
    {
      "municipios": [
        {
          "cod_ibge": "5103403",
          "nome": "Cuiabá",
          "populacao": 618124,
          "centroid": {"lat": -15.6014, "lon": -56.0967}
        }
      ],
      "total": 10
    }
    ```
    """
    # In production, load from database
    from app.services.mapa_service import MT_MUNICIPIOS
    
    municipios = [
        {
            "cod_ibge": cod,
            "nome": info['nome'],
            "populacao": info['pop'],
            "centroid": {"lat": info['lat'], "lon": info['lon']}
        }
        for cod, info in MT_MUNICIPIOS.items()
    ]
    
    return {
        "municipios": sorted(municipios, key=lambda x: x['nome']),
        "total": len(municipios)
    }


@router.get("/heatmap", response_model=HeatmapData)
async def obter_heatmap(
    ano: int = Query(..., ge=2000, le=2100, description="Ano"),
    semana_epi_inicio: Optional[int] = Query(None, ge=1, le=53, description="Semana epidemiológica início"),
    semana_epi_fim: Optional[int] = Query(None, ge=1, le=53, description="Semana epidemiológica fim"),
    doenca_tipo: Optional[str] = Query(None, description="DENGUE, ZIKA, CHIKUNGUNYA, FEBRE_AMARELA"),
    max_points: int = Query(5000, ge=1, le=10000, description="Máximo de pontos")
):
    """
    Retorna dados para camada heatmap (densidade de casos)
    
    Os pontos retornados contêm latitude, longitude e intensidade (incidência).
    Usar com bibliotecas como Leaflet.heat ou Google Maps Heatmap Layer.
    
    **Exemplo:**
    ```bash
    curl "http://localhost:8000/api/mapa/heatmap?ano=2024&semana_epi_inicio=1&semana_epi_fim=10"
    ```
    
    **Response:**
    ```json
    {
      "points": [
        {"lat": -15.6014, "lng": -56.0967, "intensity": 245.67},
        {"lat": -15.6467, "lng": -56.1326, "intensity": 180.23}
      ],
      "max_intensity": 450.5,
      "total_points": 141
    }
    ```
    """
    service = MapaService(DB_CONN_STR)
    
    try:
        filtro = FiltroMapa(
            ano=ano,
            semana_epi_inicio=semana_epi_inicio,
            semana_epi_fim=semana_epi_fim,
            doenca_tipo=doenca_tipo
        )
        
        return service.get_heatmap_data(filtro, max_points)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar heatmap: {str(e)}"
        )


@router.get("/estatisticas", response_model=EstatisticasMapa)
async def obter_estatisticas(
    ano: int = Query(..., ge=2000, le=2100, description="Ano"),
    semana_epi_inicio: Optional[int] = Query(None, ge=1, le=53),
    semana_epi_fim: Optional[int] = Query(None, ge=1, le=53),
    doenca_tipo: Optional[str] = Query(None, description="DENGUE, ZIKA, CHIKUNGUNYA"),
    data_inicio: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    data_fim: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    """
    Retorna estatísticas agregadas para exibição no dashboard do mapa
    
    Inclui totalizadores, distribuição por risco, município com mais casos, etc.
    Útil para KPIs e resumos executivos.
    
    **Exemplo:**
    ```bash
    curl "http://localhost:8000/api/mapa/estatisticas?ano=2024&semana_epi_inicio=1&semana_epi_fim=44"
    ```
    
    **Response:**
    ```json
    {
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
    ```
    """
    service = MapaService(DB_CONN_STR)
    
    try:
        filtro = FiltroMapa(
            ano=ano,
            semana_epi_inicio=semana_epi_inicio,
            semana_epi_fim=semana_epi_fim,
            doenca_tipo=doenca_tipo,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        
        return service.get_estatisticas_agregadas(filtro)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular estatísticas: {str(e)}"
        )


@router.get("/series-temporais/{codigo_ibge}", response_model=SerieTemporalMunicipio)
async def obter_serie_temporal(
    codigo_ibge: str,
    ano: int = Query(..., ge=2000, le=2100, description="Ano da série"),
    doenca_tipo: Optional[str] = Query(None, description="DENGUE, ZIKA, CHIKUNGUNYA")
):
    """
    Retorna série temporal de incidência para um município específico
    
    Útil para gráficos de linha mostrando evolução semanal/mensal.
    Pode ser usado em popups do mapa ou em drill-down.
    
    **Parâmetros:**
    - `codigo_ibge`: Código IBGE de 7 dígitos (ex: 5103403 para Cuiabá)
    - `ano`: Ano da série temporal
    - `doenca_tipo`: Filtro por tipo de doença (opcional)
    
    **Exemplo:**
    ```bash
    curl "http://localhost:8000/api/mapa/series-temporais/5103403?ano=2024&doenca_tipo=DENGUE"
    ```
    
    **Response:**
    ```json
    {
      "codigo_ibge": "5103403",
      "nome": "Cuiabá",
      "serie": [
        {"data": "2024-W01", "valor": 125.5},
        {"data": "2024-W02", "valor": 134.2},
        {"data": "2024-W03", "valor": 142.8}
      ]
    }
    ```
    """
    # Validar código IBGE
    if len(codigo_ibge) != 7 or not codigo_ibge.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Código IBGE deve ter 7 dígitos numéricos"
        )
    
    service = MapaService(DB_CONN_STR)
    
    try:
        return service.get_serie_temporal_municipio(
            codigo_ibge=codigo_ibge,
            ano=ano,
            doenca_tipo=doenca_tipo
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter série temporal: {str(e)}"
        )
