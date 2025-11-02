"""
Relatório EVD01 - Schemas for evidence report generation
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict


class FormatoRelatorio(str, Enum):
    """Report output formats"""
    PDF = "pdf"
    JSON = "json"


class TamanhoPagina(str, Enum):
    """PDF page sizes"""
    A1 = "A1"  # 594 x 841 mm (23.4 x 33.1 inches) - Landscape: 841 x 594 mm
    A4 = "A4"  # 210 x 297 mm (8.3 x 11.7 inches)


class OrientacaoPagina(str, Enum):
    """Page orientation"""
    RETRATO = "portrait"  # Vertical
    PAISAGEM = "landscape"  # Horizontal


class EVD01Request(BaseModel):
    """Request for EVD01 report generation"""
    atividade_id: int = Field(..., gt=0, description="ID da atividade")
    incluir_miniaturas: bool = Field(default=True, description="Include evidence thumbnails")
    formato: FormatoRelatorio = Field(default=FormatoRelatorio.PDF)
    tamanho_pagina: TamanhoPagina = Field(default=TamanhoPagina.A4, description="PDF page size")
    orientacao: OrientacaoPagina = Field(default=OrientacaoPagina.RETRATO, description="Page orientation")
    incluir_qrcode: bool = Field(default=True, description="Include verification QR code")
    
    model_config = SettingsConfigDict(json_schema_extra={
        "example": {
            "atividade_id": 123,
            "incluir_miniaturas": True,
            "formato": "pdf",
            "tamanho_pagina": "A4",
            "orientacao": "portrait",
            "incluir_qrcode": True
        }
    })


class EvidenciaHash(BaseModel):
    """Hash information for single evidence"""
    evidencia_id: int
    filename: str
    hash_sha256: str
    tamanho_bytes: int
    tipo: str


class MerkleTreeNode(BaseModel):
    """Node in Merkle tree"""
    hash: str = Field(..., min_length=64, max_length=64, description="SHA-256 hash")
    left: Optional['MerkleTreeNode'] = None
    right: Optional['MerkleTreeNode'] = None
    is_leaf: bool = Field(default=False)
    evidencia_id: Optional[int] = None


class MerkleTree(BaseModel):
    """Complete Merkle tree for evidence verification"""
    root_hash: str = Field(..., min_length=64, max_length=64, description="Root hash of tree")
    leaf_count: int = Field(..., ge=0, description="Number of leaf nodes (evidences)")
    tree_depth: int = Field(..., ge=0, description="Depth of tree")
    leaves: List[EvidenciaHash] = Field(..., description="Leaf nodes (evidence hashes)")
    
    def verify_evidence(self, evidencia_id: int, hash_sha256: str) -> bool:
        """Verify if an evidence is part of this tree"""
        return any(
            leaf.evidencia_id == evidencia_id and leaf.hash_sha256 == hash_sha256
            for leaf in self.leaves
        )


class EVD01Metadata(BaseModel):
    """Metadata for EVD01 report"""
    atividade_id: int
    atividade_tipo: str
    municipio_cod_ibge: str
    municipio_nome: str
    dt_geracao: datetime
    total_evidencias: int
    merkle_root_hash: str = Field(..., min_length=64, max_length=64)
    formato: FormatoRelatorio
    tamanho_pagina: TamanhoPagina
    orientacao: OrientacaoPagina
    versao_relatorio: str = Field(default="1.0.0")


class EVD01Response(BaseModel):
    """Response for EVD01 report generation"""
    metadata: EVD01Metadata
    arquivo: str = Field(..., description="Generated filename")
    tamanho_bytes: int
    url_download: Optional[str] = Field(None, description="Temporary download URL")
    qrcode_url: Optional[str] = Field(None, description="QR code verification URL")
    merkle_tree: MerkleTree


class EVD01Stats(BaseModel):
    """Statistics for EVD01 reports"""
    total_relatorios: int
    por_tamanho: Dict[str, int]
    por_formato: Dict[str, int]
    tamanho_medio_bytes: float
    ultimo_gerado: Optional[datetime] = None


class PageLayout(BaseModel):
    """Layout configuration for different page sizes"""
    page_size: TamanhoPagina
    orientation: OrientacaoPagina
    width_mm: float
    height_mm: float
    margin_mm: float = 20.0
    thumbnail_grid_cols: int
    thumbnail_grid_rows: int
    thumbnail_size_mm: float
    
    @property
    def max_thumbnails_per_page(self) -> int:
        """Maximum thumbnails that fit in one page"""
        return self.thumbnail_grid_cols * self.thumbnail_grid_rows
    
    @staticmethod
    def get_layout(page_size: TamanhoPagina, orientation: OrientacaoPagina) -> 'PageLayout':
        """Get predefined layout for page size and orientation"""
        layouts = {
            (TamanhoPagina.A4, OrientacaoPagina.RETRATO): PageLayout(
                page_size=TamanhoPagina.A4,
                orientation=OrientacaoPagina.RETRATO,
                width_mm=210,
                height_mm=297,
                thumbnail_grid_cols=4,
                thumbnail_grid_rows=4,
                thumbnail_size_mm=40
            ),
            (TamanhoPagina.A4, OrientacaoPagina.PAISAGEM): PageLayout(
                page_size=TamanhoPagina.A4,
                orientation=OrientacaoPagina.PAISAGEM,
                width_mm=297,
                height_mm=210,
                thumbnail_grid_cols=5,
                thumbnail_grid_rows=3,
                thumbnail_size_mm=45
            ),
            (TamanhoPagina.A1, OrientacaoPagina.RETRATO): PageLayout(
                page_size=TamanhoPagina.A1,
                orientation=OrientacaoPagina.RETRATO,
                width_mm=594,
                height_mm=841,
                thumbnail_grid_cols=8,
                thumbnail_grid_rows=8,
                thumbnail_size_mm=65
            ),
            (TamanhoPagina.A1, OrientacaoPagina.PAISAGEM): PageLayout(
                page_size=TamanhoPagina.A1,
                orientation=OrientacaoPagina.PAISAGEM,
                width_mm=841,
                height_mm=594,
                thumbnail_grid_cols=10,
                thumbnail_grid_rows=6,
                thumbnail_size_mm=70
            ),
        }
        return layouts.get((page_size, orientation), layouts[(TamanhoPagina.A4, OrientacaoPagina.RETRATO)])


# Resolve forward references
MerkleTreeNode.model_rebuild()
