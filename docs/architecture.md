# Chinese Auto Parts Price Bot - Architecture Documentation

## 1. Overview

The Chinese Auto Parts Price Bot is a Telegram-based price lookup system that enables users to search for Chinese car parts, receive part confirmations in Persian, and submit formal orders through a streamlined contact capture workflow. The system consists of a Telegram bot frontend, FastAPI backend, SQLite database, and admin panel, with AI-powered semantic search capabilities that can be toggled on/off by administrators.

### Major Components
- **Telegram Bot (aiogram)**: User-facing interface with Persian language support
- **FastAPI Backend**: REST API for search, orders, and admin operations
- **Database (SQLite → Postgres)**: Persistent storage for parts, prices, orders, and settings
- **Admin Panel (SPA/CSR)**: Web interface for data management and system configuration
- **AI Toggle System**: Feature flag mechanism for enabling/disabling semantic search
- **Excel Import Pipeline**: Data ingestion system for parts and pricing information

## 2. Architecture Diagrams

### System Overview (C4 Container Diagram)

```mermaid
graph TB
    subgraph "External"
        TG[Telegram API]
        USERS[End Users]
        ADMINS[Admin Users]
    end
    
    subgraph "Application Layer"
        BOT[Telegram Bot<br/>aiogram]
        API[FastAPI Backend<br/>REST API]
        ADMIN[Admin Panel<br/>SPA]
    end
    
    subgraph "Data Layer"
        DB[(Database<br/>SQLite → Postgres)]
        CACHE[(Cache<br/>In-Memory)]
    end
    
    subgraph "AI/ML"
        AI[AI Search Engine<br/>Local/External]
    end
    
    USERS --> TG
    TG --> BOT
    BOT --> API
    ADMINS --> ADMIN
    ADMIN --> API
    API --> DB
    API --> CACHE
    API --> AI
    
    style BOT fill:#e1f5fe
    style API fill:#f3e5f5
    style ADMIN fill:#e8f5e8
    style DB fill:#fff3e0
```

### Key User Flows

#### Single Query Flow
```mermaid
sequenceDiagram
    participant U as User
    participant TG as Telegram
    participant BOT as Bot
    participant API as FastAPI
    participant DB as Database
    participant AI as AI Search
    
    U->>TG: "Front brake pad X22"
    TG->>BOT: Message received
    BOT->>API: POST /search/parts
    API->>DB: Query parts table
    
    alt AI Enabled
        API->>AI: Semantic search
        AI-->>API: Enhanced results
    else AI Disabled
        API->>DB: Fuzzy/basic search
    end
    
    DB-->>API: Part matches
    API-->>BOT: Part confirmation data
    BOT->>TG: "آیا شما به دنبال لنت چراغ جلوی تیگو ۸ هستید؟"
    TG->>U: Confirmation question
    
    U->>TG: "بله" / "خیر"
    TG->>BOT: User response
    
    alt User Confirms
        BOT->>TG: Request contact (request_contact)
        TG->>U: Contact sharing prompt
        U->>TG: Share phone number
        TG->>BOT: Contact data
        BOT->>API: POST /leads (create/update)
        BOT->>API: POST /orders (create order)
        API->>DB: Save lead & order
        BOT->>TG: Order confirmation
        TG->>U: "سفارش شما ثبت شد"
    else User Denies
        BOT->>TG: "لطفاً دوباره جستجو کنید"
        TG->>U: Search again prompt
    end
```

#### Bulk Query Flow
```mermaid
sequenceDiagram
    participant U as User
    participant TG as Telegram
    participant BOT as Bot
    participant API as FastAPI
    participant DB as Database
    
    U->>TG: Multi-line part list
    TG->>BOT: Bulk message received
    BOT->>BOT: Validate bulk limit
    BOT->>API: POST /search/bulk
    
    loop For each part
        API->>DB: Search part
        DB-->>API: Part data
    end
    
    API-->>BOT: Summarized results
    BOT->>TG: "Found X parts, confirm all?"
    TG->>U: Bulk confirmation
    
    U->>TG: "بله"
    TG->>BOT: Confirmation
    BOT->>TG: Request contact
    TG->>U: Contact sharing
    U->>TG: Share phone
    TG->>BOT: Contact data
    BOT->>API: POST /orders/bulk
    API->>DB: Save bulk order
    BOT->>TG: Order confirmation
    TG->>U: "سفارش شما ثبت شد"
```

#### Admin AI Toggle Flow
```mermaid
sequenceDiagram
    participant A as Admin
    participant PANEL as Admin Panel
    participant API as FastAPI
    participant DB as Database
    participant BOT as Bot
    
    A->>PANEL: Toggle AI search
    PANEL->>API: PUT /settings/ai-enabled
    API->>DB: UPDATE settings SET ai_enabled = true/false
    DB-->>API: Confirmation
    API-->>PANEL: Success response
    PANEL->>A: UI updated
    
    Note over DB,BOT: Setting takes effect immediately
    BOT->>API: Next search request
    API->>DB: SELECT ai_enabled FROM settings
    DB-->>API: Current setting
    API->>API: Route to AI or basic search
```

#### Excel Import Flow
```mermaid
sequenceDiagram
    participant A as Admin
    participant PANEL as Admin Panel
    participant API as FastAPI
    participant DB as Database
    
    A->>PANEL: Upload Excel file
    PANEL->>API: POST /import/excel
    API->>API: Validate file format
    API->>API: Parse Excel data
    API->>API: Validate data integrity
    
    loop For each part
        API->>DB: INSERT/UPDATE parts
        API->>DB: INSERT prices
        API->>DB: INSERT synonyms
    end
    
    API->>DB: Commit transaction
    DB-->>API: Import complete
    API-->>PANEL: Import summary
    PANEL->>A: Success notification
```

## 3. Data Flow

### Input/Output Flow
1. **Telegram Updates** → **Bot Handler** → **FastAPI Endpoints** → **Database** → **Response Processing** → **Telegram API**

### AI Search Bypass Logic
```mermaid
flowchart TD
    A[Search Request] --> B{AI Enabled?}
    B -->|Yes| C[AI Semantic Search]
    B -->|No| D[Basic/Fuzzy Search]
    C --> E[Rank & Filter Results]
    D --> E
    E --> F[Return Results]
    
    G[AI Service Error] --> D
    C --> G
```

### Rate Limiting & Caching Placement
- **Rate Limiting**: FastAPI middleware (IP + telegram_user_id based)
- **Caching**: In-memory cache for frequently searched parts
- **Cache Invalidation**: On price updates, new part additions

## 4. Backend Modules & Boundaries

### Service Boundaries
- **Search Module**
  - `search_basic`: Exact/OEM code matching
  - `search_fuzzy`: Levenshtein distance matching
  - `search_ai`: Semantic embedding search
  - `rank`: Result scoring and ranking

- **Data Management**
  - `importers`: Excel parsing and validation
  - `orders`: Order lifecycle management
  - `leads`: Customer data management
  - `settings`: Feature flag management

- **Authentication & Authorization**
  - `auth`: JWT token management
  - `roles`: Role-based access control

### API Gateway Structure
```
/api/v1/
├── /search/
│   ├── /parts (single search)
│   └── /bulk (bulk search)
├── /orders/
│   ├── / (CRUD operations)
│   └── /bulk (bulk order creation)
├── /leads/
│   └── / (customer management)
├── /import/
│   └── /excel (data import)
├── /admin/
│   ├── /settings (feature flags)
│   └── /users (user management)
└── /health (health checks)
```

### CORS & Versioning
- **CORS**: Configured for admin panel domain
- **Versioning**: URL path versioning (`/api/v1/`)
- **Content Negotiation**: JSON responses with Persian UTF-8 support

## 5. Database Layer

### Logical Schema Overview
```mermaid
erDiagram
    PARTS ||--o{ PRICES : has
    PARTS ||--o{ SYNONYMS : has
    PARTS ||--o{ ORDER_ITEMS : ordered_as
    LEADS ||--o{ ORDERS : creates
    ORDERS ||--o{ ORDER_ITEMS : contains
    USERS ||--o{ SETTINGS : manages
    
    PARTS {
        int id PK
        string name
        string oem_code
        string alt_code
        string category
        string vehicle_model
        text description
        datetime created_at
        datetime updated_at
    }
    
    PRICES {
        int id PK
        int part_id FK
        decimal price
        string currency
        string source
        datetime valid_from
        datetime valid_to
        boolean is_active
    }
    
    SYNONYMS {
        int id PK
        int part_id FK
        string keyword
        string language
    }
    
    LEADS {
        int id PK
        bigint telegram_user_id UK
        string phone_number
        string first_name
        string last_name
        string city
        text notes
        datetime created_at
        datetime updated_at
    }
    
    ORDERS {
        int id PK
        int lead_id FK
        string status
        text notes
        datetime created_at
        datetime updated_at
    }
    
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int part_id FK
        int quantity
        text notes
    }
    
    SETTINGS {
        int id PK
        string key UK
        string value
        text description
        int updated_by FK
        datetime updated_at
    }
    
    USERS {
        int id PK
        string username UK
        string email
        string role
        string password_hash
        datetime created_at
        datetime last_login
    }
```

### Migration Strategy
- **Phase 1**: SQLite for MVP development and testing
- **Phase 2**: PostgreSQL migration with data export/import scripts
- **Backup Strategy**: Daily SQLite dumps, automated backup scripts

### Indexing Strategy
- **Primary Indexes**: `parts.oem_code`, `parts.name`, `leads.telegram_user_id`
- **Search Indexes**: `parts.vehicle_model`, `synonyms.keyword`
- **Performance Indexes**: `prices.is_active`, `orders.created_at`

## 6. Security & Access Control

### Role-Based Access Control
- **Admin**: Full system access, user management, settings control
- **Operator**: Order management, customer support, basic data entry
- **Manager**: Reporting, oversight, limited admin functions

### Authentication Methods
- **Admin Panel**: JWT tokens with role claims
- **API Endpoints**: Bearer token authentication
- **Telegram Users**: One-time contact capture with `telegram_user_id` tracking

### Privacy & Data Protection
- **Minimal PII**: Phone number, city, name (first/last)
- **Data Retention**: Configurable retention policies
- **Encryption**: Sensitive data encrypted at rest

## 7. Configuration & Feature Flags

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///./parts_bot.db

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/webhook

# Admin
ADMIN_TELEGRAM_IDS=123456789,987654321
JWT_SECRET_KEY=your_secret_key

# AI/ML
AI_ENABLED=true
AI_MODEL_PATH=./models/embedding_model
AI_API_KEY=optional_external_api_key

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### Settings Table Configuration
- **Runtime Toggles**: AI_ENABLED, MAINTENANCE_MODE, BULK_LIMIT
- **Priority**: Database settings override environment variables
- **Hot Reload**: Settings changes take effect immediately

### AI Toggle Impact
- **AI ON**: Semantic search → ranking → results
- **AI OFF**: Basic/fuzzy search → results
- **Fallback**: AI errors automatically fall back to basic search

## 8. Observability & Operations

### Logging Strategy
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Daily rotation with compression

### Key Metrics
- **Search Performance**: Response time, success rate
- **User Engagement**: Daily active users, queries per user
- **Business Metrics**: Order conversion rate, lead quality
- **System Health**: Uptime, error rates, database performance

### Error Handling
- **Graceful Degradation**: AI failures → basic search
- **User-Friendly Messages**: Persian error messages
- **Admin Notifications**: Critical errors sent to admin Telegram

### Rate Limiting
- **Per User**: 10 searches/minute per telegram_user_id
- **Per IP**: 100 requests/minute
- **Bulk Queries**: Special limits (TBD based on testing)

## 9. Deployment Topology (MVP)

### Systemd Services
```ini
# /etc/systemd/system/parts-bot-api.service
[Unit]
Description=Chinese Parts Bot API
After=network.target

[Service]
Type=exec
User=partsbot
WorkingDirectory=/opt/parts-bot
ExecStart=/opt/parts-bot/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/parts-bot-telegram.service
[Unit]
Description=Chinese Parts Bot Telegram
After=network.target

[Service]
Type=exec
User=partsbot
WorkingDirectory=/opt/parts-bot
ExecStart=/opt/parts-bot/venv/bin/python telegram_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Caddy Configuration
```caddy
yourdomain.com {
    reverse_proxy /api/* localhost:8000
    reverse_proxy /admin/* localhost:3000
    
    tls your_email@domain.com
}
```

### Directory Layout
```
/opt/parts-bot/
├── app/
│   ├── api/
│   ├── models/
│   ├── services/
│   └── utils/
├── telegram_bot/
├── admin_panel/
├── migrations/
├── config/
├── logs/
├── data/
└── venv/
```

## 10. Internationalization & UX Notes

### Persian Language Support
- **Bot Messages**: All user-facing text in Persian
- **Confirmation Flow**: "آیا شما به دنبال [part_name] هستید؟"
- **Error Messages**: User-friendly Persian error messages
- **Admin Panel**: English interface with Persian data display

### Bulk Query UX
- **Max Lines**: Configurable limit (default TBD)
- **Validation**: Real-time validation of bulk input
- **Progress Indication**: "Processing X of Y parts..."

## 11. Risks & Mitigations

### Data Quality Risks
- **Risk**: Duplicate OEM codes, inconsistent naming
- **Mitigation**: Data validation rules, deduplication scripts

### Search Accuracy Risks
- **Risk**: False positives in fuzzy/AI search
- **Mitigation**: Confirmation flow, confidence scoring

### Scaling Risks
- **Risk**: SQLite limitations with growth
- **Mitigation**: Planned PostgreSQL migration, performance monitoring

### Abuse Prevention
- **Risk**: Spam, excessive API usage
- **Mitigation**: Rate limiting, admin moderation tools

## 12. Next Steps

### Immediate Decisions Needed
1. **Initial Data Source**: Excel template vs. sample generator vs. scraping
2. **Bulk Query Limits**: Maximum lines per request (5-50 range)
3. **Admin Panel Stack**: React/Vue/Vanilla JS preference
4. **AI Implementation**: Local embeddings vs. external API

### Development Phases
1. **Phase 1**: Core bot functionality with basic search
2. **Phase 2**: Admin panel and Excel import
3. **Phase 3**: AI search integration
4. **Phase 4**: Advanced features and optimization

### Post-MVP Considerations
- PostgreSQL migration
- Advanced analytics and reporting
- Multi-language support
- Mobile app development
- Integration with external APIs

---

*Document Version: 1.0*  
*Last Updated: Initial Creation*  
*Status: Draft - Awaiting Review*
