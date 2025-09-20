# Production Environment Setup Guide

This guide provides comprehensive instructions for setting up the China Car Parts application in a production environment with blue-green deployment capabilities.

## 🏗️ Architecture Overview

The production environment uses a **blue-green deployment strategy** for zero-downtime deployments:

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    │     (Nginx)     │
                    └─────────┬───────┘
                              │
                    ┌─────────┴───────┐
                    │  Blue Environment│
                    │   Port: 8001    │
                    └─────────┬───────┘
                              │
                    ┌─────────┴───────┐
                    │ Green Environment│
                    │   Port: 8002    │
                    └─────────────────┘
```

## 📋 Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **CPU**: 4+ cores
- **RAM**: 8GB+ (16GB recommended)
- **Storage**: 100GB+ SSD
- **Network**: Public IP with SSL certificate

### Software Requirements
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Nginx 1.18+
- Git
- Systemd

## 🚀 Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/china-car-parts.git /opt/china-car-parts
cd /opt/china-car-parts
```

### 2. Run Setup Script
```bash
sudo ./deployment/scripts/setup-production-environment.sh
```

### 3. Configure Environment
```bash
# Copy production environment configuration
sudo cp deployment/configs/production.env /opt/china-car-parts/.env

# Edit configuration with your values
sudo nano /opt/china-car-parts/.env
```

### 4. Start Services
```bash
# Start blue environment
sudo ./deployment/scripts/blue-green-deploy.sh --deploy $(git rev-parse HEAD)
```

## 🔧 Manual Setup

### 1. System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    curl wget git unzip \
    software-properties-common \
    apt-transport-https ca-certificates gnupg \
    build-essential libssl-dev libffi-dev \
    python3.11 python3.11-venv python3.11-dev \
    nginx postgresql postgresql-contrib \
    supervisor htop vim jq bc rsync
```

### 2. Python Environment

```bash
# Create virtual environment
python3.11 -m venv /opt/china-car-parts/venv
source /opt/china-car-parts/venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Node.js Environment

```bash
# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Build frontend
cd /opt/china-car-parts/app/frontend/panel
npm ci
npm run build
```

### 4. Database Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE china_car_parts_production;
CREATE USER partsbot WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE china_car_parts_production TO partsbot;
ALTER USER partsbot CREATEDB;
\q
EOF

# Run migrations
cd /opt/china-car-parts
source venv/bin/activate
alembic upgrade head
```

### 5. Systemd Services

```bash
# Copy service files
sudo cp deployment/configs/china-car-parts-api.service /etc/systemd/system/
sudo cp deployment/configs/china-car-parts-bot.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable china-car-parts-api-blue
sudo systemctl enable china-car-parts-bot-blue
```

### 6. Nginx Configuration

```bash
# Copy Nginx configuration
sudo cp deployment/configs/nginx-production.conf /etc/nginx/sites-available/china-car-parts

# Create symlink
sudo ln -sf /etc/nginx/sites-available/china-car-parts /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 🔄 Blue-Green Deployment

### Deploy New Version
```bash
# Deploy specific commit
./deployment/scripts/blue-green-deploy.sh --deploy abc1234

# Deploy latest commit
./deployment/scripts/blue-green-deploy.sh --deploy $(git rev-parse HEAD)
```

### Switch Environments
```bash
# Switch from blue to green (or vice versa)
./deployment/scripts/blue-green-deploy.sh --switch
```

### Rollback
```bash
# Rollback to previous environment
./deployment/scripts/blue-green-deploy.sh --rollback
```

### Check Status
```bash
# Show current deployment status
./deployment/scripts/blue-green-deploy.sh --status
```

## 📊 Monitoring

### Run Monitoring Checks
```bash
# Full monitoring check
./deployment/scripts/production-monitor.sh --monitor

# Check specific components
./deployment/scripts/production-monitor.sh --health
./deployment/scripts/production-monitor.sh --services
./deployment/scripts/production-monitor.sh --resources
./deployment/scripts/production-monitor.sh --database
```

### Set Up Automated Monitoring
```bash
# Add to crontab for monitoring every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/china-car-parts/deployment/scripts/production-monitor.sh --monitor") | crontab -
```

## 🔒 Security Configuration

### SSL Certificate
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall Configuration
```bash
# Configure UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 8001  # Blue environment
sudo ufw allow 8002  # Green environment
sudo ufw enable
```

### User Permissions
```bash
# Create application user
sudo useradd -r -s /bin/bash -d /opt/china-car-parts partsbot
sudo usermod -a -G partsbot partsbot

# Set ownership
sudo chown -R partsbot:partsbot /opt/china-car-parts
sudo chmod 600 /opt/china-car-parts/.env
```

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check service status
sudo systemctl status china-car-parts-api-blue

# Check logs
sudo journalctl -u china-car-parts-api-blue -f

# Check configuration
sudo nginx -t
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
sudo -u postgres psql -c "SELECT 1;"

# Check user permissions
sudo -u postgres psql -c "SELECT * FROM pg_user WHERE usename='partsbot';"
```

#### High Resource Usage
```bash
# Check system resources
htop
df -h
free -h

# Check process usage
ps aux | grep china-car-parts
```

### Log Locations
- **Application Logs**: `/var/log/china-car-parts-production/`
- **Nginx Logs**: `/var/log/nginx/`
- **Systemd Logs**: `journalctl -u china-car-parts-api-*`
- **PostgreSQL Logs**: `/var/log/postgresql/`

## 📈 Performance Optimization

### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX CONCURRENTLY idx_parts_name ON parts(name);
CREATE INDEX CONCURRENTLY idx_parts_category ON parts(category_id);
CREATE INDEX CONCURRENTLY idx_orders_created_at ON orders(created_at);
```

### Nginx Optimization
```nginx
# Add to nginx.conf
worker_processes auto;
worker_connections 1024;

# Enable gzip compression
gzip on;
gzip_types text/plain application/json application/javascript text/css;
```

### Application Optimization
```python
# Set worker count based on CPU cores
workers = min(32, (os.cpu_count() or 1) + 1)

# Enable connection pooling
DATABASE_POOL_SIZE = 50
DATABASE_MAX_OVERFLOW = 100
```

## 🔄 Backup Strategy

### Database Backup
```bash
# Create backup script
sudo nano /usr/local/bin/backup-database.sh

#!/bin/bash
pg_dump -h localhost -U partsbot china_car_parts_production > /opt/backups/db_backup_$(date +%Y%m%d_%H%M%S).sql

# Add to crontab (daily at 2 AM)
0 2 * * * /usr/local/bin/backup-database.sh
```

### Application Backup
```bash
# Create backup script
sudo nano /usr/local/bin/backup-application.sh

#!/bin/bash
tar -czf /opt/backups/app_backup_$(date +%Y%m%d_%H%M%S).tar.gz /opt/china-car-parts

# Add to crontab (weekly on Sunday at 3 AM)
0 3 * * 0 /usr/local/bin/backup-application.sh
```

## 📞 Support

For issues and support:
- **Documentation**: Check this guide and inline comments
- **Logs**: Check application and system logs
- **Monitoring**: Use the production monitoring script
- **Health Checks**: Verify all services are running

## 🎯 Next Steps

After successful setup:
1. **Test the deployment** with a sample commit
2. **Set up monitoring alerts** (Slack, email)
3. **Configure automated backups**
4. **Set up log rotation**
5. **Implement disaster recovery procedures**
6. **Schedule regular security updates**

---

**Production Environment Setup Complete!** 🎉

Your China Car Parts application is now running in a production environment with:
- ✅ Blue-green deployment capability
- ✅ Load balancing and high availability
- ✅ Comprehensive monitoring and alerting
- ✅ Security hardening and SSL
- ✅ Automated backups and recovery
- ✅ Performance optimization
