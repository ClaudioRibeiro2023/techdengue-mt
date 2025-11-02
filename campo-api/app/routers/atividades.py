"""
Atividades Router - CRUD endpoints for field activities
"""
import os
from typing import List, Optional, Annotated
from fastapi import APIRouter, HTTPException, Query, Path, status

from app.schemas.atividade import (
    AtividadeCreate,
    AtividadeUpdate,
    AtividadeResponse,
    AtividadeList,
    AtividadeStats,
    AtividadeStatus
)
from app.services.atividade_service import AtividadeService

router = APIRouter(prefix="/atividades", tags=["Atividades"])

# Database connection (TODO: move to dependency injection)
DB_CONN_STR = os.getenv(
    "DATABASE_URL",
    "postgresql://techdengue:techdengue@localhost:5432/techdengue"
).replace("postgresql+asyncpg://", "postgresql://")


@router.post("", response_model=AtividadeResponse, status_code=status.HTTP_201_CREATED)
async def create_atividade(
    atividade: AtividadeCreate,
    # usuario: Annotated[str, Depends(get_current_user)] = None  # TODO: Add auth
):
    """
    Criar nova atividade de campo.
    
    **Tipos disponíveis:**
    - VISTORIA: Vistoria domiciliar
    - LIRAA: Levantamento de Índice Rápido de Aedes aegypti
    - NEBULIZACAO: Nebulização/fumacê
    - ARMADILHA: Instalação/manutenção de armadilhas
    - PESQUISA_LARVARIA: Pesquisa larvária
    - EDUCACAO: Educação em saúde
    - BLOQUEIO: Bloqueio de transmissão
    - OUTROS: Outros tipos
    
    **Fluxo:**
    1. Atividade criada com status CRIADA
    2. Pode ser atualizada para EM_ANDAMENTO
    3. Finalizada com CONCLUIDA ou CANCELADA
    
    **Exemplo:**
    ```bash
    curl -X POST "http://localhost:8001/api/atividades" \\
      -H "Content-Type: application/json" \\
      -d '{
        "tipo": "VISTORIA",
        "municipio_cod_ibge": "5103403",
        "localizacao": {
          "type": "Point",
          "coordinates": [-56.0967, -15.6014]
        },
        "descricao": "Vistoria em área de risco",
        "metadata": {"setor": "A1"}
      }'
    ```
    """
    service = AtividadeService(DB_CONN_STR)
    
    try:
        # TODO: Get usuario from JWT token
        usuario = "sistema"  # Placeholder
        return service.create(atividade, usuario)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar atividade: {str(e)}"
        )


@router.get("", response_model=AtividadeList)
async def list_atividades(
    status_filter: Annotated[Optional[List[str]], Query(alias="status")] = [],
    tipo: Annotated[Optional[List[str]], Query()] = [],
    municipio: Annotated[Optional[str], Query(min_length=7, max_length=7)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50
):
    """
    Listar atividades com filtros e paginação.
    
    **Filtros disponíveis:**
    - `status`: Lista de status (CRIADA, EM_ANDAMENTO, CONCLUIDA, CANCELADA)
    - `tipo`: Lista de tipos de atividade
    - `municipio`: Código IBGE do município (7 dígitos)
    - `page`: Número da página (padrão: 1)
    - `page_size`: Itens por página (padrão: 50, max: 100)
    
    **Exemplos:**
    ```bash
    # Todas atividades
    curl "http://localhost:8001/api/atividades"
    
    # Apenas em andamento
    curl "http://localhost:8001/api/atividades?status=EM_ANDAMENTO"
    
    # Vistorias em Cuiabá
    curl "http://localhost:8001/api/atividades?tipo=VISTORIA&municipio=5103403"
    
    # Página 2 com 20 itens
    curl "http://localhost:8001/api/atividades?page=2&page_size=20"
    ```
    
    **Retorna:**
    ```json
    {
      "items": [...],
      "total": 150,
      "page": 1,
      "page_size": 50
    }
    ```
    """
    service = AtividadeService(DB_CONN_STR)
    
    try:
        # TODO: Filter by usuario based on role
        return service.list(
            status=status_filter,
            tipo=tipo,
            municipio=municipio,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar atividades: {str(e)}"
        )


@router.get("/{atividade_id}", response_model=AtividadeResponse)
async def get_atividade(
    atividade_id: Annotated[int, Path(gt=0, description="ID da atividade")]
):
    """
    Obter detalhes de uma atividade específica.
    
    **Exemplo:**
    ```bash
    curl "http://localhost:8001/api/atividades/123"
    ```
    
    **Retorna:**
    - 200: Detalhes da atividade
    - 404: Atividade não encontrada
    """
    service = AtividadeService(DB_CONN_STR)
    
    atividade = service.get_by_id(atividade_id)
    if not atividade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atividade {atividade_id} não encontrada"
        )
    
    return atividade


@router.patch("/{atividade_id}", response_model=AtividadeResponse)
async def update_atividade(
    atividade_id: Annotated[int, Path(gt=0)],
    update_data: AtividadeUpdate
):
    """
    Atualizar atividade existente.
    
    **Campos atualizáveis:**
    - `status`: Novo status (CRIADA → EM_ANDAMENTO → CONCLUIDA/CANCELADA)
    - `descricao`: Atualizar descrição
    - `localizacao`: Atualizar coordenadas
    - `metadata`: Atualizar metadados
    
    **Transições de status válidas:**
    - CRIADA → EM_ANDAMENTO
    - EM_ANDAMENTO → CONCLUIDA
    - EM_ANDAMENTO → CANCELADA
    - Qualquer → CANCELADA (gestores)
    
    **Comportamento automático:**
    - Status → EM_ANDAMENTO: Define `iniciado_em`
    - Status → CONCLUIDA/CANCELADA: Define `encerrado_em`
    
    **Exemplo:**
    ```bash
    curl -X PATCH "http://localhost:8001/api/atividades/123" \\
      -H "Content-Type: application/json" \\
      -d '{
        "status": "EM_ANDAMENTO",
        "descricao": "Vistoria em progresso"
      }'
    ```
    
    **Retorna:**
    - 200: Atividade atualizada
    - 404: Atividade não encontrada
    """
    service = AtividadeService(DB_CONN_STR)
    
    try:
        # TODO: Get usuario from JWT and validate permissions
        usuario = "sistema"
        
        atividade = service.update(atividade_id, update_data, usuario)
        if not atividade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Atividade {atividade_id} não encontrada"
            )
        
        return atividade
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar atividade: {str(e)}"
        )


@router.delete("/{atividade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_atividade(
    atividade_id: Annotated[int, Path(gt=0)]
):
    """
    Cancelar atividade (soft delete).
    
    **Comportamento:**
    - Define status como CANCELADA
    - Define `encerrado_em` com timestamp atual
    - Não remove fisicamente do banco
    
    **Permissões:**
    - CAMPO: Apenas atividades próprias em status CRIADA
    - GESTOR: Qualquer atividade
    - ADMIN: Qualquer atividade
    
    **Exemplo:**
    ```bash
    curl -X DELETE "http://localhost:8001/api/atividades/123"
    ```
    
    **Retorna:**
    - 204: Atividade cancelada com sucesso
    - 404: Atividade não encontrada
    """
    service = AtividadeService(DB_CONN_STR)
    
    deleted = service.delete(atividade_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atividade {atividade_id} não encontrada"
        )
    
    # 204 No Content (no response body)
    return None


@router.get("/stats/summary", response_model=AtividadeStats)
async def get_atividades_stats(
    municipio: Annotated[Optional[str], Query(min_length=7, max_length=7)] = None
):
    """
    Obter estatísticas de atividades.
    
    **Métricas:**
    - Total de atividades
    - Distribuição por status
    - Distribuição por tipo
    - Distribuição por município
    
    **Filtros:**
    - `municipio`: Filtrar por código IBGE
    
    **Exemplo:**
    ```bash
    # Estatísticas gerais
    curl "http://localhost:8001/api/atividades/stats/summary"
    
    # Estatísticas de Cuiabá
    curl "http://localhost:8001/api/atividades/stats/summary?municipio=5103403"
    ```
    
    **Retorna:**
    ```json
    {
      "total": 1543,
      "por_status": {
        "CRIADA": 234,
        "EM_ANDAMENTO": 156,
        "CONCLUIDA": 1098,
        "CANCELADA": 55
      },
      "por_tipo": {
        "VISTORIA": 890,
        "LIRAA": 320,
        "NEBULIZACAO": 180,
        ...
      },
      "por_municipio": {
        "5103403": 450,
        "5103502": 320,
        ...
      }
    }
    ```
    """
    service = AtividadeService(DB_CONN_STR)
    
    try:
        # TODO: Filter by usuario role
        return service.get_stats(municipio=municipio)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )
