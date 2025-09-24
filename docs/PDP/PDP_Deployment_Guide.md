# Product Detail Page (PDP) - Deployment Guide

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Database Configuration](#database-configuration)
- [Frontend Build & Deployment](#frontend-build--deployment)
- [Backend Deployment](#backend-deployment)
- [Reverse Proxy Configuration](#reverse-proxy-configuration)
- [SSL/TLS Setup](#ssltls-setup)
- [Monitoring & Logging](#monitoring--logging)
- [Performance Optimization](#performance-optimization)
- [Security Hardening](#security-hardening)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)

## Overview

This guide covers deploying the PDP to production environments with high availability, security, and performance considerations.

### Architecture Diagram
```
Internet → Load Balancer → Reverse Proxy (Caddy) → Frontend (Vue.js)
                                                 → Backend (FastAPI)
                                                 → Database (PostgreSQL)
                                                 → Redis (Cache)
```

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Amazon Linux 2
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Storage**: 50GB+ SSD
- **Network**: Public IP with ports 80, 443 open

### Software Dependencies
- **Node.js**: v18+ (for frontend build)
- **Python**: 3.9+
- **PostgreSQL**: 13+
- **Redis**: 6+
- **Caddy**: 2.6+ (reverse proxy)
- **Git**: Latest version

## Environment Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git build-essential software-properties-common

# Install Node.js (using NodeSource repository)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Redis
sudo apt install -y redis-server

# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

### 2. User Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash carparts
sudo usermod -aG sudo carparts

# Switch to application user
sudo su - carparts

# Create application directory
mkdir -p /home/carparts/app
cd /home/carparts/app
```

### 3. Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/china-car-parts.git .

# Set up environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Database Configuration

### 1. PostgreSQL Setup

```bash
# Switch to postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE carparts_prod;
CREATE USER carparts_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE carparts_prod TO carparts_user;
ALTER USER carparts_user CREATEDB;
\q
```

### 2. Database Configuration

```bash
# Create production environment file
cat > /home/carparts/app/env/production.env << 'EOF'
# Database
DATABASE_URL=postgresql://carparts_user:your_secure_password@localhost/carparts_prod
DB_HOST=localhost
DB_PORT=5432
DB_NAME=carparts_prod
DB_USER=carparts_user
DB_PASSWORD=your_secure_password

# Security
SECRET_KEY=your_super_secret_key_here_64_chars_minimum_for_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["https://your-domain.com"]

# Environment
ENVIRONMENT=production
DEBUG=false

# Redis
REDIS_URL=redis://localhost:6379/0

# File Storage
UPLOAD_DIR=/home/carparts/app/uploads
MAX_FILE_SIZE=10485760  # 10MB

# External Services
SMTP_SERVER=smtp.your-email-provider.com
SMTP_PORT=587
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your_email_password

# Frontend URL
FRONTEND_URL=https://your-domain.com
EOF

# Secure the environment file
chmod 600 /home/carparts/app/env/production.env
```

### 3. Run Database Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Set environment
export ENV_FILE=/home/carparts/app/env/production.env

# Run migrations
python -m alembic upgrade head

# Create initial admin user
python create_admin_user.py
```

## Frontend Build & Deployment

### 1. Build Frontend

```bash
# Navigate to frontend directory
cd /home/carparts/app/app/frontend/web

# Install dependencies
npm ci --production

# Create production environment file
cat > .env.production << 'EOF'
VITE_API_BASE_URL=https://your-domain.com/api
VITE_FRONTEND_URL=https://your-domain.com
VITE_ENVIRONMENT=production
VITE_ANALYTICS_ID=your_analytics_id
VITE_SENTRY_DSN=your_sentry_dsn
EOF

# Build for production
npm run build

# Copy built files to web server directory
sudo mkdir -p /var/www/carparts
sudo cp -r dist/* /var/www/carparts/
sudo chown -R www-data:www-data /var/www/carparts
```

### 2. Optimize Build

```bash
# Analyze bundle (optional)
npm run build:analyze

# Generate service worker for caching
npm install -D vite-plugin-pwa
# Add PWA plugin to vite.config.js
```

## Backend Deployment

### 1. Install Dependencies

```bash
# Navigate to project root
cd /home/carparts/app

# Install production dependencies
pip install -r requirements.txt

# Install additional production packages
pip install gunicorn uvicorn[standard] psycopg2-binary redis
```

### 2. Create Systemd Services

#### API Service
```bash
sudo tee /etc/systemd/system/carparts-api.service << 'EOF'
[Unit]
Description=China Car Parts API
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=carparts
Group=carparts
WorkingDirectory=/home/carparts/app
Environment=PATH=/home/carparts/app/venv/bin
Environment=ENV_FILE=/home/carparts/app/env/production.env
ExecStart=/home/carparts/app/venv/bin/gunicorn app.api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8001
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

#### Bot Service (if applicable)
```bash
sudo tee /etc/systemd/system/carparts-bot.service << 'EOF'
[Unit]
Description=China Car Parts Telegram Bot
After=network.target carparts-api.service

[Service]
Type=simple
User=carparts
Group=carparts
WorkingDirectory=/home/carparts/app
Environment=PATH=/home/carparts/app/venv/bin
Environment=ENV_FILE=/home/carparts/app/env/production.env
ExecStart=/home/carparts/app/venv/bin/python -m app.bot.bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### 3. Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable carparts-api.service
sudo systemctl enable carparts-bot.service

# Start services
sudo systemctl start carparts-api.service
sudo systemctl start carparts-bot.service

# Check status
sudo systemctl status carparts-api.service
sudo systemctl status carparts-bot.service
```

## Reverse Proxy Configuration

### Caddy Configuration

```bash
sudo tee /etc/caddy/Caddyfile << 'EOF'
{
    # Global options
    email your-email@domain.com
    admin off
}

your-domain.com {
    # Enable GZIP compression
    encode gzip

    # Security headers
    header {
        # Security headers
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        X-XSS-Protection "1; mode=block"
        Referrer-Policy strict-origin-when-cross-origin
        Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-src 'none';"
        
        # Remove server info
        -Server
    }

    # API routes
    handle /api/* {
        reverse_proxy 127.0.0.1:8001 {
            header_up Host {host}
            header_up X-Real-IP {remote_host}
            header_up X-Forwarded-For {remote_host}
            header_up X-Forwarded-Proto {scheme}
        }
    }

    # Health check endpoint
    handle /health {
        reverse_proxy 127.0.0.1:8001
    }

    # Static file serving with cache headers
    handle /assets/* {
        root * /var/www/carparts
        file_server
        header Cache-Control "public, max-age=31536000, immutable"
    }

    # Frontend SPA
    handle {
        root * /var/www/carparts
        file_server
        try_files {path} /index.html
        
        # Cache static assets
        @static {
            path *.js *.css *.png *.jpg *.jpeg *.gif *.ico *.svg *.woff *.woff2
        }
        header @static Cache-Control "public, max-age=31536000, immutable"
        
        # No cache for HTML
        @html {
            path *.html
        }
        header @html Cache-Control "no-cache, no-store, must-revalidate"
    }

    # Logging
    log {
        output file /var/log/caddy/carparts.log {
            roll_size 100mb
            roll_keep 5
        }
        format json
    }
}

# HTTP to HTTPS redirect
http://your-domain.com {
    redir https://your-domain.com{uri} permanent
}
EOF

# Test configuration
sudo caddy validate --config /etc/caddy/Caddyfile

# Restart Caddy
sudo systemctl restart caddy
sudo systemctl enable caddy
```

## SSL/TLS Setup

Caddy automatically handles SSL/TLS certificates via Let's Encrypt. For manual certificate management:

```bash
# Generate self-signed certificate (development only)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/carparts.key \
    -out /etc/ssl/certs/carparts.crt

# For production, use Let's Encrypt with Caddy (automatic)
# Or manually with certbot:
sudo apt install -y certbot
sudo certbot certonly --standalone -d your-domain.com
```

## Monitoring & Logging

### 1. Log Configuration

```bash
# Create log directory
sudo mkdir -p /var/log/carparts
sudo chown carparts:carparts /var/log/carparts

# Configure log rotation
sudo tee /etc/logrotate.d/carparts << 'EOF'
/var/log/carparts/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 carparts carparts
    postrotate
        sudo systemctl reload carparts-api.service
    endscript
}
EOF
```

### 2. Health Monitoring

```bash
# Create health check script
tee /home/carparts/health_check.sh << 'EOF'
#!/bin/bash

# API Health Check
api_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health)
if [ "$api_status" != "200" ]; then
    echo "API is down! Status: $api_status" | logger -t carparts-health
    # Send alert (email, Slack, etc.)
fi

# Database Health Check
db_status=$(sudo -u postgres psql -d carparts_prod -c "SELECT 1;" -t -A 2>/dev/null)
if [ "$db_status" != "1" ]; then
    echo "Database is down!" | logger -t carparts-health
fi

# Redis Health Check
redis_status=$(redis-cli ping 2>/dev/null)
if [ "$redis_status" != "PONG" ]; then
    echo "Redis is down!" | logger -t carparts-health
fi
EOF

chmod +x /home/carparts/health_check.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/carparts/health_check.sh") | crontab -
```

### 3. Performance Monitoring

```bash
# Install htop for system monitoring
sudo apt install -y htop

# Setup monitoring with Prometheus (optional)
sudo apt install -y prometheus prometheus-node-exporter
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Connect to PostgreSQL
sudo -u postgres psql carparts_prod

-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_parts_category ON parts(category);
CREATE INDEX CONCURRENTLY idx_parts_brand ON parts(brand);
CREATE INDEX CONCURRENTLY idx_parts_sku ON parts(sku);
CREATE INDEX CONCURRENTLY idx_parts_active ON parts(is_active);

-- Update statistics
ANALYZE;

-- Configure PostgreSQL for production
-- Edit /etc/postgresql/13/main/postgresql.conf
```

```bash
# PostgreSQL tuning
sudo tee -a /etc/postgresql/13/main/postgresql.conf << 'EOF'
# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connection settings
max_connections = 100

# WAL settings
wal_level = replica
max_wal_size = 1GB
min_wal_size = 80MB

# Logging
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
EOF

sudo systemctl restart postgresql
```

### 2. Redis Configuration

```bash
# Configure Redis for production
sudo tee -a /etc/redis/redis.conf << 'EOF'
# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Network
bind 127.0.0.1
protected-mode yes
EOF

sudo systemctl restart redis-server
```

### 3. System Optimization

```bash
# Increase file limits
sudo tee -a /etc/security/limits.conf << 'EOF'
carparts soft nofile 65536
carparts hard nofile 65536
EOF

# Kernel parameters
sudo tee -a /etc/sysctl.conf << 'EOF'
# Network tuning
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 1024
net.core.netdev_max_backlog = 5000

# Memory management
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
EOF

sudo sysctl -p
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Install and configure UFW
sudo apt install -y ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow necessary ports
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### 2. SSH Hardening

```bash
# Edit SSH configuration
sudo tee -a /etc/ssh/sshd_config << 'EOF'
# Security settings
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
PermitEmptyPasswords no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
EOF

sudo systemctl restart ssh
```

### 3. Application Security

```bash
# Set secure file permissions
sudo chmod 750 /home/carparts/app
sudo chmod 600 /home/carparts/app/env/production.env

# Setup fail2ban for additional protection
sudo apt install -y fail2ban

sudo tee /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true

[caddy-auth]
enabled = true
filter = caddy-auth
logpath = /var/log/caddy/carparts.log
maxretry = 5
EOF
```

## Backup & Recovery

### 1. Database Backup

```bash
# Create backup script
tee /home/carparts/backup_db.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/carparts/backups/db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="carparts_backup_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -h localhost -U carparts_user -d carparts_prod > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Database backup completed: $BACKUP_FILE.gz"
EOF

chmod +x /home/carparts/backup_db.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /home/carparts/backup_db.sh") | crontab -
```

### 2. File Backup

```bash
# Create file backup script
tee /home/carparts/backup_files.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/carparts/backups/files"
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE_DIR="/home/carparts/app"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create tar backup excluding unnecessary files
tar --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='node_modules' \
    --exclude='*.log' \
    --exclude='data/app.db' \
    -czf $BACKUP_DIR/carparts_files_$DATE.tar.gz \
    $SOURCE_DIR

# Remove backups older than 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "File backup completed: carparts_files_$DATE.tar.gz"
EOF

chmod +x /home/carparts/backup_files.sh
```

## Troubleshooting

### Common Issues

#### 1. Service Not Starting
```bash
# Check service status
sudo systemctl status carparts-api.service

# Check logs
sudo journalctl -u carparts-api.service -f

# Check application logs
tail -f /var/log/carparts/*.log
```

#### 2. Database Connection Issues
```bash
# Test database connection
sudo -u postgres psql -d carparts_prod -c "SELECT version();"

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

#### 3. Frontend Not Loading
```bash
# Check Caddy logs
sudo tail -f /var/log/caddy/carparts.log

# Test API connectivity
curl -I http://localhost:8001/health

# Check file permissions
ls -la /var/www/carparts/
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
sudo caddy list-certificates

# Force certificate renewal
sudo caddy reload --config /etc/caddy/Caddyfile
```

### Performance Issues

#### 1. High CPU Usage
```bash
# Check process usage
top -p $(pgrep -f "carparts")

# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8001/api/v1/health"
```

#### 2. Memory Issues
```bash
# Check memory usage
free -h
sudo ps aux --sort=-%mem | head

# Check for memory leaks
sudo journalctl -u carparts-api.service | grep -i memory
```

#### 3. Database Performance
```sql
-- Check slow queries
SELECT query, mean_time, calls, total_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check index usage
SELECT schemaname,tablename,attname,n_distinct,correlation 
FROM pg_stats 
WHERE tablename = 'parts';
```

## Maintenance Tasks

### Weekly Maintenance
```bash
#!/bin/bash
# weekly_maintenance.sh

# Update system packages
sudo apt update && sudo apt upgrade -y

# Restart services
sudo systemctl restart carparts-api.service
sudo systemctl restart carparts-bot.service

# Clean old logs
sudo find /var/log -name "*.log" -mtime +30 -delete

# Vacuum database
sudo -u postgres psql carparts_prod -c "VACUUM ANALYZE;"

echo "Weekly maintenance completed: $(date)"
```

### Monthly Maintenance
```bash
#!/bin/bash
# monthly_maintenance.sh

# Full database vacuum
sudo -u postgres psql carparts_prod -c "VACUUM FULL;"

# Update SSL certificates (if manual)
sudo certbot renew

# Security updates
sudo apt update && sudo apt upgrade -y

# Clear Redis cache
redis-cli FLUSHDB

echo "Monthly maintenance completed: $(date)"
```

---

*This deployment guide covers a complete production setup. Adapt the configurations based on your specific infrastructure requirements and security policies.*
