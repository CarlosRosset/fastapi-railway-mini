import os
import subprocess
import sys
from api.core.logging import get_logger

logger = get_logger(__name__)


def run_migrations():
    """
    Runs Alembic database migrations using sys.executable and module execution.

    This method is more compatible with environments like Vercel where direct
    command execution might be restricted.
    
    A falha nas migrações não irá impedir a inicialização da API, permitindo
    que a aplicação continue funcionando mesmo sem banco de dados.
    """
    try:
        # Ensure the current directory is in the Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)

        # Use sys.executable to run the Alembic module
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Print the output if there's any
        if result.stdout:
            print("Migration output:", result.stdout)

        print("Migrations completed successfully!")

    except subprocess.CalledProcessError as e:
        logger.error(f"Migration failed. Error: {e}")
        logger.error(f"Standard output: {e.stdout}")
        logger.error(f"Standard error: {e.stderr}")
        # Não propaga o erro para permitir que a aplicação continue
        return False
    except Exception as e:
        logger.error(f"An error occurred while running migrations: {e}")
        # Não propaga o erro para permitir que a aplicação continue
        return False
    
    return True
