# 🚗 China Car Parts - Auto Parts Management System

A comprehensive auto parts management system with Telegram bot integration, web admin panel, and advanced analytics.

## 🌟 Features

### 🤖 Telegram Bot
- **Interactive Parts Search**: AI-powered part lookup with wizard interface
- **Multi-language Support**: Persian, English, and Chinese
- **Order Management**: Complete order processing workflow
- **Lead Generation**: Customer contact capture and management

### 🖥️ Web Admin Panel
- **Modern Vue.js Interface**: Responsive admin dashboard
- **Real-time Analytics**: Comprehensive business insights
- **Parts Management**: Full CRUD operations for parts catalog
- **User Management**: Role-based access control
- **Order Tracking**: Complete order lifecycle management

### 🔧 Backend API
- **FastAPI Framework**: High-performance REST API
- **SQLAlchemy ORM**: Robust database management
- **JWT Authentication**: Secure user authentication
- **Comprehensive Analytics**: Business intelligence and reporting
- **AI Gateway (Experimental)**: Centralized AI provider management with fallbacks

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (production) / SQLite (development)
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/oshaghisina/Cars-part.git
   cd Cars-part
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration
   
   # Run database migrations
   alembic upgrade head
   
   # Create admin user
   python create_admin_user.py
   
   # Start the API server
   uvicorn app.api.main:app --host 0.0.0.0 --port 8001 --reload
   ```

3. **Frontend Setup**
   ```bash
   cd app/frontend/panel
   npm install
   npm run dev
   ```

4. **Telegram Bot Setup**
   ```bash
   # In the main directory
   python -m app.bot.bot
   ```

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │   Web Admin     │    │   Mobile App    │
│   (aiogram)     │    │   (Vue.js)      │    │   (Future)      │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      FastAPI Backend      │
                    │   (REST API + WebSocket)  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │       Database Layer      │
                    │  (PostgreSQL + Redis)     │
                    └───────────────────────────┘
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Application
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///./app.db
# For PostgreSQL: postgresql://user:password@localhost/dbname

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_IDS=123456789,987654321

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
FRONTEND_ORIGIN=http://localhost:5173

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🚀 Deployment

### CI/CD Pipeline

This project includes a comprehensive CI/CD pipeline with:

- **Automated Testing**: Unit, integration, and E2E tests
- **Code Quality**: Linting, formatting, and security scanning
- **Multi-Environment**: Staging and production deployments
- **Blue-Green Deployment**: Zero-downtime deployments
- **Monitoring**: Health checks and performance monitoring

### Deployment Commands

```bash
# Staging deployment
git push origin staging

# Production deployment
git push origin main

# Manual deployment
./deployment/scripts/deploy-staging.sh
./deployment/scripts/blue-green-deploy.sh
```

## 📈 Monitoring & Analytics

### Available Metrics
- **Business Metrics**: Revenue, orders, parts, leads
- **Performance Metrics**: API response times, uptime
- **User Analytics**: Customer behavior, conversion rates
- **System Health**: Database performance, bot activity

### Dashboard Access
- **Admin Panel**: http://localhost:5173
- **API Documentation**: http://localhost:8001/docs
- **Analytics**: Available in the admin panel

## 🔒 Security

- **JWT Authentication**: Secure API access
- **Role-based Access**: Admin and user permissions
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: Parameterized queries
- **CORS Configuration**: Secure cross-origin requests

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=app

# Frontend tests
cd app/frontend/panel
npm test
```

## 📚 API Documentation

### Authentication
```bash
# Login
POST /api/v1/users/login
{
  "username_or_email": "admin",
  "password": "password"
}

# Get current user
GET /api/v1/users/me
Authorization: Bearer <token>
```

### Parts Management
```bash
# Search parts
GET /api/v1/search/parts?q=brake+pad

# Get part details
GET /api/v1/parts/{part_id}

# Create new part
POST /api/v1/parts/
```

### Orders
```bash
# List orders
GET /api/v1/orders/

# Create order
POST /api/v1/orders/
{
  "lead_id": 1,
  "items": [
    {
      "part_id": 1,
      "quantity": 2
    }
  ]
}
```

## 🔬 AI Gateway (Experimental)

The AI Gateway is a centralized system for managing AI providers, policies, and fallbacks. It's currently in scaffold mode and requires explicit feature flags to enable.

### Configuration

Add these environment variables to enable AI Gateway features:

```bash
# AI Gateway Configuration
AI_GATEWAY_ENABLED=false              # Master toggle for AI Gateway
AI_GATEWAY_EXPERIMENTAL=false         # Enable experimental features
AI_FALLBACK_ENABLED=true              # Enable fallback mechanisms
AI_FALLBACK_ORDER=openai,local,heuristic,basic  # Fallback sequence
AI_LOG_PROMPTS_MASKED=true            # Mask PII in logs
AI_RATE_LIMIT_PER_USER=20             # Rate limit per user
AI_BUDGET_DAILY=20                    # Daily budget limit
AI_OPENAI_API_KEY=                    # OpenAI API key
AI_OPENAI_MODEL=gpt-4o-mini           # OpenAI model
AI_OPENAI_TIMEOUT=5                   # Request timeout
AI_OPENAI_MAX_RETRIES=3               # Max retries
```

### Current Status

The AI Gateway is currently in **scaffold mode** with the following components:

- **Providers**: Abstract interfaces and stub implementations
- **Orchestrator**: Skeleton for task coordination
- **Context Builder**: Placeholder for PII sanitization
- **Normalizer**: Response standardization framework
- **Policy Engine**: Configuration management structure
- **Fallbacks**: Local processing framework
- **Admin API**: Read-only endpoints (when experimental mode enabled)

### Implementation Plan

See `/docs/ai/implementation-plan.md` for the complete rollout strategy across 9 epics (E1-E9).

**⚠️ Note**: This is scaffold-only code with no behavior changes. All methods raise `NotImplementedError` until implemented in their respective epics.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](https://github.com/oshaghisina/Cars-part/wiki)
- **Issues**: [GitHub Issues](https://github.com/oshaghisina/Cars-part/issues)
- **Discussions**: [GitHub Discussions](https://github.com/oshaghisina/Cars-part/discussions)

## 🏗️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced AI search capabilities
- [ ] Multi-tenant support
- [ ] Real-time notifications
- [ ] Advanced reporting and analytics
- [ ] Integration with external suppliers

## 📊 Project Status

![CI/CD](https://github.com/oshaghisina/Cars-part/workflows/CI/badge.svg)
![Security](https://github.com/oshaghisina/Cars-part/workflows/Security/badge.svg)
![Performance](https://github.com/oshaghisina/Cars-part/workflows/Performance/badge.svg)

---

**Built with ❤️ for the automotive industry**# Fixed environment configuration
