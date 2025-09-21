#!/bin/bash

# 🚀 Production Blue-Green Setup Script
# This script sets up the blue-green deployment directories on the production server
# Run this ONCE on the production server before the first deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROD_DIR="/opt/china-car-parts"
BLUE_DIR="/opt/china-car-parts-blue"
GREEN_DIR="/opt/china-car-parts-green"
BACKUP_DIR="/opt/backups/china-car-parts"
REPO_URL="https://github.com/your-org/china-car-parts.git"  # Update this with your actual repo URL

# Logging functions
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root. Use 'sudo ./setup_production_blue_green.sh'"
    fi
}

# Install required packages
install_packages() {
    log "📦 Installing required packages..."
    
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        git \
        python3.11 \
        python3.11-venv \
        python3.11-dev \
        pip \
        nginx \
        curl \
        jq \
        rsync \
        systemd
    
    success "Required packages installed"
}

# Create directories
create_directories() {
    log "📁 Creating blue-green deployment directories..."
    
    # Create main directories
    mkdir -p "$PROD_DIR"
    mkdir -p "$BLUE_DIR"
    mkdir -p "$GREEN_DIR"
    mkdir -p "$BACKUP_DIR"
    
    # Set proper permissions
    chown -R root:root "$PROD_DIR"
    chown -R root:root "$BLUE_DIR"
    chown -R root:root "$GREEN_DIR"
    chown -R root:root "$BACKUP_DIR"
    
    chmod 755 "$PROD_DIR"
    chmod 755 "$BLUE_DIR"
    chmod 755 "$GREEN_DIR"
    chmod 755 "$BACKUP_DIR"
    
    success "Directories created"
}

# Clone repository to both environments
clone_repositories() {
    log "📥 Cloning repository to both environments..."
    
    # Clone to blue environment
    if [ ! -d "$BLUE_DIR/.git" ]; then
        git clone "$REPO_URL" "$BLUE_DIR" || error "Failed to clone repository to blue environment"
        success "Repository cloned to blue environment"
    else
        warning "Blue environment already has repository"
    fi
    
    # Clone to green environment
    if [ ! -d "$GREEN_DIR/.git" ]; then
        git clone "$REPO_URL" "$GREEN_DIR" || error "Failed to clone repository to green environment"
        success "Repository cloned to green environment"
    else
        warning "Green environment already has repository"
    fi
}

# Set up Python environments
setup_python_environments() {
    log "🐍 Setting up Python virtual environments..."
    
    # Set up blue environment
    if [ ! -d "$BLUE_DIR/venv" ]; then
        python3.11 -m venv "$BLUE_DIR/venv" || error "Failed to create blue Python environment"
        source "$BLUE_DIR/venv/bin/activate"
        pip install --upgrade pip
        pip install -r "$BLUE_DIR/requirements.txt" || error "Failed to install blue dependencies"
        deactivate
        success "Blue Python environment set up"
    else
        warning "Blue Python environment already exists"
    fi
    
    # Set up green environment
    if [ ! -d "$GREEN_DIR/venv" ]; then
        python3.11 -m venv "$GREEN_DIR/venv" || error "Failed to create green Python environment"
        source "$GREEN_DIR/venv/bin/activate"
        pip install --upgrade pip
        pip install -r "$GREEN_DIR/requirements.txt" || error "Failed to install green dependencies"
        deactivate
        success "Green Python environment set up"
    else
        warning "Green environment already exists"
    fi
}

# Create environment files
create_environment_files() {
    log "📝 Creating environment configuration files..."
    
    # Create blue environment file
    cat > "$BLUE_DIR/.env" << EOF
# Blue Environment Configuration
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./data/china_car_parts.db

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_production_bot_token
ADMIN_TELEGRAM_IDS=your_telegram_id

# FastAPI
SECRET_KEY=your_production_secret_key_32_chars_long
JWT_SECRET_KEY=your_production_jwt_secret_key_32_chars_long
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Frontend
FRONTEND_ORIGIN=https://yourdomain.com,https://www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Server
HOST=0.0.0.0
PORT=8001

# AI Configuration
AI_ENABLED=true
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.3

# Rate Limiting
RATE_LIMIT_PER_MINUTE=1000
RATE_LIMIT_BURST=10

# Logging
LOG_FILE=/var/log/china-car-parts/app.log

# Admin Panel
ADMIN_PANEL_ENABLED=true
ADMIN_PANEL_PORT=5173

# Bulk Operations
BULK_LIMIT_DEFAULT=10

# Maintenance Mode
MAINTENANCE_MODE=false

# Redis
REDIS_URL=redis://localhost:6379/0
EOF

    # Create green environment file
    cp "$BLUE_DIR/.env" "$GREEN_DIR/.env"
    sed -i 's/PORT=8001/PORT=8002/' "$GREEN_DIR/.env"
    
    success "Environment files created"
}

# Set up systemd services
setup_systemd_services() {
    log "⚙️ Setting up systemd services..."
    
    # Create API service for blue
    cat > /etc/systemd/system/china-car-parts-api-blue.service << EOF
[Unit]
Description=China Car Parts API Service (Blue)
After=network.target

[Service]
User=root
WorkingDirectory=$BLUE_DIR
ExecStart=$BLUE_DIR/venv/bin/uvicorn app.api.main:app --host 0.0.0.0 --port 8001
Restart=always
StandardOutput=append:/var/log/china-car-parts/api-blue.log
StandardError=append:/var/log/china-car-parts/api-error-blue.log

[Install]
WantedBy=multi-user.target
EOF

    # Create API service for green
    cat > /etc/systemd/system/china-car-parts-api-green.service << EOF
[Unit]
Description=China Car Parts API Service (Green)
After=network.target

[Service]
User=root
WorkingDirectory=$GREEN_DIR
ExecStart=$GREEN_DIR/venv/bin/uvicorn app.api.main:app --host 0.0.0.0 --port 8002
Restart=always
StandardOutput=append:/var/log/china-car-parts/api-green.log
StandardError=append:/var/log/china-car-parts/api-error-green.log

[Install]
WantedBy=multi-user.target
EOF

    # Create bot service for blue
    cat > /etc/systemd/system/china-car-parts-bot-blue.service << EOF
[Unit]
Description=China Car Parts Telegram Bot Service (Blue)
After=network.target china-car-parts-api-blue.service

[Service]
User=root
WorkingDirectory=$BLUE_DIR
ExecStart=$BLUE_DIR/venv/bin/python -m app.bot.bot
Restart=always
StandardOutput=append:/var/log/china-car-parts/bot-blue.log
StandardError=append:/var/log/china-car-parts/bot-error-blue.log

[Install]
WantedBy=multi-user.target
EOF

    # Create bot service for green
    cat > /etc/systemd/system/china-car-parts-bot-green.service << EOF
[Unit]
Description=China Car Parts Telegram Bot Service (Green)
After=network.target china-car-parts-api-green.service

[Service]
User=root
WorkingDirectory=$GREEN_DIR
ExecStart=$GREEN_DIR/venv/bin/python -m app.bot.bot
Restart=always
StandardOutput=append:/var/log/china-car-parts/bot-green.log
StandardError=append:/var/log/china-car-parts/bot-error-green.log

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    systemctl daemon-reload
    
    # Enable services (but don't start yet)
    systemctl enable china-car-parts-api-blue
    systemctl enable china-car-parts-api-green
    systemctl enable china-car-parts-bot-blue
    systemctl enable china-car-parts-bot-green
    
    success "Systemd services configured"
}

# Set up Nginx configuration
setup_nginx() {
    log "🌐 Setting up Nginx configuration..."
    
    # Create Nginx configuration
    cat > /etc/nginx/sites-available/china-car-parts << EOF
upstream blue-api {
    server 127.0.0.1:8001 weight=1 max_fails=3 fail_timeout=30s;
}

upstream green-api {
    server 127.0.0.1:8002 weight=1 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # API routes
    location /api/ {
        proxy_pass http://blue-api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Frontend routes
    location / {
        root $BLUE_DIR/app/frontend/panel/dist;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Health check
    location /health {
        proxy_pass http://blue-api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/china-car-parts /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    nginx -t || error "Nginx configuration test failed"
    
    # Start Nginx
    systemctl start nginx
    systemctl enable nginx
    
    success "Nginx configured"
}

# Create log directories
create_log_directories() {
    log "📋 Creating log directories..."
    
    mkdir -p /var/log/china-car-parts
    chown -R root:root /var/log/china-car-parts
    chmod 755 /var/log/china-car-parts
    
    success "Log directories created"
}

# Set up initial blue environment
setup_initial_blue() {
    log "🔵 Setting up initial blue environment..."
    
    cd "$BLUE_DIR"
    
    # Run database migrations
    source venv/bin/activate
    alembic upgrade head || warning "Database migration failed (this is normal for first setup)"
    deactivate
    
    # Create data directory
    mkdir -p "$BLUE_DIR/data"
    
    # Start blue services
    systemctl start china-car-parts-api-blue
    systemctl start china-car-parts-bot-blue
    
    # Wait for services to start
    sleep 10
    
    # Health check
    if curl -f -s http://localhost:8001/api/v1/health > /dev/null; then
        success "Blue environment is healthy"
    else
        warning "Blue environment health check failed (this is normal for first setup)"
    fi
    
    # Set blue as current environment
    echo "blue" > "$BLUE_DIR/.environment"
    
    success "Initial blue environment set up"
}

# Main setup function
main() {
    log "🚀 Starting Blue-Green Production Setup"
    log "======================================"
    
    check_root
    install_packages
    create_directories
    clone_repositories
    setup_python_environments
    create_environment_files
    setup_systemd_services
    setup_nginx
    create_log_directories
    setup_initial_blue
    
    success "✅ Blue-Green Production Setup Completed Successfully!"
    
    log "📋 Next steps:"
    log "  1. Update the following in both environment files:"
    log "     - TELEGRAM_BOT_TOKEN (from @BotFather)"
    log "     - ADMIN_TELEGRAM_IDS (your Telegram user ID)"
    log "     - OPENAI_API_KEY (if using AI features)"
    log "     - SECRET_KEY and JWT_SECRET_KEY (generate strong keys)"
    log "  2. Update your domain name in Nginx configuration"
    log "  3. Set up SSL certificates with Certbot"
    log "  4. Test the deployment with GitHub Actions"
    log ""
    log "🔧 Manual commands:"
    log "  - Check blue environment: systemctl status china-car-parts-api-blue"
    log "  - Check green environment: systemctl status china-car-parts-api-green"
    log "  - View logs: journalctl -u china-car-parts-api-blue -f"
    log "  - Test API: curl http://localhost:8001/api/v1/health"
}

main "$@"
