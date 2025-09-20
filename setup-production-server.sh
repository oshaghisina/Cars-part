#!/bin/bash

# 🚀 Production Server Setup Script for China Car Parts
# Server: 5.223.59.155
# This script automates the server setup process

set -e

echo "🚀 **CHINA CAR PARTS - PRODUCTION SERVER SETUP**"
echo "================================================="
echo ""
echo "📋 **Server Information:**"
echo "   • Server IP: 5.223.59.155"
echo "   • Username: root"
echo "   • Purpose: Production deployment"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root"
    exit 1
fi

echo "🔧 **STEP 1: SYSTEM UPDATE**"
print_info "Updating system packages..."
apt update && apt upgrade -y
print_status "System updated successfully"

echo ""
echo "🔧 **STEP 2: INSTALLING ESSENTIAL PACKAGES**"
print_info "Installing required packages..."

# Install essential packages
apt install -y \
    curl \
    wget \
    git \
    nginx \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    nodejs \
    npm \
    postgresql \
    postgresql-contrib \
    redis-server \
    ufw \
    fail2ban \
    htop \
    certbot \
    python3-certbot-nginx \
    software-properties-common

print_status "Essential packages installed"

echo ""
echo "🔧 **STEP 3: INSTALLING PYTHON 3.11**"
print_info "Installing Python 3.11..."

# Add deadsnakes PPA for Python 3.11
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.11 python3.11-venv python3.11-dev

print_status "Python 3.11 installed"

echo ""
echo "🔧 **STEP 4: INSTALLING NODE.JS 18**"
print_info "Installing Node.js 18..."

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Verify installation
NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
print_status "Node.js $NODE_VERSION and npm $NPM_VERSION installed"

echo ""
echo "🔧 **STEP 5: CREATING APPLICATION USER**"
print_info "Creating dedicated user for the application..."

# Create partsbot user
if ! id "partsbot" &>/dev/null; then
    adduser --disabled-password --gecos "" partsbot
    usermod -aG sudo partsbot
    print_status "User 'partsbot' created successfully"
else
    print_warning "User 'partsbot' already exists"
fi

echo ""
echo "🔧 **STEP 6: SETTING UP APPLICATION DIRECTORY**"
print_info "Creating application directory structure..."

# Create application directory
mkdir -p /opt/parts-bot/{logs,backups,ssl,configs}
chown -R partsbot:partsbot /opt/parts-bot

print_status "Application directory created"

echo ""
echo "🔧 **STEP 7: CONFIGURING DATABASE**"
print_info "Setting up PostgreSQL..."

# Start PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE china_car_parts;" 2>/dev/null || print_warning "Database may already exist"
sudo -u postgres psql -c "CREATE USER partsbot WITH PASSWORD 'china_car_parts_2024!';" 2>/dev/null || print_warning "User may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE china_car_parts TO partsbot;"
sudo -u postgres psql -c "ALTER USER partsbot CREATEDB;"

print_status "Database configured"

echo ""
echo "🔧 **STEP 8: CONFIGURING REDIS**"
print_info "Setting up Redis..."

# Start Redis
systemctl start redis-server
systemctl enable redis-server

print_status "Redis configured"

echo ""
echo "🔧 **STEP 9: CONFIGURING NGINX**"
print_info "Setting up Nginx..."

# Create Nginx configuration
cat > /etc/nginx/sites-available/china-car-parts << 'EOF'
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
EOF

# Enable site
ln -sf /etc/nginx/sites-available/china-car-parts /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test configuration
nginx -t

# Start Nginx
systemctl restart nginx
systemctl enable nginx

print_status "Nginx configured"

echo ""
echo "🔧 **STEP 10: CONFIGURING FIREWALL**"
print_info "Setting up UFW firewall..."

# Configure firewall
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443

print_status "Firewall configured"

echo ""
echo "🔧 **STEP 11: CREATING SYSTEMD SERVICES**"
print_info "Creating systemd service files..."

# API service
cat > /etc/systemd/system/china-car-parts-api.service << 'EOF'
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
EOF

# Bot service
cat > /etc/systemd/system/china-car-parts-bot.service << 'EOF'
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
EOF

# Reload systemd
systemctl daemon-reload

# Enable services
systemctl enable china-car-parts-api
systemctl enable china-car-parts-bot

print_status "Systemd services created"

echo ""
echo "🔧 **STEP 12: CREATING ENVIRONMENT FILE**"
print_info "Creating environment configuration..."

# Create environment file
cat > /opt/parts-bot/.env << 'EOF'
# Application
APP_ENV=production
DEBUG=false
SECRET_KEY=china_car_parts_production_secret_key_2024

# Database
DATABASE_URL=postgresql://partsbot:china_car_parts_2024!@localhost:5432/china_car_parts

# Redis
REDIS_URL=redis://localhost:6379

# Telegram Bot (UPDATE THESE VALUES)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_ADMIN_IDS=123456789,987654321

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
FRONTEND_ORIGIN=https://5.223.59.155

# JWT
JWT_SECRET_KEY=china_car_parts_jwt_secret_key_2024
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Security
CORS_ORIGINS=https://5.223.59.155,http://5.223.59.155
EOF

chown partsbot:partsbot /opt/parts-bot/.env

print_status "Environment file created"

echo ""
echo "🎉 **SERVER SETUP COMPLETE!**"
echo "=============================="
echo ""
echo "📋 **Next Steps:**"
echo "1. Update Telegram Bot Token in /opt/parts-bot/.env"
echo "2. Update Telegram Admin IDs in /opt/parts-bot/.env"
echo "3. Clone your repository: cd /opt/parts-bot && git clone https://github.com/oshaghisina/Cars-part.git ."
echo "4. Install Python dependencies: source venv/bin/activate && pip install -r requirements.txt"
echo "5. Run database migrations: alembic upgrade head"
echo "6. Create admin user: python create_admin_user.py"
echo "7. Start services: systemctl start china-car-parts-api china-car-parts-bot"
echo ""
echo "🔑 **SSH Key Setup:**"
echo "1. Generate SSH key on your local machine:"
echo "   ssh-keygen -t rsa -b 4096 -C 'china-car-parts-deployment' -f ~/.ssh/china_car_parts_key"
echo "2. Copy public key to server:"
echo "   ssh-copy-id -i ~/.ssh/china_car_parts_key.pub root@5.223.59.155"
echo "3. Add private key to GitHub Secrets as PROD_SSH_PRIVATE_KEY"
echo ""
echo "🌐 **Access URLs:**"
echo "• HTTP: http://5.223.59.155"
echo "• HTTPS: https://5.223.59.155 (after SSL setup)"
echo ""
echo "📚 **Documentation:**"
echo "• Server Setup Guide: SERVER_SETUP_GUIDE.md"
echo "• Deployment Guide: DEPLOYMENT.md"
echo "• GitHub Actions Guide: GITHUB_ACTIONS_GUIDE.md"
echo ""

print_info "Your production server is ready for deployment! 🚀"
