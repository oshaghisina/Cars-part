# 🚀 Real Production Server Deployment Guide

This guide will walk you through deploying the China Car Parts application to a real production server.

## Prerequisites

### 1. Server Requirements
- **OS**: Ubuntu 22.04 LTS (recommended)
- **RAM**: 8GB+ (16GB recommended for production)
- **CPU**: 4+ cores
- **Storage**: 100GB+ SSD
- **Network**: Public IP with ports 80, 443, 22 open

### 2. Domain & DNS
- Domain name (e.g., `yourdomain.com`)
- DNS A record pointing to your server IP
- SSL certificate (Let's Encrypt will be configured automatically)

### 3. Required Accounts
- GitHub repository access
- Telegram Bot Token (from @BotFather)
- OpenAI API Key (optional, for AI features)
- Server SSH access

## Step 1: Server Setup

### 1.1 Connect to Your Server
```bash
ssh root@your-server-ip
```

### 1.2 Download and Run Setup Script
```bash
# Download the setup script
wget https://raw.githubusercontent.com/your-org/china-car-parts/main/setup_production_server.sh

# Make it executable
chmod +x setup_production_server.sh

# Run the setup (replace with your domain)
./setup_production_server.sh yourdomain.com https://github.com/your-org/china-car-parts.git
```

### 1.3 Configure Environment Variables
After setup, edit the production environment file:
```bash
nano /opt/china-car-parts/.env
```

Update the following values:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_actual_bot_token_from_botfather
ADMIN_TELEGRAM_IDS=your_telegram_user_id

# AI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key

# Database password (already generated)
# DATABASE_URL=postgresql://partsbot:generated_password@localhost:5432/china_car_parts_production
```

## Step 2: Initial Deployment

### 2.1 Run Database Migrations
```bash
cd /opt/china-car-parts
source venv/bin/activate
alembic upgrade head
```

### 2.2 Start Services
```bash
systemctl start china-car-parts-api
systemctl start china-car-parts-bot
```

### 2.3 Check Service Status
```bash
systemctl status china-car-parts-api
systemctl status china-car-parts-bot
```

### 2.4 Verify Deployment
```bash
# Check API health
curl https://yourdomain.com/api/v1/health

# Check if services are running
systemctl is-active china-car-parts-api china-car-parts-bot
```

## Step 3: Ongoing Deployments

### 3.1 Deploy from Local Machine
From your local development machine:

```bash
# Set environment variables
export PROD_HOST=yourdomain.com
export PROD_USER=partsbot

# Run deployment
./deploy_to_production.sh
```

### 3.2 Deploy from CI/CD
The deployment can be automated through GitHub Actions. See `.github/workflows/deploy.yml` for the CI/CD configuration.

## Step 4: Monitoring & Maintenance

### 4.1 View Logs
```bash
# API logs
journalctl -u china-car-parts-api -f

# Bot logs
journalctl -u china-car-parts-bot -f

# Application logs
tail -f /var/log/china-car-parts/api.log
```

### 4.2 Service Management
```bash
# Restart services
systemctl restart china-car-parts-api
systemctl restart china-car-parts-bot

# Stop services
systemctl stop china-car-parts-api
systemctl stop china-car-parts-bot

# Check service status
systemctl status china-car-parts-api china-car-parts-bot
```

### 4.3 Database Management
```bash
# Create backup
pg_dump china_car_parts_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql china_car_parts_production < backup_file.sql
```

## Step 5: Security Considerations

### 5.1 Firewall
The setup script configures UFW with:
- SSH (port 22)
- HTTP (port 80)
- HTTPS (port 443)
- API (port 8001, internal only)

### 5.2 SSL/TLS
- Let's Encrypt certificates are automatically configured
- Auto-renewal is set up via cron
- HTTPS redirect is configured in Nginx

### 5.3 Fail2ban
- SSH brute force protection
- Nginx attack protection
- Automatic IP blocking

## Step 6: Troubleshooting

### 6.1 Common Issues

**Service won't start:**
```bash
# Check service status
systemctl status china-car-parts-api

# Check logs
journalctl -u china-car-parts-api -n 50

# Check configuration
nginx -t
```

**Database connection issues:**
```bash
# Check PostgreSQL status
systemctl status postgresql

# Check database connection
sudo -u postgres psql -c "SELECT 1;"
```

**SSL certificate issues:**
```bash
# Check certificate status
certbot certificates

# Renew certificate
certbot renew --dry-run
```

### 6.2 Performance Monitoring
```bash
# Check system resources
htop

# Check disk usage
df -h

# Check memory usage
free -h

# Check database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

## Step 7: Backup Strategy

### 7.1 Automated Backups
The system automatically creates database backups before each deployment. Backups are stored in `/opt/backups/china-car-parts/`.

### 7.2 Manual Backups
```bash
# Create manual backup
pg_dump china_car_parts_production > /opt/backups/manual_backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip /opt/backups/manual_backup_*.sql
```

### 7.3 Backup Restoration
```bash
# Stop services
systemctl stop china-car-parts-api china-car-parts-bot

# Restore database
gunzip -c backup_file.sql.gz | psql china_car_parts_production

# Start services
systemctl start china-car-parts-api china-car-parts-bot
```

## Step 8: Scaling Considerations

### 8.1 Load Balancer
For high traffic, consider setting up a load balancer (HAProxy, Nginx, or cloud load balancer).

### 8.2 Database Scaling
- Read replicas for read-heavy operations
- Connection pooling
- Database clustering

### 8.3 Caching
- Redis for session storage
- CDN for static assets
- Application-level caching

## Step 9: Maintenance

### 9.1 Regular Updates
```bash
# Update system packages
apt update && apt upgrade -y

# Update application dependencies
cd /opt/china-car-parts
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 9.2 Log Rotation
Logs are automatically rotated daily and kept for 30 days.

### 9.3 Security Updates
- Keep system packages updated
- Monitor security advisories
- Regular security audits

## Support

If you encounter issues during deployment:

1. Check the logs: `journalctl -u china-car-parts-api -f`
2. Verify configuration: `nginx -t`
3. Check service status: `systemctl status china-car-parts-api`
4. Review the troubleshooting section above

For additional support, please refer to the project documentation or create an issue in the GitHub repository.
