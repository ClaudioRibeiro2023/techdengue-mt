"""
Relatórios - Schemas for report generation
"""
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field
from enum import Enum


class FormatoRelatorio(str, Enum):
    """Formatos disponíveis para relatório"""
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"


class TamanhoPagina(str, Enum):
    """Tamanhos de página disponíveis para PDF"""
    A1 = "A1"  # 594 x 841 mm (23.4 x 33.1 inches)
    A4 = "A4"  # 210 x 297 mm (8.3 x 11.7 inches)


class RelatorioEPI01Request(BaseModel):
    """Request parameters for EPI01 report"""
    competencia_inicio: str = Field(..., pattern=r"^\d{6}$", description="YYYYMM início")
    competencia_fim: str = Field(..., pattern=r"^\d{6}$", description="YYYYMM fim")
    municipios: Optional[List[str]] = Field(None, description="Filtrar por códigos IBGE")
    formato: FormatoRelatorio = Field(default=FormatoRelatorio.PDF, description="Formato de saída")
    tamanho_pagina: TamanhoPagina = Field(default=TamanhoPagina.A4, description="Tamanho da página (A1 ou A4)")
    incluir_grafico: bool = Field(default=True, description="Incluir gráficos no PDF")


class IndicadorMunicipio(BaseModel):
    """Indicadores agregados por município"""
    municipio_cod_ibge: str
    municipio_nome: str
    populacao: int
    casos_total: int
    casos_confirmados: int
    casos_graves: int
    casos_sinais_alarme: int
    obitos: int
    incidencia: float = Field(..., description="Incidência por 100k hab")
    letalidade: float = Field(..., description="Taxa de letalidade (%)")
    

class RelatorioEPI01Metadata(BaseModel):
    """Metadata for EPI01 report"""
    competencia_inicio: str
    competencia_fim: str
    dt_geracao: str = Field(..., description="Data/hora de geração ISO 8601")
    total_municipios: int
    total_casos: int
    total_obitos: int
    incidencia_media: float
    hash_sha256: str = Field(..., description="Hash SHA-256 do conteúdo do relatório")
    formato: FormatoRelatorio


class RelatorioEPI01Response(BaseModel):
    """Response for EPI01 report generation"""
    metadata: RelatorioEPI01Metadata
    arquivo: str = Field(..., description="Nome do arquivo gerado")
    tamanho_bytes: int
    url_download: Optional[str] = Field(None, description="URL temporária para download")
