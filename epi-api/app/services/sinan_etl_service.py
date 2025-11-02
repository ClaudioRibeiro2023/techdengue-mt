"""
Service ETL para importação SINAN
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import psycopg2
from psycopg2.extras import execute_batch

from app.services.etl_base_service import ETLBaseService
from app.schemas.etl import (
    SINANRecordRaw,
    SINANImportRequest,
    ETLValidationError,
    ETLValidationReport,
    ETLStatus,
    ETLSource,
    DoencaTipo,
    IndicadorEpiCreate
)


class SINANETLService(ETLBaseService):
    """Service para importação de dados SINAN"""
    
    # Mapeamento de classificação final SINAN
    CLASSIFICACAO_CONFIRMADO = [1, 5]  # Confirmado laboratorial, clínico-epidemiológico
    CLASSIFICACAO_DESCARTADO = [2]
    CLASSIFICACAO_SUSPEITO = [3]
    CLASSIFICACAO_GRAVE = [4]  # Dengue com sinais de alarme/grave
    
    # Mapeamento de evolução
    EVOLUCAO_OBITO = [2, 3]  # Óbito por dengue, óbito por outras causas
    
    # Colunas obrigatórias no CSV SINAN
    REQUIRED_COLUMNS = [
        'nu_notific',
        'dt_notific',
        'sg_uf',
        'id_municip',
        'nm_pacient'
    ]
    
    def validate_sinan_csv(self, file_path: str) -> ETLValidationReport:
        """
        Valida CSV SINAN
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            ETLValidationReport
        """
        # Validação estrutural
        report = self.validate_csv_structure(file_path, self.REQUIRED_COLUMNS)
        
        if not report.is_valid:
            return report
        
        # Validação de dados (sample)
        errors = []
        valid_count = 0
        
        try:
            # Ler primeiras 100 linhas para validação rápida
            batches = self.read_csv_file(file_path, batch_size=100)
            for batch in batches:
                for idx, row in enumerate(batch, start=1):
                    try:
                        # Tentar criar objeto Pydantic
                        SINANRecordRaw(**self._normalize_sinan_row(row))
                        valid_count += 1
                    except Exception as e:
                        errors.append(ETLValidationError(
                            row_number=idx,
                            field="record",
                            value=str(row),
                            error_type="validation_error",
                            error_message=str(e),
                            severity="ERROR"
                        ))
                break  # Apenas primeiro batch para validação
        except Exception as e:
            errors.append(ETLValidationError(
                row_number=0,
                field="file",
                value=str(e),
                error_type="read_error",
                error_message=f"Erro ao ler arquivo: {str(e)}",
                severity="ERROR"
            ))
        
        total_rows = self.count_total_rows(file_path)
        
        return ETLValidationReport(
            total_rows=total_rows,
            valid_rows=valid_count,
            invalid_rows=len(errors),
            errors=errors[:100]  # Limitar a 100 erros
        )
    
    def _normalize_sinan_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza linha do CSV SINAN para schema
        
        Args:
            row: Linha raw do CSV
            
        Returns:
            Dict normalizado
        """
        normalized = {}
        
        # Campos string
        str_fields = ['nu_notific', 'nm_pacient', 'sg_uf', 'id_municip', 
                      'nm_bairro', 'tp_diag', 'criterio', 'cs_sexo']
        for field in str_fields:
            normalized[field] = str(row.get(field, '')).strip() if row.get(field) else None
        
        # Campos date
        date_fields = ['dt_notific', 'dt_sin_pri', 'dt_nasc', 'dt_diag', 
                       'dt_encerra', 'dt_obito']
        for field in date_fields:
            value = row.get(field)
            if value and str(value).strip():
                try:
                    # Tentar formato DD/MM/YYYY
                    normalized[field] = datetime.strptime(str(value).strip(), '%d/%m/%Y').date()
                except:
                    try:
                        # Tentar formato YYYY-MM-DD
                        normalized[field] = datetime.strptime(str(value).strip(), '%Y-%m-%d').date()
                    except:
                        normalized[field] = None
            else:
                normalized[field] = None
        
        # Campos int
        int_fields = ['nu_idade_n', 'classi_fin', 'evolucao']
        for field in int_fields:
            value = row.get(field)
            if value and str(value).strip():
                try:
                    normalized[field] = int(float(str(value).strip()))
                except:
                    normalized[field] = None
            else:
                normalized[field] = None
        
        # Extra fields (demais colunas)
        extra = {}
        for key, value in row.items():
            if key not in normalized and value:
                extra[key] = str(value)
        normalized['extra_fields'] = extra
        
        return normalized
    
    def process_sinan_import(
        self,
        job_id: str,
        request: SINANImportRequest
    ) -> Dict[str, Any]:
        """
        Processa importação SINAN
        
        Args:
            job_id: ID do job
            request: Request de importação
            
        Returns:
            Dict com estatísticas do processamento
        """
        # Atualizar job para PROCESSING
        self.update_job_status(job_id, ETLStatus.PROCESSING)
        
        # Contar total de linhas
        total_rows = self.count_total_rows(request.file_path)
        
        conn = self._get_connection()
        try:
            # Atualizar total_rows no job
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE etl_jobs SET total_rows = %s WHERE job_id = %s",
                    (total_rows, job_id)
                )
            conn.commit()
            
            # Processar em batches
            processed = 0
            success = 0
            errors = []
            
            batches = self.read_csv_file(request.file_path, request.batch_size)
            
            for batch in batches:
                batch_result = self._process_sinan_batch(
                    batch,
                    request.doenca_tipo,
                    request.ano_epidemiologico,
                    request.overwrite,
                    conn
                )
                
                processed += batch_result['processed']
                success += batch_result['success']
                errors.extend(batch_result['errors'])
                
                # Atualizar progresso
                self.update_job_status(
                    job_id,
                    ETLStatus.PROCESSING,
                    processed_rows=processed,
                    success_rows=success,
                    error_rows=len(errors)
                )
            
            # Finalizar
            final_status = ETLStatus.COMPLETED if len(errors) == 0 else ETLStatus.PARTIAL
            
            self.update_job_status(
                job_id,
                final_status,
                processed_rows=processed,
                success_rows=success,
                error_rows=len(errors),
                error_details=errors[:100] if errors else None
            )
            
            return {
                'processed': processed,
                'success': success,
                'errors': len(errors),
                'status': final_status.value
            }
            
        except Exception as e:
            self.update_job_status(
                job_id,
                ETLStatus.FAILED,
                error_message=str(e)
            )
            raise
        finally:
            conn.close()
    
    def _process_sinan_batch(
        self,
        batch: List[Dict[str, Any]],
        doenca_tipo: DoencaTipo,
        ano: int,
        overwrite: bool,
        conn
    ) -> Dict[str, Any]:
        """
        Processa um batch de registros SINAN
        
        Args:
            batch: Lista de registros
            doenca_tipo: Tipo de doença
            ano: Ano epidemiológico
            overwrite: Sobrescrever existentes
            conn: Conexão DB
            
        Returns:
            Dict com estatísticas
        """
        processed = 0
        success = 0
        errors = []
        
        # Agregar por município + semana epidemiológica
        aggregated = {}
        
        for row in batch:
            processed += 1
            
            try:
                # Normalizar e validar
                normalized = self._normalize_sinan_row(row)
                record = SINANRecordRaw(**normalized)
                
                # Calcular semana epidemiológica
                dt_notific = record.dt_notific
                semana_epi = self._get_semana_epi(dt_notific)
                
                # Chave de agregação
                key = (record.id_municip, ano, semana_epi)
                
                if key not in aggregated:
                    aggregated[key] = {
                        'municipio_codigo': record.id_municip,
                        'ano': ano,
                        'semana_epi': semana_epi,
                        'casos_confirmados': 0,
                        'casos_suspeitos': 0,
                        'casos_graves': 0,
                        'obitos': 0
                    }
                
                # Classificar caso
                classi_fin = record.classi_fin
                if classi_fin in self.CLASSIFICACAO_CONFIRMADO:
                    aggregated[key]['casos_confirmados'] += 1
                elif classi_fin in self.CLASSIFICACAO_SUSPEITO:
                    aggregated[key]['casos_suspeitos'] += 1
                
                if classi_fin in self.CLASSIFICACAO_GRAVE:
                    aggregated[key]['casos_graves'] += 1
                
                if record.evolucao in self.EVOLUCAO_OBITO:
                    aggregated[key]['obitos'] += 1
                
                success += 1
                
            except Exception as e:
                errors.append({
                    'row': row,
                    'error': str(e)
                })
        
        # Inserir/atualizar agregados no banco
        if aggregated:
            self._upsert_indicadores(aggregated, doenca_tipo, overwrite, conn)
        
        return {
            'processed': processed,
            'success': success,
            'errors': errors
        }
    
    def _get_semana_epi(self, dt: date) -> int:
        """
        Calcula semana epidemiológica (ISO week)
        
        Args:
            dt: Data
            
        Returns:
            Semana epidemiológica (1-53)
        """
        return dt.isocalendar()[1]
    
    def _upsert_indicadores(
        self,
        aggregated: Dict,
        doenca_tipo: DoencaTipo,
        overwrite: bool,
        conn
    ) -> None:
        """
        Insere ou atualiza indicadores no banco
        
        Args:
            aggregated: Dados agregados
            doenca_tipo: Tipo de doença
            overwrite: Sobrescrever existentes
            conn: Conexão DB
        """
        with conn.cursor() as cur:
            for data in aggregated.values():
                if overwrite:
                    # UPSERT
                    cur.execute("""
                        INSERT INTO indicador_epi (
                            municipio_codigo, ano, semana_epi, doenca_tipo,
                            casos_confirmados, casos_suspeitos, casos_graves, obitos,
                            fonte, data_atualizacao
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (municipio_codigo, ano, semana_epi, doenca_tipo)
                        DO UPDATE SET
                            casos_confirmados = EXCLUDED.casos_confirmados,
                            casos_suspeitos = EXCLUDED.casos_suspeitos,
                            casos_graves = EXCLUDED.casos_graves,
                            obitos = EXCLUDED.obitos,
                            fonte = EXCLUDED.fonte,
                            data_atualizacao = EXCLUDED.data_atualizacao
                    """, (
                        data['municipio_codigo'],
                        data['ano'],
                        data['semana_epi'],
                        doenca_tipo.value,
                        data['casos_confirmados'],
                        data['casos_suspeitos'],
                        data['casos_graves'],
                        data['obitos'],
                        ETLSource.SINAN.value,
                        datetime.utcnow()
                    ))
                else:
                    # INSERT apenas se não existir
                    cur.execute("""
                        INSERT INTO indicador_epi (
                            municipio_codigo, ano, semana_epi, doenca_tipo,
                            casos_confirmados, casos_suspeitos, casos_graves, obitos,
                            fonte, data_atualizacao
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (municipio_codigo, ano, semana_epi, doenca_tipo) DO NOTHING
                    """, (
                        data['municipio_codigo'],
                        data['ano'],
                        data['semana_epi'],
                        doenca_tipo.value,
                        data['casos_confirmados'],
                        data['casos_suspeitos'],
                        data['casos_graves'],
                        data['obitos'],
                        ETLSource.SINAN.value,
                        datetime.utcnow()
                    ))
        
        conn.commit()
