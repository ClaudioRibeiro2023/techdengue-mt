"""
Atividade Service - Business logic for field activities
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from app.schemas.atividade import (
    AtividadeCreate,
    AtividadeUpdate,
    AtividadeResponse,
    AtividadeList,
    AtividadeStatus,
    AtividadeStats,
    GeoPoint
)


class AtividadeService:
    """Service for managing field activities"""
    
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
    
    def _row_to_response(self, row: Dict[str, Any]) -> AtividadeResponse:
        """Convert database row to AtividadeResponse"""
        # Build GeoPoint if coordinates exist
        localizacao = None
        if row.get('localizacao_lon') and row.get('localizacao_lat'):
            coords = [row['localizacao_lon'], row['localizacao_lat']]
            if row.get('localizacao_alt'):
                coords.append(row['localizacao_alt'])
            localizacao = GeoPoint(coordinates=coords)
        
        return AtividadeResponse(
            id=row['id'],
            tipo=row['tipo'],
            status=row['status'],
            origem=row['origem'],
            municipio_cod_ibge=row['municipio_cod_ibge'],
            localizacao=localizacao,
            descricao=row.get('descricao'),
            metadata=row.get('metadata', {}),
            criado_em=row['criado_em'],
            iniciado_em=row.get('iniciado_em'),
            encerrado_em=row.get('encerrado_em'),
            usuario_criacao=row.get('usuario_criacao'),
            usuario_responsavel=row.get('usuario_responsavel')
        )
    
    def create(self, atividade: AtividadeCreate, usuario: Optional[str] = None) -> AtividadeResponse:
        """
        Create a new activity.
        
        Args:
            atividade: Activity data
            usuario: Username of creator
            
        Returns:
            Created activity
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Extract coordinates if location provided
                lon, lat, alt = None, None, None
                if atividade.localizacao:
                    lon = atividade.localizacao.coordinates[0]
                    lat = atividade.localizacao.coordinates[1]
                    if len(atividade.localizacao.coordinates) > 2:
                        alt = atividade.localizacao.coordinates[2]
                
                cur.execute("""
                    INSERT INTO atividade (
                        tipo, status, origem, municipio_cod_ibge,
                        localizacao_lon, localizacao_lat, localizacao_alt,
                        descricao, metadata, usuario_criacao, usuario_responsavel
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING *
                """, (
                    atividade.tipo.value,
                    AtividadeStatus.CRIADA.value,
                    atividade.origem.value,
                    atividade.municipio_cod_ibge,
                    lon, lat, alt,
                    atividade.descricao,
                    psycopg2.extras.Json(atividade.metadata or {}),
                    usuario,
                    usuario
                ))
                
                row = cur.fetchone()
                conn.commit()
                return self._row_to_response(row)
        finally:
            conn.close()
    
    def get_by_id(self, atividade_id: int) -> Optional[AtividadeResponse]:
        """
        Get activity by ID.
        
        Args:
            atividade_id: Activity ID
            
        Returns:
            Activity or None if not found
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM atividade WHERE id = %s", (atividade_id,))
                row = cur.fetchone()
                return self._row_to_response(row) if row else None
        finally:
            conn.close()
    
    def list(
        self,
        status: Optional[List[str]] = None,
        tipo: Optional[List[str]] = None,
        municipio: Optional[str] = None,
        usuario: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> AtividadeList:
        """
        List activities with filters and pagination.
        
        Args:
            status: Filter by status (CRIADA, EM_ANDAMENTO, etc)
            tipo: Filter by type
            municipio: Filter by municipality IBGE code
            usuario: Filter by user
            page: Page number (1-indexed)
            page_size: Items per page
            
        Returns:
            Paginated list of activities
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build WHERE clause
                where_clauses = []
                params = []
                
                if status and len(status) > 0:
                    where_clauses.append(f"status = ANY(%s::text[])")
                    params.append(status)
                
                if tipo and len(tipo) > 0:
                    where_clauses.append(f"tipo = ANY(%s::text[])")
                    params.append(tipo)
                
                if municipio:
                    where_clauses.append("municipio_cod_ibge = %s")
                    params.append(municipio)
                
                if usuario:
                    where_clauses.append(
                        "(usuario_criacao = %s OR usuario_responsavel = %s)"
                    )
                    params.extend([usuario, usuario])
                
                where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                # Count total
                cur.execute(f"SELECT COUNT(*) as total FROM atividade {where_sql}", params)
                total = cur.fetchone()['total']
                
                # Get page
                offset = (page - 1) * page_size
                params.extend([page_size, offset])
                
                cur.execute(f"""
                    SELECT * FROM atividade
                    {where_sql}
                    ORDER BY criado_em DESC
                    LIMIT %s OFFSET %s
                """, params)
                
                rows = cur.fetchall()
                items = [self._row_to_response(row) for row in rows]
                
                return AtividadeList(
                    items=items,
                    total=total,
                    page=page,
                    page_size=page_size
                )
        finally:
            conn.close()
    
    def update(
        self,
        atividade_id: int,
        update_data: AtividadeUpdate,
        usuario: Optional[str] = None
    ) -> Optional[AtividadeResponse]:
        """
        Update activity.
        
        Args:
            atividade_id: Activity ID
            update_data: Fields to update
            usuario: Username performing update
            
        Returns:
            Updated activity or None if not found
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if exists
                cur.execute("SELECT * FROM atividade WHERE id = %s", (atividade_id,))
                if not cur.fetchone():
                    return None
                
                # Build UPDATE SET clause
                set_clauses = []
                params = []
                
                if update_data.status is not None:
                    set_clauses.append("status = %s")
                    params.append(update_data.status.value)
                    
                    # Auto-set timestamps based on status transitions
                    if update_data.status == AtividadeStatus.EM_ANDAMENTO:
                        set_clauses.append("iniciado_em = COALESCE(iniciado_em, now())")
                    elif update_data.status in [AtividadeStatus.CONCLUIDA, AtividadeStatus.CANCELADA]:
                        set_clauses.append("encerrado_em = COALESCE(encerrado_em, now())")
                
                if update_data.descricao is not None:
                    set_clauses.append("descricao = %s")
                    params.append(update_data.descricao)
                
                if update_data.localizacao is not None:
                    lon = update_data.localizacao.coordinates[0]
                    lat = update_data.localizacao.coordinates[1]
                    alt = update_data.localizacao.coordinates[2] if len(update_data.localizacao.coordinates) > 2 else None
                    
                    set_clauses.extend([
                        "localizacao_lon = %s",
                        "localizacao_lat = %s",
                        "localizacao_alt = %s"
                    ])
                    params.extend([lon, lat, alt])
                
                if update_data.metadata is not None:
                    set_clauses.append("metadata = %s")
                    params.append(psycopg2.extras.Json(update_data.metadata))
                
                if not set_clauses:
                    # No changes, return current
                    return self.get_by_id(atividade_id)
                
                # Add ID to params
                params.append(atividade_id)
                
                set_sql = ", ".join(set_clauses)
                cur.execute(f"""
                    UPDATE atividade
                    SET {set_sql}
                    WHERE id = %s
                    RETURNING *
                """, params)
                
                row = cur.fetchone()
                conn.commit()
                return self._row_to_response(row)
        finally:
            conn.close()
    
    def delete(self, atividade_id: int) -> bool:
        """
        Delete (cancel) activity.
        
        Args:
            atividade_id: Activity ID
            
        Returns:
            True if deleted, False if not found
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Soft delete: set status to CANCELADA
                cur.execute("""
                    UPDATE atividade
                    SET status = %s, encerrado_em = COALESCE(encerrado_em, now())
                    WHERE id = %s
                """, (AtividadeStatus.CANCELADA.value, atividade_id))
                
                affected = cur.rowcount
                conn.commit()
                return affected > 0
        finally:
            conn.close()
    
    def get_stats(
        self,
        municipio: Optional[str] = None,
        usuario: Optional[str] = None
    ) -> AtividadeStats:
        """
        Get activity statistics.
        
        Args:
            municipio: Filter by municipality
            usuario: Filter by user
            
        Returns:
            Activity statistics
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build WHERE clause
                where_clauses = []
                params = []
                
                if municipio:
                    where_clauses.append("municipio_cod_ibge = %s")
                    params.append(municipio)
                
                if usuario:
                    where_clauses.append(
                        "(usuario_criacao = %s OR usuario_responsavel = %s)"
                    )
                    params.extend([usuario, usuario])
                
                where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                # Total count
                cur.execute(f"SELECT COUNT(*) as total FROM atividade {where_sql}", params)
                total = cur.fetchone()['total']
                
                # By status
                cur.execute(f"""
                    SELECT status, COUNT(*) as count
                    FROM atividade
                    {where_sql}
                    GROUP BY status
                """, params)
                por_status = {row['status']: row['count'] for row in cur.fetchall()}
                
                # By type
                cur.execute(f"""
                    SELECT tipo, COUNT(*) as count
                    FROM atividade
                    {where_sql}
                    GROUP BY tipo
                """, params)
                por_tipo = {row['tipo']: row['count'] for row in cur.fetchall()}
                
                # By municipality
                cur.execute(f"""
                    SELECT municipio_cod_ibge, COUNT(*) as count
                    FROM atividade
                    {where_sql}
                    GROUP BY municipio_cod_ibge
                """, params)
                por_municipio = {row['municipio_cod_ibge']: row['count'] for row in cur.fetchall()}
                
                return AtividadeStats(
                    total=total,
                    por_status=por_status,
                    por_tipo=por_tipo,
                    por_municipio=por_municipio
                )
        finally:
            conn.close()
