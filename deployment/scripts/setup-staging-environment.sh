#!/bin/bash

# Staging Environment Setup Script
# This script sets up a complete staging environment for China Car Parts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STAGING_USER="partsbot"
STAGING_GROUP="partsbot"
STAGING_DIR="/opt/china-car-parts-staging"
VENV_DIR="$STAGING_DIR/venv"
BACKUP_DIR="/opt/backups/china-car-parts-staging"
LOG_DIR="/var/log/china-car-parts-staging"
PYTHON_VERSION="3.11"
NODE_VERSION="18"

# Logging function
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
        error "This script must be run as root"
    fi
}

# Install system dependencies
install_system_dependencies() {
    log "📦 Installing system dependencies..."
    
    # Update package list
    apt-get update
    
    # Install essential packages
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
        rsync
    
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

# Create staging user
create_staging_user() {
    log "👤 Creating staging user..."
    
    # Create user and group
    if ! id "$STAGING_USER" &>/dev/null; then
        useradd -r -s /bin/bash -d "$STAGING_DIR" -m "$STAGING_USER"
        success "User $STAGING_USER created"
    else
        warning "User $STAGING_USER already exists"
    fi
    
    # Create group if it doesn't exist
    if ! getent group "$STAGING_GROUP" > /dev/null 2>&1; then
        groupadd "$STAGING_GROUP"
        usermod -a -G "$STAGING_GROUP" "$STAGING_USER"
        success "Group $STAGING_GROUP created"
    fi
}

# Setup directories
setup_directories() {
    log "📁 Setting up directories..."
    
    # Create main directories
    mkdir -p "$STAGING_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOG_DIR"
    
    # Set ownership
    chown -R "$STAGING_USER:$STAGING_GROUP" "$STAGING_DIR"
    chown -R "$STAGING_USER:$STAGING_GROUP" "$BACKUP_DIR"
    chown -R "$STAGING_USER:$STAGING_GROUP" "$LOG_DIR"
    
    # Set permissions
    chmod 755 "$STAGING_DIR"
    chmod 755 "$BACKUP_DIR"
    chmod 755 "$LOG_DIR"
    
    success "Directories created and configured"
}

# Setup PostgreSQL
setup_postgresql() {
    log "🗄️ Setting up PostgreSQL..."
    
    # Start and enable PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql << EOF
CREATE DATABASE china_car_parts_staging;
CREATE USER partsbot WITH ENCRYPTED PASSWORD 'staging_password_$(openssl rand -hex 8)';
GRANT ALL PRIVILEGES ON DATABASE china_car_parts_staging TO partsbot;
ALTER USER partsbot CREATEDB;
\q
EOF
    
    # Configure PostgreSQL
    PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '\d+\.\d+' | head -1)
    PG_CONFIG="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
    
    # Update PostgreSQL configuration for staging
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" "$PG_CONFIG"
    sed -i "s/#port = 5432/port = 5432/" "$PG_CONFIG"
    
    # Restart PostgreSQL
    systemctl restart postgresql
    
    success "PostgreSQL configured"
}

# Clone repository
clone_repository() {
    log "📥 Cloning repository..."
    
    # Clone repository (you'll need to provide the actual repository URL)
    cd /tmp
    git clone https://github.com/your-org/china-car-parts.git temp-repo
    
    # Copy to staging directory
    cp -r temp-repo/* "$STAGING_DIR/"
    rm -rf temp-repo
    
    # Set ownership
    chown -R "$STAGING_USER:$STAGING_GROUP" "$STAGING_DIR"
    
    success "Repository cloned"
}

# Setup Python virtual environment
setup_python_venv() {
    log "🐍 Setting up Python virtual environment..."
    
    # Create virtual environment
    sudo -u "$STAGING_USER" python$PYTHON_VERSION -m venv "$VENV_DIR"
    
    # Activate and install dependencies
    sudo -u "$STAGING_USER" bash -c "source $VENV_DIR/bin/activate && pip install --upgrade pip"
    sudo -u "$STAGING_USER" bash -c "source $VENV_DIR/bin/activate && pip install -r $STAGING_DIR/requirements.txt"
    
    success "Python virtual environment created"
}

# Setup frontend
setup_frontend() {
    log "🎨 Setting up frontend..."
    
    cd "$STAGING_DIR/app/frontend/panel"
    
    # Install dependencies
    sudo -u "$STAGING_USER" npm ci
    
    # Build frontend
    sudo -u "$STAGING_USER" npm run build
    
    success "Frontend setup completed"
}

# Setup systemd services
setup_systemd_services() {
    log "⚙️ Setting up systemd services..."
    
    # Copy service files
    cp "$STAGING_DIR/deployment/configs/china-car-parts-api-staging.service" /etc/systemd/system/
    cp "$STAGING_DIR/deployment/configs/china-car-parts-bot-staging.service" /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable services
    systemctl enable china-car-parts-api-staging
    systemctl enable china-car-parts-bot-staging
    
    success "Systemd services configured"
}

# Setup Nginx
setup_nginx() {
    log "🌐 Setting up Nginx..."
    
    # Copy Nginx configuration
    cp "$STAGING_DIR/deployment/configs/nginx-staging.conf" /etc/nginx/sites-available/china-car-parts-staging
    
    # Create symlink
    ln -sf /etc/nginx/sites-available/china-car-parts-staging /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx configuration
    nginx -t
    
    # Start and enable Nginx
    systemctl start nginx
    systemctl enable nginx
    
    success "Nginx configured"
}

# Create environment file
create_env_file() {
    log "📝 Creating environment file..."
    
    cat > "$STAGING_DIR/.env" << EOF
# Staging Environment Configuration
APP_ENV=staging
DEBUG=false

# Database
DATABASE_URL=postgresql://partsbot:staging_password_$(openssl rand -hex 8)@localhost:5432/china_car_parts_staging

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_staging_bot_token
ADMIN_TELEGRAM_IDS=your_telegram_id

# FastAPI
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
FRONTEND_ORIGIN=https://staging.yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/china-car-parts-staging/app.log

# Security
CORS_ORIGINS=https://staging.yourdomain.com,http://localhost:5173
EOF
    
    # Set ownership and permissions
    chown "$STAGING_USER:$STAGING_GROUP" "$STAGING_DIR/.env"
    chmod 600 "$STAGING_DIR/.env"
    
    success "Environment file created"
}

# Setup log rotation
setup_log_rotation() {
    log "📋 Setting up log rotation..."
    
    cat > /etc/logrotate.d/china-car-parts-staging << EOF
/var/log/china-car-parts-staging/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $STAGING_USER $STAGING_GROUP
    postrotate
        systemctl reload china-car-parts-api-staging
        systemctl reload china-car-parts-bot-staging
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

# Simple monitoring script for China Car Parts staging

API_URL="http://localhost:8001"
LOG_FILE="/var/log/china-car-parts-staging/monitor.log"

check_api() {
    if curl -f -s "$API_URL/api/v1/health" > /dev/null; then
        echo "$(date): API health check passed" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): API health check failed" >> "$LOG_FILE"
        return 1
    fi
}

check_services() {
    if systemctl is-active --quiet china-car-parts-api-staging && systemctl is-active --quiet china-car-parts-bot-staging; then
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
    log "🚀 Starting staging environment setup..."
    
    check_root
    install_system_dependencies
    install_python
    install_nodejs
    create_staging_user
    setup_directories
    setup_postgresql
    clone_repository
    setup_python_venv
    setup_frontend
    setup_systemd_services
    setup_nginx
    create_env_file
    setup_log_rotation
    setup_monitoring
    
    success "✅ Staging environment setup completed!"
    
    log "📋 Next steps:"
    log "  1. Update .env file with actual values"
    log "  2. Configure SSL certificates"
    log "  3. Update DNS to point staging.yourdomain.com to this server"
    log "  4. Start services: systemctl start china-car-parts-api-staging china-car-parts-bot-staging"
    log "  5. Run database migrations: cd $STAGING_DIR && source venv/bin/activate && alembic upgrade head"
}

# Run main function
main "$@"
