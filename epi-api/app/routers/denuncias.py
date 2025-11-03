"""
Router para Denúncias Públicas (e-Denúncia)
Módulo PoC - Fase P (ELIMINATÓRIA)
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Request
from typing import Optional, List
from datetime import datetime
from collections import defaultdict, deque
import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor

from app.models.denuncia import (
    DenunciaCreate,
    DenunciaResponse,
    DenunciaUpdate,
    DenunciaListResponse,
    DenunciaStatsResponse,
    DenunciaStatus,
    DenunciaPrioridade
)

logger = logging.getLogger(__name__)

# Database connection string
DB_CONN_STR = os.getenv(
    "DATABASE_URL",
    "postgresql://techdengue:techdengue@db:5432/techdengue"
).replace("postgresql+asyncpg://", "postgresql://")

router = APIRouter(
    prefix="/api/denuncias",
    tags=["e-Denúncia"]
)


# =============================================================================
# HELPERS
# =============================================================================

def get_db_connection():
    """Cria nova conexão com banco de dados"""
    return psycopg2.connect(DB_CONN_STR)


# Rate limiting simples: 5 requisições/minuto por IP (configurável via env)
RATE_LIMIT_PER_MINUTE = int(os.getenv("DENUNCIAS_RATE_LIMIT_PER_MINUTE", "5"))
_rate_limit_window = 60.0
_request_times = defaultdict(deque)  # ip -> deque[timestamps]

def is_rate_limited(ip: str) -> bool:
    now = datetime.utcnow().timestamp()
    dq = _request_times[ip]
    while dq and (now - dq[0]) > _rate_limit_window:
        dq.popleft()
    if len(dq) >= RATE_LIMIT_PER_MINUTE:
        return True
    dq.append(now)
    return False


def lookup_municipio_nome(municipio_codigo: str) -> Optional[str]:
    """Busca nome do município pelo código IBGE"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nome FROM municipios_ibge WHERE codigo_ibge = %s LIMIT 1",
            (municipio_codigo,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        logger.warning(f"Erro ao buscar município {municipio_codigo}: {e}")
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


async def criar_atividade_from_denuncia(denuncia_id: str):
    """
    Cria uma Atividade de campo a partir de uma denúncia
    Background task executada após criação da denúncia com prioridade ALTA
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar denúncia (com lat/lon)
        cursor.execute("""
            SELECT 
                numero_protocolo, endereco, bairro, municipio_codigo, 
                descricao,
                ST_Y(coordenadas::geometry) as latitude,
                ST_X(coordenadas::geometry) as longitude,
                chatbot_classificacao, foto_url
            FROM denuncias_publicas
            WHERE id = %s
        """, (denuncia_id,))
        
        denuncia = cursor.fetchone()
        if not denuncia:
            logger.error(f"Denúncia {denuncia_id} não encontrada")
            return
        
        # Criar atividade
        titulo = f"Denúncia {denuncia[0]} - Foco de Aedes"
        descricao_atividade = f"""
Atividade criada automaticamente a partir de denúncia pública.

Protocolo: {denuncia[0]}
Local: {denuncia[1]}, {denuncia[2]}
Descrição: {denuncia[4]}
Classificação Chatbot: {denuncia[6]}
        """.strip()
        
        # Coordenadas
        lat, lon = denuncia[5], denuncia[6]
        coord_wkt = f"POINT({lon} {lat})" if (lat is not None and lon is not None) else None

        cursor.execute("""
            INSERT INTO atividades (
                titulo, descricao, tipo, prioridade, status,
                municipio_codigo, endereco, coordenadas,
                origem, criado_em
            ) VALUES (
                %s, %s, 'VISITA', 'ALTA', 'PENDENTE',
                %s, %s, CASE WHEN %s IS NULL THEN NULL ELSE ST_GeogFromText(%s) END,
                'DENUNCIA', NOW()
            )
            RETURNING id
        """, (
            titulo, descricao_atividade,
            denuncia[3], denuncia[1], coord_wkt, coord_wkt
        ))
        
        atividade_id = cursor.fetchone()[0]
        
        # Anexar foto como evidência (se houver)
        if denuncia[7]:
            cursor.execute("""
                INSERT INTO atividade_evidencias (
                    atividade_id, tipo, arquivo_url, criado_em
                ) VALUES (%s, 'FOTO', %s, NOW())
            """, (atividade_id, denuncia[7]))
        
        # Atualizar denúncia
        cursor.execute("""
            UPDATE denuncias_publicas
            SET atividade_id = %s, status = 'ATIVIDADE_CRIADA'
            WHERE id = %s
        """, (atividade_id, denuncia_id))
        
        conn.commit()
        logger.info(f"Atividade {atividade_id} criada para denúncia {denuncia_id}")
        
    except Exception as e:
        logger.error(f"Erro ao criar atividade: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("", response_model=DenunciaResponse, status_code=201)
async def criar_denuncia(
    denuncia: DenunciaCreate,
    background_tasks: BackgroundTasks,
    request: Request
):
    """
    Cria uma nova denúncia pública
    
    **Fluxo**:
    1. Valida dados e código IBGE
    2. Insere denúncia no banco
    3. Se prioridade ALTA, cria atividade automaticamente (background)
    4. Retorna protocolo e dados da denúncia
    
    **Autenticação**: NÃO REQUERIDA (acesso público)
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Lookup município
        municipio_nome = lookup_municipio_nome(denuncia.municipio_codigo)
        if not municipio_nome:
            raise HTTPException(
                status_code=400,
                detail=f"Código IBGE inválido ou município não encontrado: {denuncia.municipio_codigo}"
            )
        
        # Capturar IP
        ip_origem = None
        try:
            xff = request.headers.get("x-forwarded-for")
            if xff:
                ip_origem = xff.split(",")[0].strip()
            else:
                ip_origem = request.client.host if request.client else None
        except Exception:
            ip_origem = request.client.host if request.client else None

        # Rate limit
        if ip_origem and is_rate_limited(ip_origem):
            raise HTTPException(status_code=429, detail="Muitas solicitações. Tente novamente em instantes.")
        
        # Converter coordenadas para PostGIS POINT
        coordenadas_wkt = f"POINT({denuncia.coordenadas.longitude} {denuncia.coordenadas.latitude})"
        
        # Serializar respostas chatbot para JSONB (garante datetime -> ISO8601)
        import json
        chatbot_respostas_json = json.dumps([r.model_dump(mode="json") for r in denuncia.chatbot_respostas])
        
        # Offline sync header
        is_offline_sync = request.headers.get("X-Offline-Sync") == "1"

        # Insert
        cursor.execute("""
            INSERT INTO denuncias_publicas (
                endereco, bairro, municipio_codigo, municipio_nome,
                coordenadas, coordenadas_precisao,
                descricao, foto_url,
                chatbot_classificacao, chatbot_respostas, chatbot_duracao_segundos,
                contato_nome, contato_telefone, contato_email, contato_anonimo,
                origem, user_agent, ip_origem,
                criado_em, sincronizado_em
            ) VALUES (
                %s, %s, %s, %s,
                ST_GeogFromText(%s), %s,
                %s, %s,
                %s, %s::jsonb, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                NOW(), %s
            )
            RETURNING id, numero_protocolo, criado_em, atualizado_em
        """, (
            denuncia.endereco, denuncia.bairro, denuncia.municipio_codigo, municipio_nome,
            coordenadas_wkt, denuncia.coordenadas.precisao,
            denuncia.descricao, denuncia.foto_url,
            denuncia.chatbot_classificacao.value, chatbot_respostas_json, denuncia.chatbot_duracao_segundos,
            denuncia.contato_nome, denuncia.contato_telefone, denuncia.contato_email, denuncia.contato_anonimo,
            denuncia.origem, denuncia.user_agent, ip_origem,
            datetime.utcnow() if is_offline_sync else None
        ))
        
        result = cursor.fetchone()
        denuncia_id, numero_protocolo, criado_em, atualizado_em = result
        
        conn.commit()
        
        # Se prioridade ALTA, criar atividade em background
        if denuncia.chatbot_classificacao == DenunciaPrioridade.ALTO:
            background_tasks.add_task(criar_atividade_from_denuncia, str(denuncia_id))
        
        logger.info(f"Denúncia criada: {numero_protocolo} ({denuncia_id})")
        
        # Retornar response
        return DenunciaResponse(
            id=str(denuncia_id),
            numero_protocolo=numero_protocolo,
            endereco=denuncia.endereco,
            bairro=denuncia.bairro,
            municipio_codigo=denuncia.municipio_codigo,
            municipio_nome=municipio_nome,
            coordenadas=denuncia.coordenadas,
            descricao=denuncia.descricao,
            foto_url=denuncia.foto_url,
            chatbot_classificacao=denuncia.chatbot_classificacao,
            chatbot_duracao_segundos=denuncia.chatbot_duracao_segundos,
            contato_nome=denuncia.contato_nome if not denuncia.contato_anonimo else None,
            contato_telefone=denuncia.contato_telefone if not denuncia.contato_anonimo else None,
            contato_anonimo=denuncia.contato_anonimo,
            status=DenunciaStatus.PENDENTE,
            atividade_id=None,
            criado_em=criado_em,
            atualizado_em=atualizado_em,
            sincronizado_em=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar denúncia: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar denúncia")
    finally:
        try:
            conn.close()
        except Exception:
            pass


@router.get("/{protocolo}", response_model=DenunciaResponse)
async def consultar_denuncia(
    protocolo: str
):
    """
    Consulta denúncia pelo número de protocolo
    
    **Autenticação**: NÃO REQUERIDA (cidadão pode consultar com protocolo)
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, numero_protocolo, endereco, bairro,
                municipio_codigo, municipio_nome,
                ST_Y(coordenadas::geometry) as latitude,
                ST_X(coordenadas::geometry) as longitude,
                coordenadas_precisao,
                descricao, foto_url,
                chatbot_classificacao, chatbot_duracao_segundos,
                contato_nome, contato_telefone, contato_anonimo,
                status, atividade_id,
                criado_em, atualizado_em, sincronizado_em
            FROM denuncias_publicas
            WHERE numero_protocolo = %s AND deleted_at IS NULL
            LIMIT 1
        """, (protocolo,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Denúncia não encontrada")
        
        # Parse result
        from app.models.denuncia import CoordenadasGPS
        
        return DenunciaResponse(
            id=str(result[0]),
            numero_protocolo=result[1],
            endereco=result[2],
            bairro=result[3],
            municipio_codigo=result[4],
            municipio_nome=result[5],
            coordenadas=CoordenadasGPS(
                latitude=result[6],
                longitude=result[7],
                precisao=result[8]
            ) if result[6] else None,
            descricao=result[9],
            foto_url=result[10],
            chatbot_classificacao=DenunciaPrioridade(result[11]),
            chatbot_duracao_segundos=result[12],
            contato_nome=result[13] if not result[15] else None,
            contato_telefone=result[14] if not result[15] else None,
            contato_anonimo=result[15],
            status=DenunciaStatus(result[16]),
            atividade_id=str(result[17]) if result[17] else None,
            criado_em=result[18],
            atualizado_em=result[19],
            sincronizado_em=result[20]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao consultar denúncia: {e}")
        raise HTTPException(status_code=500, detail="Erro ao consultar denúncia")
    finally:
        try:
            conn.close()
        except Exception:
            pass


@router.get("", response_model=DenunciaListResponse)
async def listar_denuncias(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    municipio_codigo: Optional[str] = None,
    status: Optional[DenunciaStatus] = None,
    prioridade: Optional[DenunciaPrioridade] = None
):
    """
    Lista denúncias com paginação e filtros
    
    **Autenticação**: REQUERIDA (apenas admin/gestor)
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_conditions = ["deleted_at IS NULL"]
        params = []
        
        if municipio_codigo:
            where_conditions.append("municipio_codigo = %s")
            params.append(municipio_codigo)
        
        if status:
            where_conditions.append("status = %s")
            params.append(status.value)
        
        if prioridade:
            where_conditions.append("chatbot_classificacao = %s")
            params.append(prioridade.value)
        
        where_clause = " AND ".join(where_conditions)
        
        # Count total
        cursor.execute(f"SELECT COUNT(*) FROM denuncias_publicas WHERE {where_clause}", params)
        total = cursor.fetchone()[0]
        
        # Query paginated
        offset = (page - 1) * per_page
        params.extend([per_page, offset])
        
        cursor.execute(f"""
            SELECT 
                id, numero_protocolo, endereco, bairro,
                municipio_codigo, municipio_nome,
                ST_Y(coordenadas::geometry) as latitude,
                ST_X(coordenadas::geometry) as longitude,
                coordenadas_precisao,
                descricao, foto_url,
                chatbot_classificacao, chatbot_duracao_segundos,
                contato_anonimo, status, atividade_id,
                criado_em, atualizado_em, sincronizado_em
            FROM denuncias_publicas
            WHERE {where_clause}
            ORDER BY criado_em DESC
            LIMIT %s OFFSET %s
        """, params)
        
        items = []
        for row in cursor.fetchall():
            from app.models.denuncia import CoordenadasGPS
            items.append(DenunciaResponse(
                id=str(row[0]),
                numero_protocolo=row[1],
                endereco=row[2],
                bairro=row[3],
                municipio_codigo=row[4],
                municipio_nome=row[5],
                coordenadas=CoordenadasGPS(
                    latitude=row[6], longitude=row[7], precisao=row[8]
                ) if row[6] else None,
                descricao=row[9],
                foto_url=row[10],
                chatbot_classificacao=DenunciaPrioridade(row[11]),
                chatbot_duracao_segundos=row[12],
                contato_nome=None,  # Masked na listagem
                contato_telefone=None,  # Masked na listagem
                contato_anonimo=row[13],
                status=DenunciaStatus(row[14]),
                atividade_id=str(row[15]) if row[15] else None,
                criado_em=row[16],
                atualizado_em=row[17],
                sincronizado_em=row[18]
            ))
        
        has_next = (offset + per_page) < total
        
        return DenunciaListResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar denúncias: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar denúncias")
    finally:
        try:
            conn.close()
        except Exception:
            pass


@router.get("/stats/resumo", response_model=DenunciaStatsResponse)
async def estatisticas_denuncias(
    municipio_codigo: Optional[str] = None
):
    """
    Estatísticas agregadas de denúncias
    
    **Autenticação**: REQUERIDA
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        where_clause = "deleted_at IS NULL"
        params = []
        
        if municipio_codigo:
            where_clause += " AND municipio_codigo = %s"
            params.append(municipio_codigo)
        
        # Total
        cursor.execute(f"SELECT COUNT(*) FROM denuncias_publicas WHERE {where_clause}", params)
        total_denuncias = cursor.fetchone()[0]
        
        # Por prioridade
        cursor.execute(f"""
            SELECT chatbot_classificacao, COUNT(*)
            FROM denuncias_publicas
            WHERE {where_clause}
            GROUP BY chatbot_classificacao
        """, params)
        por_prioridade = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Por status
        cursor.execute(f"""
            SELECT status, COUNT(*)
            FROM denuncias_publicas
            WHERE {where_clause}
            GROUP BY status
        """, params)
        por_status = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Por município
        cursor.execute(f"""
            SELECT municipio_codigo, municipio_nome, COUNT(*)
            FROM denuncias_publicas
            WHERE {where_clause}
            GROUP BY municipio_codigo, municipio_nome
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """, params)
        por_municipio = [
            {"codigo": row[0], "nome": row[1], "total": row[2]}
            for row in cursor.fetchall()
        ]
        
        # Tempo médio chatbot
        cursor.execute(f"""
            SELECT AVG(chatbot_duracao_segundos)
            FROM denuncias_publicas
            WHERE {where_clause} AND chatbot_duracao_segundos IS NOT NULL
        """, params)
        tempo_medio = cursor.fetchone()[0]
        
        # Taxa conversão atividade
        cursor.execute(f"""
            SELECT 
                COUNT(CASE WHEN atividade_id IS NOT NULL THEN 1 END)::float / COUNT(*)
            FROM denuncias_publicas
            WHERE {where_clause}
        """, params)
        taxa_conversao = cursor.fetchone()[0]
        
        return DenunciaStatsResponse(
            total_denuncias=total_denuncias,
            por_prioridade=por_prioridade,
            por_status=por_status,
            por_municipio=por_municipio,
            tempo_medio_chatbot=round(tempo_medio, 1) if tempo_medio else None,
            taxa_conversao_atividade=round(taxa_conversao * 100, 1) if taxa_conversao else None
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar estatísticas")
    finally:
        try:
            conn.close()
        except Exception:
            pass
