# ED CT Brain Workflow System - Technical Specification

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ED CT Brain Workflow System                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                           Frontend Layer                              │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  Dashboard │  │  Patients  │  │   Scans    │  │ Resources  │     │   │
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
│  │                        Multi-Agent Layer (LangChain)                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  Patient   │  │  Clinical  │  │  Resource  │  │Orchestration│     │   │
│  │  │   Agent    │  │   Agent    │  │   Agent    │  │   Agent    │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                    ┌─────────────────┼─────────────────┐                    │
│                    ▼                 ▼                 ▼                    │
│  ┌─────────────────────┐  ┌─────────────────┐  ┌─────────────────────┐    │
│  │    PostgreSQL       │  │      Redis      │  │       LLM API       │    │
│  │  (Persistent Data)  │  │ (Cache/Real-time)│  │  (AI Processing)   │    │
│  └─────────────────────┘  └─────────────────┘  └─────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

| Component | Technology | Responsibility |
|-----------|------------|----------------|
| Frontend | React + TypeScript | UI/UX, user interactions |
| Backend API | Python FastAPI | REST endpoints, business logic |
| WebSocket Server | FastAPI + Socket.io | Real-time updates |
| Agent Framework | LangChain | AI agent orchestration |
| Database | PostgreSQL 15 | Persistent data storage |
| Cache | Redis 7 | Session, cache, pub/sub |
| LLM | Local Qwen3 Model | Natural language processing |

---

## 2. Technology Stack

### 2.1 Backend Dependencies

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
websocket-client==1.7.0
```

### 2.2 Frontend Dependencies

```
# package.json
react: ^18.2.0
react-dom: ^18.2.0
react-router-dom: ^6.22.0
react-scripts: 5.0.1
typescript: ^5.3.3
axios: ^1.6.5
socket.io-client: ^4.7.4
react-hook-form: ^7.49.3
date-fns: ^3.3.1
lucide-react: ^0.312.0
recharts: ^2.10.4
zustand: ^4.5.0
tailwindcss: ^3.4.1
```

### 2.3 Infrastructure

| Service | Image | Version |
|---------|-------|---------|
| PostgreSQL | postgres | 15-alpine |
| Redis | redis | 7-alpine |
| Backend | custom Dockerfile | Python 3.11 |
| Frontend | custom Dockerfile | Node 20 |

---

## 3. Database Schema

### 3.1 Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │       │   Patient   │       │  CT_Scan    │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ email       │       │ mrn         │       │ patient_id  │
│ password    │◄─────►│ name        │◄─────►│ (FK)        │
│ role        │       │ dob         │       │ scan_type   │
│ created_at  │       │ contact     │       │ urgency     │
│ updated_at  │       │ created_at  │       │ status      │
└─────────────┘       │ updated_at  │       │ scheduled_at│
                      └─────────────┘       │ completed_at│
                                            │ result      │
                                            │ created_at  │
                                            └─────────────┘
                           │                         │
                           │                         │
                           ▼                         ▼
                      ┌─────────────┐       ┌─────────────┐
                      │ Notification│       │  Scanner    │
                      ├─────────────┤       ├─────────────┤
                      │ id (PK)     │       │ id (PK)     │
                      │ patient_id  │       │ name        │
                      │ (FK)        │       │ status      │
                      │ type        │       │ location    │
                      │ message     │       │ is_active   │
                      │ sent_at     │       └─────────────┘
                      │ read        │
                      └─────────────┘

┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    FAQ      │       │  Consent    │       │  Audit_Log  │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ question    │       │ patient_id  │       │ user_id     │
│ answer      │       │ (FK)        │       │ (FK)        │
│ category    │       │ scan_id     │       │ action      │
│ is_active   │       │ (FK)        │       │ entity_type │
│ created_at  │       │ consent_given│      │ entity_id   │
│ updated_at  │       │ signed_at   │       │ details     │
└─────────────┘       │ ip_address  │       │ timestamp   │
                      └─────────────┘       └─────────────┘
```

### 3.2 Table Definitions

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'physician', 'nurse', 'radiologist', 'technician', 'transporter')),
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Patients Table
```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    mrn VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20) CHECK (gender IN ('male', 'female', 'other')),
    phone VARCHAR(50),
    email VARCHAR(255),
    address TEXT,
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(50),
    allergies TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### CT Scans Table
```sql
CREATE TABLE ct_scans (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    scan_type VARCHAR(100) NOT NULL CHECK (scan_type IN ('brain', 'brain_with_contrast', 'angiography')),
    indication TEXT NOT NULL,
    urgency VARCHAR(20) NOT NULL CHECK (urgency IN ('immediate', 'urgent', 'routine')),
    status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'scheduled', 'in_progress', 'completed', 'cancelled')),
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result TEXT,
    preliminary_findings TEXT,
    ordered_by INTEGER REFERENCES users(id),
    assigned_scanner_id INTEGER REFERENCES scanners(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Scanners Table
```sql
CREATE TABLE scanners (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    status VARCHAR(30) DEFAULT 'available' CHECK (status IN ('available', 'in_use', 'maintenance', 'offline')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Notifications Table
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    scan_id INTEGER REFERENCES ct_scans(id) ON DELETE SET NULL,
    type VARCHAR(50) CHECK (type IN ('status_update', 'reminder', 'result_ready', 'general')),
    channel VARCHAR(20) CHECK (channel IN ('sms', 'whatsapp', 'email', 'in_app')),
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);
```

#### Consent Table
```sql
CREATE TABLE consents (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    scan_id INTEGER REFERENCES ct_scans(id) ON DELETE CASCADE,
    consent_type VARCHAR(50) NOT NULL,
    consent_given BOOLEAN NOT NULL,
    consent_details JSONB,
    signed_at TIMESTAMP,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### FAQ Table
```sql
CREATE TABLE faqs (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100),
    keywords JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. API Specification

### 4.1 Authentication Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/login` | User login | Public |
| POST | `/api/v1/auth/logout` | User logout | JWT |
| POST | `/api/v1/auth/refresh` | Refresh token | JWT |
| GET | `/api/v1/auth/me` | Current user | JWT |

### 4.2 Patient Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/patients` | List all patients | JWT |
| GET | `/api/v1/patients/{id}` | Get patient details | JWT |
| POST | `/api/v1/patients` | Create patient | JWT |
| PUT | `/api/v1/patients/{id}` | Update patient | JWT |
| DELETE | `/api/v1/patients/{id}` | Delete patient | Admin |

### 4.3 Scan Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/scans` | List all scans | JWT |
| GET | `/api/v1/scans/{id}` | Get scan details | JWT |
| POST | `/api/v1/scans` | Create scan order | JWT |
| PUT | `/api/v1/scans/{id}` | Update scan | JWT |
| PUT | `/api/v1/scans/{id}/status` | Update status | JWT |
| POST | `/api/v1/scans/{id}/schedule` | Schedule scan | JWT |
| POST | `/api/v1/scans/{id}/complete` | Complete scan | JWT |

### 4.4 Resource Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/resources/scanners` | List scanners | JWT |
| GET | `/api/v1/resources/scanners/{id}` | Scanner details | JWT |
| PUT | `/api/v1/resources/scanners/{id}` | Update scanner | JWT |
| GET | `/api/v1/resources/availability` | Check availability | JWT |

### 4.5 Dashboard Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/dashboard/stats` | Dashboard statistics | JWT |
| GET | `/api/v1/dashboard/queue` | Current queue | JWT |
| GET | `/api/v1/dashboard/tat` | Turnaround time | JWT |

### 4.6 FAQ Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/faq` | List FAQs | Public |
| GET | `/api/v1/faq/{id}` | FAQ details | Public |
| POST | `/api/v1/faq` | Create FAQ | Admin |
| PUT | `/api/v1/faq/{id}` | Update FAQ | Admin |
| DELETE | `/api/v1/faq/{id}` | Delete FAQ | Admin |
| POST | `/api/v1/faq/chat` | AI Chatbot | Public |

### 4.7 WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `scan:created` | Server → Client | New scan ordered |
| `scan:updated` | Server → Client | Scan status changed |
| `scan:completed` | Server → Client | Scan completed |
| `notification` | Server → Client | New notification |
| `queue:update` | Server → Client | Queue position changed |

---

## 5. Multi-Agent System

### 5.1 Agent Architecture

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
│  Patient Agent  │ │ Clinical Agent  │ │ Resource Agent  │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ - FAQ Chatbot   │ │ - Triage        │ │ - Scheduler     │
│ - Notifications │ │ - Urgency       │ │ - Capacity      │
│ - Consent       │ │   Scoring       │ │ - Availability  │
│ - Updates       │ │ - Guidelines    │ │ - Optimization  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 5.2 Agent Prompts (Simplified)

#### Patient Agent
- Role: Patient communication specialist
- Responsibilities: Answer FAQs, send notifications, manage digital consent
- Tools: Notification service, FAQ database, consent form handler

#### Clinical Agent
- Role: Clinical decision support
- Responsibilities: Validate CT indications, calculate urgency scores, suggest protocols
- Tools: Medical guidelines database, clinical scoring algorithms

#### Resource Agent
- Role: Resource optimization
- Responsibilities: Schedule scans, manage scanner availability, predict capacity
- Tools: Scheduler, capacity forecasting, scanner status

#### Orchestration Agent
- Role: Workflow coordination
- Responsibilities: Route tasks, manage escalations, maintain audit trail
- Tools: Task queue, escalation rules, audit logger

---

## 6. Security Specification

### 6.1 Authentication & Authorization

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
│   │  Compare password hash              │                   │
│   └─────────────────────────────────────┘                   │
│     │                                                       │
│     │ Valid                                                 │
│     ▼                                                       │
│   ┌─────────────────────────────────────┐                   │
│   │  Generate JWT tokens                │                   │
│   │  - Access token (15 min)            │                   │
│   │  - Refresh token (24 hours)         │                   │
│   └─────────────────────────────────────┘                   │
│     │                                                       │
│     ▼                                                       │
│   Response: {access_token, refresh_token, user}             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Role-Based Access Control

| Role | Permissions |
|------|-------------|
| `admin` | Full system access |
| `physician` | Order scans, view all patients, manage triage |
| `nurse` | View patients, update status, manage queue |
| `radiologist` | View scans, add results, review images |
| `technician` | Manage scanners, update scan status |
| `transporter` | View transport tasks, update patient location |

### 6.3 Security Headers

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6.4 Data Protection

- Passwords: bcrypt hashing with salt
- API Keys: Environment variable storage
- Database: Connection string via environment variables
- Audit Logs: Immutable records with timestamps

---

## 7. Deployment Architecture

### 7.1 Docker Compose Setup

```yaml
services:
  postgres:
    image: postgres:15-alpine
    volumes: postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes: redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8877:8000"
    env_file:
      - ./backend/.env
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "5173:3000"
    env_file:
      - ./frontend/.env
    depends_on:
      - backend
```

### 7.2 Production Deployment Recommendations

| Component | Recommendation |
|-----------|----------------|
| Reverse Proxy | Nginx with SSL termination |
| SSL/TLS | Let's Encrypt certificates |
| Database | PostgreSQL with replication |
| Cache | Redis Sentinel for HA |
| Container Orchestration | Kubernetes (future) |
| Monitoring | Prometheus + Grafana |
| Logging | ELK Stack or Loki |

---

## 8. Environment Variables

### 8.1 Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection | `postgresql+asyncpg://user:pass@host:5432/db` |
| REDIS_URL | Redis connection | `redis://host:6379` |
| JWT_SECRET | JWT signing key | `your-secret-key` |
| JWT_ALGORITHM | JWT algorithm | `HS256` |
| JWT_EXPIRATION_MINUTES | Token expiry | `1440` |
| LLM_BASE_URL | LLM API endpoint | `http://localhost:9999` |
| LLM_API_KEY | LLM API key | `sk-...` |
| LLM_MODEL | Model name | `qwen3.5-...` |

### 8.2 Frontend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| REACT_APP_API_URL | Backend URL | `http://localhost:8877` |
| REACT_APP_WS_URL | WebSocket URL | `ws://localhost:8877` |

---

## 9. File Structure

```
ct_workflow/
├── SPEC.md                    # Business specification
├── TECHNICAL_SPEC.md          # This file
├── README.md                  # Project readme
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
│       │   ├── patient_agent.py
│       │   ├── clinical_agent.py
│       │   ├── resource_agent.py
│       │   └── orchestration_agent.py
│       ├── api/
│       │   ├── routes/        # API endpoints
│       │   ├── middleware/    # Auth, logging
│       │   └── websocket.py   # WebSocket handler
│       ├── models/            # SQLAlchemy models
│       │   ├── user.py
│       │   ├── patient.py
│       │   ├── ct_scan.py
│       │   ├── scanner.py
│       │   └── ...
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
│       ├── pages/             # Page components
│       ├── hooks/             # Custom hooks
│       ├── services/          # API services
│       └── types/             # TypeScript types
│
└── docs/
    └── screenshots/           # UI screenshots
        ├── dashboard.png
        ├── patients.png
        ├── scans.png
        └── resources.png
```

---

## 10. Testing Strategy

### 10.1 Testing Types

| Type | Tool | Coverage Target |
|------|------|-----------------|
| Unit Tests | pytest | 80% backend |
| Integration Tests | pytest + httpx | API endpoints |
| Component Tests | React Testing Library | UI components |
| E2E Tests | Playwright | Critical flows |

### 10.2 Key Test Scenarios

- User authentication (login, logout, token refresh)
- Patient CRUD operations
- Scan workflow (order → schedule → complete)
- Real-time updates via WebSocket
- Agent responses for FAQ chatbot
- Role-based access control

---

## 11. Monitoring & Observability

### 11.1 Health Checks

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Basic health check |
| `GET /health/db` | Database connectivity |
| `GET /health/redis` | Redis connectivity |

### 11.2 Logging

- Application logs: Structured JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR
- Include: timestamp, level, message, context, trace_id

### 11.3 Metrics

- Request latency (p50, p95, p99)
- Error rate by endpoint
- Active WebSocket connections
- Database query performance
- Agent response times

---

*Document Version: 1.0*
*Last Updated: 2026-02-23*
*For: Hospital Shah Alam Emergency Department*