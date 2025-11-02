"""
Sync - Schemas for offline synchronization
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from app.schemas.atividade import AtividadeCreate, AtividadeUpdate
from app.schemas.evidencia import EvidenciaCreate


class SyncOperationType(str, Enum):
    """Types of sync operations"""
    CREATE_ATIVIDADE = "CREATE_ATIVIDADE"
    UPDATE_ATIVIDADE = "UPDATE_ATIVIDADE"
    CREATE_EVIDENCIA = "CREATE_EVIDENCIA"
    DELETE_EVIDENCIA = "DELETE_EVIDENCIA"


class SyncOperation(BaseModel):
    """Single sync operation from client"""
    idempotency_key: str = Field(
        ..., 
        min_length=36,
        max_length=36,
        description="UUID v4 for idempotency"
    )
    operation_type: SyncOperationType
    timestamp: datetime = Field(..., description="Client timestamp when operation was created")
    payload: Dict[str, Any] = Field(..., description="Operation data")


class SyncBatch(BaseModel):
    """Batch of operations to sync"""
    operations: List[SyncOperation] = Field(..., min_items=1, max_items=100)
    device_id: str = Field(..., description="Unique device identifier")
    client_version: str = Field(..., description="Client app version")


class SyncResult(BaseModel):
    """Result of a single sync operation"""
    idempotency_key: str
    success: bool
    message: Optional[str] = None
    resource_id: Optional[int] = None  # ID of created/updated resource
    conflict: bool = Field(default=False, description="Indicates a conflict was detected")


class SyncBatchResponse(BaseModel):
    """Response for sync batch"""
    results: List[SyncResult]
    total_operations: int
    successful: int
    failed: int
    conflicts: int
    server_timestamp: datetime


class SyncLog(BaseModel):
    """Log entry for sync operation"""
    id: int
    device_id: str
    idempotency_key: str
    operation_type: SyncOperationType
    success: bool
    conflict: bool
    error_message: Optional[str] = None
    criado_em: datetime
    
    model_config = SettingsConfigDict(from_attributes=True)


class ConflictResolution(str, Enum):
    """Conflict resolution strategies"""
    LWW = "LAST_WRITE_WINS"  # Server timestamp wins
    CLIENT_WINS = "CLIENT_WINS"
    SERVER_WINS = "SERVER_WINS"
    MANUAL = "MANUAL"


class SyncStats(BaseModel):
    """Statistics for sync operations"""
    total_syncs: int
    successful_syncs: int
    failed_syncs: int
    total_conflicts: int
    last_sync: Optional[datetime] = None
    pending_operations: int = 0
