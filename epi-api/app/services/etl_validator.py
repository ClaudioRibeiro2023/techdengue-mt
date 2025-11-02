"""
ETL EPI Validator Service
Validates CSV-EPI01 files and generates quality reports
"""
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional
import pandas as pd
from pydantic import ValidationError as PydanticValidationError

from app.schemas.etl_epi import (
    EPIRecordCSV,
    ValidationError,
    ValidationWarning,
    ETLQualityReport,
    FaixaEtaria
)


class EPIValidator:
    """Validates EPI CSV files and generates quality reports"""
    
    # Expected CSV columns (must match EPIRecordCSV model)
    REQUIRED_COLUMNS = [
        "dt_notificacao", "dt_sintomas", "municipio_cod_ibge",
        "sexo", "idade", "gestante",
        "classificacao_final", "criterio_confirmacao",
        "febre", "cefaleia", "dor_retroocular", "mialgia", "artralgia",
        "exantema", "vomito", "nausea", "dor_abdominal",
        "plaquetas_baixas", "hemorragia", "hepatomegalia", "acumulo_liquidos",
        "diabetes", "hipertensao",
        "evolucao", "dt_obito", "dt_encerramento"
    ]
    
    def __init__(self):
        self.erros: List[ValidationError] = []
        self.avisos: List[ValidationWarning] = []
        self.valid_records: List[EPIRecordCSV] = []
        
    def validate_csv(self, filepath: str, filename: str) -> ETLQualityReport:
        """
        Validate a CSV-EPI01 file and return quality report.
        
        Args:
            filepath: Path to the CSV file
            filename: Original filename (for reporting)
            
        Returns:
            ETLQualityReport with validation results
        """
        self.erros = []
        self.avisos = []
        self.valid_records = []
        
        try:
            # Read CSV with pandas
            df = pd.read_csv(filepath, sep=";", encoding="utf-8", dtype=str)
        except Exception as e:
            # Fatal error: can't read file
            return self._build_fatal_error_report(filename, str(e))
        
        total_linhas = len(df)
        
        # Validate columns
        missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            return self._build_fatal_error_report(
                filename,
                f"Colunas obrigatórias ausentes: {', '.join(missing_cols)}"
            )
        
        # Validate each row
        for idx, row in df.iterrows():
            linha_num = idx + 2  # +2 because: 0-indexed + 1 (skip header line)
            self._validate_row(linha_num, row)
        
        # Build quality report
        linhas_validas = len(self.valid_records)
        linhas_com_erro = len({e.linha for e in self.erros})
        linhas_com_aviso = len({a.linha for a in self.avisos})
        
        # Calculate statistics from valid records
        periodo_inicio, periodo_fim = self._calc_periodo(self.valid_records)
        municipios_unicos = len({r.municipio_cod_ibge for r in self.valid_records})
        total_confirmados = sum(
            1 for r in self.valid_records
            if r.classificacao_final.startswith("DENGUE")
        )
        total_obitos = sum(
            1 for r in self.valid_records
            if r.evolucao == "OBITO"
        )
        
        taxa_qualidade = (linhas_validas / total_linhas * 100) if total_linhas > 0 else 0.0
        
        # Approve if > 95% valid and no critical structural errors
        aprovado = taxa_qualidade >= 95.0 and linhas_com_erro < (total_linhas * 0.05)
        
        return ETLQualityReport(
            arquivo=filename,
            dt_processamento=datetime.utcnow().isoformat() + "Z",
            total_linhas=total_linhas,
            linhas_validas=linhas_validas,
            linhas_com_erro=linhas_com_erro,
            linhas_com_aviso=linhas_com_aviso,
            erros=self.erros[:100],  # Limit to first 100 errors
            avisos=self.avisos[:100],  # Limit to first 100 warnings
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            municipios_unicos=municipios_unicos,
            total_casos_confirmados=total_confirmados,
            total_obitos=total_obitos,
            taxa_qualidade=round(taxa_qualidade, 2),
            aprovado_para_carga=aprovado
        )
    
    def _validate_row(self, linha: int, row: pd.Series) -> None:
        """Validate a single CSV row"""
        try:
            # Convert pandas row to dict, handle NaN/None
            row_dict = row.where(pd.notna(row), None).to_dict()
            
            # Try to parse with Pydantic
            record = EPIRecordCSV(**row_dict)
            
            # Additional cross-field validations
            self._validate_cross_fields(linha, record)
            
            # If all OK, add to valid records
            self.valid_records.append(record)
            
        except PydanticValidationError as e:
            # Pydantic validation failed
            for error in e.errors():
                field = ".".join(str(x) for x in error["loc"])
                self.erros.append(ValidationError(
                    linha=linha,
                    campo=field,
                    valor=str(row.get(field, "")),
                    erro=error["msg"],
                    severidade="ERRO"
                ))
        except Exception as e:
            # Unexpected error
            self.erros.append(ValidationError(
                linha=linha,
                campo="geral",
                valor="",
                erro=f"Erro inesperado: {str(e)}",
                severidade="ERRO"
            ))
    
    def _validate_cross_fields(self, linha: int, record: EPIRecordCSV) -> None:
        """Validate relationships between fields"""
        
        # dt_sintomas must be <= dt_notificacao
        if record.dt_sintomas > record.dt_notificacao:
            self.erros.append(ValidationError(
                linha=linha,
                campo="dt_sintomas",
                valor=str(record.dt_sintomas),
                erro="Data de sintomas posterior à data de notificação",
                severidade="ERRO"
            ))
        
        # If evolucao = OBITO, dt_obito should be present
        if record.evolucao == "OBITO" and record.dt_obito is None:
            self.avisos.append(ValidationWarning(
                linha=linha,
                campo="dt_obito",
                valor="null",
                aviso="Evolução = OBITO mas dt_obito não informada"
            ))
        
        # If dt_obito present, evolucao should be OBITO
        if record.dt_obito is not None and record.evolucao != "OBITO":
            self.avisos.append(ValidationWarning(
                linha=linha,
                campo="evolucao",
                valor=record.evolucao,
                aviso=f"dt_obito informada mas evolucao = {record.evolucao}"
            ))
        
        # Gestante only for females aged 10-49
        if record.gestante and record.gestante not in ["N", "9"]:
            if record.sexo != "F":
                self.avisos.append(ValidationWarning(
                    linha=linha,
                    campo="gestante",
                    valor=record.gestante,
                    aviso="Campo gestante preenchido para sexo != F"
                ))
            if record.idade < 10 or record.idade > 49:
                self.avisos.append(ValidationWarning(
                    linha=linha,
                    campo="gestante",
                    valor=record.gestante,
                    aviso="Gestante informada para idade fora da faixa 10-49"
                ))
        
        # Classification consistency
        if record.classificacao_final == "DESCARTADO":
            if record.criterio_confirmacao == "LABORATORIAL":
                self.avisos.append(ValidationWarning(
                    linha=linha,
                    campo="classificacao_final",
                    valor=record.classificacao_final,
                    aviso="Caso DESCARTADO com critério LABORATORIAL (incomum)"
                ))
    
    def _calc_periodo(self, records: List[EPIRecordCSV]) -> Tuple[Optional[date], Optional[date]]:
        """Calculate min and max symptom dates"""
        if not records:
            return None, None
        dates = [r.dt_sintomas for r in records]
        return min(dates), max(dates)
    
    def _build_fatal_error_report(self, filename: str, error_msg: str) -> ETLQualityReport:
        """Build error report for fatal validation errors"""
        return ETLQualityReport(
            arquivo=filename,
            dt_processamento=datetime.utcnow().isoformat() + "Z",
            total_linhas=0,
            linhas_validas=0,
            linhas_com_erro=1,
            linhas_com_aviso=0,
            erros=[ValidationError(
                linha=0,
                campo="arquivo",
                valor=filename,
                erro=error_msg,
                severidade="ERRO"
            )],
            avisos=[],
            periodo_inicio=None,
            periodo_fim=None,
            municipios_unicos=0,
            total_casos_confirmados=0,
            total_obitos=0,
            taxa_qualidade=0.0,
            aprovado_para_carga=False
        )


def calcular_faixa_etaria(idade: int) -> FaixaEtaria:
    """Calculate age group from age in years"""
    if idade < 1:
        return FaixaEtaria.MENOR_1
    elif idade <= 4:
        return FaixaEtaria.E1_4
    elif idade <= 9:
        return FaixaEtaria.E5_9
    elif idade <= 14:
        return FaixaEtaria.E10_14
    elif idade <= 19:
        return FaixaEtaria.E15_19
    elif idade <= 29:
        return FaixaEtaria.E20_29
    elif idade <= 39:
        return FaixaEtaria.E30_39
    elif idade <= 49:
        return FaixaEtaria.E40_49
    elif idade <= 59:
        return FaixaEtaria.E50_59
    else:
        return FaixaEtaria.E60_MAIS
