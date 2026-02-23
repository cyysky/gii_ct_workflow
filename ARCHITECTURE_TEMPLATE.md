# Technical Architecture Template

A reusable technical structure for building multi-agent AI web applications.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Application Name                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                           Frontend Layer                              │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  Page 1    │  │  Page 2    │  │  Page 3    │  │  Page 4    │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                              HTTPS / WebSocket                               │
│                                      ▼                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                           Backend Layer (FastAPI)                     │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  REST API  │  │  WebSocket │  │  Auth/JWT  │  │  Middleware│     │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                                      ▼                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Business Logic Layer                           │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  Agent 1   │  │  Agent 2   │  │  Agent 3   │  │   Service  │     │   │
│  │  │            │  │            │  │            │  │   Layer    │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                    ┌─────────────────┼─────────────────┐                    │
│                    ▼                 ▼                 ▼                    │
│  ┌─────────────────────┐  ┌─────────────────┐  ┌─────────────────────┐    │
│  │  PostgreSQL         │  │      Redis      │  │       LLM API       │    │
│  │  (Persistent Data)  │  │ (Cache/Real-time)│  │  (AI Processing)   │    │
│  └─────────────────────┘  └─────────────────┘  └─────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Responsibility |
|-------|----------------|
| Frontend | UI/UX, user interactions, state management |
| Backend API | REST endpoints, request validation, business logic orchestration |
| Business Logic | Domain logic, AI agents, data processing |
| Data | Database operations, caching, external API calls |

---

## 2. Technology Stack

### 2.1 Backend Stack

```
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
redis==5.0.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
langchain==0.1.4
langchain-community==0.0.17
httpx==0.26.0
```

### 2.2 Frontend Stack

```
# package.json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "react-scripts": "5.0.1",
    "typescript": "^5.3.3",
    "axios": "^1.6.5",
    "socket.io-client": "^4.7.4",
    "react-hook-form": "^7.49.3",
    "date-fns": "^3.3.1",
    "lucide-react": "^0.312.0",
    "recharts": "^2.10.4",
    "zustand": "^4.5.0",
    "tailwindcss": "^3.4.1"
  }
}
```

### 2.3 Infrastructure

| Service | Image | Purpose |
|---------|-------|---------|
| PostgreSQL | postgres:15-alpine | Primary database |
| Redis | redis:7-alpine | Cache, sessions, pub/sub |
| Backend | custom | Python 3.11 container |
| Frontend | custom | Node 20 container |

---

## 3. Database Schema Template

### 3.1 Base Tables

```sql
-- Users table (authentication)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Entity tables (customize per project)
CREATE TABLE entities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(30) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Related entities
CREATE TABLE entity_relations (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES entities(id),
    related_entity_id INTEGER REFERENCES entities(id),
    relation_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activity/Audit
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(50),
    title VARCHAR(255),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 Common Entity Patterns

```python
# SQLAlchemy Model Template
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base

class EntityName(Base):
    __tablename__ = "entity_names"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    status = Column(String(30), default="active")
    metadata = Column(JSON, default={})

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="entity_names")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

---

## 4. API Structure

### 4.1 REST Endpoints Pattern

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/{resource}` | List all |
| GET | `/api/v1/{resource}/{id}` | Get one |
| POST | `/api/v1/{resource}` | Create |
| PUT | `/api/v1/{resource}/{id}` | Update |
| DELETE | `/api/v1/{resource}/{id}` | Delete |
| PATCH | `/api/v1/{resource}/{id}/status` | Update status |

### 4.2 Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Create schema
class EntityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    metadata: Optional[dict] = {}

# Update schema
class EntityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[dict] = None

# Response schema
class EntityResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 4.3 Router Template

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.models import User
from src.utils.auth import get_current_user
from .schemas import EntityCreate, EntityUpdate, EntityResponse
from .service import EntityService

router = APIRouter()

@router.get("/", response_model=list[EntityResponse])
async def list_entities(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EntityService(db)
    return await service.list_all()

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entity = await service.get_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.post("/", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    data: EntityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.create(data.dict(), current_user.id)

@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: int,
    data: EntityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entity = await service.update(entity_id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    entity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await service.delete(entity_id)
```

---

## 5. Authentication & Authorization

### 5.1 Auth Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Authentication Flow                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Client                                                     │
│     │                                                       │
│     │ POST /api/v1/auth/login                               │
│     │ {email, password}                                     │
│     ▼                                                       │
│   ┌─────────────────────────────────────┐                   │
│   │  Verify credentials                 │                   │
│   │  - Find user by email               │                   │
│   │  - Verify password hash             │                   │
│   └─────────────────────────────────────┘                   │
│     │                                                       │
│     │ Valid                                                 │
│     ▼                                                       │
│   ┌─────────────────────────────────────┐                   │
│   │  Generate JWT tokens                │                   │
│   │  - Access token (short expiry)      │                   │
│   │  - Refresh token (long expiry)      │                   │
│   └─────────────────────────────────────┘                   │
│     │                                                       │
│     ▼                                                       │
│   Response: {access_token, refresh_token, user}             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 JWT Implementation

```python
# src/utils/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
```

### 5.3 Role-Based Access

```python
from enum import Enum
from functools import wraps
from fastapi import HTTPException, status

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

def require_roles(*roles: UserRole):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user, **kwargs):
            if current_user.role not in [r.value for r in roles]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@router.get("/admin-only")
@require_roles(UserRole.ADMIN)
async def admin_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": "Admin access"}
```

---

## 6. Multi-Agent Architecture

### 6.1 Agent Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestration Agent                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Task       │  │    Queue     │  │   Escalation │          │
│  │  Dispatcher  │  │   Manager    │  │   Handler    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
           │                  │                   │
           ▼                  ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│    Agent 1      │ │    Agent 2      │ │    Agent 3      │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ - Responsibility│ │ - Responsibility│ │ - Responsibility│
│ - Tool 1        │ │ - Tool 1        │ │ - Tool 1        │
│ - Tool 2        │ │ - Tool 2        │ │ - Tool 2        │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 6.2 Agent Implementation Template

```python
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage
from src.llm import llm

class BaseAgent:
    def __init__(self, name: str, role: str, tools: list):
        self.name = name
        self.role = role
        self.tools = tools
        self.conversation_history = []

    def get_prompt(self) -> ChatPromptTemplate:
        raise NotImplementedError

    async def process(self, user_input: str) -> str:
        prompt = self.get_prompt().format(
            role=self.role,
            history=self.conversation_history,
            input=user_input
        )
        response = await llm.apredict(prompt)
        self.conversation_history.append(HumanMessage(content=user_input))
        self.conversation_history.append(AIMessage(content=response))
        return response


class CustomAgent(BaseAgent):
    def get_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template("""
You are {role}.

Conversation history:
{history}

User input: {input}

Provide a helpful response.
        """)
```

---

## 7. Project Structure

```
project_name/
├── SPEC.md                    # Business specification
├── TECHNICAL_SPEC.md          # Technical specification
├── README.md                  # Project readme
├── ARCHITECTURE_TEMPLATE.md   # This template
├── .gitignore                 # Git ignore rules
├── docker-compose.yml         # Docker compose config
│
├── backend/
│   ├── .env                   # Environment (not committed)
│   ├── .env.example           # Environment template
│   ├── Dockerfile             # Backend container
│   ├── requirements.txt       # Python dependencies
│   └── src/
│       ├── main.py            # FastAPI app entry
│       ├── config.py          # Settings
│       ├── database.py        # DB connection
│       ├── agents/            # AI agents
│       │   └── agent_template.py
│       ├── api/
│       │   ├── routes/        # API endpoints
│       │   │   └── example.py
│       │   ├── middleware/    # Auth, logging
│       │   └── websocket.py   # WebSocket handler
│       ├── models/            # SQLAlchemy models
│       │   └── base.py
│       ├── schemas/           # Pydantic schemas
│       │   └── base.py
│       ├── services/          # Business logic
│       │   └── base.py
│       └── utils/             # Utilities
│           └── auth.py
│
├── frontend/
│   ├── .env                   # Environment (not committed)
│   ├── .env.example           # Environment template
│   ├── Dockerfile             # Frontend container
│   ├── package.json           # Node dependencies
│   ├── tailwind.config.js     # Tailwind config
│   ├── tsconfig.json          # TypeScript config
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── index.js           # React entry
│       ├── index.css          # Global styles
│       ├── App.tsx            # Main app
│       ├── components/        # Reusable components
│       │   ├── Layout.tsx
│       │   └── common/
│       ├── pages/             # Page components
│       │   └── ExamplePage.tsx
│       ├── hooks/             # Custom hooks
│       │   └── useAuth.ts
│       ├── services/          # API services
│       │   └── api.ts
│       ├── types/             # TypeScript types
│       │   └── index.ts
│       └── store/             # State management
│           └── useStore.ts
│
└── docs/
    └── screenshots/           # UI screenshots
```

---

## 8. Docker Configuration

### 8.1 Docker Compose Template

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: ${PROJECT_NAME}_db
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - "${DB_PORT}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ${PROJECT_NAME}_redis
    ports:
      - "${REDIS_PORT}:6379"
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ${PROJECT_NAME}_backend
    ports:
      - "${BACKEND_PORT}:8000"
    env_file:
      - ./backend/.env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend/src:/app/src

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: ${PROJECT_NAME}_frontend
    ports:
      - "${FRONTEND_PORT}:3000"
    env_file:
      - ./frontend/.env
    depends_on:
      - backend
    volumes:
      - ./frontend/src:/app/src
      - /app/node_modules

volumes:
  postgres_data:
  redis_data:
```

### 8.2 Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 8.3 Frontend Dockerfile

```dockerfile
FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

---

## 9. Environment Variables

### 9.1 Backend Template

```bash
# .env.example

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/db_name

# Redis
REDIS_URL=redis://localhost:6379

# JWT Authentication
JWT_SECRET=your_jwt_secret_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# LLM Configuration (optional)
LLM_BASE_URL=http://localhost:9999
LLM_API_KEY=your_api_key_here
LLM_MODEL=your_model_name

# Application
DEBUG=false
```

### 9.2 Frontend Template

```bash
# .env.example
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

---

## 10. Common Utilities

### 10.1 Database Connection

```python
# src/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    await engine.dispose()
```

### 10.2 Settings

```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/db"
    REDIS_URL: str = "redis://localhost:6379"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440

    LLM_BASE_URL: str = ""
    LLM_API_KEY: str = ""
    LLM_MODEL: str = ""

    DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

*Template Version: 1.0*
*Use this as a starting point for new projects*