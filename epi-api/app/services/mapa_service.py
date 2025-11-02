"""
Mapa Service - Calculate epidemiological indicators for map visualization
"""
from typing import List, Dict, Tuple, Optional
from datetime import date
import psycopg2
from psycopg2.extras import RealDictCursor

from app.schemas.mapa import (
    TipoCamada,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONGeometry,
    MunicipioProperties,
    MapaCamadasResponse,
    HeatmapPoint,
    HeatmapData,
    ChoroplethFeature,
    ChoroplethFeatureCollection,
    ChoroplethMunicipioProperties,
    PolygonCoordinates,
    EstatisticasMapa,
    FiltroMapa,
    SerieTemporal,
    SerieTemporalMunicipio
)


# MT municipalities with approximate centroids and population (sample data)
# In production, this would be loaded from a municipalities reference table
MT_MUNICIPIOS = {
    "5103403": {"nome": "Cuiabá", "lat": -15.6014, "lon": -56.0967, "pop": 618124},
    "5105606": {"nome": "Várzea Grande", "lat": -15.6467, "lon": -56.1326, "pop": 290215},
    "5103900": {"nome": "Rondonópolis", "lat": -16.4708, "lon": -54.6351, "pop": 238400},
    "5107909": {"nome": "Sinop", "lat": -11.8608, "lon": -55.5047, "pop": 142291},
    "5106505": {"nome": "Tangará da Serra", "lat": -14.6233, "lon": -57.4936, "pop": 103750},
    "5100201": {"nome": "Alta Floresta", "lat": -9.8757, "lon": -56.0875, "pop": 55347},
    "5103379": {"nome": "Cáceres", "lat": -16.0728, "lon": -57.6823, "pop": 94861},
    "5101001": {"nome": "Barra do Garças", "lat": -15.8897, "lon": -52.2564, "pop": 59727},
    "5107602": {"nome": "Sorriso", "lat": -12.5436, "lon": -55.7147, "pop": 91382},
    "5104104": {"nome": "Pontes e Lacerda", "lat": -15.2261, "lon": -59.3356, "pop": 46822},
}


class MapaService:
    """Service for calculating map indicators and generating GeoJSON layers"""
    
    def __init__(self, db_connection_string: str):
        self.conn_str = db_connection_string
    
    def get_camada_incidencia(
        self,
        competencia_inicio: str,
        competencia_fim: str,
        municipios: Optional[List[str]] = None,
        cluster: bool = False,
        max_features: int = 10000
    ) -> MapaCamadasResponse:
        """
        Generate incidence map layer (casos / 100k habitantes).
        
        Args:
            competencia_inicio: Start period YYYYMM
            competencia_fim: End period YYYYMM
            municipios: Filter by specific IBGE codes (optional)
            cluster: Apply clustering to reduce features
            max_features: Maximum features to return
            
        Returns:
            MapaCamadasResponse with GeoJSON features
        """
        # Convert competencias to dates
        dt_inicio = self._competencia_to_date(competencia_inicio)
        dt_fim = self._competencia_to_date(competencia_fim)
        
        # Query aggregated data by municipality
        conn = psycopg2.connect(self.conn_str)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                municipio_filter = ""
                params = [dt_inicio, dt_fim]
                
                if municipios:
                    municipio_filter = "AND municipio_cod_ibge = ANY(%s)"
                    params.append(municipios)
                
                query = f"""
                    SELECT 
                        municipio_cod_ibge,
                        COUNT(*) as total_casos,
                        COUNT(*) FILTER (WHERE evolucao = 'OBITO') as total_obitos,
                        COUNT(*) FILTER (WHERE classificacao_final LIKE 'DENGUE%%') as casos_confirmados
                    FROM indicador_epi
                    WHERE competencia >= %s AND competencia <= %s
                      {municipio_filter}
                    GROUP BY municipio_cod_ibge
                    ORDER BY total_casos DESC
                    LIMIT %s
                """
                params.append(max_features)
                
                cur.execute(query, params)
                rows = cur.fetchall()
        finally:
            conn.close()
        
        # Build GeoJSON features
        features = []
        total_casos = 0
        total_obitos = 0
        incidencias = []
        
        for row in rows:
            cod_ibge = row['municipio_cod_ibge']
            casos = row['total_casos']
            obitos = row['total_obitos']
            
            # Get municipality info
            mun_info = MT_MUNICIPIOS.get(cod_ibge)
            if not mun_info:
                continue  # Skip if municipality not in reference data
            
            pop = mun_info['pop']
            incidencia = (casos / pop * 100000) if pop > 0 else 0.0
            letalidade = (obitos / casos * 100) if casos > 0 else 0.0
            
            # Risk classification based on incidence
            classe_risco, cor_hex = self._classify_risk_incidencia(incidencia)
            
            feature = GeoJSONFeature(
                geometry=GeoJSONGeometry(
                    type="Point",
                    coordinates=[mun_info['lon'], mun_info['lat']]
                ),
                properties=MunicipioProperties(
                    municipio_cod_ibge=cod_ibge,
                    municipio_nome=mun_info['nome'],
                    populacao=pop,
                    casos=casos,
                    incidencia=round(incidencia, 2),
                    obitos=obitos,
                    letalidade=round(letalidade, 2),
                    classe_risco=classe_risco,
                    cor_hex=cor_hex
                )
            )
            features.append(feature)
            
            total_casos += casos
            total_obitos += obitos
            incidencias.append(incidencia)
        
        incidencia_media = sum(incidencias) / len(incidencias) if incidencias else 0.0
        
        # Apply clustering if requested
        metadata = {}
        if cluster and len(features) > 100:
            features, metadata = self._apply_clustering(features, max_features)
        
        return MapaCamadasResponse(
            tipo_camada=TipoCamada.INCIDENCIA,
            competencia_inicio=competencia_inicio,
            competencia_fim=competencia_fim,
            total_municipios=len(features),
            total_casos=total_casos,
            total_obitos=total_obitos,
            incidencia_media=round(incidencia_media, 2),
            data=GeoJSONFeatureCollection(features=features),
            metadata=metadata
        )
    
    def _classify_risk_incidencia(self, incidencia: float) -> Tuple[str, str]:
        """
        Classify risk level based on incidence rate.
        
        Thresholds (WHO/PAHO recommendations):
        - < 100: baixo (green)
        - 100-300: medio (yellow)
        - 300-500: alto (orange)
        - > 500: muito_alto (red)
        """
        if incidencia < 100:
            return "baixo", "#4CAF50"  # Green
        elif incidencia < 300:
            return "medio", "#FFC107"  # Yellow
        elif incidencia < 500:
            return "alto", "#FF9800"  # Orange
        else:
            return "muito_alto", "#F44336"  # Red
    
    def _competencia_to_date(self, competencia: str) -> date:
        """Convert YYYYMM to first day of month"""
        year = int(competencia[:4])
        month = int(competencia[4:6])
        return date(year, month, 1)
    
    def _apply_clustering(
        self,
        features: List[GeoJSONFeature],
        max_features: int
    ) -> Tuple[List[GeoJSONFeature], Dict]:
        """
        Apply simple grid-based clustering to reduce feature count.
        
        In production, use algorithms like K-means or DBSCAN.
        For now, implements a simple spatial grid aggregation.
        """
        # Simple implementation: keep top N features by case count
        # In production, implement proper clustering (e.g., supercluster algorithm)
        features_sorted = sorted(
            features,
            key=lambda f: f.properties.casos,
            reverse=True
        )
        
        clustered = features_sorted[:max_features]
        
        metadata = {
            "clustering_applied": True,
            "original_count": len(features),
            "clustered_count": len(clustered),
            "algorithm": "top_n_by_cases"
        }
        
        return clustered, metadata
    
    def get_heatmap_data(
        self,
        filtro: FiltroMapa,
        max_points: int = 5000
    ) -> HeatmapData:
        """
        Gera dados para camada heatmap
        
        Args:
            filtro: Filtros temporais e espaciais
            max_points: Máximo de pontos a retornar
            
        Returns:
            HeatmapData com pontos e intensidades
        """
        conn = psycopg2.connect(self.conn_str)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Montar query baseada nos filtros
                where_clauses = []
                params = []
                
                if filtro.ano:
                    where_clauses.append("ano = %s")
                    params.append(filtro.ano)
                
                if filtro.semana_epi_inicio and filtro.semana_epi_fim:
                    where_clauses.append("semana_epi BETWEEN %s AND %s")
                    params.extend([filtro.semana_epi_inicio, filtro.semana_epi_fim])
                
                if filtro.municipios:
                    where_clauses.append("municipio_codigo = ANY(%s)")
                    params.append(filtro.municipios)
                
                if filtro.doenca_tipo:
                    where_clauses.append("doenca_tipo = %s")
                    params.append(filtro.doenca_tipo)
                
                where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                query = f"""
                    SELECT 
                        municipio_codigo,
                        SUM(casos_confirmados) as casos
                    FROM indicador_epi
                    {where_sql}
                    GROUP BY municipio_codigo
                    ORDER BY casos DESC
                    LIMIT %s
                """
                params.append(max_points)
                
                cur.execute(query, params)
                rows = cur.fetchall()
        finally:
            conn.close()
        
        # Converter para pontos de heatmap
        points = []
        max_intensity = 0.0
        
        for row in rows:
            cod_ibge = row['municipio_codigo']
            casos = row['casos']
            
            mun_info = MT_MUNICIPIOS.get(cod_ibge)
            if not mun_info:
                continue
            
            # Calcular intensidade (incidência)
            intensity = (casos / mun_info['pop'] * 100000) if mun_info['pop'] > 0 else 0
            
            points.append(HeatmapPoint(
                lat=mun_info['lat'],
                lng=mun_info['lon'],
                intensity=round(intensity, 2)
            ))
            
            max_intensity = max(max_intensity, intensity)
        
        return HeatmapData(
            points=points,
            max_intensity=round(max_intensity, 2),
            total_points=len(points),
            metadata={"filtro_aplicado": filtro.model_dump(exclude_none=True)}
        )
    
    def get_estatisticas_agregadas(
        self,
        filtro: FiltroMapa
    ) -> EstatisticasMapa:
        """
        Calcula estatísticas agregadas para o período
        
        Args:
            filtro: Filtros temporais e espaciais
            
        Returns:
            EstatisticasMapa com totalizadores e distribuições
        """
        conn = psycopg2.connect(self.conn_str)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Montar filtros
                where_clauses = []
                params = []
                
                if filtro.ano:
                    where_clauses.append("ano = %s")
                    params.append(filtro.ano)
                
                if filtro.semana_epi_inicio and filtro.semana_epi_fim:
                    where_clauses.append("semana_epi BETWEEN %s AND %s")
                    params.extend([filtro.semana_epi_inicio, filtro.semana_epi_fim])
                
                if filtro.doenca_tipo:
                    where_clauses.append("doenca_tipo = %s")
                    params.append(filtro.doenca_tipo)
                
                where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                # Query principal
                query = f"""
                    SELECT 
                        COUNT(DISTINCT municipio_codigo) as total_municipios,
                        SUM(casos_confirmados) as total_casos,
                        SUM(obitos) as total_obitos,
                        municipio_codigo,
                        SUM(casos_confirmados) as casos_mun
                    FROM indicador_epi
                    {where_sql}
                    GROUP BY municipio_codigo
                """
                
                cur.execute(query, params)
                rows = cur.fetchall()
                
                if not rows:
                    # Retornar estatísticas vazias
                    return EstatisticasMapa(
                        total_municipios=0,
                        total_casos=0,
                        total_obitos=0,
                        taxa_letalidade=0.0,
                        incidencia_media=0.0,
                        incidencia_maxima=0.0,
                        distribuicao_risco={},
                        periodo_inicio=filtro.data_inicio or "",
                        periodo_fim=filtro.data_fim or ""
                    )
                
                # Calcular totais
                total_municipios = len(rows)
                total_casos = sum(r['casos_mun'] for r in rows)
                total_obitos = sum(r.get('total_obitos', 0) or 0 for r in rows)
                
                taxa_letalidade = (total_obitos / total_casos * 100) if total_casos > 0 else 0.0
                
                # Calcular incidências
                incidencias = []
                max_incidencia = 0.0
                municipio_max_casos = None
                max_casos_valor = 0
                distribuicao_risco = {"BAIXO": 0, "MEDIO": 0, "ALTO": 0, "MUITO_ALTO": 0}
                
                for row in rows:
                    cod_ibge = row['municipio_codigo']
                    casos = row['casos_mun']
                    
                    mun_info = MT_MUNICIPIOS.get(cod_ibge)
                    if not mun_info:
                        continue
                    
                    incidencia = (casos / mun_info['pop'] * 100000) if mun_info['pop'] > 0 else 0
                    incidencias.append(incidencia)
                    
                    if incidencia > max_incidencia:
                        max_incidencia = incidencia
                    
                    if casos > max_casos_valor:
                        max_casos_valor = casos
                        municipio_max_casos = mun_info['nome']
                    
                    # Classificar risco
                    if incidencia < 100:
                        distribuicao_risco["BAIXO"] += 1
                    elif incidencia < 300:
                        distribuicao_risco["MEDIO"] += 1
                    elif incidencia < 500:
                        distribuicao_risco["ALTO"] += 1
                    else:
                        distribuicao_risco["MUITO_ALTO"] += 1
                
                incidencia_media = sum(incidencias) / len(incidencias) if incidencias else 0.0
                
                return EstatisticasMapa(
                    total_municipios=total_municipios,
                    total_casos=total_casos,
                    total_obitos=total_obitos,
                    taxa_letalidade=round(taxa_letalidade, 2),
                    incidencia_media=round(incidencia_media, 2),
                    incidencia_maxima=round(max_incidencia, 2),
                    municipio_max_casos=municipio_max_casos,
                    distribuicao_risco=distribuicao_risco,
                    periodo_inicio=filtro.data_inicio or f"{filtro.ano}-01-01" if filtro.ano else "",
                    periodo_fim=filtro.data_fim or f"{filtro.ano}-12-31" if filtro.ano else ""
                )
        finally:
            conn.close()
    
    def get_serie_temporal_municipio(
        self,
        codigo_ibge: str,
        ano: int,
        doenca_tipo: Optional[str] = None
    ) -> SerieTemporalMunicipio:
        """
        Retorna série temporal de incidência para um município
        
        Args:
            codigo_ibge: Código IBGE do município
            ano: Ano da série
            doenca_tipo: Tipo de doença (opcional)
            
        Returns:
            SerieTemporalMunicipio com série semanal
        """
        conn = psycopg2.connect(self.conn_str)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                where_clauses = [
                    "municipio_codigo = %s",
                    "ano = %s"
                ]
                params = [codigo_ibge, ano]
                
                if doenca_tipo:
                    where_clauses.append("doenca_tipo = %s")
                    params.append(doenca_tipo)
                
                where_sql = " AND ".join(where_clauses)
                
                query = f"""
                    SELECT 
                        semana_epi,
                        SUM(casos_confirmados) as casos
                    FROM indicador_epi
                    WHERE {where_sql}
                    GROUP BY semana_epi
                    ORDER BY semana_epi
                """
                
                cur.execute(query, params)
                rows = cur.fetchall()
        finally:
            conn.close()
        
        # Obter info do município
        mun_info = MT_MUNICIPIOS.get(codigo_ibge, {"nome": "Desconhecido", "pop": 1})
        
        # Construir série
        serie = []
        for row in rows:
            semana = row['semana_epi']
            casos = row['casos']
            
            # Calcular incidência
            incidencia = (casos / mun_info['pop'] * 100000) if mun_info['pop'] > 0 else 0
            
            serie.append(SerieTemporal(
                data=f"{ano}-W{semana:02d}",
                valor=round(incidencia, 2)
            ))
        
        return SerieTemporalMunicipio(
            codigo_ibge=codigo_ibge,
            nome=mun_info['nome'],
            serie=serie
        )
