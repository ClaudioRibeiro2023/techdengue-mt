"""
Sync Router - Advanced synchronization endpoints
"""
import os
from typing import List, Annotated
from fastapi import APIRouter, HTTPException, Header, status

from app.schemas.sync import (
    SyncOperationRequest,
    SyncOperationResponse,
    SyncBatchRequest
)
from app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["Sincronização"])

# Database connection
DB_CONN_STR = os.getenv(
    "DATABASE_URL",
    "postgresql://techdengue:techdengue@localhost:5432/techdengue"
).replace("postgresql+asyncpg://", "postgresql://")


@router.post("", response_model=SyncOperationResponse)
async def sync_batch(
    request: SyncBatchRequest,
    x_device_id: Annotated[str, Header()] = "unknown"
):
    """
    Sincronizar batch de operações com conflict resolution.
    
    **Funcionalidades:**
    - Batch de operações (create, update, delete)
    - Detecção automática de conflitos
    - Resolução configurável (client_wins, server_wins, merge, manual)
    - Idempotency via chave única
    - Logging completo de sincronização
    
    **Estratégias de Resolução:**
    
    1. **CLIENT_WINS**: Cliente sempre vence
       - Útil para: Dados coletados em campo (autoridade local)
       - Risco: Pode sobrescrever mudanças do servidor
    
    2. **SERVER_WINS**: Servidor sempre vence
       - Útil para: Dados administrativos (autoridade central)
       - Risco: Pode perder dados do cliente
    
    3. **LAST_WRITE_WINS**: Última escrita vence (timestamp)
       - Útil para: Cenários gerais
       - Risco: Depende de relógios sincronizados
    
    4. **MERGE**: Tentar merge inteligente
       - Útil para: Metadata e campos não-conflitantes
       - Risco: Pode gerar estados inconsistentes
    
    5. **MANUAL**: Retornar conflito para resolução manual
       - Útil para: Dados críticos
       - Risco: Requer intervenção do usuário
    
    **Request Body:**
    ```json
    {
      "operations": [
        {
          "entity_type": "atividade",
          "entity_id": 123,
          "operation": "update",
          "data": {
            "status": "CONCLUIDA",
            "descricao": "Atualizado offline"
          },
          "client_timestamp": "2024-01-15T14:30:00Z",
          "idempotency_key": "550e8400-e29b-41d4-a716-446655440000",
          "conflict_resolution_strategy": "last_write_wins"
        }
      ],
      "device_id": "android-abc123",
      "batch_id": "batch-001"
    }
    ```
    
    **Response:**
    ```json
    {
      "processed": 1,
      "successes": [
        {
          "entity_type": "atividade",
          "entity_id": 123,
          "operation": "update",
          "status": "success"
        }
      ],
      "conflicts": [],
      "errors": [],
      "server_timestamp": "2024-01-15T14:31:00Z"
    }
    ```
    
    **Conflitos:**
    ```json
    {
      "conflicts": [
        {
          "entity_type": "atividade",
          "entity_id": 123,
          "conflict_type": "update_update",
          "client_version": "2024-01-15T14:30:00Z",
          "server_version": "2024-01-15T14:30:30Z",
          "client_data": {...},
          "server_data": {...},
          "suggested_resolution": "Review changes and choose MERGE"
        }
      ]
    }
    ```
    
    **Tipos de Conflito:**
    - `update_update`: Cliente e servidor modificaram
    - `update_delete`: Cliente modificou, servidor deletou
    - `delete_update`: Cliente deletou, servidor modificou
    - `create_create`: Mesmo ID criado nos dois lados
    
    **Exemplo de Uso:**
    ```bash
    # Sync batch após trabalho offline
    curl -X POST "http://localhost:8001/api/sync" \\
      -H "Content-Type: application/json" \\
      -H "X-Device-ID: android-abc123" \\
      -d '{
        "operations": [
          {
            "entity_type": "atividade",
            "entity_id": 123,
            "operation": "update",
            "data": {"status": "CONCLUIDA"},
            "client_timestamp": "2024-01-15T14:30:00Z",
            "idempotency_key": "uuid-1",
            "conflict_resolution_strategy": "client_wins"
          }
        ],
        "batch_id": "batch-001"
      }'
    ```
    
    **Headers:**
    - `X-Device-ID`: Identificador único do dispositivo
    
    **Retorna:**
    - 200: Sync processado (pode ter conflitos)
    - 400: Request inválido
    - 500: Erro no servidor
    """
    sync_service = SyncService(DB_CONN_STR)
    
    try:
        # TODO: Get usuario from JWT token
        usuario = "sistema"  # Placeholder
        
        result = sync_service.sync_operations(
            operations=request.operations,
            device_id=x_device_id or request.device_id,
            usuario=usuario
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar sincronização: {str(e)}"
        )


@router.get("/status/{device_id}")
async def get_sync_status(device_id: str):
    """
    Obter status de sincronização de um dispositivo.
    
    **Retorna:**
    - Total de operações sincronizadas
    - Última sincronização
    - Operações pendentes (se houver)
    
    **Exemplo:**
    ```bash
    curl "http://localhost:8001/api/sync/status/android-abc123"
    ```
    
    **Response:**
    ```json
    {
      "device_id": "android-abc123",
      "total_synced": 150,
      "last_sync": "2024-01-15T14:30:00Z",
      "success_rate": 0.98,
      "pending_conflicts": 2
    }
    ```
    """
    sync_service = SyncService(DB_CONN_STR)
    conn = sync_service._get_connection()
    
    try:
        with conn.cursor() as cur:
            # Get sync stats
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    MAX(server_timestamp) as last_sync,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successes
                FROM sync_log
                WHERE device_id = %s
            """, (device_id,))
            
            row = cur.fetchone()
            
            if not row or row[0] == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dispositivo {device_id} não encontrado"
                )
            
            total, last_sync, successes = row
            success_rate = successes / total if total > 0 else 0
            
            return {
                "device_id": device_id,
                "total_synced": total,
                "last_sync": last_sync,
                "success_rate": success_rate,
                "pending_conflicts": 0  # TODO: Count actual conflicts
            }
    finally:
        conn.close()
