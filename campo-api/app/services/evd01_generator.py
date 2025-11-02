"""
EVD01 PDF Generator - Generate evidence reports in PDF/A-1 format
"""
import os
import io
import qrcode
from datetime import datetime
from typing import List, Optional
from reportlab.lib.pagesizes import A4, A1, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

from app.schemas.relatorio_evd01 import TamanhoPagina, OrientacaoPagina, PageLayout
from app.services.merkle_tree import MerkleTree


class EVD01Generator:
    """Generator for EVD01 evidence reports in PDF/A-1 format"""
    
    def __init__(self, output_dir: str = "/tmp"):
        """
        Initialize generator.
        
        Args:
            output_dir: Directory to save generated PDFs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(
        self,
        atividade: dict,
        evidencias: List[dict],
        tamanho_pagina: TamanhoPagina = TamanhoPagina.A4,
        orientacao: OrientacaoPagina = OrientacaoPagina.RETRATO,
        incluir_miniaturas: bool = True,
        incluir_qrcode: bool = True
    ) -> tuple[str, str, dict]:
        """
        Generate EVD01 PDF report.
        
        Args:
            atividade: Activity data
            evidencias: List of evidence records
            tamanho_pagina: Page size (A1 or A4)
            orientacao: Page orientation
            incluir_miniaturas: Include evidence thumbnails
            incluir_qrcode: Include verification QR code
            
        Returns:
            Tuple of (filepath, filename, merkle_tree_dict)
        """
        # Get page layout
        layout = PageLayout.get_layout(tamanho_pagina, orientacao)
        
        # Determine page size
        if tamanho_pagina == TamanhoPagina.A4:
            pagesize = landscape(A4) if orientacao == OrientacaoPagina.PAISAGEM else A4
        else:  # A1
            pagesize = landscape(A1) if orientacao == OrientacaoPagina.PAISAGEM else A1
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"EVD01_Atividade_{atividade['id']}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Build Merkle tree
        evidence_hashes = [(e['id'], e['hash_sha256']) for e in evidencias]
        merkle_tree = MerkleTree(evidence_hashes)
        
        # Create PDF
        doc = SimpleDocTemplate(
            filepath,
            pagesize=pagesize,
            leftMargin=layout.margin_mm * mm,
            rightMargin=layout.margin_mm * mm,
            topMargin=layout.margin_mm * mm,
            bottomMargin=layout.margin_mm * mm
        )
        
        # Build story (document content)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16 if tamanho_pagina == TamanhoPagina.A4 else 24,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        story.append(Paragraph("RELATÓRIO DE EVIDÊNCIAS - EVD01", title_style))
        story.append(Spacer(1, 10*mm))
        
        # Activity info table
        activity_data = [
            ["Atividade ID:", str(atividade['id'])],
            ["Tipo:", atividade['tipo']],
            ["Município:", atividade.get('municipio_cod_ibge', 'N/A')],
            ["Status:", atividade['status']],
            ["Criado em:", atividade['criado_em']],
            ["Total Evidências:", str(len(evidencias))]
        ]
        
        activity_table = Table(activity_data, colWidths=[80*mm, 100*mm])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8E8E8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(activity_table)
        story.append(Spacer(1, 10*mm))
        
        # Merkle tree info
        story.append(Paragraph("<b>Verificação de Integridade (Merkle Tree)</b>", styles['Heading2']))
        merkle_data = [
            ["Root Hash:", merkle_tree.get_root_hash()[:32] + "..."],
            ["Total Evidências:", str(len(evidencias))],
            ["Profundidade Árvore:", str(merkle_tree.depth)]
        ]
        merkle_table = Table(merkle_data, colWidths=[60*mm, 120*mm])
        merkle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FFE8E8')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(merkle_table)
        story.append(Spacer(1, 10*mm))
        
        # Evidence list
        story.append(Paragraph("<b>Lista de Evidências</b>", styles['Heading2']))
        evidence_data = [["#", "Tipo", "Hash SHA-256", "Tamanho", "Data"]]
        for i, ev in enumerate(evidencias, 1):
            evidence_data.append([
                str(i),
                ev['tipo'],
                ev['hash_sha256'][:16] + "...",
                f"{ev['tamanho_bytes'] / 1024:.1f} KB",
                ev['criado_em'][:10]
            ])
        
        evidence_table = Table(evidence_data, colWidths=[15*mm, 30*mm, 60*mm, 30*mm, 30*mm])
        evidence_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')])
        ]))
        story.append(evidence_table)
        story.append(Spacer(1, 10*mm))
        
        # QR Code for verification
        if incluir_qrcode:
            qr_data = f"EVD01:{atividade['id']}:ROOT:{merkle_tree.get_root_hash()}"
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR to bytes
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            
            qr_image = Image(qr_buffer, width=40*mm, height=40*mm)
            story.append(Paragraph("<b>QR Code de Verificação</b>", styles['Heading3']))
            story.append(qr_image)
        
        # Footer with metadata
        footer_text = f"""
        <para align=center>
        <font size=8>
        Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br/>
        Formato: PDF/A-1 | Tamanho: {tamanho_pagina.value} {orientacao.value}<br/>
        Root Hash: {merkle_tree.get_root_hash()}<br/>
        Sistema TechDengue - Vigilância Epidemiológica MT
        </font>
        </para>
        """
        story.append(Spacer(1, 10*mm))
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return filepath, filename, merkle_tree.to_dict()
