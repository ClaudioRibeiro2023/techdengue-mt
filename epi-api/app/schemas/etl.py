"""
Schemas Pydantic para ETL (SINAN e LIRAa)
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from pydantic import BaseModel, Field, validator, field_validator
from decimal import Decimal


# ============================================================================
# ENUMS
# ============================================================================

class ETLStatus(str, Enum):
    """Status do job ETL"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"  # Concluído com erros não-críticos


class ETLSource(str, Enum):
    """Fonte de dados ETL"""
    SINAN = "SINAN"
    LIRAA = "LIRAA"
    MANUAL = "MANUAL"


class DoencaTipo(str, Enum):
    """Tipo de doença"""
    DENGUE = "DENGUE"
    ZIKA = "ZIKA"
    CHIKUNGUNYA = "CHIKUNGUNYA"
    FEBRE_AMARELA = "FEBRE_AMARELA"


class RiscoNivel(str, Enum):
    """Nível de risco (LIRAa)"""
    BAIXO = "BAIXO"          # IIP < 1%
    MEDIO = "MEDIO"          # 1% ≤ IIP < 3.9%
    ALTO = "ALTO"            # IIP ≥ 3.9%
    MUITO_ALTO = "MUITO_ALTO"  # IIP ≥ 5%


# ============================================================================
# SINAN SCHEMAS
# ============================================================================

class SINANRecordRaw(BaseModel):
    """
    Registro raw SINAN (exemplo campos principais)
    Baseado no padrão SINAN do Ministério da Saúde
    """
    # Identificação
    nu_notific: str = Field(..., description="Número da notificação")
    dt_notific: date = Field(..., description="Data da notificação")
    dt_sin_pri: Optional[date] = Field(None, description="Data dos primeiros sintomas")
    
    # Paciente
    nm_pacient: str = Field(..., description="Nome do paciente")
    dt_nasc: Optional[date] = Field(None, description="Data de nascimento")
    nu_idade_n: Optional[int] = Field(None, ge=0, le=120, description="Idade")
    cs_sexo: Optional[str] = Field(None, description="Sexo (M/F)")
    
    # Localização
    sg_uf: str = Field(..., description="Sigla UF")
    id_municip: str = Field(..., description="Código município IBGE")
    nm_bairro: Optional[str] = Field(None, description="Bairro")
    
    # Doença
    dt_diag: Optional[date] = Field(None, description="Data do diagnóstico")
    tp_diag: Optional[str] = Field(None, description="Tipo diagnóstico (laboratorial/clínico)")
    classi_fin: Optional[int] = Field(None, description="Classificação final (1-5)")
    criterio: Optional[str] = Field(None, description="Critério confirmação")
    
    # Desfecho
    dt_encerra: Optional[date] = Field(None, description="Data encerramento")
    dt_obito: Optional[date] = Field(None, description="Data óbito")
    evolucao: Optional[int] = Field(None, description="Evolução (1=Cura, 2=Óbito, etc)")
    
    # Metadata adicional
    extra_fields: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Campos extras do CSV")
    
    @field_validator('sg_uf')
    @classmethod
    def validate_uf(cls, v: str) -> str:
        """Valida UF"""
        if v.upper() != 'MT':
            raise ValueError('Apenas dados de MT são aceitos')
        return v.upper()
    
    @field_validator('cs_sexo')
    @classmethod
    def validate_sexo(cls, v: Optional[str]) -> Optional[str]:
        """Valida sexo"""
        if v is None:
            return v
        v_upper = v.upper()
        if v_upper not in ['M', 'F', 'I']:  # M, F, Ignorado
            raise ValueError('Sexo deve ser M, F ou I')
        return v_upper


class SINANImportRequest(BaseModel):
    """Request para importação SINAN"""
    file_path: str = Field(..., description="Caminho do arquivo CSV no S3")
    doenca_tipo: DoencaTipo = Field(..., description="Tipo de doença")
    ano_epidemiologico: int = Field(..., ge=2000, le=2100, description="Ano epidemiológico")
    semana_epi_inicio: Optional[int] = Field(None, ge=1, le=53, description="Semana epi início")
    semana_epi_fim: Optional[int] = Field(None, ge=1, le=53, description="Semana epi fim")
    overwrite: bool = Field(False, description="Sobrescrever dados existentes")
    batch_size: int = Field(500, ge=10, le=5000, description="Tamanho do batch para processamento")
    
    @field_validator('semana_epi_fim')
    @classmethod
    def validate_semana_range(cls, v: Optional[int], info) -> Optional[int]:
        """Valida range de semanas"""
        if v is not None and 'semana_epi_inicio' in info.data:
            inicio = info.data['semana_epi_inicio']
            if inicio and v < inicio:
                raise ValueError('semana_epi_fim deve ser >= semana_epi_inicio')
        return v


class SINANImportResponse(BaseModel):
    """Response da importação SINAN"""
    job_id: str = Field(..., description="ID do job ETL")
    status: ETLStatus = Field(..., description="Status do job")
    message: str = Field(..., description="Mensagem")
    file_path: str = Field(..., description="Caminho do arquivo")
    started_at: datetime = Field(..., description="Início do processamento")
    
    # Estatísticas iniciais
    total_rows: Optional[int] = Field(None, description="Total de linhas no CSV")
    estimated_time_seconds: Optional[int] = Field(None, description="Tempo estimado (segundos)")


# ============================================================================
# LIRAa SCHEMAS
# ============================================================================

class LIRaaRecordRaw(BaseModel):
    """
    Registro raw LIRAa (Levantamento Rápido de Índices para Aedes aegypti)
    Padrão MS: IIP, IB, IDC
    """
    # Identificação
    municipio_codigo: str = Field(..., description="Código IBGE município")
    municipio_nome: str = Field(..., description="Nome município")
    ano: int = Field(..., ge=2000, le=2100, description="Ano do levantamento")
    ciclo: int = Field(..., ge=1, le=6, description="Ciclo LIRAa (1-6)")
    
    # Estratificação
    estrato: Optional[str] = Field(None, description="Estrato/Bairro/Região")
    zona: Optional[str] = Field(None, description="Zona (urbana/rural)")
    
    # Imóveis
    imoveis_pesquisados: int = Field(..., ge=0, description="Total imóveis pesquisados")
    imoveis_positivos: int = Field(..., ge=0, description="Imóveis com larvas/pupas")
    imoveis_fechados: Optional[int] = Field(0, ge=0, description="Imóveis fechados")
    imoveis_recusados: Optional[int] = Field(0, ge=0, description="Imóveis recusados")
    
    # Depósitos
    depositos_inspecionados: int = Field(..., ge=0, description="Total depósitos inspecionados")
    depositos_positivos: int = Field(..., ge=0, description="Depósitos com larvas/pupas")
    
    # Tipos de depósito (A1, A2, B, C, D1, D2, E)
    depositos_a1: Optional[int] = Field(0, ge=0, description="Depósitos A1 (caixa d'água)")
    depositos_a2: Optional[int] = Field(0, ge=0, description="Depósitos A2 (outros elevados)")
    depositos_b: Optional[int] = Field(0, ge=0, description="Depósitos B (nível solo)")
    depositos_c: Optional[int] = Field(0, ge=0, description="Depósitos C (móveis)")
    depositos_d1: Optional[int] = Field(0, ge=0, description="Depósitos D1 (pneus)")
    depositos_d2: Optional[int] = Field(0, ge=0, description="Depósitos D2 (lixo)")
    depositos_e: Optional[int] = Field(0, ge=0, description="Depósitos E (naturais)")
    
    # Índices calculados (podem vir no CSV ou serem calculados)
    iip: Optional[Decimal] = Field(None, ge=0, le=100, description="Índice de Infestação Predial (%)")
    ib: Optional[Decimal] = Field(None, ge=0, description="Índice de Breteau (por 100 imóveis)")
    idc: Optional[Decimal] = Field(None, ge=0, le=100, description="Índice de Depósitos por Tipo (%)")
    
    # Metadata
    data_levantamento: Optional[date] = Field(None, description="Data do levantamento")
    responsavel: Optional[str] = Field(None, description="Responsável técnico")
    observacoes: Optional[str] = Field(None, description="Observações")
    
    @field_validator('imoveis_positivos')
    @classmethod
    def validate_positivos(cls, v: int, info) -> int:
        """Valida que positivos <= pesquisados"""
        if 'imoveis_pesquisados' in info.data:
            pesquisados = info.data['imoveis_pesquisados']
            if v > pesquisados:
                raise ValueError('imoveis_positivos não pode ser maior que imoveis_pesquisados')
        return v


class LIRaaImportRequest(BaseModel):
    """Request para importação LIRAa"""
    file_path: str = Field(..., description="Caminho do arquivo CSV no S3")
    ano: int = Field(..., ge=2000, le=2100, description="Ano do levantamento")
    ciclo: int = Field(..., ge=1, le=6, description="Ciclo LIRAa")
    calcular_indices: bool = Field(True, description="Calcular IIP/IB/IDC se não fornecidos")
    overwrite: bool = Field(False, description="Sobrescrever dados existentes")
    batch_size: int = Field(500, ge=10, le=5000, description="Tamanho do batch")


class LIRaaImportResponse(BaseModel):
    """Response da importação LIRAa"""
    job_id: str = Field(..., description="ID do job ETL")
    status: ETLStatus = Field(..., description="Status do job")
    message: str = Field(..., description="Mensagem")
    file_path: str = Field(..., description="Caminho do arquivo")
    started_at: datetime = Field(..., description="Início do processamento")
    
    # Estatísticas
    total_rows: Optional[int] = Field(None, description="Total de linhas")
    estimated_time_seconds: Optional[int] = Field(None, description="Tempo estimado")


# ============================================================================
# ETL JOB SCHEMAS
# ============================================================================

class ETLJobStatus(BaseModel):
    """Status de um job ETL"""
    job_id: str = Field(..., description="ID do job")
    source: ETLSource = Field(..., description="Fonte (SINAN/LIRAa)")
    status: ETLStatus = Field(..., description="Status atual")
    file_path: str = Field(..., description="Caminho do arquivo")
    
    # Timestamps
    started_at: datetime = Field(..., description="Início")
    updated_at: datetime = Field(..., description="Última atualização")
    completed_at: Optional[datetime] = Field(None, description="Conclusão")
    
    # Progress
    total_rows: Optional[int] = Field(None, description="Total de linhas no CSV")
    processed_rows: Optional[int] = Field(None, description="Linhas processadas")
    success_rows: Optional[int] = Field(None, description="Linhas com sucesso")
    error_rows: Optional[int] = Field(None, description="Linhas com erro")
    
    # Errors
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    error_details: Optional[List[Dict[str, Any]]] = Field(None, description="Detalhes dos erros")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata adicional")
    
    @property
    def progress_percentage(self) -> Optional[float]:
        """Calcula percentual de progresso"""
        if self.total_rows and self.total_rows > 0:
            return round((self.processed_rows or 0) / self.total_rows * 100, 2)
        return None
    
    @property
    def success_rate(self) -> Optional[float]:
        """Calcula taxa de sucesso"""
        if self.processed_rows and self.processed_rows > 0:
            return round((self.success_rows or 0) / self.processed_rows * 100, 2)
        return None


class ETLJobList(BaseModel):
    """Lista de jobs ETL"""
    jobs: List[ETLJobStatus] = Field(..., description="Lista de jobs")
    total: int = Field(..., description="Total de jobs")
    page: int = Field(1, ge=1, description="Página atual")
    page_size: int = Field(20, ge=1, le=100, description="Itens por página")


# ============================================================================
# VALIDATION ERROR SCHEMAS
# ============================================================================

class ETLValidationError(BaseModel):
    """Erro de validação ETL"""
    row_number: int = Field(..., description="Número da linha no CSV")
    field: str = Field(..., description="Campo com erro")
    value: Optional[Any] = Field(None, description="Valor inválido")
    error_type: str = Field(..., description="Tipo de erro")
    error_message: str = Field(..., description="Mensagem de erro")
    severity: Literal["ERROR", "WARNING"] = Field("ERROR", description="Severidade")


class ETLValidationReport(BaseModel):
    """Relatório de validação ETL"""
    total_rows: int = Field(..., description="Total de linhas validadas")
    valid_rows: int = Field(..., description="Linhas válidas")
    invalid_rows: int = Field(..., description="Linhas inválidas")
    warnings: int = Field(0, description="Warnings")
    errors: List[ETLValidationError] = Field(default_factory=list, description="Lista de erros")
    
    @property
    def is_valid(self) -> bool:
        """Verifica se a validação passou (sem erros críticos)"""
        critical_errors = [e for e in self.errors if e.severity == "ERROR"]
        return len(critical_errors) == 0


# ============================================================================
# INDICADOR EPI SCHEMAS (para carga final)
# ============================================================================

class IndicadorEpiCreate(BaseModel):
    """Schema para criar indicador_epi (resultado do ETL)"""
    municipio_codigo: str = Field(..., min_length=7, max_length=7, description="Código IBGE município")
    ano: int = Field(..., ge=2000, le=2100, description="Ano")
    semana_epi: int = Field(..., ge=1, le=53, description="Semana epidemiológica")
    doenca_tipo: DoencaTipo = Field(..., description="Tipo de doença")
    
    # SINAN - Casos
    casos_confirmados: Optional[int] = Field(0, ge=0, description="Casos confirmados")
    casos_suspeitos: Optional[int] = Field(0, ge=0, description="Casos suspeitos")
    casos_graves: Optional[int] = Field(0, ge=0, description="Casos graves")
    obitos: Optional[int] = Field(0, ge=0, description="Óbitos")
    
    # LIRAa - Índices
    iip: Optional[Decimal] = Field(None, ge=0, le=100, description="Índice Infestação Predial")
    ib: Optional[Decimal] = Field(None, ge=0, description="Índice de Breteau")
    idc: Optional[Decimal] = Field(None, ge=0, le=100, description="Índice Depósitos por Tipo")
    nivel_risco: Optional[RiscoNivel] = Field(None, description="Nível de risco")
    
    # Metadata
    fonte: ETLSource = Field(..., description="Fonte dos dados")
    data_atualizacao: datetime = Field(default_factory=datetime.utcnow, description="Data atualização")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata adicional")
    
    class Config:
        json_schema_extra = {
            "example": {
                "municipio_codigo": "5103403",  # Cuiabá
                "ano": 2024,
                "semana_epi": 44,
                "doenca_tipo": "DENGUE",
                "casos_confirmados": 150,
                "casos_suspeitos": 45,
                "casos_graves": 12,
                "obitos": 2,
                "iip": 3.5,
                "ib": 5.2,
                "nivel_risco": "ALTO",
                "fonte": "SINAN"
            }
        }
