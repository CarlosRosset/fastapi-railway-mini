# Autenticação JWT no Template FastAPI

## Introdução

JWT (JSON Web Token) é um padrão aberto (RFC 7519) que define uma maneira compacta e autocontida para transmitir informações com segurança entre partes como um objeto JSON. No contexto do template FastAPI, JWT é utilizado como mecanismo principal de autenticação, permitindo que a API proteja rotas específicas e identifique usuários de forma segura e eficiente.

## O que é JWT?

JWT consiste em três partes separadas por pontos:

1. **Header**: Contém informações sobre o tipo de token e o algoritmo de assinatura
2. **Payload**: Contém as informações (claims) que queremos transmitir
3. **Signature**: Assinatura digital que verifica a autenticidade do token

Exemplo de JWT:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

## Vantagens do JWT no FastAPI

1. **Stateless**: O servidor não precisa manter estado da sessão
2. **Escalabilidade**: Facilita a escalabilidade horizontal sem necessidade de compartilhamento de sessão
3. **Cross-domain**: Funciona bem em ambientes com múltiplos domínios
4. **Informação autocontida**: O token contém todas as informações necessárias do usuário
5. **Integração perfeita**: O FastAPI oferece suporte nativo a JWT através do pacote `python-jose`

## Implementação no Template

No template FastAPI, a autenticação JWT é implementada de forma modular e segura, seguindo as melhores práticas de segurança.

### Componentes Principais

1. **Configuração**: Definições em `api/core/config.py`
2. **Segurança**: Implementação em `api/core/security.py`
3. **Rotas de Autenticação**: Implementadas em `api/src/users/routes.py`
4. **Dependências**: Funções para proteger rotas em `api/core/security.py`

### Configuração JWT

No arquivo `api/core/config.py`, configuramos os parâmetros essenciais do JWT:

```python
class Settings(BaseSettings):
    # ... outras configurações ...
    
    # JWT Settings
    JWT_SECRET: str  # Chave secreta para assinatura dos tokens
    JWT_ALGORITHM: str = "HS256"  # Algoritmo de criptografia
    JWT_EXPIRATION: int = 30  # Duração do token em minutos
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
```

### Implementação de Segurança

O arquivo `api/core/security.py` contém a lógica principal de autenticação:

```python
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.core.database import get_session
from api.src.users.models import User
from api.src.users.repository import UserRepository

# Configuração para hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 para extração de token da requisição
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash armazenado."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera um hash da senha em texto plano."""
    return pwd_context.hash(password)

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT com o ID do usuário como subject.
    
    Args:
        subject: ID do usuário ou outra identificação única
        expires_delta: Tempo opcional de expiração do token
        
    Returns:
        Token JWT codificado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION)
    
    # Definição do payload do token
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Codificação e assinatura do token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Dependência para obter o usuário atual a partir do token JWT.
    
    Valida o token JWT e retorna o usuário correspondente.
    Lança exceção se o token for inválido ou o usuário não existir.
    
    Args:
        token: Token JWT extraído da requisição
        session: Sessão do banco de dados
        
    Returns:
        Objeto User correspondente ao token
        
    Raises:
        HTTPException: Se o token for inválido ou o usuário não existir
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodifica o token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # Busca o usuário no banco de dados
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(int(user_id))
    
    if user is None:
        raise credentials_exception
        
    return user
```

### Rotas de Autenticação

As rotas de autenticação são implementadas em `api/src/users/routes.py`:

```python
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.core.database import get_session
from api.core.security import create_access_token, get_current_user, verify_password
from api.src.users.models import User
from api.src.users.repository import UserRepository
from api.src.users.schemas import UserCreate, UserResponse, Token

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
) -> Any:
    """Registra um novo usuário."""
    user_repo = UserRepository(session)
    
    # Verifica se o usuário já existe
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Cria o novo usuário
    user = await user_repo.create(user_data)
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
) -> Any:
    """
    Autentica o usuário e retorna um token JWT.
    
    Utiliza o fluxo OAuth2 com formulário padrão do FastAPI.
    """
    user_repo = UserRepository(session)
    
    # Busca o usuário pelo email
    user = await user_repo.get_by_email(form_data.username)  # No OAuth2PasswordRequestForm, username é o email
    
    # Verifica se o usuário existe e a senha está correta
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria o token JWT
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION)
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Retorna informações do usuário atualmente autenticado."""
    return current_user
```

### Schemas para Autenticação

Os schemas relacionados à autenticação são definidos em `api/src/users/schemas.py`:

```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class Token(BaseModel):
    """Esquema para resposta de token JWT."""
    access_token: str
    token_type: str

class UserBase(BaseModel):
    """Esquema base para dados de usuário."""
    email: EmailStr = Field(..., description="Email do usuário")
    username: str = Field(..., min_length=3, max_length=50, description="Nome de usuário")

class UserCreate(UserBase):
    """Esquema para criação de usuário."""
    password: str = Field(..., min_length=8, description="Senha do usuário")

class UserResponse(UserBase):
    """Esquema para resposta com dados do usuário."""
    model_config = ConfigDict(from_attributes=True)
    id: int
```

## Proteção de Rotas

Uma das principais funcionalidades do sistema JWT é a proteção de rotas específicas. No template, isso é implementado através de dependências do FastAPI:

```python
from fastapi import APIRouter, Depends

from api.core.security import get_current_user
from api.src.users.models import User

router = APIRouter()

@router.get("/protected-route")
async def protected_route(current_user: User = Depends(get_current_user)):
    """
    Esta rota só pode ser acessada por usuários autenticados.
    O token JWT deve ser fornecido no cabeçalho Authorization.
    """
    return {
        "message": "Esta é uma rota protegida",
        "user_id": current_user.id,
        "email": current_user.email
    }
```

### Diferentes Níveis de Autorização

Para implementar diferentes níveis de autorização (como admin, usuário comum, etc.), podemos expandir a função de dependência:

```python
async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Verifica se o usuário autenticado é um administrador."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente"
        )
    return current_user

@router.get("/admin-only")
async def admin_route(admin_user: User = Depends(get_admin_user)):
    """Esta rota só pode ser acessada por administradores."""
    return {"message": "Área de administração"}
```

## Fluxo de Autenticação

O fluxo completo de autenticação no template funciona da seguinte forma:

1. **Registro**: O usuário se registra fornecendo email, username e senha
2. **Login**: O usuário fornece credenciais (email e senha) e recebe um token JWT
3. **Acesso a rotas protegidas**: O usuário inclui o token JWT no cabeçalho de autorização
4. **Validação**: O sistema valida o token e identifica o usuário
5. **Acesso**: Se o token for válido, o usuário obtém acesso à rota protegida

### Exemplo de Uso com Curl

```bash
# Registro de usuário
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email":"usuario@exemplo.com","username":"usuario","password":"senha123"}'

# Login e obtenção de token
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=usuario@exemplo.com&password=senha123"

# Acesso a rota protegida com token
curl -X GET "http://localhost:8000/auth/me" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Configuração do JWT em Ambiente de Desenvolvimento

Para desenvolvimento local, configure as variáveis de ambiente necessárias no arquivo `.env`:

```
JWT_SECRET=sua_chave_secreta_super_segura
JWT_ALGORITHM=HS256
JWT_EXPIRATION=30
```

**Importante**: Nunca utilize a mesma chave secreta em ambientes de produção e desenvolvimento. Para produção, utilize uma chave forte e única, de preferência gerada aleatoriamente.

## Configuração em Produção

Para ambientes de produção, recomendamos:

1. **Chave secreta forte**: Use uma chave gerada aleatoriamente com alta entropia
2. **Tempo de expiração reduzido**: Defina um tempo de expiração apropriado para sua aplicação
3. **HTTPS**: Sempre utilize HTTPS para transmitir tokens JWT
4. **Cookie seguro**: Considere armazenar o token em um cookie HTTP-only com flag secure
5. **JWT Secret rotativa**: Implemente uma estratégia para rotacionar a chave secreta periodicamente

### Geração de Chave Secreta Segura

Para gerar uma chave secreta forte:

```python
import secrets
secrets.token_hex(32)  # Gera uma string hexadecimal de 32 bytes
```

## Renovação de Tokens

O template não implementa renovação de tokens por padrão, mas você pode adicionar esta funcionalidade:

```python
@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Renova o token JWT atual."""
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION)
    access_token = create_access_token(
        subject=str(current_user.id),
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
```

## Considerações de Segurança

### Boas Práticas

1. **Sempre use HTTPS**: Tokens JWT devem ser transmitidos apenas em conexões seguras
2. **Minimize dados no payload**: Inclua apenas informações essenciais no token
3. **Use expiração adequada**: Tokens com longa duração representam um risco de segurança
4. **Implemente blacklist**: Para casos de logout ou comprometimento de tokens
5. **Rotacione as chaves secretas**: Mude periodicamente a chave de assinatura
6. **Valide todos os dados**: Mesmo após decodificar o token, valide os dados do payload
7. **Use algoritmos seguros**: Prefira algoritmos de assinatura como HS256, RS256 ou ES256

### Vulnerabilidades Comuns

1. **Armazenamento inseguro**: Tokens armazenados em localStorage são vulneráveis a XSS
2. **Falta de expiração**: Tokens sem expiração podem ser usados indefinidamente
3. **Dados sensíveis no payload**: O payload do JWT é apenas codificado, não criptografado
4. **Algoritmo None**: Verifique explicitamente o algoritmo para evitar ataques com alg:none
5. **Chave secreta fraca**: Use chaves fortes e seguras para assinatura

## Depuração de Problemas

### Token Expirado

Se você estiver recebendo erro de token expirado, verifique:
- A configuração `JWT_EXPIRATION` pode ser muito curta
- Pode haver diferença de fuso horário entre cliente e servidor
- O cliente pode estar usando um token antigo

### Token Inválido

Se o sistema rejeitar um token como inválido:
- Verifique se a `JWT_SECRET` está correta e consistente
- Certifique-se de que o token não foi alterado durante a transmissão
- Confirme se o algoritmo usado para decodificação corresponde ao de codificação

### Usuário Não Encontrado

Se o token for válido mas o usuário não for encontrado:
- O usuário pode ter sido excluído após a emissão do token
- O ID do usuário no token pode estar incorreto
- Pode haver um problema na função `get_by_id` do repositório

## Conclusão

A implementação de autenticação JWT no template FastAPI oferece um sistema robusto e seguro para proteger rotas e autenticar usuários. Seguindo as melhores práticas de segurança e aproveitando os recursos nativos do FastAPI, o template fornece uma base sólida que pode ser facilmente adaptada às necessidades específicas de cada projeto.

A combinação de JWT com o sistema de dependências do FastAPI torna a proteção de rotas simples e direta, permitindo diferentes níveis de autorização e uma experiência de desenvolvimento fluida.

---

*[Voltar ao Índice](./index.md)*
