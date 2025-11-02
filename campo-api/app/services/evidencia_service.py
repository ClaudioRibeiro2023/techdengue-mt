"""
Evidencia Service - Business logic for evidence management
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from app.schemas.evidencia import (
    EvidenciaCreate,
    EvidenciaResponse,
    EvidenciaList,
    EvidenciaStatus,
    EvidenciaTipo
)


class EvidenciaService:
    """Service for managing evidence/media"""
    
    def __init__(self, db_connection_string: str):
        """
        Initialize service with database connection.
        
        Args:
            db_connection_string: PostgreSQL connection string
        """
        self.conn_str = db_connection_string
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.conn_str)
    
    def _row_to_response(self, row: Dict[str, Any]) -> EvidenciaResponse:
        """Convert database row to EvidenciaResponse"""
        return EvidenciaResponse(
            id=row['id'],
            atividade_id=row['atividade_id'],
            tipo=row['tipo'],
            status=row['status'],
            hash_sha256=row['hash_sha256'],
            tamanho_bytes=row['tamanho_bytes'],
            url_s3=row['url_s3'],
            url_download=None,  # Will be set by router with presigned URL
            descricao=row.get('descricao'),
            metadata=row.get('metadata', {}),
            criado_em=row['criado_em'],
            atualizado_em=row['atualizado_em']
        )
    
    def create(
        self,
        evidencia: EvidenciaCreate
    ) -> EvidenciaResponse:
        """
        Create new evidence record after successful upload.
        
        Args:
            evidencia: Evidence data
            
        Returns:
            Created evidence
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Verify atividade exists
                cur.execute("SELECT id FROM atividade WHERE id = %s", (evidencia.atividade_id,))
                if not cur.fetchone():
                    raise ValueError(f"Atividade {evidencia.atividade_id} not found")
                
                cur.execute("""
                    INSERT INTO evidencia (
                        atividade_id, tipo, status, hash_sha256, tamanho_bytes,
                        url_s3, upload_id, descricao, metadata
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING *
                """, (
                    evidencia.atividade_id,
                    evidencia.tipo.value,
                    EvidenciaStatus.CONCLUIDA.value,  # Upload completed
                    evidencia.hash_sha256,
                    evidencia.tamanho_bytes,
                    evidencia.url_s3,
                    evidencia.upload_id,
                    evidencia.descricao,
                    psycopg2.extras.Json(evidencia.metadata or {})
                ))
                
                row = cur.fetchone()
                conn.commit()
                return self._row_to_response(row)
        finally:
            conn.close()
    
    def get_by_id(self, evidencia_id: int) -> Optional[EvidenciaResponse]:
        """
        Get evidence by ID.
        
        Args:
            evidencia_id: Evidence ID
            
        Returns:
            Evidence or None if not found
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM evidencia 
                    WHERE id = %s AND status != 'DELETADA'
                """, (evidencia_id,))
                row = cur.fetchone()
                return self._row_to_response(row) if row else None
        finally:
            conn.close()
    
    def list_by_atividade(
        self,
        atividade_id: int,
        tipo: Optional[List[str]] = None
    ) -> EvidenciaList:
        """
        List evidence for an activity.
        
        Args:
            atividade_id: Activity ID
            tipo: Filter by evidence type
            
        Returns:
            List of evidence
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build WHERE clause
                where_clauses = ["atividade_id = %s", "status != 'DELETADA'"]
                params = [atividade_id]
                
                if tipo and len(tipo) > 0:
                    where_clauses.append("tipo = ANY(%s::text[])")
                    params.append(tipo)
                
                where_sql = " AND ".join(where_clauses)
                
                # Get evidences
                cur.execute(f"""
                    SELECT * FROM evidencia
                    WHERE {where_sql}
                    ORDER BY criado_em DESC
                """, params)
                
                rows = cur.fetchall()
                items = [self._row_to_response(row) for row in rows]
                
                return EvidenciaList(
                    items=items,
                    total=len(items)
                )
        finally:
            conn.close()
    
    def delete(self, evidencia_id: int) -> bool:
        """
        Delete (soft delete) evidence.
        
        Args:
            evidencia_id: Evidence ID
            
        Returns:
            True if deleted, False if not found
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE evidencia
                    SET status = %s
                    WHERE id = %s AND status != 'DELETADA'
                """, (EvidenciaStatus.DELETADA.value, evidencia_id))
                
                affected = cur.rowcount
                conn.commit()
                return affected > 0
        finally:
            conn.close()
    
    def update_status(
        self,
        evidencia_id: int,
        status: EvidenciaStatus
    ) -> Optional[EvidenciaResponse]:
        """
        Update evidence status.
        
        Args:
            evidencia_id: Evidence ID
            status: New status
            
        Returns:
            Updated evidence or None if not found
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    UPDATE evidencia
                    SET status = %s
                    WHERE id = %s
                    RETURNING *
                """, (status.value, evidencia_id))
                
                row = cur.fetchone()
                if row:
                    conn.commit()
                    return self._row_to_response(row)
                return None
        finally:
            conn.close()
    
    def verify_upload(
        self,
        upload_id: str,
        expected_hash: str
    ) -> bool:
        """
        Verify if upload with given ID and hash exists.
        
        Args:
            upload_id: Upload ID from presigned URL
            expected_hash: Expected SHA-256 hash
            
        Returns:
            True if exists and matches, False otherwise
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) FROM evidencia
                    WHERE upload_id = %s AND hash_sha256 = %s
                """, (upload_id, expected_hash))
                
                count = cur.fetchone()[0]
                return count > 0
        finally:
            conn.close()
