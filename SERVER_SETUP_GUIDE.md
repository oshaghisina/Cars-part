# 🖥️ Production Server Setup Guide

This guide will help you set up your production server for the China Car Parts application.

## 📋 Server Information

- **Server IP**: 5.223.59.155
- **Username**: root
- **Operating System**: Linux (Ubuntu/CentOS)
- **Purpose**: Production deployment for China Car Parts

## 🔧 Server Setup Steps

### 1. Initial Server Configuration

Connect to your server and run the following commands:

```bash
# Connect to server
ssh root@5.223.59.155

# Update system packages
apt update && apt upgrade -y  # For Ubuntu/Debian
# OR
yum update -y  # For CentOS/RHEL

# Install essential packages
apt install -y curl wget git nginx python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib redis-server ufw fail2ban htop
```

### 2. Create Application User

```bash
# Create dedicated user for the application
adduser partsbot
usermod -aG sudo partsbot

# Switch to partsbot user
su - partsbot
```

### 3. Set Up Application Directory

```bash
# Create application directory
sudo mkdir -p /opt/parts-bot
sudo chown partsbot:partsbot /opt/parts-bot

# Create necessary subdirectories
mkdir -p /opt/parts-bot/{logs,backups,ssl,configs}
```

### 4. Install Python Dependencies

```bash
# Install Python 3.11+ (if not available)
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Create virtual environment
cd /opt/parts-bot
python3.11 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart aiogram redis
```

### 5. Install Node.js and Frontend Dependencies

```bash
# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### 6. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE china_car_parts;
CREATE USER partsbot WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE china_car_parts TO partsbot;
\q

# Test connection
psql -h localhost -U partsbot -d china_car_parts
```

### 7. Redis Setup

```bash
# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
```

### 8. Nginx Configuration

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/china-car-parts
```

Add the following configuration:

```nginx
upstream api_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

upstream frontend_backend {
    server 127.0.0.1:5173;
}

server {
    listen 80;
    server_name 5.223.59.155;

    # Frontend
    location / {
        proxy_pass http://frontend_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API
    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/china-car-parts /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 9. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d 5.223.59.155

# Test automatic renewal
sudo certbot renew --dry-run
```

### 10. Firewall Configuration

```bash
# Configure UFW
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Check status
sudo ufw status
```

### 11. Systemd Services

Create service files for the application:

```bash
# API service
sudo nano /etc/systemd/system/china-car-parts-api.service
```

```ini
[Unit]
Description=China Car Parts API
After=network.target

[Service]
Type=exec
User=partsbot
Group=partsbot
WorkingDirectory=/opt/parts-bot
Environment=PATH=/opt/parts-bot/venv/bin
ExecStart=/opt/parts-bot/venv/bin/uvicorn app.api.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Bot service
sudo nano /etc/systemd/system/china-car-parts-bot.service
```

```ini
[Unit]
Description=China Car Parts Telegram Bot
After=network.target

[Service]
Type=exec
User=partsbot
Group=partsbot
WorkingDirectory=/opt/parts-bot
Environment=PATH=/opt/parts-bot/venv/bin
ExecStart=/opt/parts-bot/venv/bin/python -m app.bot.bot
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable china-car-parts-api
sudo systemctl enable china-car-parts-bot
```

## 🔑 SSH Key Setup

### Generate SSH Key Pair

On your local machine:

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "china-car-parts-deployment" -f ~/.ssh/china_car_parts_key

# Copy public key to server
ssh-copy-id -i ~/.ssh/china_car_parts_key.pub root@5.223.59.155

# Test connection
ssh -i ~/.ssh/china_car_parts_key root@5.223.59.155
```

### Add Private Key to GitHub Secrets

1. Go to your GitHub repository: https://github.com/oshaghisina/Cars-part/settings/secrets/actions
2. Add the following secrets:

```
PROD_SSH_PRIVATE_KEY=<content of ~/.ssh/china_car_parts_key>
PROD_HOST=5.223.59.155
PROD_USER=root
PROD_API_URL=https://5.223.59.155/api
PROD_FRONTEND_ORIGIN=https://5.223.59.155
```

## 📝 Environment Configuration

Create environment file on the server:

```bash
# Switch to partsbot user
su - partsbot

# Create environment file
nano /opt/parts-bot/.env
```

Add the following configuration:

```bash
# Application
APP_ENV=production
DEBUG=false
SECRET_KEY=your_super_secret_key_here

# Database
DATABASE_URL=postgresql://partsbot:secure_password_here@localhost:5432/china_car_parts

# Redis
REDIS_URL=redis://localhost:6379

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_ADMIN_IDS=123456789,987654321

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
FRONTEND_ORIGIN=https://5.223.59.155

# JWT
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Security
CORS_ORIGINS=https://5.223.59.155,http://5.223.59.155
```

## 🚀 Deployment Test

### Manual Deployment Test

```bash
# Clone repository
cd /opt/parts-bot
git clone https://github.com/oshaghisina/Cars-part.git .

# Install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Create admin user
python create_admin_user.py

# Start services
sudo systemctl start china-car-parts-api
sudo systemctl start china-car-parts-bot

# Check status
sudo systemctl status china-car-parts-api
sudo systemctl status china-car-parts-bot
```

### Test Endpoints

```bash
# Test API health
curl https://5.223.59.155/api/health

# Test frontend
curl https://5.223.59.155/
```

## 🔍 Monitoring and Logs

### View Logs

```bash
# API logs
sudo journalctl -u china-car-parts-api -f

# Bot logs
sudo journalctl -u china-car-parts-bot -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### System Monitoring

```bash
# System resources
htop

# Disk usage
df -h

# Memory usage
free -h

# Network connections
netstat -tulpn
```

## 🚨 Troubleshooting

### Common Issues

1. **Service won't start**:
   ```bash
   sudo journalctl -u china-car-parts-api --no-pager
   ```

2. **Database connection issues**:
   ```bash
   sudo systemctl status postgresql
   psql -h localhost -U partsbot -d china_car_parts
   ```

3. **Nginx configuration issues**:
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. **SSL certificate issues**:
   ```bash
   sudo certbot certificates
   sudo certbot renew
   ```

## 🔒 Security Checklist

- [ ] Firewall configured (UFW)
- [ ] SSH key authentication enabled
- [ ] Fail2ban installed and configured
- [ ] SSL certificate installed
- [ ] Database user has limited privileges
- [ ] Application runs as non-root user
- [ ] Regular security updates enabled
- [ ] Log monitoring configured

## 📞 Support

If you encounter any issues during setup:

1. Check the logs for error messages
2. Verify all services are running
3. Test network connectivity
4. Review firewall rules
5. Check disk space and system resources

---

**Your production server is now ready for CI/CD deployment! 🎉**
