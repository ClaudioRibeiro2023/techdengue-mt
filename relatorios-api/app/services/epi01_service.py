"""
EPI01 Service - Generate epidemiological reports (PDF/CSV)
"""
import os
import hashlib
import csv
import io
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import matplotlib
matplotlib.use('Agg')  # Backend non-GUI
import matplotlib.pyplot as plt

from app.schemas.epi01 import (
    EPI01Request,
    ConteudoRelatorioEPI01,
    DadosResumo,
    DadosMunicipio,
    DadosSemana,
    FormatoRelatorio,
    ValidacaoRelatorio
)


# MT municipalities reference
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


class EPI01Service:
    """Service para geração de relatórios EPI01"""
    
    def __init__(self, db_connection_string: str, storage_path: str = "/tmp/relatorios"):
        self.conn_str = db_connection_string
        self.storage_path = storage_path
        
        # Criar diretório de storage se não existir
        os.makedirs(storage_path, exist_ok=True)
    
    def gerar_relatorio(
        self,
        relatorio_id: str,
        request: EPI01Request
    ) -> Tuple[List[str], List[int], List[str]]:
        """
        Gera relatório EPI01 nos formatos solicitados
        
        Args:
            relatorio_id: ID único do relatório
            request: Parâmetros da solicitação
            
        Returns:
            Tuple com (arquivos_gerados, tamanhos, hashes)
        """
        # 1. Coletar dados
        conteudo = self._coletar_dados(request)
        
        # 2. Gerar arquivos
        arquivos_gerados = []
        tamanhos = []
        hashes = []
        
        if request.formato in [FormatoRelatorio.PDF, FormatoRelatorio.BOTH]:
            pdf_path, pdf_size, pdf_hash = self._gerar_pdf(
                relatorio_id,
                conteudo,
                request
            )
            arquivos_gerados.append(pdf_path)
            tamanhos.append(pdf_size)
            hashes.append(pdf_hash)
        
        if request.formato in [FormatoRelatorio.CSV, FormatoRelatorio.BOTH]:
            csv_path, csv_size, csv_hash = self._gerar_csv(
                relatorio_id,
                conteudo,
                request
            )
            arquivos_gerados.append(csv_path)
            tamanhos.append(csv_size)
            hashes.append(csv_hash)
        
        return arquivos_gerados, tamanhos, hashes
    
    def _coletar_dados(self, request: EPI01Request) -> ConteudoRelatorioEPI01:
        """Coleta dados do banco para o relatório"""
        conn = psycopg2.connect(self.conn_str)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Filtros WHERE
                where_clauses = ["ano = %s"]
                params = [request.ano]
                
                if request.semana_epi_inicio and request.semana_epi_fim:
                    where_clauses.append("semana_epi BETWEEN %s AND %s")
                    params.extend([request.semana_epi_inicio, request.semana_epi_fim])
                
                if request.codigo_ibge:
                    where_clauses.append("municipio_codigo = %s")
                    params.append(request.codigo_ibge)
                
                if request.doenca_tipo.value != "TODAS":
                    where_clauses.append("doenca_tipo = %s")
                    params.append(request.doenca_tipo.value)
                
                where_sql = " AND ".join(where_clauses)
                
                # Query de resumo
                query_resumo = f"""
                    SELECT 
                        SUM(casos_confirmados) as total_casos,
                        SUM(obitos) as total_obitos,
                        SUM(casos_graves) as casos_graves,
                        COUNT(DISTINCT municipio_codigo) as municipios_afetados
                    FROM indicador_epi
                    WHERE {where_sql}
                """
                
                cur.execute(query_resumo, params)
                row_resumo = cur.fetchone()
                
                total_casos = row_resumo['total_casos'] or 0
                total_obitos = row_resumo['total_obitos'] or 0
                casos_graves = row_resumo['casos_graves'] or 0
                municipios_afetados = row_resumo['municipios_afetados'] or 0
                
                taxa_letalidade = (total_obitos / total_casos * 100) if total_casos > 0 else 0.0
                
                # Calcular incidência média (aproximada)
                pop_total = sum(m['pop'] for m in MT_MUNICIPIOS.values())
                incidencia_media = (total_casos / pop_total * 100000) if pop_total > 0 else 0.0
                
                resumo = DadosResumo(
                    total_casos=total_casos,
                    total_obitos=total_obitos,
                    taxa_letalidade=round(taxa_letalidade, 2),
                    incidencia_media=round(incidencia_media, 2),
                    municipios_afetados=municipios_afetados,
                    casos_graves=casos_graves
                )
                
                # Query de municípios
                query_municipios = f"""
                    SELECT 
                        municipio_codigo,
                        SUM(casos_confirmados) as casos,
                        SUM(obitos) as obitos
                    FROM indicador_epi
                    WHERE {where_sql}
                    GROUP BY municipio_codigo
                    ORDER BY casos DESC
                    LIMIT 20
                """
                
                cur.execute(query_municipios, params)
                rows_municipios = cur.fetchall()
                
                municipios = []
                for row in rows_municipios:
                    cod_ibge = row['municipio_codigo']
                    casos = row['casos'] or 0
                    obitos = row['obitos'] or 0
                    
                    mun_info = MT_MUNICIPIOS.get(cod_ibge)
                    if not mun_info:
                        continue
                    
                    pop = mun_info['pop']
                    incidencia = (casos / pop * 100000) if pop > 0 else 0
                    letalidade = (obitos / casos * 100) if casos > 0 else 0
                    
                    nivel_risco = self._classificar_risco(incidencia)
                    
                    municipios.append(DadosMunicipio(
                        codigo_ibge=cod_ibge,
                        nome=mun_info['nome'],
                        populacao=pop,
                        casos=casos,
                        obitos=obitos,
                        incidencia=round(incidencia, 2),
                        taxa_letalidade=round(letalidade, 2),
                        nivel_risco=nivel_risco
                    ))
                
                # Query de série temporal
                query_serie = f"""
                    SELECT 
                        semana_epi,
                        SUM(casos_confirmados) as casos,
                        SUM(obitos) as obitos,
                        SUM(casos_graves) as casos_graves
                    FROM indicador_epi
                    WHERE {where_sql}
                    GROUP BY semana_epi
                    ORDER BY semana_epi
                """
                
                cur.execute(query_serie, params)
                rows_serie = cur.fetchall()
                
                serie_temporal = []
                for row in rows_serie:
                    semana = row['semana_epi']
                    serie_temporal.append(DadosSemana(
                        ano=request.ano,
                        semana_epi=semana,
                        data_inicio=f"{request.ano}-W{semana:02d}-1",
                        data_fim=f"{request.ano}-W{semana:02d}-7",
                        casos=row['casos'] or 0,
                        obitos=row['obitos'] or 0,
                        casos_graves=row['casos_graves'] or 0
                    ))
                
                # Construir título
                titulo = request.titulo_customizado or f"Relatório Epidemiológico EPI01 - {request.doenca_tipo.value} {request.ano}"
                
                periodo_str = f"{request.ano}"
                if request.semana_epi_inicio and request.semana_epi_fim:
                    periodo_str += f" (Semanas {request.semana_epi_inicio}-{request.semana_epi_fim})"
                
                conteudo = ConteudoRelatorioEPI01(
                    titulo=titulo,
                    periodo=periodo_str,
                    data_geracao=datetime.now(),
                    doenca_tipo=request.doenca_tipo.value,
                    resumo=resumo,
                    municipios=municipios,
                    serie_temporal=serie_temporal,
                    observacoes=request.observacoes
                )
                
                return conteudo
        finally:
            conn.close()
    
    def _classificar_risco(self, incidencia: float) -> str:
        """Classifica risco baseado na incidência"""
        if incidencia < 100:
            return "BAIXO"
        elif incidencia < 300:
            return "MEDIO"
        elif incidencia < 500:
            return "ALTO"
        else:
            return "MUITO_ALTO"
    
    def _gerar_pdf(
        self,
        relatorio_id: str,
        conteudo: ConteudoRelatorioEPI01,
        request: EPI01Request
    ) -> Tuple[str, int, str]:
        """Gera relatório em PDF/A-1"""
        filename = f"{relatorio_id}.pdf"
        filepath = os.path.join(self.storage_path, filename)
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Estilo customizado para título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # 1. Cabeçalho
        story.append(Paragraph(conteudo.titulo, title_style))
        story.append(Paragraph(f"Período: {conteudo.periodo}", styles['Normal']))
        story.append(Paragraph(f"Data de Geração: {conteudo.data_geracao.strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # 2. Resumo Executivo
        story.append(Paragraph("Resumo Executivo", styles['Heading2']))
        
        resumo_data = [
            ['Indicador', 'Valor'],
            ['Total de Casos', f"{conteudo.resumo.total_casos:,}"],
            ['Total de Óbitos', f"{conteudo.resumo.total_obitos:,}"],
            ['Taxa de Letalidade', f"{conteudo.resumo.taxa_letalidade:.2f}%"],
            ['Incidência Média', f"{conteudo.resumo.incidencia_media:.2f}/100k"],
            ['Municípios Afetados', f"{conteudo.resumo.municipios_afetados}"],
            ['Casos Graves', f"{conteudo.resumo.casos_graves:,}"],
        ]
        
        resumo_table = Table(resumo_data, colWidths=[8*cm, 6*cm])
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(resumo_table)
        story.append(Spacer(1, 1*cm))
        
        # 3. Top Municípios
        if conteudo.municipios:
            story.append(Paragraph("Municípios Mais Afetados (Top 20)", styles['Heading2']))
            
            mun_data = [['Município', 'Casos', 'Óbitos', 'Incidência', 'Letalidade', 'Risco']]
            
            for mun in conteudo.municipios[:20]:
                mun_data.append([
                    mun.nome,
                    f"{mun.casos:,}",
                    str(mun.obitos),
                    f"{mun.incidencia:.1f}",
                    f"{mun.taxa_letalidade:.2f}%",
                    mun.nivel_risco
                ])
            
            mun_table = Table(mun_data, colWidths=[4.5*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm, 2.5*cm])
            mun_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
            ]))
            
            story.append(mun_table)
            story.append(Spacer(1, 1*cm))
        
        # 4. Gráfico de Série Temporal (se solicitado)
        if request.incluir_graficos and conteudo.serie_temporal:
            story.append(PageBreak())
            story.append(Paragraph("Evolução Temporal", styles['Heading2']))
            
            # Gerar gráfico com matplotlib
            chart_path = self._gerar_grafico_serie(relatorio_id, conteudo.serie_temporal)
            if chart_path and os.path.exists(chart_path):
                img = Image(chart_path, width=14*cm, height=8*cm)
                story.append(img)
                story.append(Spacer(1, 0.5*cm))
        
        # 5. Observações
        if conteudo.observacoes:
            story.append(Paragraph("Observações", styles['Heading2']))
            story.append(Paragraph(conteudo.observacoes, styles['Normal']))
        
        # 6. Rodapé com hash
        story.append(Spacer(1, 2*cm))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_RIGHT
        )
        story.append(Paragraph(f"Relatório ID: {relatorio_id}", footer_style))
        
        # Construir PDF
        doc.build(story)
        
        # Calcular hash e tamanho
        file_size = os.path.getsize(filepath)
        file_hash = self._calcular_hash(filepath)
        
        return filepath, file_size, file_hash
    
    def _gerar_grafico_serie(self, relatorio_id: str, serie: List[DadosSemana]) -> Optional[str]:
        """Gera gráfico de série temporal"""
        try:
            semanas = [f"W{s.semana_epi:02d}" for s in serie]
            casos = [s.casos for s in serie]
            obitos = [s.obitos for s in serie]
            
            fig, ax1 = plt.subplots(figsize=(12, 6))
            
            color = 'tab:red'
            ax1.set_xlabel('Semana Epidemiológica')
            ax1.set_ylabel('Casos', color=color)
            ax1.plot(semanas, casos, color=color, marker='o', label='Casos')
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.grid(True, alpha=0.3)
            
            ax2 = ax1.twinx()
            color = 'tab:blue'
            ax2.set_ylabel('Óbitos', color=color)
            ax2.plot(semanas, obitos, color=color, marker='s', label='Óbitos')
            ax2.tick_params(axis='y', labelcolor=color)
            
            # Rotacionar labels do eixo X
            plt.xticks(rotation=45, ha='right')
            
            fig.tight_layout()
            
            chart_path = os.path.join(self.storage_path, f"{relatorio_id}_chart.png")
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return chart_path
        except Exception as e:
            print(f"Erro ao gerar gráfico: {e}")
            return None
    
    def _gerar_csv(
        self,
        relatorio_id: str,
        conteudo: ConteudoRelatorioEPI01,
        request: EPI01Request
    ) -> Tuple[str, int, str]:
        """Gera relatório em CSV"""
        filename = f"{relatorio_id}.csv"
        filepath = os.path.join(self.storage_path, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Cabeçalho
            writer.writerow([f"# {conteudo.titulo}"])
            writer.writerow([f"# Período: {conteudo.periodo}"])
            writer.writerow([f"# Gerado em: {conteudo.data_geracao.strftime('%d/%m/%Y %H:%M')}"])
            writer.writerow([])
            
            # Resumo
            writer.writerow(["## RESUMO EXECUTIVO"])
            writer.writerow(["Indicador", "Valor"])
            writer.writerow(["Total de Casos", conteudo.resumo.total_casos])
            writer.writerow(["Total de Óbitos", conteudo.resumo.total_obitos])
            writer.writerow(["Taxa de Letalidade (%)", f"{conteudo.resumo.taxa_letalidade:.2f}"])
            writer.writerow(["Incidência Média (/100k)", f"{conteudo.resumo.incidencia_media:.2f}"])
            writer.writerow(["Municípios Afetados", conteudo.resumo.municipios_afetados])
            writer.writerow(["Casos Graves", conteudo.resumo.casos_graves])
            writer.writerow([])
            
            # Municípios
            writer.writerow(["## MUNICÍPIOS"])
            writer.writerow(["Código IBGE", "Município", "População", "Casos", "Óbitos", "Incidência", "Letalidade (%)", "Nível de Risco"])
            
            for mun in conteudo.municipios:
                writer.writerow([
                    mun.codigo_ibge,
                    mun.nome,
                    mun.populacao,
                    mun.casos,
                    mun.obitos,
                    f"{mun.incidencia:.2f}",
                    f"{mun.taxa_letalidade:.2f}",
                    mun.nivel_risco
                ])
            
            writer.writerow([])
            
            # Série Temporal
            writer.writerow(["## SÉRIE TEMPORAL"])
            writer.writerow(["Ano", "Semana Epi", "Data Início", "Data Fim", "Casos", "Óbitos", "Casos Graves"])
            
            for semana in conteudo.serie_temporal:
                writer.writerow([
                    semana.ano,
                    semana.semana_epi,
                    semana.data_inicio,
                    semana.data_fim,
                    semana.casos,
                    semana.obitos,
                    semana.casos_graves
                ])
        
        # Calcular hash e tamanho
        file_size = os.path.getsize(filepath)
        file_hash = self._calcular_hash(filepath)
        
        return filepath, file_size, file_hash
    
    def _calcular_hash(self, filepath: str) -> str:
        """Calcula hash SHA-256 de um arquivo"""
        sha256_hash = hashlib.sha256()
        
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def validar_relatorio(self, filepath: str, hash_esperado: Optional[str] = None) -> ValidacaoRelatorio:
        """Valida integridade e conformidade de relatório"""
        erros = []
        avisos = []
        
        # Verificar se arquivo existe
        if not os.path.exists(filepath):
            erros.append("Arquivo não encontrado")
            return ValidacaoRelatorio(
                valido=False,
                erros=erros,
                avisos=avisos
            )
        
        # Verificar tamanho
        tamanho = os.path.getsize(filepath)
        if tamanho == 0:
            erros.append("Arquivo vazio")
        elif tamanho > 50 * 1024 * 1024:  # 50 MB
            avisos.append("Arquivo muito grande (> 50 MB)")
        
        # Verificar hash
        hash_atual = self._calcular_hash(filepath)
        hash_verificado = None
        
        if hash_esperado:
            hash_verificado = (hash_atual == hash_esperado)
            if not hash_verificado:
                erros.append("Hash não corresponde ao esperado")
        
        # Verificar formato (PDF/A-1 básico)
        formato_conforme = None
        if filepath.endswith('.pdf'):
            try:
                with open(filepath, 'rb') as f:
                    header = f.read(8)
                    if header.startswith(b'%PDF-'):
                        formato_conforme = True
                    else:
                        erros.append("Formato PDF inválido")
                        formato_conforme = False
            except Exception as e:
                erros.append(f"Erro ao validar PDF: {str(e)}")
                formato_conforme = False
        
        valido = len(erros) == 0
        
        return ValidacaoRelatorio(
            valido=valido,
            erros=erros,
            avisos=avisos,
            hash_verificado=hash_verificado,
            tamanho_bytes=tamanho,
            formato_conforme=formato_conforme
        )
