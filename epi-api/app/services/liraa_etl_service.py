"""
Service ETL para importação LIRAa
"""
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal
import psycopg2

from app.services.etl_base_service import ETLBaseService
from app.schemas.etl import (
    LIRaaRecordRaw,
    LIRaaImportRequest,
    ETLValidationError,
    ETLValidationReport,
    ETLStatus,
    ETLSource,
    RiscoNivel
)


class LIRaaETLService(ETLBaseService):
    """Service para importação de dados LIRAa"""
    
    # Colunas obrigatórias no CSV LIRAa
    REQUIRED_COLUMNS = [
        'municipio_codigo',
        'municipio_nome',
        'ano',
        'ciclo',
        'imoveis_pesquisados',
        'depositos_inspecionados'
    ]
    
    def validate_liraa_csv(self, file_path: str) -> ETLValidationReport:
        """
        Valida CSV LIRAa
        
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
            # Ler primeiras 100 linhas
            batches = self.read_csv_file(file_path, batch_size=100)
            for batch in batches:
                for idx, row in enumerate(batch, start=1):
                    try:
                        # Tentar criar objeto Pydantic
                        LIRaaRecordRaw(**self._normalize_liraa_row(row))
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
                break  # Apenas primeiro batch
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
            errors=errors[:100]
        )
    
    def _normalize_liraa_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza linha do CSV LIRAa para schema
        
        Args:
            row: Linha raw do CSV
            
        Returns:
            Dict normalizado
        """
        normalized = {}
        
        # Campos string
        str_fields = ['municipio_codigo', 'municipio_nome', 'estrato', 'zona', 
                      'responsavel', 'observacoes']
        for field in str_fields:
            value = row.get(field)
            normalized[field] = str(value).strip() if value else None
        
        # Campos int
        int_fields = [
            'ano', 'ciclo',
            'imoveis_pesquisados', 'imoveis_positivos', 
            'imoveis_fechados', 'imoveis_recusados',
            'depositos_inspecionados', 'depositos_positivos',
            'depositos_a1', 'depositos_a2', 'depositos_b', 'depositos_c',
            'depositos_d1', 'depositos_d2', 'depositos_e'
        ]
        for field in int_fields:
            value = row.get(field)
            if value and str(value).strip():
                try:
                    normalized[field] = int(float(str(value).strip()))
                except:
                    normalized[field] = 0 if field.startswith('depositos_') or field.startswith('imoveis_') else None
            else:
                normalized[field] = 0 if field.startswith('depositos_') or field.startswith('imoveis_') else None
        
        # Campos Decimal (índices)
        decimal_fields = ['iip', 'ib', 'idc']
        for field in decimal_fields:
            value = row.get(field)
            if value and str(value).strip():
                try:
                    normalized[field] = Decimal(str(value).strip())
                except:
                    normalized[field] = None
            else:
                normalized[field] = None
        
        # Data do levantamento
        value = row.get('data_levantamento')
        if value and str(value).strip():
            try:
                normalized['data_levantamento'] = datetime.strptime(
                    str(value).strip(), '%d/%m/%Y'
                ).date()
            except:
                try:
                    normalized['data_levantamento'] = datetime.strptime(
                        str(value).strip(), '%Y-%m-%d'
                    ).date()
                except:
                    normalized['data_levantamento'] = None
        else:
            normalized['data_levantamento'] = None
        
        return normalized
    
    def process_liraa_import(
        self,
        job_id: str,
        request: LIRaaImportRequest
    ) -> Dict[str, Any]:
        """
        Processa importação LIRAa
        
        Args:
            job_id: ID do job
            request: Request de importação
            
        Returns:
            Dict com estatísticas
        """
        # Atualizar job para PROCESSING
        self.update_job_status(job_id, ETLStatus.PROCESSING)
        
        # Contar total de linhas
        total_rows = self.count_total_rows(request.file_path)
        
        conn = self._get_connection()
        try:
            # Atualizar total_rows
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
                batch_result = self._process_liraa_batch(
                    batch,
                    request.ano,
                    request.ciclo,
                    request.calcular_indices,
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
    
    def _process_liraa_batch(
        self,
        batch: List[Dict[str, Any]],
        ano: int,
        ciclo: int,
        calcular_indices: bool,
        overwrite: bool,
        conn
    ) -> Dict[str, Any]:
        """
        Processa um batch de registros LIRAa
        
        Args:
            batch: Lista de registros
            ano: Ano do levantamento
            ciclo: Ciclo LIRAa
            calcular_indices: Calcular índices se não fornecidos
            overwrite: Sobrescrever existentes
            conn: Conexão DB
            
        Returns:
            Dict com estatísticas
        """
        processed = 0
        success = 0
        errors = []
        
        records_to_insert = []
        
        for row in batch:
            processed += 1
            
            try:
                # Normalizar e validar
                normalized = self._normalize_liraa_row(row)
                record = LIRaaRecordRaw(**normalized)
                
                # Calcular índices se necessário
                if calcular_indices and (
                    record.iip is None or 
                    record.ib is None or 
                    record.idc is None
                ):
                    indices = self.calculate_liraa_indices(
                        record.imoveis_pesquisados,
                        record.imoveis_positivos or 0,
                        record.depositos_inspecionados,
                        record.depositos_positivos or 0
                    )
                    
                    iip = indices['iip']
                    ib = indices['ib']
                    idc = indices['idc']
                else:
                    iip = record.iip
                    ib = record.ib
                    idc = record.idc
                
                # Classificar nível de risco
                nivel_risco = self.classify_risk_level(iip) if iip else None
                
                # Preparar para inserção
                records_to_insert.append({
                    'municipio_codigo': record.municipio_codigo,
                    'ano': ano,
                    'ciclo': ciclo,
                    'estrato': record.estrato,
                    'imoveis_pesquisados': record.imoveis_pesquisados,
                    'imoveis_positivos': record.imoveis_positivos or 0,
                    'depositos_inspecionados': record.depositos_inspecionados,
                    'depositos_positivos': record.depositos_positivos or 0,
                    'iip': iip,
                    'ib': ib,
                    'idc': idc,
                    'nivel_risco': nivel_risco
                })
                
                success += 1
                
            except Exception as e:
                errors.append({
                    'row': row,
                    'error': str(e)
                })
        
        # Inserir registros no banco
        if records_to_insert:
            self._upsert_liraa_data(records_to_insert, overwrite, conn)
        
        return {
            'processed': processed,
            'success': success,
            'errors': errors
        }
    
    def _upsert_liraa_data(
        self,
        records: List[Dict[str, Any]],
        overwrite: bool,
        conn
    ) -> None:
        """
        Insere ou atualiza dados LIRAa no banco
        
        Args:
            records: Lista de registros
            overwrite: Sobrescrever existentes
            conn: Conexão DB
        """
        with conn.cursor() as cur:
            for record in records:
                # Calcular semana epidemiológica média do ciclo
                # Ciclo 1: ~semana 1-9, Ciclo 2: ~semana 10-17, etc
                semana_epi = (record['ciclo'] - 1) * 9 + 5  # Semana média do ciclo
                
                if overwrite:
                    # UPSERT em indicador_epi
                    cur.execute("""
                        INSERT INTO indicador_epi (
                            municipio_codigo, ano, semana_epi, doenca_tipo,
                            iip, ib, idc, nivel_risco,
                            fonte, data_atualizacao, metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (municipio_codigo, ano, semana_epi, doenca_tipo)
                        DO UPDATE SET
                            iip = EXCLUDED.iip,
                            ib = EXCLUDED.ib,
                            idc = EXCLUDED.idc,
                            nivel_risco = EXCLUDED.nivel_risco,
                            fonte = EXCLUDED.fonte,
                            data_atualizacao = EXCLUDED.data_atualizacao,
                            metadata = EXCLUDED.metadata
                    """, (
                        record['municipio_codigo'],
                        record['ano'],
                        semana_epi,
                        'DENGUE',  # LIRAa é específico para Dengue
                        record['iip'],
                        record['ib'],
                        record['idc'],
                        record['nivel_risco'],
                        ETLSource.LIRAA.value,
                        datetime.utcnow(),
                        psycopg2.extras.Json({
                            'ciclo': record['ciclo'],
                            'estrato': record['estrato'],
                            'imoveis_pesquisados': record['imoveis_pesquisados'],
                            'imoveis_positivos': record['imoveis_positivos']
                        })
                    ))
                else:
                    # INSERT apenas se não existir
                    cur.execute("""
                        INSERT INTO indicador_epi (
                            municipio_codigo, ano, semana_epi, doenca_tipo,
                            iip, ib, idc, nivel_risco,
                            fonte, data_atualizacao, metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (municipio_codigo, ano, semana_epi, doenca_tipo) DO NOTHING
                    """, (
                        record['municipio_codigo'],
                        record['ano'],
                        semana_epi,
                        'DENGUE',
                        record['iip'],
                        record['ib'],
                        record['idc'],
                        record['nivel_risco'],
                        ETLSource.LIRAA.value,
                        datetime.utcnow(),
                        psycopg2.extras.Json({
                            'ciclo': record['ciclo'],
                            'estrato': record['estrato'],
                            'imoveis_pesquisados': record['imoveis_pesquisados'],
                            'imoveis_positivos': record['imoveis_positivos']
                        })
                    ))
        
        conn.commit()
