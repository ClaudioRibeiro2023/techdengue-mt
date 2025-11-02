"""
Sync Service - Advanced synchronization with conflict resolution
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
import json

from app.schemas.sync import (
    SyncOperationRequest,
    SyncOperationResponse,
    SyncConflict,
    ConflictResolutionStrategy
)


class ConflictType(str, Enum):
    """Types of sync conflicts"""
    UPDATE_UPDATE = "update_update"  # Both client and server updated
    UPDATE_DELETE = "update_delete"  # Client updated, server deleted
    DELETE_UPDATE = "delete_update"  # Client deleted, server updated
    CREATE_CREATE = "create_create"  # Same ID created on both sides


class SyncService:
    """Service for advanced synchronization with conflict resolution"""
    
    def __init__(self, db_connection_string: str):
        """
        Initialize sync service.
        
        Args:
            db_connection_string: PostgreSQL connection string
        """
        self.conn_str = db_connection_string
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.conn_str)
    
    def sync_operations(
        self,
        operations: List[SyncOperationRequest],
        device_id: str,
        usuario: str
    ) -> SyncOperationResponse:
        """
        Process batch of sync operations with conflict detection.
        
        Args:
            operations: List of sync operations
            device_id: Unique device identifier
            usuario: Current user
            
        Returns:
            Sync response with success/conflicts/errors
        """
        conn = self._get_connection()
        successes = []
        conflicts = []
        errors = []
        
        try:
            for op in operations:
                try:
                    # Check for existing sync log (idempotency)
                    if self._is_operation_processed(conn, op.idempotency_key):
                        successes.append({
                            "entity_type": op.entity_type,
                            "entity_id": op.entity_id,
                            "operation": op.operation,
                            "status": "already_processed"
                        })
                        continue
                    
                    # Detect conflicts
                    conflict = self._detect_conflict(conn, op)
                    
                    if conflict:
                        # Handle conflict based on strategy
                        resolution = self._resolve_conflict(
                            conn, 
                            op, 
                            conflict, 
                            op.conflict_resolution_strategy
                        )
                        
                        if resolution["resolved"]:
                            successes.append(resolution["result"])
                        else:
                            conflicts.append(SyncConflict(
                                entity_type=op.entity_type,
                                entity_id=op.entity_id,
                                conflict_type=conflict["type"],
                                client_version=op.client_timestamp,
                                server_version=conflict["server_timestamp"],
                                client_data=op.data,
                                server_data=conflict["server_data"],
                                suggested_resolution=self._suggest_resolution(conflict)
                            ))
                    else:
                        # No conflict, apply operation
                        result = self._apply_operation(conn, op, usuario)
                        successes.append(result)
                        
                        # Log sync operation
                        self._log_sync_operation(conn, op, device_id, usuario, "success")
                    
                except Exception as e:
                    errors.append({
                        "entity_type": op.entity_type,
                        "entity_id": op.entity_id,
                        "operation": op.operation,
                        "error": str(e)
                    })
                    
                    # Log error
                    self._log_sync_operation(conn, op, device_id, usuario, "error", str(e))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
        
        return SyncOperationResponse(
            processed=len(operations),
            successes=successes,
            conflicts=conflicts,
            errors=errors,
            server_timestamp=datetime.utcnow()
        )
    
    def _is_operation_processed(
        self,
        conn,
        idempotency_key: str
    ) -> bool:
        """Check if operation already processed"""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM sync_log
                WHERE idempotency_key = %s
                AND status = 'success'
            """, (idempotency_key,))
            
            return cur.fetchone()[0] > 0
    
    def _detect_conflict(
        self,
        conn,
        op: SyncOperationRequest
    ) -> Optional[Dict[str, Any]]:
        """
        Detect if operation conflicts with server state.
        
        Returns:
            Conflict info dict or None if no conflict
        """
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if op.entity_type == "atividade":
                cur.execute("""
                    SELECT 
                        atualizado_em,
                        status,
                        descricao,
                        metadata
                    FROM atividade
                    WHERE id = %s
                """, (op.entity_id,))
            elif op.entity_type == "evidencia":
                cur.execute("""
                    SELECT 
                        atualizado_em,
                        status,
                        descricao,
                        metadata
                    FROM evidencia
                    WHERE id = %s
                """, (op.entity_id,))
            else:
                return None
            
            server_record = cur.fetchone()
            
            if not server_record:
                if op.operation in ["update", "delete"]:
                    # Client trying to update/delete non-existent record
                    return {
                        "type": ConflictType.UPDATE_DELETE if op.operation == "update" else ConflictType.DELETE_UPDATE,
                        "server_timestamp": None,
                        "server_data": None
                    }
                return None
            
            # Check if server version is newer
            server_timestamp = server_record['atualizado_em']
            client_timestamp = op.client_timestamp
            
            if server_timestamp > client_timestamp:
                # Server has newer version - potential conflict
                return {
                    "type": ConflictType.UPDATE_UPDATE,
                    "server_timestamp": server_timestamp,
                    "server_data": dict(server_record)
                }
            
            return None
    
    def _resolve_conflict(
        self,
        conn,
        op: SyncOperationRequest,
        conflict: Dict[str, Any],
        strategy: ConflictResolutionStrategy
    ) -> Dict[str, Any]:
        """
        Resolve conflict based on strategy.
        
        Returns:
            Dict with resolved=True/False and result
        """
        if strategy == ConflictResolutionStrategy.CLIENT_WINS:
            # Force client version
            result = self._apply_operation(conn, op, "system")
            return {"resolved": True, "result": result}
        
        elif strategy == ConflictResolutionStrategy.SERVER_WINS:
            # Keep server version, don't apply client changes
            return {
                "resolved": True,
                "result": {
                    "entity_type": op.entity_type,
                    "entity_id": op.entity_id,
                    "operation": "skipped",
                    "status": "server_wins"
                }
            }
        
        elif strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
            # Already handled by timestamp check
            if conflict["server_timestamp"] and conflict["server_timestamp"] > op.client_timestamp:
                return {"resolved": True, "result": {"status": "server_newer"}}
            else:
                result = self._apply_operation(conn, op, "system")
                return {"resolved": True, "result": result}
        
        elif strategy == ConflictResolutionStrategy.MERGE:
            # Attempt to merge changes
            merged = self._merge_data(
                conflict.get("server_data", {}),
                op.data or {}
            )
            
            # Apply merged data
            op.data = merged
            result = self._apply_operation(conn, op, "system")
            return {"resolved": True, "result": result}
        
        else:  # MANUAL
            # Cannot auto-resolve, return conflict
            return {"resolved": False}
    
    def _merge_data(
        self,
        server_data: Dict[str, Any],
        client_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge server and client data intelligently.
        
        Rules:
        - Non-conflicting fields: take client version
        - Conflicting fields: take newest (or client if same)
        - Arrays: merge unique items
        - Objects: recursive merge
        """
        merged = server_data.copy()
        
        for key, client_value in client_data.items():
            if key not in merged:
                # New field from client
                merged[key] = client_value
            else:
                server_value = merged[key]
                
                # Type-specific merge
                if isinstance(client_value, dict) and isinstance(server_value, dict):
                    # Recursive merge for nested objects
                    merged[key] = self._merge_data(server_value, client_value)
                elif isinstance(client_value, list) and isinstance(server_value, list):
                    # Merge arrays (unique items)
                    merged[key] = list(set(server_value + client_value))
                else:
                    # Scalar: take client value
                    merged[key] = client_value
        
        return merged
    
    def _suggest_resolution(
        self,
        conflict: Dict[str, Any]
    ) -> str:
        """Suggest resolution strategy for manual conflicts"""
        conflict_type = conflict["type"]
        
        if conflict_type == ConflictType.UPDATE_UPDATE:
            return "Both versions modified. Review changes and choose MERGE or CLIENT_WINS."
        elif conflict_type == ConflictType.UPDATE_DELETE:
            return "Client updated but server deleted. Choose CLIENT_WINS to restore or SERVER_WINS to keep deleted."
        elif conflict_type == ConflictType.DELETE_UPDATE:
            return "Client deleted but server updated. Choose CLIENT_WINS to delete or SERVER_WINS to keep."
        else:
            return "Manual review required."
    
    def _apply_operation(
        self,
        conn,
        op: SyncOperationRequest,
        usuario: str
    ) -> Dict[str, Any]:
        """Apply sync operation to database"""
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if op.entity_type == "atividade":
                if op.operation == "create":
                    return self._create_atividade(cur, op, usuario)
                elif op.operation == "update":
                    return self._update_atividade(cur, op, usuario)
                elif op.operation == "delete":
                    return self._delete_atividade(cur, op)
            
            elif op.entity_type == "evidencia":
                if op.operation == "create":
                    return self._create_evidencia(cur, op)
                elif op.operation == "update":
                    return self._update_evidencia(cur, op)
                elif op.operation == "delete":
                    return self._delete_evidencia(cur, op)
            
            raise ValueError(f"Unsupported entity type: {op.entity_type}")
    
    def _create_atividade(self, cur, op: SyncOperationRequest, usuario: str) -> Dict:
        """Create atividade from sync"""
        data = op.data or {}
        
        cur.execute("""
            INSERT INTO atividade (
                tipo, status, municipio_cod_ibge, descricao, metadata,
                usuario_criacao, criado_em, atualizado_em
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """, (
            data.get('tipo'),
            data.get('status', 'CRIADA'),
            data.get('municipio_cod_ibge'),
            data.get('descricao'),
            psycopg2.extras.Json(data.get('metadata', {})),
            usuario,
            op.client_timestamp,
            op.client_timestamp
        ))
        
        new_id = cur.fetchone()['id']
        
        return {
            "entity_type": "atividade",
            "entity_id": new_id,
            "operation": "create",
            "status": "success"
        }
    
    def _update_atividade(self, cur, op: SyncOperationRequest, usuario: str) -> Dict:
        """Update atividade from sync"""
        data = op.data or {}
        
        # Build dynamic UPDATE
        set_clauses = []
        params = []
        
        if 'status' in data:
            set_clauses.append("status = %s")
            params.append(data['status'])
        
        if 'descricao' in data:
            set_clauses.append("descricao = %s")
            params.append(data['descricao'])
        
        if 'metadata' in data:
            set_clauses.append("metadata = %s")
            params.append(psycopg2.extras.Json(data['metadata']))
        
        set_clauses.append("atualizado_em = %s")
        params.append(op.client_timestamp)
        
        params.append(op.entity_id)
        
        cur.execute(f"""
            UPDATE atividade
            SET {', '.join(set_clauses)}
            WHERE id = %s
        """, params)
        
        return {
            "entity_type": "atividade",
            "entity_id": op.entity_id,
            "operation": "update",
            "status": "success"
        }
    
    def _delete_atividade(self, cur, op: SyncOperationRequest) -> Dict:
        """Delete atividade from sync"""
        cur.execute("""
            UPDATE atividade
            SET status = 'CANCELADA'
            WHERE id = %s
        """, (op.entity_id,))
        
        return {
            "entity_type": "atividade",
            "entity_id": op.entity_id,
            "operation": "delete",
            "status": "success"
        }
    
    def _create_evidencia(self, cur, op: SyncOperationRequest) -> Dict:
        """Create evidencia from sync"""
        data = op.data or {}
        
        cur.execute("""
            INSERT INTO evidencia (
                atividade_id, tipo, status, hash_sha256, tamanho_bytes,
                url_s3, upload_id, descricao, metadata, criado_em
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """, (
            data.get('atividade_id'),
            data.get('tipo'),
            data.get('status', 'PENDENTE'),
            data.get('hash_sha256'),
            data.get('tamanho_bytes'),
            data.get('url_s3'),
            data.get('upload_id'),
            data.get('descricao'),
            psycopg2.extras.Json(data.get('metadata', {})),
            op.client_timestamp
        ))
        
        new_id = cur.fetchone()['id']
        
        return {
            "entity_type": "evidencia",
            "entity_id": new_id,
            "operation": "create",
            "status": "success"
        }
    
    def _update_evidencia(self, cur, op: SyncOperationRequest) -> Dict:
        """Update evidencia from sync"""
        data = op.data or {}
        
        set_clauses = []
        params = []
        
        if 'status' in data:
            set_clauses.append("status = %s")
            params.append(data['status'])
        
        if 'descricao' in data:
            set_clauses.append("descricao = %s")
            params.append(data['descricao'])
        
        set_clauses.append("atualizado_em = %s")
        params.append(op.client_timestamp)
        
        params.append(op.entity_id)
        
        cur.execute(f"""
            UPDATE evidencia
            SET {', '.join(set_clauses)}
            WHERE id = %s
        """, params)
        
        return {
            "entity_type": "evidencia",
            "entity_id": op.entity_id,
            "operation": "update",
            "status": "success"
        }
    
    def _delete_evidencia(self, cur, op: SyncOperationRequest) -> Dict:
        """Delete evidencia from sync"""
        cur.execute("""
            UPDATE evidencia
            SET status = 'DELETADA'
            WHERE id = %s
        """, (op.entity_id,))
        
        return {
            "entity_type": "evidencia",
            "entity_id": op.entity_id,
            "operation": "delete",
            "status": "success"
        }
    
    def _log_sync_operation(
        self,
        conn,
        op: SyncOperationRequest,
        device_id: str,
        usuario: str,
        status: str,
        error: Optional[str] = None
    ):
        """Log sync operation to sync_log table"""
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sync_log (
                    device_id,
                    usuario,
                    entity_type,
                    entity_id,
                    operation,
                    idempotency_key,
                    client_timestamp,
                    server_timestamp,
                    status,
                    error_message
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                device_id,
                usuario,
                op.entity_type,
                op.entity_id,
                op.operation,
                op.idempotency_key,
                op.client_timestamp,
                datetime.utcnow(),
                status,
                error
            ))
