from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError

from api.core.config import settings
from api.core.logging import get_logger, setup_logging
from api.core.database import get_session
from api.core.middleware import db_exception_handler
from api.src.heroes.routes import router as heroes_router
from api.src.users.routes import router as auth_router
from api.utils.migrations import run_migrations

# Set up logging configuration
setup_logging()

# Set up logger for this module
logger = get_logger(__name__)

# Optional: Run migrations on startup - não impede a inicialização se falhar
migrations_success = run_migrations()
if not migrations_success:
    logger.warning("Database migrations failed but API will continue to function with limited capabilities")

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

# Adiciona middleware para CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em ambiente de produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adiciona middleware personalizado para tratamento de erros de banco de dados
@app.middleware("http")
async def db_errors_middleware(request, call_next):
    return await db_exception_handler(request, call_next)

# Include routers
app.include_router(auth_router)
app.include_router(heroes_router)


@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_session)):
    """Verificar se a API está funcionando e a conexão com o banco de dados está ativa.
    
    A API continuará funcionando mesmo se o banco de dados estiver indisponível.
    """
    db_status = "connected"
    api_status = "ok"
    
    try:
        # Tenta executar uma consulta simples para verificar a conexão
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        db_status = "disconnected"
        logger.error(f"Database connection failed: {str(e)}")
    except Exception as e:
        db_status = "error"
        logger.error(f"Unexpected error checking database: {str(e)}")
    
    return {
        "api_status": api_status,
        "database_status": db_status,
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Rota raiz da API, retorna uma mensagem de boas-vindas.
    
    Esta rota sempre funcionará, independentemente da conexão com o banco de dados.
    """
    logger.debug("Root endpoint called")
    return {
        "message": "Bem-vindo à API do template-railway-fastapi!",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }
