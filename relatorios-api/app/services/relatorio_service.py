"""
Relatório Service - Generate epidemiological reports from database data
"""
import os
import tempfile
from typing import List, Optional
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor

from app.schemas.relatorio import (
    IndicadorMunicipio,
    RelatorioEPI01Response,
    RelatorioEPI01Metadata,
    FormatoRelatorio
)
from app.services.pdf_generator import EPI01PDFGenerator, generate_csv_export


# MT municipalities reference data (same as mapa service)
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


class RelatorioService:
    """Service for generating epidemiological reports"""
    
    def __init__(self, db_connection_string: str, reports_dir: str = "/tmp/relatorios"):
        self.conn_str = db_connection_string
        self.reports_dir = reports_dir
        os.makedirs(reports_dir, exist_ok=True)
    
    def generate_epi01(
        self,
        competencia_inicio: str,
        competencia_fim: str,
        municipios_filter: Optional[List[str]] = None,
        formato: FormatoRelatorio = FormatoRelatorio.PDF,
        incluir_grafico: bool = True
    ) -> RelatorioEPI01Response:
        """
        Generate EPI01 report in specified format.
        
        Args:
            competencia_inicio: Start period YYYYMM
            competencia_fim: End period YYYYMM
            municipios_filter: Filter by specific IBGE codes
            formato: Output format (pdf, csv, json)
            incluir_grafico: Include charts in PDF
            
        Returns:
            RelatorioEPI01Response with file info and metadata
        """
        # Fetch data from database
        municipios_data = self._fetch_municipality_indicators(
            competencia_inicio,
            competencia_fim,
            municipios_filter
        )
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"epi01_{competencia_inicio}_{competencia_fim}_{timestamp}"
        
        if formato == FormatoRelatorio.PDF:
            return self._generate_pdf(
                filename_base,
                competencia_inicio,
                competencia_fim,
                municipios_data
            )
        elif formato == FormatoRelatorio.CSV:
            return self._generate_csv(
                filename_base,
                competencia_inicio,
                competencia_fim,
                municipios_data
            )
        else:
            raise ValueError(f"Formato não suportado: {formato}")
    
    def _fetch_municipality_indicators(
        self,
        competencia_inicio: str,
        competencia_fim: str,
        municipios_filter: Optional[List[str]] = None
    ) -> List[IndicadorMunicipio]:
        """Fetch aggregated indicators by municipality from database"""
        dt_inicio = self._competencia_to_date(competencia_inicio)
        dt_fim = self._competencia_to_date(competencia_fim)
        
        conn = psycopg2.connect(self.conn_str)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                municipio_filter = ""
                params = [dt_inicio, dt_fim]
                
                if municipios_filter:
                    municipio_filter = "AND municipio_cod_ibge = ANY(%s)"
                    params.append(municipios_filter)
                
                query = f"""
                    SELECT 
                        municipio_cod_ibge,
                        COUNT(*) as casos_total,
                        COUNT(*) FILTER (WHERE classificacao_final LIKE 'DENGUE%%') as casos_confirmados,
                        COUNT(*) FILTER (WHERE classificacao_final = 'DENGUE_GRAVE') as casos_graves,
                        COUNT(*) FILTER (WHERE classificacao_final = 'DENGUE_SINAIS_ALARME') as casos_sinais_alarme,
                        COUNT(*) FILTER (WHERE evolucao = 'OBITO') as obitos
                    FROM indicador_epi
                    WHERE competencia >= %s AND competencia <= %s
                      {municipio_filter}
                    GROUP BY municipio_cod_ibge
                    ORDER BY casos_total DESC
                """
                
                cur.execute(query, params)
                rows = cur.fetchall()
        finally:
            conn.close()
        
        # Build IndicadorMunicipio objects
        municipios = []
        for row in rows:
            cod_ibge = row['municipio_cod_ibge']
            mun_info = MT_MUNICIPIOS.get(cod_ibge)
            
            if not mun_info:
                continue
            
            pop = mun_info['pop']
            casos = row['casos_total']
            obitos = row['obitos']
            
            incidencia = (casos / pop * 100000) if pop > 0 else 0.0
            letalidade = (obitos / casos * 100) if casos > 0 else 0.0
            
            municipios.append(IndicadorMunicipio(
                municipio_cod_ibge=cod_ibge,
                municipio_nome=mun_info['nome'],
                populacao=pop,
                casos_total=casos,
                casos_confirmados=row['casos_confirmados'],
                casos_graves=row['casos_graves'],
                casos_sinais_alarme=row['casos_sinais_alarme'],
                obitos=obitos,
                incidencia=round(incidencia, 2),
                letalidade=round(letalidade, 2)
            ))
        
        return municipios
    
    def _generate_pdf(
        self,
        filename_base: str,
        competencia_inicio: str,
        competencia_fim: str,
        municipios: List[IndicadorMunicipio]
    ) -> RelatorioEPI01Response:
        """Generate PDF report"""
        filename = f"{filename_base}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        generator = EPI01PDFGenerator()
        sha256_hash, file_size = generator.generate_epi01(
            competencia_inicio,
            competencia_fim,
            municipios,
            filepath
        )
        
        # Calculate summary statistics
        total_casos = sum(m.casos_total for m in municipios)
        total_obitos = sum(m.obitos for m in municipios)
        incidencia_media = sum(m.incidencia for m in municipios) / len(municipios) if municipios else 0.0
        
        metadata = RelatorioEPI01Metadata(
            competencia_inicio=competencia_inicio,
            competencia_fim=competencia_fim,
            dt_geracao=datetime.now().isoformat() + "Z",
            total_municipios=len(municipios),
            total_casos=total_casos,
            total_obitos=total_obitos,
            incidencia_media=round(incidencia_media, 2),
            hash_sha256=sha256_hash,
            formato=FormatoRelatorio.PDF
        )
        
        return RelatorioEPI01Response(
            metadata=metadata,
            arquivo=filename,
            tamanho_bytes=file_size,
            url_download=f"/api/relatorios/download/{filename}"
        )
    
    def _generate_csv(
        self,
        filename_base: str,
        competencia_inicio: str,
        competencia_fim: str,
        municipios: List[IndicadorMunicipio]
    ) -> RelatorioEPI01Response:
        """Generate CSV export"""
        filename = f"{filename_base}.csv"
        filepath = os.path.join(self.reports_dir, filename)
        
        csv_content = generate_csv_export(municipios)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        # Calculate hash
        import hashlib
        sha256_hash = hashlib.sha256(csv_content.encode('utf-8')).hexdigest()
        file_size = len(csv_content.encode('utf-8'))
        
        # Calculate summary
        total_casos = sum(m.casos_total for m in municipios)
        total_obitos = sum(m.obitos for m in municipios)
        incidencia_media = sum(m.incidencia for m in municipios) / len(municipios) if municipios else 0.0
        
        metadata = RelatorioEPI01Metadata(
            competencia_inicio=competencia_inicio,
            competencia_fim=competencia_fim,
            dt_geracao=datetime.now().isoformat() + "Z",
            total_municipios=len(municipios),
            total_casos=total_casos,
            total_obitos=total_obitos,
            incidencia_media=round(incidencia_media, 2),
            hash_sha256=sha256_hash,
            formato=FormatoRelatorio.CSV
        )
        
        return RelatorioEPI01Response(
            metadata=metadata,
            arquivo=filename,
            tamanho_bytes=file_size,
            url_download=f"/api/relatorios/download/{filename}"
        )
    
    def _competencia_to_date(self, competencia: str) -> date:
        """Convert YYYYMM to first day of month"""
        year = int(competencia[:4])
        month = int(competencia[4:6])
        return date(year, month, 1)
