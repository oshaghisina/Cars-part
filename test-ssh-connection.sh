#!/bin/bash

# Test SSH connection to production server
# Usage: ./test-ssh-connection.sh

echo "🔍 Testing SSH connection to production server..."
echo ""

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass is not installed. Please install it first:"
    echo "   - Ubuntu/Debian: sudo apt-get install sshpass"
    echo "   - macOS: brew install sshpass"
    echo "   - Or install manually from source"
    exit 1
fi

# Test basic SSH connection
echo "🔍 Testing basic SSH connection..."
echo "Please enter your server details:"
read -p "Host (IP address): " HOST
read -p "Username: " USER
read -s -p "Password: " PASS
echo ""

# Test connection
echo "🔍 Testing connection to $USER@$HOST..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 $USER@$HOST "echo 'SSH connection test successful'"

if [ $? -eq 0 ]; then
    echo "✅ SSH connection successful!"
    echo "🔍 Getting system information..."
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $USER@$HOST "
        echo 'System info:'
        echo '  - OS: $(uname -a)'
        echo '  - User: $(whoami)'
        echo '  - Python: $(python3 --version 2>/dev/null || echo \"Not found\")'
        echo '  - Node: $(node --version 2>/dev/null || echo \"Not found\")'
        echo '  - Git: $(git --version 2>/dev/null || echo \"Not found\")'
    "
else
    echo "❌ SSH connection failed!"
    echo "Possible issues:"
    echo "  - Wrong host/IP address"
    echo "  - Wrong username"
    echo "  - Wrong password"
    echo "  - SSH service not running"
    echo "  - Firewall blocking connection"
    echo "  - User account locked or disabled"
fi
