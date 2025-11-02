"""
Base Service para ETL - Funcionalidades comuns
"""
import csv
import io
import uuid
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
from decimal import Decimal
import psycopg2
from psycopg2.extras import execute_batch
import pandas as pd

from app.schemas.etl import (
    ETLValidationError,
    ETLValidationReport,
    ETLStatus,
    ETLSource,
    ETLJobStatus
)


class ETLBaseService:
    """Service base para ETL com funcionalidades comuns"""
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        Inicializa service ETL
        
        Args:
            db_config: Configuração do banco de dados
        """
        self.db_config = db_config
    
    def _get_connection(self):
        """Cria conexão com banco de dados"""
        return psycopg2.connect(**self.db_config)
    
    def create_job(
        self,
        source: ETLSource,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Cria um novo job ETL
        
        Args:
            source: Fonte dos dados (SINAN/LIRAa)
            file_path: Caminho do arquivo
            metadata: Metadata adicional
            
        Returns:
            job_id: ID do job criado
        """
        job_id = str(uuid.uuid4())
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO etl_jobs (
                        job_id, source, status, file_path,
                        started_at, updated_at, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    job_id,
                    source.value,
                    ETLStatus.PENDING.value,
                    file_path,
                    datetime.utcnow(),
                    datetime.utcnow(),
                    psycopg2.extras.Json(metadata or {})
                ))
            conn.commit()
            return job_id
        finally:
            conn.close()
    
    def update_job_status(
        self,
        job_id: str,
        status: ETLStatus,
        processed_rows: Optional[int] = None,
        success_rows: Optional[int] = None,
        error_rows: Optional[int] = None,
        error_message: Optional[str] = None,
        error_details: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Atualiza status de um job ETL
        
        Args:
            job_id: ID do job
            status: Novo status
            processed_rows: Linhas processadas
            success_rows: Linhas com sucesso
            error_rows: Linhas com erro
            error_message: Mensagem de erro
            error_details: Detalhes dos erros
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                completed_at = datetime.utcnow() if status in [
                    ETLStatus.COMPLETED, ETLStatus.FAILED, ETLStatus.PARTIAL
                ] else None
                
                cur.execute("""
                    UPDATE etl_jobs
                    SET status = %s,
                        updated_at = %s,
                        completed_at = %s,
                        processed_rows = COALESCE(%s, processed_rows),
                        success_rows = COALESCE(%s, success_rows),
                        error_rows = COALESCE(%s, error_rows),
                        error_message = COALESCE(%s, error_message),
                        error_details = COALESCE(%s, error_details)
                    WHERE job_id = %s
                """, (
                    status.value,
                    datetime.utcnow(),
                    completed_at,
                    processed_rows,
                    success_rows,
                    error_rows,
                    error_message,
                    psycopg2.extras.Json(error_details) if error_details else None,
                    job_id
                ))
            conn.commit()
        finally:
            conn.close()
    
    def get_job_status(self, job_id: str) -> Optional[ETLJobStatus]:
        """
        Obtém status de um job ETL
        
        Args:
            job_id: ID do job
            
        Returns:
            ETLJobStatus ou None se não encontrado
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT job_id, source, status, file_path,
                           started_at, updated_at, completed_at,
                           total_rows, processed_rows, success_rows, error_rows,
                           error_message, error_details, metadata
                    FROM etl_jobs
                    WHERE job_id = %s
                """, (job_id,))
                
                row = cur.fetchone()
                if not row:
                    return None
                
                return ETLJobStatus(
                    job_id=row[0],
                    source=ETLSource(row[1]),
                    status=ETLStatus(row[2]),
                    file_path=row[3],
                    started_at=row[4],
                    updated_at=row[5],
                    completed_at=row[6],
                    total_rows=row[7],
                    processed_rows=row[8],
                    success_rows=row[9],
                    error_rows=row[10],
                    error_message=row[11],
                    error_details=row[12],
                    metadata=row[13] or {}
                )
        finally:
            conn.close()
    
    def read_csv_file(
        self,
        file_path: str,
        batch_size: int = 500
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Lê arquivo CSV em batches
        
        Args:
            file_path: Caminho do arquivo (local ou S3)
            batch_size: Tamanho do batch
            
        Yields:
            List de dicts representando linhas do CSV
        """
        # Se for S3, baixar para temp (implementar depois)
        # Por enquanto, assumir arquivo local
        
        try:
            # Usar pandas para leitura robusta
            df = pd.read_csv(
                file_path,
                encoding='utf-8',
                dtype=str,  # Ler tudo como string inicialmente
                na_values=['', 'NA', 'N/A', 'null', 'NULL'],
                keep_default_na=False
            )
            
            # Converter para list of dicts
            records = df.to_dict('records')
            
            # Yield em batches
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                yield batch
                
        except Exception as e:
            raise ValueError(f"Erro ao ler CSV: {str(e)}")
    
    def validate_csv_structure(
        self,
        file_path: str,
        required_columns: List[str]
    ) -> ETLValidationReport:
        """
        Valida estrutura básica do CSV
        
        Args:
            file_path: Caminho do arquivo
            required_columns: Colunas obrigatórias
            
        Returns:
            ETLValidationReport
        """
        errors = []
        
        try:
            df = pd.read_csv(file_path, nrows=1)
            columns = df.columns.tolist()
            
            # Verificar colunas obrigatórias
            missing_columns = set(required_columns) - set(columns)
            if missing_columns:
                errors.append(ETLValidationError(
                    row_number=0,
                    field="columns",
                    value=list(missing_columns),
                    error_type="missing_columns",
                    error_message=f"Colunas obrigatórias faltando: {missing_columns}",
                    severity="ERROR"
                ))
            
            # Contar linhas
            df_full = pd.read_csv(file_path)
            total_rows = len(df_full)
            
            return ETLValidationReport(
                total_rows=total_rows,
                valid_rows=total_rows if not errors else 0,
                invalid_rows=total_rows if errors else 0,
                errors=errors
            )
            
        except Exception as e:
            errors.append(ETLValidationError(
                row_number=0,
                field="file",
                value=str(e),
                error_type="file_read_error",
                error_message=f"Erro ao ler arquivo: {str(e)}",
                severity="ERROR"
            ))
            
            return ETLValidationReport(
                total_rows=0,
                valid_rows=0,
                invalid_rows=0,
                errors=errors
            )
    
    def calculate_liraa_indices(
        self,
        imoveis_pesquisados: int,
        imoveis_positivos: int,
        depositos_inspecionados: int,
        depositos_positivos: int
    ) -> Dict[str, Decimal]:
        """
        Calcula índices LIRAa (IIP, IB, IDC)
        
        Args:
            imoveis_pesquisados: Total de imóveis pesquisados
            imoveis_positivos: Imóveis com larvas/pupas
            depositos_inspecionados: Total de depósitos inspecionados
            depositos_positivos: Depósitos com larvas/pupas
            
        Returns:
            Dict com IIP, IB, IDC
        """
        indices = {}
        
        # IIP = (Imóveis positivos / Imóveis pesquisados) * 100
        if imoveis_pesquisados > 0:
            iip = Decimal(imoveis_positivos) / Decimal(imoveis_pesquisados) * 100
            indices['iip'] = round(iip, 2)
        else:
            indices['iip'] = Decimal('0.00')
        
        # IB = (Depósitos positivos / Imóveis pesquisados) * 100
        if imoveis_pesquisados > 0:
            ib = Decimal(depositos_positivos) / Decimal(imoveis_pesquisados) * 100
            indices['ib'] = round(ib, 2)
        else:
            indices['ib'] = Decimal('0.00')
        
        # IDC = (Depósitos positivos / Depósitos inspecionados) * 100
        if depositos_inspecionados > 0:
            idc = Decimal(depositos_positivos) / Decimal(depositos_inspecionados) * 100
            indices['idc'] = round(idc, 2)
        else:
            indices['idc'] = Decimal('0.00')
        
        return indices
    
    def classify_risk_level(self, iip: Decimal) -> str:
        """
        Classifica nível de risco baseado no IIP
        
        Args:
            iip: Índice de Infestação Predial
            
        Returns:
            Nível de risco (BAIXO, MEDIO, ALTO, MUITO_ALTO)
        """
        if iip < Decimal('1.0'):
            return 'BAIXO'
        elif iip < Decimal('3.9'):
            return 'MEDIO'
        elif iip < Decimal('5.0'):
            return 'ALTO'
        else:
            return 'MUITO_ALTO'
    
    def count_total_rows(self, file_path: str) -> int:
        """
        Conta total de linhas no CSV (excluindo header)
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Total de linhas
        """
        try:
            df = pd.read_csv(file_path)
            return len(df)
        except Exception:
            return 0
