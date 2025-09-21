#!/bin/bash

# 🚀 Production Server Setup Script for China Car Parts
# This script sets up a complete production environment on Ubuntu 22.04+

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROD_USER="partsbot"
PROD_GROUP="partsbot"
PROD_DIR="/opt/china-car-parts"
VENV_DIR="$PROD_DIR/venv"
BACKUP_DIR="/opt/backups/china-car-parts"
LOG_DIR="/var/log/china-car-parts"
PYTHON_VERSION="3.11"
NODE_VERSION="18"
DOMAIN="${DOMAIN:-yourdomain.com}"

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

info() {
    echo -e "${PURPLE}[INFO]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root. Use: sudo $0"
    fi
}

# Update system
update_system() {
    log "🔄 Updating system packages..."
    apt-get update
    apt-get upgrade -y
    success "System updated"
}

# Install system dependencies
install_system_dependencies() {
    log "📦 Installing system dependencies..."
    
    apt-get install -y \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        python3-pip \
        python3-venv \
        nginx \
        postgresql \
        postgresql-contrib \
        supervisor \
        htop \
        vim \
        jq \
        bc \
        rsync \
        ufw \
        fail2ban \
        certbot \
        python3-certbot-nginx
    
    success "System dependencies installed"
}

# Install Python
install_python() {
    log "🐍 Installing Python $PYTHON_VERSION..."
    
    # Add deadsnakes PPA for Python versions
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update
    
    # Install Python and pip
    apt-get install -y python$PYTHON_VERSION python$PYTHON_VERSION-venv python$PYTHON_VERSION-dev
    
    # Create symlinks
    ln -sf /usr/bin/python$PYTHON_VERSION /usr/bin/python3
    ln -sf /usr/bin/python$PYTHON_VERSION /usr/bin/python
    
    success "Python $PYTHON_VERSION installed"
}

# Install Node.js
install_nodejs() {
    log "📦 Installing Node.js $NODE_VERSION..."
    
    # Install NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_$NODE_VERSION.x | bash -
    
    # Install Node.js
    apt-get install -y nodejs
    
    # Install global npm packages
    npm install -g npm@latest
    
    success "Node.js $NODE_VERSION installed"
}

# Create production user
create_production_user() {
    log "👤 Creating production user..."
    
    # Create user and group
    if ! id "$PROD_USER" &>/dev/null; then
        useradd -r -s /bin/bash -d "$PROD_DIR" -m "$PROD_USER"
        success "User $PROD_USER created"
    else
        warning "User $PROD_USER already exists"
    fi
    
    # Create group if it doesn't exist
    if ! getent group "$PROD_GROUP" > /dev/null 2>&1; then
        groupadd "$PROD_GROUP"
        usermod -a -G "$PROD_GROUP" "$PROD_USER"
        success "Group $PROD_GROUP created"
    fi
}

# Setup directories
setup_directories() {
    log "📁 Setting up directories..."
    
    # Create main directories
    mkdir -p "$PROD_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$PROD_DIR/uploads"
    
    # Set ownership
    chown -R "$PROD_USER:$PROD_GROUP" "$PROD_DIR"
    chown -R "$PROD_USER:$PROD_GROUP" "$BACKUP_DIR"
    chown -R "$PROD_USER:$PROD_GROUP" "$LOG_DIR"
    
    # Set permissions
    chmod 755 "$PROD_DIR"
    chmod 755 "$BACKUP_DIR"
    chmod 755 "$LOG_DIR"
    chmod 755 "$PROD_DIR/uploads"
    
    success "Directories created and configured"
}

# Setup PostgreSQL
setup_postgresql() {
    log "🗄️ Setting up PostgreSQL..."
    
    # Start and enable PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    # Generate secure password
    DB_PASSWORD=$(openssl rand -hex 16)
    
    # Create database and user
    sudo -u postgres psql << EOF
CREATE DATABASE china_car_parts_production;
CREATE USER partsbot WITH ENCRYPTED PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE china_car_parts_production TO partsbot;
ALTER USER partsbot CREATEDB;
\q
EOF
    
    # Configure PostgreSQL
    PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '\d+\.\d+' | head -1)
    PG_CONFIG="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
    
    # Update PostgreSQL configuration for production
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" "$PG_CONFIG"
    sed -i "s/#port = 5432/port = 5432/" "$PG_CONFIG"
    sed -i "s/#max_connections = 100/max_connections = 200/" "$PG_CONFIG"
    sed -i "s/#shared_buffers = 128MB/shared_buffers = 256MB/" "$PG_CONFIG"
    
    # Restart PostgreSQL
    systemctl restart postgresql
    
    # Save database password for later use
    echo "DB_PASSWORD=$DB_PASSWORD" > /root/db_password.txt
    chmod 600 /root/db_password.txt
    
    success "PostgreSQL configured with password: $DB_PASSWORD"
}

# Setup firewall
setup_firewall() {
    log "🔥 Setting up firewall..."
    
    # Enable UFW
    ufw --force enable
    
    # Allow SSH
    ufw allow ssh
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Allow API port (internal only)
    ufw allow from 127.0.0.1 to any port 8001
    
    success "Firewall configured"
}

# Setup fail2ban
setup_fail2ban() {
    log "🛡️ Setting up fail2ban..."
    
    # Create jail.local
    cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
EOF
    
    # Start and enable fail2ban
    systemctl start fail2ban
    systemctl enable fail2ban
    
    success "Fail2ban configured"
}

# Clone repository
clone_repository() {
    log "📥 Cloning repository..."
    
    # You need to replace this with your actual repository URL
    REPO_URL="${REPO_URL:-https://github.com/your-org/china-car-parts.git}"
    
    # Clone repository
    cd /tmp
    git clone "$REPO_URL" temp-repo
    
    # Copy to production directory
    cp -r temp-repo/* "$PROD_DIR/"
    rm -rf temp-repo
    
    # Set ownership
    chown -R "$PROD_USER:$PROD_GROUP" "$PROD_DIR"
    
    success "Repository cloned"
}

# Setup Python virtual environment
setup_python_venv() {
    log "🐍 Setting up Python virtual environment..."
    
    # Create virtual environment
    sudo -u "$PROD_USER" python$PYTHON_VERSION -m venv "$VENV_DIR"
    
    # Activate and install dependencies
    sudo -u "$PROD_USER" bash -c "source $VENV_DIR/bin/activate && pip install --upgrade pip"
    sudo -u "$PROD_USER" bash -c "source $VENV_DIR/bin/activate && pip install -r $PROD_DIR/requirements.txt"
    
    success "Python virtual environment created"
}

# Setup frontend
setup_frontend() {
    log "🎨 Setting up frontend..."
    
    cd "$PROD_DIR/app/frontend/panel"
    
    # Install dependencies
    sudo -u "$PROD_USER" npm ci
    
    # Build frontend
    sudo -u "$PROD_USER" npm run build
    
    success "Frontend setup completed"
}

# Setup systemd services
setup_systemd_services() {
    log "⚙️ Setting up systemd services..."
    
    # Copy service files
    cp "$PROD_DIR/deployment/configs/china-car-parts-api.service" /etc/systemd/system/
    cp "$PROD_DIR/deployment/configs/china-car-parts-bot.service" /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable services
    systemctl enable china-car-parts-api
    systemctl enable china-car-parts-bot
    
    success "Systemd services configured"
}

# Setup Nginx
setup_nginx() {
    log "🌐 Setting up Nginx..."
    
    # Copy Nginx configuration
    cp "$PROD_DIR/deployment/configs/nginx-production.conf" /etc/nginx/sites-available/china-car-parts
    
    # Replace domain placeholder
    sed -i "s/yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/china-car-parts
    
    # Create symlink
    ln -sf /etc/nginx/sites-available/china-car-parts /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx configuration
    nginx -t
    
    # Start and enable Nginx
    systemctl start nginx
    systemctl enable nginx
    
    success "Nginx configured"
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    log "🔒 Setting up SSL with Let's Encrypt..."
    
    if [ "$DOMAIN" != "yourdomain.com" ]; then
        # Get SSL certificate
        certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN"
        
        # Setup auto-renewal
        (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
        
        success "SSL certificate configured for $DOMAIN"
    else
        warning "Domain not set, skipping SSL setup. Please configure SSL manually."
    fi
}

# Create production environment file
create_production_env() {
    log "📝 Creating production environment file..."
    
    # Get database password
    DB_PASSWORD=$(cat /root/db_password.txt | cut -d'=' -f2)
    
    # Generate secure keys
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET_KEY=$(openssl rand -hex 32)
    
    cat > "$PROD_DIR/.env" << EOF
# Production Environment Configuration
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://partsbot:$DB_PASSWORD@localhost:5432/china_car_parts_production

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=CHANGEME_YOUR_PRODUCTION_BOT_TOKEN
ADMIN_TELEGRAM_IDS=CHANGEME_YOUR_TELEGRAM_ID

# FastAPI Configuration
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Frontend Configuration
FRONTEND_ORIGIN=https://$DOMAIN
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# Server Configuration
HOST=0.0.0.0
PORT=8001

# AI Configuration
AI_ENABLED=true
OPENAI_API_KEY=CHANGEME_YOUR_OPENAI_API_KEY
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.3

# Rate Limiting
RATE_LIMIT_PER_MINUTE=1000
RATE_LIMIT_BURST=10

# Logging
LOG_FILE=$LOG_DIR/api.log

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
    
    # Set ownership and permissions
    chown "$PROD_USER:$PROD_GROUP" "$PROD_DIR/.env"
    chmod 600 "$PROD_DIR/.env"
    
    success "Production environment file created"
}

# Setup log rotation
setup_log_rotation() {
    log "📋 Setting up log rotation..."
    
    cat > /etc/logrotate.d/china-car-parts << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $PROD_USER $PROD_GROUP
    postrotate
        systemctl reload china-car-parts-api
        systemctl reload china-car-parts-bot
    endscript
}
EOF
    
    success "Log rotation configured"
}

# Setup monitoring
setup_monitoring() {
    log "📊 Setting up monitoring..."
    
    # Create monitoring script
    cat > /usr/local/bin/china-car-parts-monitor.sh << 'EOF'
#!/bin/bash

# Production monitoring script for China Car Parts

API_URL="http://localhost:8001"
LOG_FILE="/var/log/china-car-parts/monitor.log"

check_api() {
    if curl -f -s "$API_URL/health" > /dev/null; then
        echo "$(date): API health check passed" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): API health check failed" >> "$LOG_FILE"
        return 1
    fi
}

check_services() {
    if systemctl is-active --quiet china-car-parts-api && systemctl is-active --quiet china-car-parts-bot; then
        echo "$(date): All services running" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): Some services not running" >> "$LOG_FILE"
        return 1
    fi
}

# Run checks
check_api
check_services
EOF
    
    chmod +x /usr/local/bin/china-car-parts-monitor.sh
    
    # Add to crontab for monitoring every 5 minutes
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/china-car-parts-monitor.sh") | crontab -
    
    success "Monitoring setup completed"
}

# Main setup function
main() {
    log "🚀 Starting production server setup..."
    log "🌐 Domain: $DOMAIN"
    log "📁 Production directory: $PROD_DIR"
    
    check_root
    update_system
    install_system_dependencies
    install_python
    install_nodejs
    create_production_user
    setup_directories
    setup_postgresql
    setup_firewall
    setup_fail2ban
    clone_repository
    setup_python_venv
    setup_frontend
    setup_systemd_services
    setup_nginx
    setup_ssl
    create_production_env
    setup_log_rotation
    setup_monitoring
    
    success "✅ Production server setup completed!"
    
    log ""
    log "📋 Next steps:"
    log "  1. Update $PROD_DIR/.env with actual values:"
    log "     - TELEGRAM_BOT_TOKEN"
    log "     - ADMIN_TELEGRAM_IDS"
    log "     - OPENAI_API_KEY"
    log ""
    log "  2. Run database migrations:"
    log "     cd $PROD_DIR && source venv/bin/activate && alembic upgrade head"
    log ""
    log "  3. Start services:"
    log "     systemctl start china-car-parts-api china-car-parts-bot"
    log ""
    log "  4. Check service status:"
    log "     systemctl status china-car-parts-api china-car-parts-bot"
    log ""
    log "  5. View logs:"
    log "     journalctl -u china-car-parts-api -f"
    log "     journalctl -u china-car-parts-bot -f"
    log ""
    log "🌐 Your application will be available at: https://$DOMAIN"
    log "📊 API Health: https://$DOMAIN/api/v1/health"
    log "📈 Admin Panel: https://$DOMAIN"
}

# Check for domain parameter
if [ -z "$1" ]; then
    echo "Usage: $0 <domain> [repository_url]"
    echo "Example: $0 yourdomain.com https://github.com/your-org/china-car-parts.git"
    exit 1
fi

DOMAIN="$1"
REPO_URL="${2:-https://github.com/your-org/china-car-parts.git}"

# Run main function
main "$@"
