# 🌍 Environment Configuration

## Environment Strategy

### **Development** (Local)
- **Purpose**: Local development and testing
- **Database**: SQLite (`data/development.db`)
- **API Port**: 8001
- **Frontend Port**: 5173
- **Bot**: Development token
- **Features**: Hot reload, debug mode, verbose logging

### **Staging** (Mirror of Production)
- **Purpose**: Pre-production testing and validation
- **Database**: PostgreSQL (`china_car_parts_staging`)
- **Domain**: `staging.yourdomain.com`
- **API Port**: 8001
- **Features**: Production-like setup, test data, monitoring

### **Production** (Live System)
- **Purpose**: Live production environment
- **Database**: PostgreSQL (`china_car_parts`)
- **Domain**: `yourdomain.com`
- **API Port**: 8001
- **Features**: Optimized performance, security hardening, monitoring

## Environment Variables

### **Development**
```bash
APP_ENV=development
DEBUG=true
DATABASE_URL=sqlite:///./data/development.db
TELEGRAM_BOT_TOKEN=your_dev_bot_token
SECRET_KEY=dev_secret_key_not_secure
FRONTEND_ORIGIN=http://localhost:5173
```

### **Staging**
```bash
APP_ENV=staging
DEBUG=false
DATABASE_URL=postgresql://user:pass@localhost:5432/china_car_parts_staging
TELEGRAM_BOT_TOKEN=your_staging_bot_token
SECRET_KEY=staging_secret_key_secure
FRONTEND_ORIGIN=https://staging.yourdomain.com
ADMIN_TELEGRAM_IDS=176007160
```

### **Production**
```bash
APP_ENV=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@localhost:5432/china_car_parts
TELEGRAM_BOT_TOKEN=your_production_bot_token
SECRET_KEY=production_secret_key_very_secure
FRONTEND_ORIGIN=https://yourdomain.com
ADMIN_TELEGRAM_IDS=176007160,additional_admin_ids
```

## Server Configuration

### **Staging Server**
- **Host**: `staging.yourdomain.com` or separate IP
- **Services**:
  - `china-car-parts-api-staging.service`
  - `china-car-parts-bot-staging.service`
- **Database**: Separate PostgreSQL instance
- **Nginx**: Separate virtual host

### **Production Server**
- **Host**: `yourdomain.com`
- **Services**:
  - `china-car-parts-api.service`
  - `china-car-parts-bot.service`
- **Database**: Production PostgreSQL instance
- **Nginx**: Main virtual host with SSL

## Deployment Flow

```
feature/* → develop → staging → main (production)
     ↓         ↓         ↓         ↓
   Local    Develop   Staging   Production
```

## Health Check Endpoints

- **Development**: `http://localhost:8001/health`
- **Staging**: `https://staging.yourdomain.com/api/v1/health`
- **Production**: `https://yourdomain.com/api/v1/health`

## Monitoring & Logging

### **Development**
- Console logging
- Debug information
- Hot reload enabled

### **Staging**
- File logging
- Error tracking
- Performance monitoring

### **Production**
- Structured logging
- Error alerting
- Performance metrics
- Uptime monitoring
