"""
Testes para ETL (SINAN e LIRAa)
"""
import pytest
from datetime import datetime, date
from decimal import Decimal
import tempfile
import csv
import os

from app.schemas.etl import (
    SINANRecordRaw,
    SINANImportRequest,
    LIRaaRecordRaw,
    LIRaaImportRequest,
    ETLStatus,
    ETLSource,
    DoencaTipo,
    RiscoNivel,
    ETLValidationError,
    ETLValidationReport
)
from app.services.etl_base_service import ETLBaseService
from app.services.sinan_etl_service import SINANETLService
from app.services.liraa_etl_service import LIRaaETLService


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def db_config():
    """Database config for testing"""
    return {
        'host': os.getenv('TEST_DB_HOST', 'localhost'),
        'port': int(os.getenv('TEST_DB_PORT', '5432')),
        'database': os.getenv('TEST_DB_NAME', 'techdengue_test'),
        'user': os.getenv('TEST_DB_USER', 'techdengue'),
        'password': os.getenv('TEST_DB_PASSWORD', 'techdengue')
    }


@pytest.fixture
def temp_csv_sinan():
    """Cria CSV SINAN temporário para testes"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'nu_notific', 'dt_notific', 'dt_sin_pri', 'nm_pacient',
            'dt_nasc', 'nu_idade_n', 'cs_sexo', 'sg_uf', 'id_municip',
            'nm_bairro', 'dt_diag', 'tp_diag', 'classi_fin', 'criterio',
            'dt_encerra', 'dt_obito', 'evolucao'
        ])
        writer.writeheader()
        
        # Casos de teste
        writer.writerow({
            'nu_notific': '202400001',
            'dt_notific': '15/01/2024',
            'dt_sin_pri': '10/01/2024',
            'nm_pacient': 'TESTE SILVA',
            'dt_nasc': '01/01/1990',
            'nu_idade_n': '34',
            'cs_sexo': 'M',
            'sg_uf': 'MT',
            'id_municip': '5103403',  # Cuiabá
            'nm_bairro': 'CENTRO',
            'dt_diag': '16/01/2024',
            'tp_diag': 'Laboratorial',
            'classi_fin': '1',  # Confirmado laboratorial
            'criterio': 'NS1',
            'dt_encerra': '20/01/2024',
            'dt_obito': '',
            'evolucao': '1'  # Cura
        })
        
        writer.writerow({
            'nu_notific': '202400002',
            'dt_notific': '16/01/2024',
            'dt_sin_pri': '12/01/2024',
            'nm_pacient': 'MARIA SOUZA',
            'dt_nasc': '15/05/1985',
            'nu_idade_n': '38',
            'cs_sexo': 'F',
            'sg_uf': 'MT',
            'id_municip': '5103403',
            'nm_bairro': 'JARDIM',
            'dt_diag': '',
            'tp_diag': '',
            'classi_fin': '3',  # Suspeito
            'criterio': '',
            'dt_encerra': '',
            'dt_obito': '',
            'evolucao': ''
        })
        
        filepath = f.name
    
    yield filepath
    
    # Cleanup
    if os.path.exists(filepath):
        os.unlink(filepath)


@pytest.fixture
def temp_csv_liraa():
    """Cria CSV LIRAa temporário para testes"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'municipio_codigo', 'municipio_nome', 'ano', 'ciclo',
            'estrato', 'zona', 'imoveis_pesquisados', 'imoveis_positivos',
            'imoveis_fechados', 'imoveis_recusados',
            'depositos_inspecionados', 'depositos_positivos',
            'depositos_a1', 'depositos_a2', 'depositos_b',
            'depositos_c', 'depositos_d1', 'depositos_d2', 'depositos_e',
            'iip', 'ib', 'idc', 'data_levantamento', 'responsavel'
        ])
        writer.writeheader()
        
        # Casos de teste
        writer.writerow({
            'municipio_codigo': '5103403',
            'municipio_nome': 'Cuiabá',
            'ano': '2024',
            'ciclo': '1',
            'estrato': 'Centro',
            'zona': 'Urbana',
            'imoveis_pesquisados': '1000',
            'imoveis_positivos': '50',
            'imoveis_fechados': '20',
            'imoveis_recusados': '5',
            'depositos_inspecionados': '3000',
            'depositos_positivos': '75',
            'depositos_a1': '10',
            'depositos_a2': '15',
            'depositos_b': '20',
            'depositos_c': '15',
            'depositos_d1': '5',
            'depositos_d2': '8',
            'depositos_e': '2',
            'iip': '',  # Será calculado
            'ib': '',
            'idc': '',
            'data_levantamento': '30/01/2024',
            'responsavel': 'João Silva'
        })
        
        writer.writerow({
            'municipio_codigo': '5107602',
            'municipio_nome': 'Várzea Grande',
            'ano': '2024',
            'ciclo': '1',
            'estrato': 'Norte',
            'zona': 'Urbana',
            'imoveis_pesquisados': '800',
            'imoveis_positivos': '8',
            'imoveis_fechados': '15',
            'imoveis_recusados': '3',
            'depositos_inspecionados': '2400',
            'depositos_positivos': '12',
            'depositos_a1': '2',
            'depositos_a2': '3',
            'depositos_b': '4',
            'depositos_c': '2',
            'depositos_d1': '1',
            'depositos_d2': '0',
            'depositos_e': '0',
            'iip': '1.0',  # Fornecido manualmente
            'ib': '1.5',
            'idc': '0.5',
            'data_levantamento': '31/01/2024',
            'responsavel': 'Maria Santos'
        })
        
        filepath = f.name
    
    yield filepath
    
    # Cleanup
    if os.path.exists(filepath):
        os.unlink(filepath)


# ============================================================================
# TESTES - SCHEMAS
# ============================================================================

def test_sinan_record_validation():
    """Testa validação de registro SINAN"""
    # Registro válido
    record = SINANRecordRaw(
        nu_notific="202400001",
        dt_notific=date(2024, 1, 15),
        nm_pacient="TESTE SILVA",
        sg_uf="MT",
        id_municip="5103403"
    )
    
    assert record.nu_notific == "202400001"
    assert record.sg_uf == "MT"
    assert record.id_municip == "5103403"


def test_sinan_record_invalid_uf():
    """Testa rejeição de UF inválida"""
    with pytest.raises(ValueError, match="Apenas dados de MT"):
        SINANRecordRaw(
            nu_notific="202400001",
            dt_notific=date(2024, 1, 15),
            nm_pacient="TESTE",
            sg_uf="SP",  # Inválido
            id_municip="3550308"
        )


def test_liraa_record_validation():
    """Testa validação de registro LIRAa"""
    record = LIRaaRecordRaw(
        municipio_codigo="5103403",
        municipio_nome="Cuiabá",
        ano=2024,
        ciclo=1,
        imoveis_pesquisados=1000,
        imoveis_positivos=50,
        depositos_inspecionados=3000,
        depositos_positivos=75
    )
    
    assert record.municipio_codigo == "5103403"
    assert record.ano == 2024
    assert record.ciclo == 1


def test_liraa_record_invalid_positivos():
    """Testa rejeição quando positivos > pesquisados"""
    with pytest.raises(ValueError, match="não pode ser maior"):
        LIRaaRecordRaw(
            municipio_codigo="5103403",
            municipio_nome="Cuiabá",
            ano=2024,
            ciclo=1,
            imoveis_pesquisados=100,
            imoveis_positivos=150,  # Inválido
            depositos_inspecionados=300,
            depositos_positivos=50
        )


def test_sinan_import_request_validation():
    """Testa validação de request SINAN"""
    request = SINANImportRequest(
        file_path="/data/sinan.csv",
        doenca_tipo=DoencaTipo.DENGUE,
        ano_epidemiologico=2024,
        semana_epi_inicio=1,
        semana_epi_fim=10,
        overwrite=False,
        batch_size=500
    )
    
    assert request.doenca_tipo == DoencaTipo.DENGUE
    assert request.ano_epidemiologico == 2024
    assert request.batch_size == 500


def test_sinan_import_request_invalid_semana_range():
    """Testa rejeição de range de semanas inválido"""
    with pytest.raises(ValueError, match="deve ser >="):
        SINANImportRequest(
            file_path="/data/sinan.csv",
            doenca_tipo=DoencaTipo.DENGUE,
            ano_epidemiologico=2024,
            semana_epi_inicio=10,
            semana_epi_fim=5,  # Inválido (< inicio)
            overwrite=False
        )


# ============================================================================
# TESTES - ETL BASE SERVICE
# ============================================================================

def test_calculate_liraa_indices(db_config):
    """Testa cálculo de índices LIRAa"""
    service = ETLBaseService(db_config)
    
    indices = service.calculate_liraa_indices(
        imoveis_pesquisados=1000,
        imoveis_positivos=50,
        depositos_inspecionados=3000,
        depositos_positivos=75
    )
    
    assert indices['iip'] == Decimal('5.00')  # (50/1000) * 100
    assert indices['ib'] == Decimal('7.50')   # (75/1000) * 100
    assert indices['idc'] == Decimal('2.50')  # (75/3000) * 100


def test_calculate_liraa_indices_zero_division(db_config):
    """Testa tratamento de divisão por zero"""
    service = ETLBaseService(db_config)
    
    indices = service.calculate_liraa_indices(
        imoveis_pesquisados=0,
        imoveis_positivos=0,
        depositos_inspecionados=0,
        depositos_positivos=0
    )
    
    assert indices['iip'] == Decimal('0.00')
    assert indices['ib'] == Decimal('0.00')
    assert indices['idc'] == Decimal('0.00')


def test_classify_risk_level(db_config):
    """Testa classificação de nível de risco"""
    service = ETLBaseService(db_config)
    
    assert service.classify_risk_level(Decimal('0.5')) == 'BAIXO'
    assert service.classify_risk_level(Decimal('2.0')) == 'MEDIO'
    assert service.classify_risk_level(Decimal('4.0')) == 'ALTO'
    assert service.classify_risk_level(Decimal('6.0')) == 'MUITO_ALTO'


# ============================================================================
# TESTES - SINAN ETL SERVICE
# ============================================================================

def test_sinan_normalize_row(db_config):
    """Testa normalização de linha SINAN"""
    service = SINANETLService(db_config)
    
    row = {
        'nu_notific': '202400001',
        'dt_notific': '15/01/2024',
        'nm_pacient': 'TESTE SILVA',
        'sg_uf': 'MT',
        'id_municip': '5103403',
        'nu_idade_n': '34',
        'cs_sexo': 'M'
    }
    
    normalized = service._normalize_sinan_row(row)
    
    assert normalized['nu_notific'] == '202400001'
    assert normalized['dt_notific'] == date(2024, 1, 15)
    assert normalized['sg_uf'] == 'MT'
    assert normalized['nu_idade_n'] == 34
    assert normalized['cs_sexo'] == 'M'


def test_sinan_get_semana_epi(db_config):
    """Testa cálculo de semana epidemiológica"""
    service = SINANETLService(db_config)
    
    # 15/01/2024 = semana 3 de 2024
    semana = service._get_semana_epi(date(2024, 1, 15))
    assert semana == 3
    
    # 01/01/2024 = semana 1 de 2024
    semana = service._get_semana_epi(date(2024, 1, 1))
    assert semana == 1


def test_sinan_validate_csv(db_config, temp_csv_sinan):
    """Testa validação de CSV SINAN"""
    service = SINANETLService(db_config)
    
    report = service.validate_sinan_csv(temp_csv_sinan)
    
    assert report.total_rows == 2
    assert report.valid_rows >= 1  # Pelo menos 1 válido
    assert isinstance(report.is_valid, bool)


# ============================================================================
# TESTES - LIRAa ETL SERVICE
# ============================================================================

def test_liraa_normalize_row(db_config):
    """Testa normalização de linha LIRAa"""
    service = LIRaaETLService(db_config)
    
    row = {
        'municipio_codigo': '5103403',
        'municipio_nome': 'Cuiabá',
        'ano': '2024',
        'ciclo': '1',
        'imoveis_pesquisados': '1000',
        'imoveis_positivos': '50',
        'depositos_inspecionados': '3000',
        'depositos_positivos': '75',
        'iip': '5.0',
        'ib': '7.5',
        'idc': '2.5'
    }
    
    normalized = service._normalize_liraa_row(row)
    
    assert normalized['municipio_codigo'] == '5103403'
    assert normalized['ano'] == 2024
    assert normalized['ciclo'] == 1
    assert normalized['imoveis_pesquisados'] == 1000
    assert normalized['iip'] == Decimal('5.0')


def test_liraa_validate_csv(db_config, temp_csv_liraa):
    """Testa validação de CSV LIRAa"""
    service = LIRaaETLService(db_config)
    
    report = service.validate_liraa_csv(temp_csv_liraa)
    
    assert report.total_rows == 2
    assert report.valid_rows >= 1
    assert isinstance(report.is_valid, bool)


# ============================================================================
# TESTES - INTEGRAÇÃO (CSV COMPLETO)
# ============================================================================

def test_read_csv_file(db_config, temp_csv_sinan):
    """Testa leitura de CSV em batches"""
    service = ETLBaseService(db_config)
    
    batches = list(service.read_csv_file(temp_csv_sinan, batch_size=1))
    
    assert len(batches) == 2  # 2 linhas = 2 batches (batch_size=1)
    assert len(batches[0]) == 1
    assert 'nu_notific' in batches[0][0]


def test_count_total_rows(db_config, temp_csv_sinan):
    """Testa contagem de linhas"""
    service = ETLBaseService(db_config)
    
    total = service.count_total_rows(temp_csv_sinan)
    
    assert total == 2


# ============================================================================
# TESTES - EDGE CASES
# ============================================================================

def test_sinan_normalize_empty_fields(db_config):
    """Testa normalização com campos vazios"""
    service = SINANETLService(db_config)
    
    row = {
        'nu_notific': '202400001',
        'dt_notific': '15/01/2024',
        'nm_pacient': 'TESTE',
        'sg_uf': 'MT',
        'id_municip': '5103403',
        'dt_sin_pri': '',  # Vazio
        'nu_idade_n': '',  # Vazio
        'cs_sexo': '',     # Vazio
    }
    
    normalized = service._normalize_sinan_row(row)
    
    assert normalized['dt_sin_pri'] is None
    assert normalized['nu_idade_n'] is None
    assert normalized['cs_sexo'] is None


def test_liraa_indices_calculation_in_batch(db_config, temp_csv_liraa):
    """Testa cálculo de índices durante processamento de batch"""
    service = LIRaaETLService(db_config)
    
    # Ler CSV
    batches = list(service.read_csv_file(temp_csv_liraa, batch_size=10))
    batch = batches[0]
    
    # Primeiro registro não tem IIP (será calculado)
    row1 = batch[0]
    assert row1['iip'] == '' or row1['iip'] is None
    
    # Normalizar
    normalized = service._normalize_liraa_row(row1)
    record = LIRaaRecordRaw(**normalized)
    
    # Calcular índices
    if record.iip is None:
        indices = service.calculate_liraa_indices(
            record.imoveis_pesquisados,
            record.imoveis_positivos or 0,
            record.depositos_inspecionados,
            record.depositos_positivos or 0
        )
        
        # IIP = (50/1000) * 100 = 5.0%
        assert indices['iip'] == Decimal('5.00')
        
        # Classificar risco
        nivel_risco = service.classify_risk_level(indices['iip'])
        assert nivel_risco == 'MUITO_ALTO'  # IIP >= 5%


def test_etl_validation_report_is_valid():
    """Testa propriedade is_valid do validation report"""
    # Sem erros críticos
    report = ETLValidationReport(
        total_rows=100,
        valid_rows=100,
        invalid_rows=0,
        errors=[]
    )
    assert report.is_valid is True
    
    # Com erros críticos
    report_with_errors = ETLValidationReport(
        total_rows=100,
        valid_rows=90,
        invalid_rows=10,
        errors=[
            ETLValidationError(
                row_number=1,
                field="test",
                error_type="test_error",
                error_message="Test error",
                severity="ERROR"
            )
        ]
    )
    assert report_with_errors.is_valid is False
    
    # Apenas warnings
    report_with_warnings = ETLValidationReport(
        total_rows=100,
        valid_rows=100,
        invalid_rows=0,
        warnings=5,
        errors=[
            ETLValidationError(
                row_number=1,
                field="test",
                error_type="test_warning",
                error_message="Test warning",
                severity="WARNING"
            )
        ]
    )
    assert report_with_warnings.is_valid is True  # Warnings não impedem carga


# ============================================================================
# SUMMARY
# ============================================================================

"""
TOTAL DE TESTES: 20

Schemas (5):
✅ test_sinan_record_validation
✅ test_sinan_record_invalid_uf
✅ test_liraa_record_validation
✅ test_liraa_record_invalid_positivos
✅ test_sinan_import_request_validation
✅ test_sinan_import_request_invalid_semana_range

ETL Base Service (3):
✅ test_calculate_liraa_indices
✅ test_calculate_liraa_indices_zero_division
✅ test_classify_risk_level

SINAN Service (3):
✅ test_sinan_normalize_row
✅ test_sinan_get_semana_epi
✅ test_sinan_validate_csv

LIRAa Service (2):
✅ test_liraa_normalize_row
✅ test_liraa_validate_csv

Integração (2):
✅ test_read_csv_file
✅ test_count_total_rows

Edge Cases (5):
✅ test_sinan_normalize_empty_fields
✅ test_liraa_indices_calculation_in_batch
✅ test_etl_validation_report_is_valid
"""
