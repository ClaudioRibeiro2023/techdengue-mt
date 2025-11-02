"""
Dashboard Service - Calculate KPIs, series and rankings for dashboard
"""
from typing import List, Optional, Dict, Tuple
from datetime import date, datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

from app.schemas.dashboard import (
    DashboardKPIs,
    KPICard,
    KPIVariacao,
    TendenciaDirecao,
    SeriesTemporaisResponse,
    SerieTemporal,
    PontoSerie,
    TopNResponse,
    ItemRanking,
    PeriodoAgregacao,
    DrillDownDados,
    DoencaTipo
)

# MT municipalities reference (usar tabela de municípios em produção)
MT_MUNICIPIOS = {
    "5103403": {"nome": "Cuiabá", "pop": 618124},
    "5105606": {"nome": "Várzea Grande", "pop": 290215},
    "5103900": {"nome": "Rondonópolis", "pop": 238400},
    "5107909": {"nome": "Sinop", "pop": 142291},
    "5106505": {"nome": "Tangará da Serra", "pop": 103750},
    "5100201": {"nome": "Alta Floresta", "pop": 55347},
    "5103379": {"nome": "Cáceres", "pop": 94861},
    "5101001": {"nome": "Barra do Garças", "pop": 59727},
    "5107602": {"nome": "Sorriso", "pop": 91382},
    "5104104": {"nome": "Pontes e Lacerda", "pop": 46822},
}


class DashboardService:
    """Service para cálculos de indicadores do dashboard"""
    
    def __init__(self, db_connection_string: str):
        self.conn_str = db_connection_string
    
    def get_kpis(
        self,
        ano: int,
        semana_epi_inicio: Optional[int] = None,
        semana_epi_fim: Optional[int] = None,
        doenca_tipo: Optional[str] = None,
        comparar_com_periodo_anterior: bool = True
    ) -> DashboardKPIs:
        """
        Calcula KPIs principais do dashboard
        
        Args:
            ano: Ano de referência
            semana_epi_inicio: Semana epi início (opcional)
            semana_epi_fim: Semana epi fim (opcional)
            doenca_tipo: Filtro por doença (opcional)
            comparar_com_periodo_anterior: Se True, calcula variações
            
        Returns:
            DashboardKPIs com todos os cards
        """
        conn = psycopg2.connect(self.conn_str)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Montar filtros
                where_clauses = ["ano = %s"]
                params = [ano]
                
                if semana_epi_inicio and semana_epi_fim:
                    where_clauses.append("semana_epi BETWEEN %s AND %s")
                    params.extend([semana_epi_inicio, semana_epi_fim])
                
                if doenca_tipo:
                    where_clauses.append("doenca_tipo = %s")
                    params.append(doenca_tipo)
                
                where_sql = " AND ".join(where_clauses)
                
                # Query principal - período atual
                query_atual = f"""
                    SELECT 
                        COUNT(DISTINCT municipio_codigo) as total_municipios,
                        SUM(casos_confirmados) as total_casos,
                        SUM(obitos) as total_obitos,
                        SUM(casos_graves) as casos_graves,
                        municipio_codigo,
                        SUM(casos_confirmados) as casos_mun
                    FROM indicador_epi
                    WHERE {where_sql}
                    GROUP BY municipio_codigo
                """
                
                cur.execute(query_atual, params)
                rows_atual = cur.fetchall()
                
                # Calcular totais do período atual
                total_casos = sum(r['casos_mun'] for r in rows_atual)
                total_obitos = sum(r.get('total_obitos', 0) or 0 for r in rows_atual)
                casos_graves = sum(r.get('casos_graves', 0) or 0 for r in rows_atual)
                
                taxa_letalidade = (total_obitos / total_casos * 100) if total_casos > 0 else 0.0
                
                # Calcular incidência média
                incidencias = []
                municipios_risco_alto = 0
                
                for row in rows_atual:
                    cod_ibge = row['municipio_codigo']
                    casos = row['casos_mun']
                    
                    mun_info = MT_MUNICIPIOS.get(cod_ibge)
                    if not mun_info:
                        continue
                    
                    incidencia = (casos / mun_info['pop'] * 100000) if mun_info['pop'] > 0 else 0
                    incidencias.append(incidencia)
                    
                    # Contar municípios em risco alto/muito alto
                    if incidencia >= 300:  # Alto ou Muito Alto
                        municipios_risco_alto += 1
                
                incidencia_media = sum(incidencias) / len(incidencias) if incidencias else 0.0
                
                # Variações (comparar com período anterior se solicitado)
                variacao_casos = None
                variacao_obitos = None
                variacao_letalidade = None
                variacao_incidencia = None
                
                if comparar_com_periodo_anterior:
                    # Calcular período anterior (mesmo intervalo, ano/semanas anteriores)
                    if semana_epi_inicio and semana_epi_fim:
                        # Período anterior: mesmas semanas, ano anterior
                        ano_anterior = ano - 1
                        params_anterior = [ano_anterior]
                        
                        if semana_epi_inicio and semana_epi_fim:
                            params_anterior.extend([semana_epi_inicio, semana_epi_fim])
                        
                        if doenca_tipo:
                            params_anterior.append(doenca_tipo)
                        
                        cur.execute(query_atual, params_anterior)
                        rows_anterior = cur.fetchall()
                        
                        total_casos_anterior = sum(r['casos_mun'] for r in rows_anterior)
                        total_obitos_anterior = sum(r.get('total_obitos', 0) or 0 for r in rows_anterior)
                        
                        taxa_letalidade_anterior = (total_obitos_anterior / total_casos_anterior * 100) if total_casos_anterior > 0 else 0.0
                        
                        incidencias_anterior = []
                        for row in rows_anterior:
                            cod_ibge = row['municipio_codigo']
                            casos = row['casos_mun']
                            mun_info = MT_MUNICIPIOS.get(cod_ibge)
                            if mun_info:
                                inc = (casos / mun_info['pop'] * 100000) if mun_info['pop'] > 0 else 0
                                incidencias_anterior.append(inc)
                        
                        incidencia_media_anterior = sum(incidencias_anterior) / len(incidencias_anterior) if incidencias_anterior else 0.0
                        
                        # Calcular variações
                        variacao_casos = self._calc_variacao(total_casos, total_casos_anterior)
                        variacao_obitos = self._calc_variacao(total_obitos, total_obitos_anterior)
                        variacao_letalidade = self._calc_variacao(taxa_letalidade, taxa_letalidade_anterior)
                        variacao_incidencia = self._calc_variacao(incidencia_media, incidencia_media_anterior)
                
                # Construir KPI Cards
                periodo_inicio = f"{ano}-01-01" if not semana_epi_inicio else f"{ano}-W{semana_epi_inicio:02d}"
                periodo_fim = f"{ano}-12-31" if not semana_epi_fim else f"{ano}-W{semana_epi_fim:02d}"
                
                return DashboardKPIs(
                    total_casos=KPICard(
                        titulo="Total de Casos",
                        valor=float(total_casos),
                        unidade="casos",
                        variacao=variacao_casos,
                        icone="Activity",
                        cor="#FF6B6B",
                        descricao=f"Casos confirmados em {ano}"
                    ),
                    total_obitos=KPICard(
                        titulo="Óbitos",
                        valor=float(total_obitos),
                        unidade="óbitos",
                        variacao=variacao_obitos,
                        icone="AlertTriangle",
                        cor="#F44336",
                        descricao=f"Total de óbitos em {ano}"
                    ),
                    taxa_letalidade=KPICard(
                        titulo="Taxa de Letalidade",
                        valor=round(taxa_letalidade, 2),
                        unidade="%",
                        variacao=variacao_letalidade,
                        icone="TrendingUp",
                        cor="#FFC107",
                        descricao="Óbitos / Casos confirmados"
                    ),
                    incidencia_media=KPICard(
                        titulo="Incidência Média",
                        valor=round(incidencia_media, 2),
                        unidade="/100k hab",
                        variacao=variacao_incidencia,
                        icone="Users",
                        cor="#2196F3",
                        descricao="Incidência média nos municípios"
                    ),
                    municipios_risco_alto=KPICard(
                        titulo="Municípios Alto Risco",
                        valor=float(municipios_risco_alto),
                        unidade="municípios",
                        icone="AlertCircle",
                        cor="#FF9800",
                        descricao="Incidência ≥ 300 casos/100k"
                    ) if municipios_risco_alto > 0 else None,
                    casos_graves=KPICard(
                        titulo="Casos Graves",
                        valor=float(casos_graves),
                        unidade="casos",
                        icone="Heart",
                        cor="#9C27B0",
                        descricao="Casos com sinais de alarme"
                    ) if casos_graves > 0 else None,
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    ultima_atualizacao=datetime.now().isoformat()
                )
        finally:
            conn.close()
    
    def _calc_variacao(self, valor_atual: float, valor_anterior: float) -> Optional[KPIVariacao]:
        """Calcula variação entre períodos"""
        if valor_anterior == 0:
            return None
        
        variacao_abs = valor_atual - valor_anterior
        variacao_pct = (variacao_abs / valor_anterior * 100) if valor_anterior > 0 else 0.0
        
        # Determinar tendência
        if abs(variacao_pct) < 5:  # Menos de 5% = estável
            tendencia = TendenciaDirecao.ESTAVEL
        elif variacao_pct > 0:
            tendencia = TendenciaDirecao.ALTA
        else:
            tendencia = TendenciaDirecao.BAIXA
        
        return KPIVariacao(
            valor_atual=valor_atual,
            valor_anterior=valor_anterior,
            variacao_absoluta=round(variacao_abs, 2),
            variacao_percentual=round(variacao_pct, 2),
            tendencia=tendencia
        )
    
    def get_series_temporais(
        self,
        ano: int,
        periodo_agregacao: PeriodoAgregacao = PeriodoAgregacao.SEMANAL,
        doenca_tipo: Optional[str] = None,
        codigo_ibge: Optional[str] = None
    ) -> SeriesTemporaisResponse:
        """
        Gera séries temporais de indicadores
        
        Args:
            ano: Ano de referência
            periodo_agregacao: semanal, mensal, anual
            doenca_tipo: Filtro por doença (opcional)
            codigo_ibge: Filtro por município (opcional)
            
        Returns:
            SeriesTemporaisResponse com séries
        """
        conn = psycopg2.connect(self.conn_str)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Montar filtros
                where_clauses = ["ano = %s"]
                params = [ano]
                
                if doenca_tipo:
                    where_clauses.append("doenca_tipo = %s")
                    params.append(doenca_tipo)
                
                if codigo_ibge:
                    where_clauses.append("municipio_codigo = %s")
                    params.append(codigo_ibge)
                
                where_sql = " AND ".join(where_clauses)
                
                # Determinar agrupamento
                if periodo_agregacao == PeriodoAgregacao.SEMANAL:
                    group_field = "semana_epi"
                    date_format = f"{ano}-W%02d"
                elif periodo_agregacao == PeriodoAgregacao.MENSAL:
                    group_field = "EXTRACT(MONTH FROM data_notificacao)"
                    date_format = f"{ano}-%02d"
                else:  # ANUAL
                    group_field = "ano"
                    date_format = "%d"
                
                # Query de série temporal
                if periodo_agregacao == PeriodoAgregacao.SEMANAL:
                    query = f"""
                        SELECT 
                            semana_epi,
                            SUM(casos_confirmados) as casos,
                            SUM(obitos) as obitos
                        FROM indicador_epi
                        WHERE {where_sql}
                        GROUP BY semana_epi
                        ORDER BY semana_epi
                    """
                else:
                    # Mensal ou anual (ajustar conforme schema real)
                    query = f"""
                        SELECT 
                            {group_field} as periodo,
                            SUM(casos_confirmados) as casos,
                            SUM(obitos) as obitos
                        FROM indicador_epi
                        WHERE {where_sql}
                        GROUP BY {group_field}
                        ORDER BY {group_field}
                    """
                
                cur.execute(query, params)
                rows = cur.fetchall()
                
                # Construir pontos
                pontos_casos = []
                pontos_obitos = []
                
                for row in rows:
                    if periodo_agregacao == PeriodoAgregacao.SEMANAL:
                        semana = row['semana_epi']
                        data_label = f"{ano}-W{semana:02d}"
                    else:
                        periodo = int(row['periodo'])
                        data_label = date_format % periodo
                    
                    casos = row['casos'] or 0
                    obitos = row['obitos'] or 0
                    
                    pontos_casos.append(PontoSerie(
                        data=data_label,
                        valor=float(casos)
                    ))
                    
                    pontos_obitos.append(PontoSerie(
                        data=data_label,
                        valor=float(obitos)
                    ))
                
                # Construir séries
                series = []
                
                if pontos_casos:
                    series.append(SerieTemporal(
                        nome=f"Casos {doenca_tipo or 'Todas'} {ano}",
                        tipo="casos",
                        unidade="casos",
                        dados=pontos_casos,
                        cor="#FF6B6B"
                    ))
                
                if pontos_obitos:
                    series.append(SerieTemporal(
                        nome=f"Óbitos {doenca_tipo or 'Todas'} {ano}",
                        tipo="obitos",
                        unidade="óbitos",
                        dados=pontos_obitos,
                        cor="#F44336"
                    ))
                
                total_pontos = sum(len(s.dados) for s in series)
                
                return SeriesTemporaisResponse(
                    series=series,
                    periodo_agregacao=periodo_agregacao,
                    periodo_inicio=f"{ano}-01-01",
                    periodo_fim=f"{ano}-12-31",
                    total_pontos=total_pontos
                )
        finally:
            conn.close()
    
    def get_top_n(
        self,
        ano: int,
        limite: int = 10,
        tipo_indicador: str = "casos",
        semana_epi_inicio: Optional[int] = None,
        semana_epi_fim: Optional[int] = None,
        doenca_tipo: Optional[str] = None
    ) -> TopNResponse:
        """
        Retorna Top N municípios por indicador
        
        Args:
            ano: Ano de referência
            limite: Número de itens no ranking (top N)
            tipo_indicador: casos, incidencia, obitos
            semana_epi_inicio: Semana epi início (opcional)
            semana_epi_fim: Semana epi fim (opcional)
            doenca_tipo: Filtro por doença (opcional)
            
        Returns:
            TopNResponse com ranking
        """
        conn = psycopg2.connect(self.conn_str)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Montar filtros
                where_clauses = ["ano = %s"]
                params = [ano]
                
                if semana_epi_inicio and semana_epi_fim:
                    where_clauses.append("semana_epi BETWEEN %s AND %s")
                    params.extend([semana_epi_inicio, semana_epi_fim])
                
                if doenca_tipo:
                    where_clauses.append("doenca_tipo = %s")
                    params.append(doenca_tipo)
                
                where_sql = " AND ".join(where_clauses)
                
                # Query
                query = f"""
                    SELECT 
                        municipio_codigo,
                        SUM(casos_confirmados) as casos,
                        SUM(obitos) as obitos
                    FROM indicador_epi
                    WHERE {where_sql}
                    GROUP BY municipio_codigo
                """
                
                cur.execute(query, params)
                rows = cur.fetchall()
                
                # Calcular ranking
                ranking_data = []
                total_geral = 0
                
                for row in rows:
                    cod_ibge = row['municipio_codigo']
                    casos = row['casos'] or 0
                    obitos = row['obitos'] or 0
                    
                    mun_info = MT_MUNICIPIOS.get(cod_ibge)
                    if not mun_info:
                        continue
                    
                    # Calcular valor conforme indicador
                    if tipo_indicador == "casos":
                        valor = casos
                    elif tipo_indicador == "obitos":
                        valor = obitos
                    else:  # incidencia
                        valor = (casos / mun_info['pop'] * 100000) if mun_info['pop'] > 0 else 0
                    
                    total_geral += casos  # Para calcular %
                    
                    # Classificar risco
                    incidencia = (casos / mun_info['pop'] * 100000) if mun_info['pop'] > 0 else 0
                    nivel_risco, cor = self._classificar_risco_incidencia(incidencia)
                    
                    ranking_data.append({
                        'codigo_ibge': cod_ibge,
                        'nome': mun_info['nome'],
                        'valor': valor,
                        'casos': casos,
                        'populacao': mun_info['pop'],
                        'nivel_risco': nivel_risco,
                        'cor_hex': cor
                    })
                
                # Ordenar por valor (desc)
                ranking_data.sort(key=lambda x: x['valor'], reverse=True)
                
                # Construir itens do ranking (top N)
                ranking_items = []
                for i, item in enumerate(ranking_data[:limite], start=1):
                    percentual = (item['casos'] / total_geral * 100) if total_geral > 0 else 0
                    
                    ranking_items.append(ItemRanking(
                        posicao=i,
                        codigo_ibge=item['codigo_ibge'],
                        nome=item['nome'],
                        valor=round(item['valor'], 2),
                        valor_secundario=float(item['populacao']),
                        percentual=round(percentual, 2),
                        nivel_risco=item['nivel_risco'],
                        cor_hex=item['cor_hex']
                    ))
                
                # Unidade
                unidade = "casos" if tipo_indicador == "casos" else "óbitos" if tipo_indicador == "obitos" else "/100k hab"
                
                periodo_inicio = f"{ano}-01-01" if not semana_epi_inicio else f"{ano}-W{semana_epi_inicio:02d}"
                periodo_fim = f"{ano}-12-31" if not semana_epi_fim else f"{ano}-W{semana_epi_fim:02d}"
                
                return TopNResponse(
                    ranking=ranking_items,
                    tipo_indicador=tipo_indicador,
                    unidade=unidade,
                    total_items=len(ranking_data),
                    limite=limite,
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    agregacao="municipio"
                )
        finally:
            conn.close()
    
    def _classificar_risco_incidencia(self, incidencia: float) -> Tuple[str, str]:
        """Classifica risco baseado na incidência"""
        if incidencia < 100:
            return "BAIXO", "#4CAF50"
        elif incidencia < 300:
            return "MEDIO", "#FFC107"
        elif incidencia < 500:
            return "ALTO", "#FF9800"
        else:
            return "MUITO_ALTO", "#F44336"
