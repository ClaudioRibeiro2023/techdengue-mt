"""
PDF Generator Service - Generate PDF/A-1 compliant reports with SHA-256 hash
"""
import hashlib
import io
from datetime import datetime, date
from typing import List, Tuple
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from app.schemas.relatorio import IndicadorMunicipio


class EPI01PDFGenerator:
    """Generate EPI01 (Epidemiological Report) in PDF/A-1 format"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#424242'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
    
    def generate_epi01(
        self,
        competencia_inicio: str,
        competencia_fim: str,
        municipios: List[IndicadorMunicipio],
        output_path: str
    ) -> Tuple[str, int]:
        """
        Generate EPI01 PDF report.
        
        Args:
            competencia_inicio: Start period YYYYMM
            competencia_fim: End period YYYYMM
            municipios: List of municipality indicators
            output_path: Path to save PDF file
            
        Returns:
            Tuple of (SHA-256 hash, file size in bytes)
        """
        # Create PDF in memory first to calculate hash
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title="Relatório EPI01 - Dengue",
            author="TechDengue - Vigilância em Saúde MT"
        )
        
        # Build content
        story = []
        
        # Header
        story.append(Paragraph("RELATÓRIO EPI01", self.styles['CustomTitle']))
        story.append(Paragraph("Boletim Epidemiológico - Dengue", self.styles['Heading2']))
        story.append(Spacer(1, 0.5*cm))
        
        # Period info
        periodo_texto = f"<b>Período:</b> {self._format_competencia(competencia_inicio)} a {self._format_competencia(competencia_fim)}"
        story.append(Paragraph(periodo_texto, self.styles['Normal']))
        
        geracao_texto = f"<b>Data de Geração:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        story.append(Paragraph(geracao_texto, self.styles['Normal']))
        story.append(Spacer(1, 1*cm))
        
        # Summary statistics
        total_casos = sum(m.casos_total for m in municipios)
        total_obitos = sum(m.obitos for m in municipios)
        incidencia_media = sum(m.incidencia for m in municipios) / len(municipios) if municipios else 0
        letalidade_geral = (total_obitos / total_casos * 100) if total_casos > 0 else 0
        
        story.append(Paragraph("RESUMO GERAL", self.styles['CustomHeading']))
        
        summary_data = [
            ['Indicador', 'Valor'],
            ['Municípios Analisados', str(len(municipios))],
            ['Total de Casos', f"{total_casos:,}".replace(',', '.')],
            ['Total de Óbitos', str(total_obitos)],
            ['Incidência Média (por 100k hab)', f"{incidencia_media:.2f}"],
            ['Letalidade Geral (%)', f"{letalidade_geral:.2f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[10*cm, 5*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 1*cm))
        
        # Municipality details
        story.append(Paragraph("DETALHAMENTO POR MUNICÍPIO", self.styles['CustomHeading']))
        
        # Sort by incidence (descending)
        municipios_sorted = sorted(municipios, key=lambda m: m.incidencia, reverse=True)
        
        table_data = [
            ['Município', 'População', 'Casos', 'Óbitos', 'Incidência\n(/100k)', 'Letalidade\n(%)']
        ]
        
        for mun in municipios_sorted:
            table_data.append([
                mun.municipio_nome,
                f"{mun.populacao:,}".replace(',', '.'),
                str(mun.casos_total),
                str(mun.obitos),
                f"{mun.incidencia:.1f}",
                f"{mun.letalidade:.2f}%"
            ])
        
        detail_table = Table(table_data, colWidths=[4*cm, 2.5*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Municipality names left-aligned
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(detail_table)
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Calculate SHA-256 hash
        sha256_hash = hashlib.sha256(pdf_content).hexdigest()
        
        # Save to file
        with open(output_path, 'wb') as f:
            f.write(pdf_content)
        
        file_size = len(pdf_content)
        
        return sha256_hash, file_size
    
    def _format_competencia(self, competencia: str) -> str:
        """Format YYYYMM to 'Mês/Ano'"""
        year = competencia[:4]
        month = competencia[4:6]
        
        meses = {
            '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março',
            '04': 'Abril', '05': 'Maio', '06': 'Junho',
            '07': 'Julho', '08': 'Agosto', '09': 'Setembro',
            '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
        }
        
        return f"{meses.get(month, month)}/{year}"
    
    def _add_footer(self, canvas, doc):
        """Add footer with page number and hash placeholder"""
        canvas.saveState()
        
        footer_text = f"Página {doc.page} | TechDengue - Vigilância em Saúde MT"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(
            A4[0] / 2,
            1.5*cm,
            footer_text
        )
        
        canvas.restoreState()


def generate_csv_export(municipios: List[IndicadorMunicipio]) -> str:
    """Generate CSV export of municipality indicators"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    
    # Header
    writer.writerow([
        'municipio_cod_ibge',
        'municipio_nome',
        'populacao',
        'casos_total',
        'casos_confirmados',
        'casos_graves',
        'casos_sinais_alarme',
        'obitos',
        'incidencia_100k',
        'letalidade_pct'
    ])
    
    # Data
    for mun in municipios:
        writer.writerow([
            mun.municipio_cod_ibge,
            mun.municipio_nome,
            mun.populacao,
            mun.casos_total,
            mun.casos_confirmados,
            mun.casos_graves,
            mun.casos_sinais_alarme,
            mun.obitos,
            f"{mun.incidencia:.2f}",
            f"{mun.letalidade:.2f}"
        ])
    
    return output.getvalue()
