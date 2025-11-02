"""
Unit tests for ETL EPI Validator
"""
import pytest
from datetime import date
from pathlib import Path

from app.services.etl_validator import EPIValidator, calcular_faixa_etaria
from app.schemas.etl_epi import FaixaEtaria


class TestCalcularFaixaEtaria:
    """Test age group calculation"""
    
    def test_faixa_menor_1(self):
        assert calcular_faixa_etaria(0) == FaixaEtaria.MENOR_1
    
    def test_faixa_1_4(self):
        assert calcular_faixa_etaria(1) == FaixaEtaria.E1_4
        assert calcular_faixa_etaria(4) == FaixaEtaria.E1_4
    
    def test_faixa_5_9(self):
        assert calcular_faixa_etaria(5) == FaixaEtaria.E5_9
        assert calcular_faixa_etaria(9) == FaixaEtaria.E5_9
    
    def test_faixa_10_14(self):
        assert calcular_faixa_etaria(10) == FaixaEtaria.E10_14
        assert calcular_faixa_etaria(14) == FaixaEtaria.E10_14
    
    def test_faixa_60_mais(self):
        assert calcular_faixa_etaria(60) == FaixaEtaria.E60_MAIS
        assert calcular_faixa_etaria(90) == FaixaEtaria.E60_MAIS


class TestEPIValidator:
    """Test EPIValidator service"""
    
    @pytest.fixture
    def validator(self):
        return EPIValidator()
    
    @pytest.fixture
    def valid_csv_path(self):
        return Path(__file__).parent / "test_data" / "epi_example_valid.csv"
    
    def test_validate_valid_csv(self, validator, valid_csv_path):
        """Test validation of a valid CSV file"""
        relatorio = validator.validate_csv(str(valid_csv_path), "epi_example_valid.csv")
        
        # Basic checks
        assert relatorio.total_linhas == 5
        assert relatorio.linhas_validas == 5
        assert relatorio.linhas_com_erro == 0
        assert relatorio.taxa_qualidade == 100.0
        assert relatorio.aprovado_para_carga is True
        
        # Statistics checks
        assert relatorio.periodo_inicio == date(2024, 1, 13)
        assert relatorio.periodo_fim == date(2024, 1, 17)
        assert relatorio.municipios_unicos == 2
        assert relatorio.total_casos_confirmados == 4  # 4 rows with DENGUE* (excluding DESCARTADO)
        assert relatorio.total_obitos == 1
    
    def test_validate_csv_with_missing_columns(self, validator, tmp_path):
        """Test validation fails when required columns are missing"""
        # Create CSV with missing columns
        csv_path = tmp_path / "missing_cols.csv"
        csv_path.write_text("dt_notificacao;dt_sintomas;municipio_cod_ibge\n2024-01-01;2024-01-01;5103403\n")
        
        relatorio = validator.validate_csv(str(csv_path), "missing_cols.csv")
        
        assert relatorio.aprovado_para_carga is False
        assert "ausentes" in relatorio.erros[0].erro.lower()
    
    def test_validate_csv_with_invalid_ibge_code(self, validator, tmp_path):
        """Test validation catches invalid IBGE codes"""
        # Create CSV with invalid IBGE (not MT state)
        csv_content = """dt_notificacao;dt_sintomas;municipio_cod_ibge;sexo;idade;gestante;classificacao_final;criterio_confirmacao;febre;cefaleia;dor_retroocular;mialgia;artralgia;exantema;vomito;nausea;dor_abdominal;plaquetas_baixas;hemorragia;hepatomegalia;acumulo_liquidos;diabetes;hipertensao;evolucao;dt_obito;dt_encerramento
2024-01-15;2024-01-13;3550308;F;28;N;DENGUE;LABORATORIAL;1;1;1;1;1;0;0;0;0;0;0;0;0;0;0;CURA;;2024-01-30
"""
        csv_path = tmp_path / "invalid_ibge.csv"
        csv_path.write_text(csv_content)
        
        relatorio = validator.validate_csv(str(csv_path), "invalid_ibge.csv")
        
        assert relatorio.linhas_com_erro == 1
        assert relatorio.taxa_qualidade < 100.0
        assert any("51" in erro.erro for erro in relatorio.erros)
    
    def test_validate_csv_with_future_dates(self, validator, tmp_path):
        """Test validation catches future dates"""
        future_date = date.today().replace(year=date.today().year + 1)
        csv_content = f"""dt_notificacao;dt_sintomas;municipio_cod_ibge;sexo;idade;gestante;classificacao_final;criterio_confirmacao;febre;cefaleia;dor_retroocular;mialgia;artralgia;exantema;vomito;nausea;dor_abdominal;plaquetas_baixas;hemorragia;hepatomegalia;acumulo_liquidos;diabetes;hipertensao;evolucao;dt_obito;dt_encerramento
2024-01-15;{future_date};5103403;F;28;N;DENGUE;LABORATORIAL;1;1;1;1;1;0;0;0;0;0;0;0;0;0;0;CURA;;2024-01-30
"""
        csv_path = tmp_path / "future_dates.csv"
        csv_path.write_text(csv_content)
        
        relatorio = validator.validate_csv(str(csv_path), "future_dates.csv")
        
        assert relatorio.linhas_com_erro >= 1
        assert any("futura" in erro.erro.lower() for erro in relatorio.erros)
    
    def test_cross_field_validation_sintomas_after_notificacao(self, validator, tmp_path):
        """Test that symptoms date after notification date is caught"""
        csv_content = """dt_notificacao;dt_sintomas;municipio_cod_ibge;sexo;idade;gestante;classificacao_final;criterio_confirmacao;febre;cefaleia;dor_retroocular;mialgia;artralgia;exantema;vomito;nausea;dor_abdominal;plaquetas_baixas;hemorragia;hepatomegalia;acumulo_liquidos;diabetes;hipertensao;evolucao;dt_obito;dt_encerramento
2024-01-10;2024-01-15;5103403;F;28;N;DENGUE;LABORATORIAL;1;1;1;1;1;0;0;0;0;0;0;0;0;0;0;CURA;;2024-01-30
"""
        csv_path = tmp_path / "invalid_dates.csv"
        csv_path.write_text(csv_content)
        
        relatorio = validator.validate_csv(str(csv_path), "invalid_dates.csv")
        
        assert relatorio.linhas_com_erro == 1
        assert any("posterior" in erro.erro.lower() for erro in relatorio.erros)
    
    def test_warning_obito_without_dt_obito(self, validator, tmp_path):
        """Test warning is generated when OBITO evolution but no death date"""
        csv_content = """dt_notificacao;dt_sintomas;municipio_cod_ibge;sexo;idade;gestante;classificacao_final;criterio_confirmacao;febre;cefaleia;dor_retroocular;mialgia;artralgia;exantema;vomito;nausea;dor_abdominal;plaquetas_baixas;hemorragia;hepatomegalia;acumulo_liquidos;diabetes;hipertensao;evolucao;dt_obito;dt_encerramento
2024-01-18;2024-01-16;5105606;M;62;;DENGUE_GRAVE;LABORATORIAL;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;OBITO;;2024-01-26
"""
        csv_path = tmp_path / "obito_no_date.csv"
        csv_path.write_text(csv_content)
        
        relatorio = validator.validate_csv(str(csv_path), "obito_no_date.csv")
        
        # Should have 1 valid record but 1 warning
        assert relatorio.linhas_validas == 1
        assert relatorio.linhas_com_aviso == 1
        assert any("OBITO" in aviso.aviso for aviso in relatorio.avisos)
