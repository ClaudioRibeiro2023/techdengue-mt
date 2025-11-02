"""
ETL EPI - Schemas and validators for epidemiological data import
Based on SINAN/SIVEP-DDA format for dengue surveillance
"""
from datetime import date
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class ClassificacaoFinal(str, Enum):
    """Classificação final do caso"""
    DENGUE = "DENGUE"
    DENGUE_GRAVE = "DENGUE_GRAVE"
    DENGUE_SINAIS_ALARME = "DENGUE_SINAIS_ALARME"
    DESCARTADO = "DESCARTADO"
    INCONCLUSIVO = "INCONCLUSIVO"


class CriterioConfirmacao(str, Enum):
    """Critério de confirmação do caso"""
    LABORATORIAL = "LABORATORIAL"
    CLINICO_EPIDEMIOLOGICO = "CLINICO_EPIDEMIOLOGICO"
    EM_INVESTIGACAO = "EM_INVESTIGACAO"


class Evolucao(str, Enum):
    """Evolução do caso"""
    CURA = "CURA"
    OBITO = "OBITO"
    OBITO_OUTRA_CAUSA = "OBITO_OUTRA_CAUSA"
    IGNORADO = "IGNORADO"


class FaixaEtaria(str, Enum):
    """Faixas etárias para agregação"""
    MENOR_1 = "<1"
    E1_4 = "1-4"
    E5_9 = "5-9"
    E10_14 = "10-14"
    E15_19 = "15-19"
    E20_29 = "20-29"
    E30_39 = "30-39"
    E40_49 = "40-49"
    E50_59 = "50-59"
    E60_MAIS = "60+"


class EPIRecordCSV(BaseModel):
    """
    Schema for a single row in the CSV-EPI01 file.
    Represents one case notification.
    """
    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)
    
    # Identificação
    dt_notificacao: date = Field(..., description="Data da notificação (YYYY-MM-DD)")
    dt_sintomas: date = Field(..., description="Data dos primeiros sintomas (YYYY-MM-DD)")
    municipio_cod_ibge: str = Field(..., min_length=7, max_length=7, description="Código IBGE 7 dígitos")
    
    # Demografia
    sexo: str = Field(..., pattern=r"^[MFI]$", description="Sexo: M, F ou I (Ignorado)")
    idade: int = Field(..., ge=0, le=120, description="Idade em anos")
    gestante: Optional[str] = Field(None, pattern=r"^[123489N]$", description="1-3T, 4-idade ign, 8-NAO, 9-ign, N-não se aplica")
    
    # Classificação clínica
    classificacao_final: ClassificacaoFinal = Field(..., description="Classificação final do caso")
    criterio_confirmacao: CriterioConfirmacao = Field(..., description="Critério de confirmação")
    
    # Sinais/sintomas (flags 0/1)
    febre: int = Field(..., ge=0, le=1, description="Presença de febre (0=não, 1=sim)")
    cefaleia: int = Field(..., ge=0, le=1, description="Presença de cefaleia")
    dor_retroocular: int = Field(..., ge=0, le=1, description="Dor retroocular")
    mialgia: int = Field(..., ge=0, le=1, description="Mialgia")
    artralgia: int = Field(..., ge=0, le=1, description="Artralgia")
    exantema: int = Field(..., ge=0, le=1, description="Exantema")
    vomito: int = Field(..., ge=0, le=1, description="Vômito")
    nausea: int = Field(..., ge=0, le=1, description="Náusea")
    dor_abdominal: int = Field(..., ge=0, le=1, description="Dor abdominal")
    
    # Sinais de alarme (flags 0/1)
    plaquetas_baixas: int = Field(..., ge=0, le=1, description="Plaquetopenia (<100k)")
    hemorragia: int = Field(..., ge=0, le=1, description="Manifestações hemorrágicas")
    hepatomegalia: int = Field(..., ge=0, le=1, description="Hepatomegalia")
    acumulo_liquidos: int = Field(..., ge=0, le=1, description="Acúmulo de líquidos")
    
    # Comorbidades (flags 0/1)
    diabetes: int = Field(..., ge=0, le=1, description="Diabetes")
    hipertensao: int = Field(..., ge=0, le=1, description="Hipertensão")
    
    # Evolução
    evolucao: Evolucao = Field(..., description="Evolução do caso")
    dt_obito: Optional[date] = Field(None, description="Data do óbito (se aplicável)")
    dt_encerramento: Optional[date] = Field(None, description="Data de encerramento do caso")
    
    @field_validator("municipio_cod_ibge")
    @classmethod
    def validate_cod_ibge(cls, v: str) -> str:
        """Validate IBGE code format (7 digits, state code 51=MT)"""
        if not re.match(r"^\d{7}$", v):
            raise ValueError("Código IBGE deve ter exatamente 7 dígitos numéricos")
        # MT state code is 51
        if not v.startswith("51"):
            raise ValueError("Código IBGE deve ser de município de MT (inicia com 51)")
        return v
    
    @field_validator("dt_sintomas")
    @classmethod
    def validate_dt_sintomas(cls, v: date, info) -> date:
        """Validate that symptoms date is before notification date"""
        # Can't access dt_notificacao here in v2, will validate at record level
        if v > date.today():
            raise ValueError("Data de sintomas não pode ser futura")
        return v
    
    @field_validator("dt_obito")
    @classmethod
    def validate_dt_obito(cls, v: Optional[date], info) -> Optional[date]:
        """Validate death date if present"""
        if v is not None and v > date.today():
            raise ValueError("Data de óbito não pode ser futura")
        return v


class ValidationError(BaseModel):
    """A validation error for a single field"""
    linha: int = Field(..., description="Linha do CSV (1-indexed, contando header)")
    campo: str = Field(..., description="Nome do campo com erro")
    valor: str = Field(..., description="Valor inválido")
    erro: str = Field(..., description="Descrição do erro")
    severidade: str = Field(..., pattern=r"^(ERRO|AVISO)$", description="Severidade: ERRO ou AVISO")


class ValidationWarning(BaseModel):
    """A validation warning (non-blocking issue)"""
    linha: int
    campo: str
    valor: str
    aviso: str


class ETLQualityReport(BaseModel):
    """Quality report for ETL EPI upload"""
    arquivo: str = Field(..., description="Nome do arquivo processado")
    dt_processamento: str = Field(..., description="Timestamp do processamento (ISO 8601)")
    total_linhas: int = Field(..., ge=0, description="Total de linhas no CSV (excluindo header)")
    linhas_validas: int = Field(..., ge=0, description="Linhas que passaram na validação")
    linhas_com_erro: int = Field(..., ge=0, description="Linhas com erros bloqueantes")
    linhas_com_aviso: int = Field(..., ge=0, description="Linhas com avisos (não bloqueantes)")
    
    # Detalhamento
    erros: List[ValidationError] = Field(default_factory=list, description="Lista de erros encontrados")
    avisos: List[ValidationWarning] = Field(default_factory=list, description="Lista de avisos encontrados")
    
    # Estatísticas descritivas
    periodo_inicio: Optional[date] = Field(None, description="Data de sintomas mais antiga")
    periodo_fim: Optional[date] = Field(None, description="Data de sintomas mais recente")
    municipios_unicos: int = Field(..., ge=0, description="Quantidade de municípios únicos")
    total_casos_confirmados: int = Field(..., ge=0, description="Casos com classificação = DENGUE*")
    total_obitos: int = Field(..., ge=0, description="Casos com evolução = OBITO")
    
    # Taxa de qualidade
    taxa_qualidade: float = Field(..., ge=0.0, le=100.0, description="% de linhas válidas")
    
    # Status final
    aprovado_para_carga: bool = Field(..., description="True se pode prosseguir com carga no banco")


class ETLUploadResponse(BaseModel):
    """Response for ETL EPI upload endpoint"""
    mensagem: str
    relatorio: ETLQualityReport
    casos_inseridos: int = Field(..., ge=0, description="Quantidade de casos inseridos no banco")
