from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import traceback

from api.core.logging import get_logger

logger = get_logger(__name__)


async def db_exception_handler(request: Request, call_next):
    """
    Middleware para capturar exceções de banco de dados e retornar
    respostas apropriadas.
    
    Permite que a API continue funcionando mesmo quando ocorrem erros
    de conexão com o banco de dados.
    """
    
    # Todas as rotas devem funcionar igualmente, sem verificação prévia de disponibilidade
    # Apenas as rotas críticas recebem tratamento especial quando ocorre um erro
    safe_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json"]
    # Adiciona rotas de autenticação à lista de rotas seguras
    auth_paths = ["/auth/register", "/auth/login", "/auth/me"]
    is_static = request.url.path.startswith("/static/")
    is_safe_path = request.url.path in safe_paths or request.url.path in auth_paths or is_static
    
    # Para todas as rotas, tentamos executar normalmente e só capturamos erros quando ocorrem
    try:
        
        # Executa a rota normalmente se tudo estiver ok ou é uma rota crítica
        return await call_next(request)
    
    except SQLAlchemyError as e:
        # Log completo do erro para depuração
        logger.error(f"Database error: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        
        # Verifica se é rota de saúde ou raiz - essas devem continuar funcionando
        if is_safe_path:
            logger.warning(f"Critical route affected by DB error: {request.url.path}")
            # Para essas rotas, tentar retornar uma resposta parcial
            if request.url.path == "/health":
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "api_status": "ok",
                        "database_status": "error",
                        "error": "Database connection failed",
                        "version": "1.0.0"
                    }
                )
            # Outras rotas críticas continuam normalmente
            return await call_next(request)
        
        # Para demais rotas com dados do banco, retornar erro informativo
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Database service unavailable",
                "message": "O serviço de banco de dados está temporariamente indisponível. Tente novamente mais tarde.",
                "type": "database_error"
            }
        )
    except Exception as e:
        # Captura outras exceções não relacionadas ao banco
        logger.error(f"Unhandled error: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "message": "Ocorreu um erro interno no servidor. Nossa equipe foi notificada."
            }
        )
