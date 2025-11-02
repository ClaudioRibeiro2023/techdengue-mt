"""
Dashboard Router - Endpoints for KPIs, charts and analytics
"""
import os
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from app.schemas.dashboard import (
    DashboardKPIs,
    SeriesTemporaisResponse,
    TopNResponse,
    PeriodoAgregacao,
    DoencaTipo
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/indicadores", tags=["Dashboard"])

# Database connection
DB_CONN_STR = os.getenv(
    "DATABASE_URL",
    "postgresql://techdengue:techdengue@localhost:5432/techdengue"
).replace("postgresql+asyncpg://", "postgresql://")


@router.get("/kpis", response_model=DashboardKPIs)
async def obter_kpis(
    ano: int = Query(..., ge=2000, le=2100, description="Ano de referência"),
    semana_epi_inicio: Optional[int] = Query(None, ge=1, le=53, description="Semana epidemiológica início"),
    semana_epi_fim: Optional[int] = Query(None, ge=1, le=53, description="Semana epidemiológica fim"),
    doenca_tipo: Optional[DoencaTipo] = Query(None, description="Tipo de doença"),
    comparar_periodo_anterior: bool = Query(True, description="Calcular variações vs período anterior")
):
    """
    Retorna KPIs principais do dashboard epidemiológico
    
    **KPIs incluídos:**
    - Total de Casos (com variação vs período anterior)
    - Total de Óbitos
    - Taxa de Letalidade (%)
    - Incidência Média (/100k habitantes)
    - Municípios em Alto Risco (incidência ≥ 300)
    - Casos Graves (com sinais de alarme)
    
    **Variações:**
    - Se `comparar_periodo_anterior=true`, calcula variação % vs mesmo período do ano anterior
    - Tendência: ALTA (>5%), BAIXA (<-5%), ESTAVEL (-5% a +5%)
    
    **Filtros:**
    - `ano`: Ano de referência (obrigatório)
    - `semana_epi_inicio` / `semana_epi_fim`: Intervalo de semanas epidemiológicas (opcional)
    - `doenca_tipo`: DENGUE, ZIKA, CHIKUNGUNYA, FEBRE_AMARELA (opcional)
    
    **Exemplo:**
    ```bash
    # KPIs do ano completo
    curl "http://localhost:8000/api/indicadores/kpis?ano=2024"
    
    # KPIs das primeiras 10 semanas de 2024
    curl "http://localhost:8000/api/indicadores/kpis?ano=2024&semana_epi_inicio=1&semana_epi_fim=10"
    
    # KPIs apenas de dengue em 2024
    curl "http://localhost:8000/api/indicadores/kpis?ano=2024&doenca_tipo=DENGUE"
    ```
    
    **Response:**
    ```json
    {
      "total_casos": {
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
        "cor": "#FF6B6B"
      },
      "total_obitos": {...},
      "taxa_letalidade": {...},
      "incidencia_media": {...},
      "periodo_inicio": "2024-01-01",
      "periodo_fim": "2024-12-31",
      "ultima_atualizacao": "2024-11-02T16:30:00Z"
    }
    ```
    
    **Uso no frontend:**
    - Exibir em cards no topo do dashboard
    - Usar ícones do lucide-react
    - Aplicar cores nos cards
    - Mostrar setas de tendência (↑ ↓ →)
    """
    service = DashboardService(DB_CONN_STR)
    
    try:
        return service.get_kpis(
            ano=ano,
            semana_epi_inicio=semana_epi_inicio,
            semana_epi_fim=semana_epi_fim,
            doenca_tipo=doenca_tipo.value if doenca_tipo else None,
            comparar_com_periodo_anterior=comparar_periodo_anterior
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular KPIs: {str(e)}"
        )


@router.get("/series-temporais", response_model=SeriesTemporaisResponse)
async def obter_series_temporais(
    ano: int = Query(..., ge=2000, le=2100, description="Ano de referência"),
    periodo_agregacao: PeriodoAgregacao = Query(
        PeriodoAgregacao.SEMANAL,
        description="Agregação: semanal, mensal, anual"
    ),
    doenca_tipo: Optional[DoencaTipo] = Query(None, description="Filtro por doença"),
    codigo_ibge: Optional[str] = Query(
        None,
        min_length=7,
        max_length=7,
        description="Filtro por município (código IBGE)"
    )
):
    """
    Retorna séries temporais de indicadores epidemiológicos
    
    **Séries disponíveis:**
    - Casos confirmados (por período)
    - Óbitos (por período)
    
    **Agregações:**
    - `semanal`: Por semana epidemiológica (formato: 2024-W01, 2024-W02, ...)
    - `mensal`: Por mês (formato: 2024-01, 2024-02, ...)
    - `anual`: Por ano (formato: 2024)
    
    **Filtros:**
    - `ano`: Ano de referência (obrigatório)
    - `periodo_agregacao`: semanal | mensal | anual (default: semanal)
    - `doenca_tipo`: DENGUE, ZIKA, CHIKUNGUNYA, FEBRE_AMARELA (opcional)
    - `codigo_ibge`: 7 dígitos para filtrar por município (opcional)
    
    **Exemplos:**
    ```bash
    # Série semanal de 2024 (todas doenças)
    curl "http://localhost:8000/api/indicadores/series-temporais?ano=2024&periodo_agregacao=semanal"
    
    # Série mensal de dengue em 2024
    curl "http://localhost:8000/api/indicadores/series-temporais?ano=2024&periodo_agregacao=mensal&doenca_tipo=DENGUE"
    
    # Série semanal de Cuiabá em 2024
    curl "http://localhost:8000/api/indicadores/series-temporais?ano=2024&codigo_ibge=5103403"
    ```
    
    **Response:**
    ```json
    {
      "series": [
        {
          "nome": "Casos DENGUE 2024",
          "tipo": "casos",
          "unidade": "casos",
          "dados": [
            {"data": "2024-W01", "valor": 1523.0},
            {"data": "2024-W02", "valor": 1687.0},
            {"data": "2024-W03", "valor": 1845.0}
          ],
          "cor": "#FF6B6B"
        },
        {
          "nome": "Óbitos DENGUE 2024",
          "tipo": "obitos",
          "unidade": "óbitos",
          "dados": [
            {"data": "2024-W01", "valor": 4.0},
            {"data": "2024-W02", "valor": 5.0},
            {"data": "2024-W03", "valor": 3.0}
          ],
          "cor": "#F44336"
        }
      ],
      "periodo_agregacao": "semanal",
      "periodo_inicio": "2024-01-01",
      "periodo_fim": "2024-12-31",
      "total_pontos": 106
    }
    ```
    
    **Uso no frontend:**
    - Gráfico de linha (Chart.js ou Recharts)
    - Eixo X: data, Eixo Y: valor
    - Múltiplas séries com cores diferentes
    - Tooltip com detalhes ao passar mouse
    - Zoom/pan para explorar períodos
    """
    service = DashboardService(DB_CONN_STR)
    
    try:
        return service.get_series_temporais(
            ano=ano,
            periodo_agregacao=periodo_agregacao,
            doenca_tipo=doenca_tipo.value if doenca_tipo else None,
            codigo_ibge=codigo_ibge
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar séries temporais: {str(e)}"
        )


@router.get("/top", response_model=TopNResponse)
async def obter_top_n(
    ano: int = Query(..., ge=2000, le=2100, description="Ano de referência"),
    limite: int = Query(10, ge=1, le=50, description="Top N (1 a 50)"),
    tipo_indicador: str = Query(
        "casos",
        pattern=r"^(casos|incidencia|obitos)$",
        description="casos | incidencia | obitos"
    ),
    semana_epi_inicio: Optional[int] = Query(None, ge=1, le=53),
    semana_epi_fim: Optional[int] = Query(None, ge=1, le=53),
    doenca_tipo: Optional[DoencaTipo] = Query(None, description="Filtro por doença")
):
    """
    Retorna Top N municípios por indicador (ranking)
    
    **Indicadores disponíveis:**
    - `casos`: Total de casos confirmados
    - `incidencia`: Incidência por 100k habitantes
    - `obitos`: Total de óbitos
    
    **Ranking:**
    - Ordenado por valor (decrescente)
    - Inclui posição, município, valor, % do total
    - Classificação de risco (BAIXO, MEDIO, ALTO, MUITO_ALTO)
    - Cores para visualização
    
    **Filtros:**
    - `ano`: Ano de referência (obrigatório)
    - `limite`: Número de itens no ranking - top N (default: 10, max: 50)
    - `tipo_indicador`: casos | incidencia | obitos (default: casos)
    - `semana_epi_inicio` / `semana_epi_fim`: Intervalo de semanas (opcional)
    - `doenca_tipo`: DENGUE, ZIKA, CHIKUNGUNYA, FEBRE_AMARELA (opcional)
    
    **Exemplos:**
    ```bash
    # Top 10 municípios por casos em 2024
    curl "http://localhost:8000/api/indicadores/top?ano=2024&tipo_indicador=casos&limite=10"
    
    # Top 5 por incidência (dengue, semanas 1-10)
    curl "http://localhost:8000/api/indicadores/top?ano=2024&tipo_indicador=incidencia&limite=5&doenca_tipo=DENGUE&semana_epi_inicio=1&semana_epi_fim=10"
    
    # Top 20 por óbitos em 2024
    curl "http://localhost:8000/api/indicadores/top?ano=2024&tipo_indicador=obitos&limite=20"
    ```
    
    **Response:**
    ```json
    {
      "ranking": [
        {
          "posicao": 1,
          "codigo_ibge": "5103403",
          "nome": "Cuiabá",
          "valor": 3845.0,
          "valor_secundario": 618124.0,
          "percentual": 25.23,
          "nivel_risco": "MUITO_ALTO",
          "cor_hex": "#F44336"
        },
        {
          "posicao": 2,
          "codigo_ibge": "5105606",
          "nome": "Várzea Grande",
          "valor": 2134.0,
          "valor_secundario": 290215.0,
          "percentual": 14.01,
          "nivel_risco": "ALTO",
          "cor_hex": "#FF9800"
        }
      ],
      "tipo_indicador": "casos",
      "unidade": "casos",
      "total_items": 141,
      "limite": 10,
      "periodo_inicio": "2024-01-01",
      "periodo_fim": "2024-12-31",
      "agregacao": "municipio"
    }
    ```
    
    **Uso no frontend:**
    - Gráfico de barras horizontais (Chart.js)
    - Lista ordenada com cards
    - Badges com nível de risco
    - Click para drill-down no município
    - Export para CSV/Excel
    """
    service = DashboardService(DB_CONN_STR)
    
    try:
        return service.get_top_n(
            ano=ano,
            limite=limite,
            tipo_indicador=tipo_indicador,
            semana_epi_inicio=semana_epi_inicio,
            semana_epi_fim=semana_epi_fim,
            doenca_tipo=doenca_tipo.value if doenca_tipo else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar ranking: {str(e)}"
        )
