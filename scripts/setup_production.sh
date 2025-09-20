#!/bin/bash

# Production Setup Script for China Car Parts System
# This script sets up the production environment

set -e

echo "🚀 Setting up China Car Parts Production Environment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
print_status "Project directory: $PROJECT_DIR"

# 1. Install PostgreSQL
print_status "Installing PostgreSQL..."
if command -v psql &> /dev/null; then
    print_success "PostgreSQL is already installed"
else
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install postgresql@14
            brew services start postgresql@14
        else
            print_error "Homebrew not found. Please install PostgreSQL manually."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y postgresql postgresql-contrib
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
fi

# 2. Create database and user
print_status "Setting up database..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - create user and database
    createuser -s admin 2>/dev/null || print_warning "User 'admin' might already exist"
    createdb china_car_parts -O admin 2>/dev/null || print_warning "Database 'china_car_parts' might already exist"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - use sudo
    sudo -u postgres createuser -s admin 2>/dev/null || print_warning "User 'admin' might already exist"
    sudo -u postgres createdb china_car_parts -O admin 2>/dev/null || print_warning "Database 'china_car_parts' might already exist"
fi

# 3. Install Python dependencies
print_status "Installing Python dependencies..."
cd "$PROJECT_DIR"
source venv/bin/activate
pip install -r requirements.txt
pip install psycopg2-binary

# 4. Set up environment variables
print_status "Setting up environment variables..."
if [ ! -f .env ]; then
    cp env/production.env .env
    print_warning "Please edit .env file with your production values:"
    print_warning "- TELEGRAM_BOT_TOKEN"
    print_warning "- SECRET_KEY (generate a secure random string)"
    print_warning "- JWT_SECRET_KEY (generate a secure random string)"
    print_warning "- Database credentials if different"
fi

# 5. Run database migrations
print_status "Running database migrations..."
alembic upgrade head

# 6. Create sample data
print_status "Creating sample data..."
python create_sample_data.py

# 7. Set up systemd services
print_status "Setting up systemd services..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Create systemd service files
    sudo tee /etc/systemd/system/china-car-parts-api.service > /dev/null <<EOF
[Unit]
Description=China Car Parts API
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/uvicorn app.api.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo tee /etc/systemd/system/china-car-parts-bot.service > /dev/null <<EOF
[Unit]
Description=China Car Parts Telegram Bot
After=network.target postgresql.service china-car-parts-api.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python -m app.bot.bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable services
    sudo systemctl daemon-reload
    sudo systemctl enable china-car-parts-api
    sudo systemctl enable china-car-parts-bot
    
    print_success "Systemd services created and enabled"
else
    print_warning "Systemd services not created (not on Linux)"
fi

# 8. Set up log directory
print_status "Setting up logging..."
mkdir -p "$PROJECT_DIR/logs"
mkdir -p /var/log/china-car-parts 2>/dev/null || print_warning "Could not create /var/log/china-car-parts (requires sudo)"

# 9. Set up SSL certificates (placeholder)
print_status "SSL Certificate Setup..."
print_warning "Please obtain SSL certificates for your domain and update the paths in .env file"
print_warning "You can use Let's Encrypt: certbot --nginx -d your-domain.com"

# 10. Set up Nginx configuration
print_status "Setting up Nginx configuration..."
if command -v nginx &> /dev/null; then
    sudo tee /etc/nginx/sites-available/china-car-parts > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # API Backend
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Admin Panel Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/china-car-parts /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    print_success "Nginx configuration created"
else
    print_warning "Nginx not found. Please install and configure manually."
fi

print_success "Production setup completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file with your production values"
echo "2. Obtain SSL certificates for your domain"
echo "3. Update Nginx configuration with your domain"
echo "4. Start services:"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "   sudo systemctl start china-car-parts-api"
    echo "   sudo systemctl start china-car-parts-bot"
    echo "   sudo systemctl start nginx"
else
    echo "   # Manual start commands for macOS:"
    echo "   cd $PROJECT_DIR && source venv/bin/activate"
    echo "   uvicorn app.api.main:app --host 0.0.0.0 --port 8001 &"
    echo "   python -m app.bot.bot &"
fi
echo "5. Test your setup: https://your-domain.com"
echo ""
print_success "🎉 China Car Parts is ready for production!"
