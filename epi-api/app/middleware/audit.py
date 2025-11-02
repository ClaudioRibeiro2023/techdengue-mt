"""
Audit Logging Middleware
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import logging
import json
import time

logger = logging.getLogger("audit")


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Registra todas as requisições para auditoria
    """
    
    # Endpoints sensíveis que sempre devem ser auditados
    SENSITIVE_ENDPOINTS = [
        "/api/etl/",
        "/api/relatorios/",
        "/api/admin/",
        "/api/users/",
    ]
    
    # Métodos que modificam dados
    WRITE_METHODS = ["POST", "PUT", "DELETE", "PATCH"]
    
    async def dispatch(self, request: Request, call_next):
        # Capturar tempo de início
        start_time = time.time()
        
        # Verificar se deve auditar
        should_audit = self._should_audit(request)
        
        # Capturar request data (apenas para write operations)
        request_data = None
        if should_audit and request.method in self.WRITE_METHODS:
            request_data = await self._get_request_body(request)
        
        # Processar request
        response = await call_next(request)
        
        # Calcular tempo de processamento
        process_time = time.time() - start_time
        
        # Auditar se necessário
        if should_audit:
            await self._log_audit(request, response, request_data, process_time)
        
        return response
    
    def _should_audit(self, request: Request) -> bool:
        """Determina se request deve ser auditada"""
        path = request.url.path
        
        # Sempre auditar endpoints sensíveis
        if any(sensitive in path for sensitive in self.SENSITIVE_ENDPOINTS):
            return True
        
        # Sempre auditar write operations
        if request.method in self.WRITE_METHODS:
            return True
        
        # Não auditar health checks e metrics
        if path in ["/health", "/metrics", "/docs", "/openapi.json"]:
            return False
        
        return False
    
    async def _get_request_body(self, request: Request) -> dict | None:
        """Captura body do request (com cuidado para não consumir stream)"""
        try:
            # Ler body
            body = await request.body()
            
            # Tentar decodificar como JSON
            if body:
                try:
                    data = json.loads(body)
                    # Remover campos sensíveis
                    return self._sanitize_data(data)
                except json.JSONDecodeError:
                    return {"_raw": body[:200].decode("utf-8", errors="ignore")}
            
            return None
        except Exception as e:
            logger.error(f"Error capturing request body: {e}")
            return None
    
    def _sanitize_data(self, data: dict) -> dict:
        """Remove campos sensíveis dos dados"""
        sensitive_fields = [
            "password",
            "token",
            "secret",
            "api_key",
            "access_token",
            "refresh_token",
        ]
        
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if any(field in key.lower() for field in sensitive_fields):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    async def _log_audit(
        self,
        request: Request,
        response: Response,
        request_data: dict | None,
        process_time: float
    ):
        """Registra log de auditoria"""
        
        # Extrair informações do usuário
        user_id = getattr(request.state, "user_id", None)
        user_email = getattr(request.state, "user_email", None)
        
        # Extrair Request ID
        request_id = getattr(request.state, "request_id", None)
        
        # Extrair IP
        client_ip = request.headers.get("X-Forwarded-For", request.client.host)
        
        # Montar log entry
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "user_id": user_id,
            "user_email": user_email,
            "client_ip": client_ip,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
            "user_agent": request.headers.get("User-Agent"),
        }
        
        # Adicionar request data se disponível
        if request_data:
            audit_entry["request_data"] = request_data
        
        # Log em formato JSON
        logger.info(
            "AUDIT",
            extra={
                "audit_entry": audit_entry,
                "event_type": "api_request",
            }
        )
        
        # Para operações críticas, também pode salvar em banco
        if self._is_critical_operation(request):
            await self._save_to_database(audit_entry)
    
    def _is_critical_operation(self, request: Request) -> bool:
        """Determina se é operação crítica que deve ser salva em banco"""
        critical_paths = [
            "/api/admin/",
            "/api/etl/sinan/import",
            "/api/users/delete",
        ]
        
        return any(path in request.url.path for path in critical_paths)
    
    async def _save_to_database(self, audit_entry: dict):
        """Salva log de auditoria em banco de dados (implementar se necessário)"""
        # TODO: Implementar persistência em banco
        # Exemplo: await db.audit_logs.insert_one(audit_entry)
        pass


# ============================================================================
# AUDIT LOGGER CONFIGURATION
# ============================================================================

def configure_audit_logger():
    """
    Configura logger dedicado para auditoria
    """
    import logging.handlers
    import os
    
    # Criar logger de auditoria
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False
    
    # Criar diretório de logs se não existir
    log_dir = os.getenv("LOG_DIR", "/var/log/techdengue")
    os.makedirs(log_dir, exist_ok=True)
    
    # Handler para arquivo (com rotação)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=f"{log_dir}/audit.log",
        maxBytes=100 * 1024 * 1024,  # 100 MB
        backupCount=10,
        encoding="utf-8",
    )
    
    # Formatter JSON
    formatter = logging.Formatter(
        '{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s",'
        '"extra":%(audit_entry)s}'
    )
    file_handler.setFormatter(formatter)
    
    # Adicionar handler
    audit_logger.addHandler(file_handler)
    
    # Handler para console (development)
    if os.getenv("ENVIRONMENT") == "development":
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        audit_logger.addHandler(console_handler)
    
    return audit_logger
