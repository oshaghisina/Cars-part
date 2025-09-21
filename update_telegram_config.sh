#!/bin/bash

# 🤖 Telegram Bot Configuration Update Script
# This script helps you update your Telegram bot configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 Telegram Bot Configuration Update${NC}"
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Current Telegram Configuration:${NC}"
echo "----------------------------------------"
grep -E "telegram_bot_token|admin_telegram_ids" .env
echo ""

# Get bot token
echo -e "${BLUE}🔑 Enter your Telegram Bot Token:${NC}"
echo "   (Get this from @BotFather - format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890)"
read -p "Bot Token: " BOT_TOKEN

if [ -z "$BOT_TOKEN" ]; then
    echo -e "${RED}❌ Bot token cannot be empty!${NC}"
    exit 1
fi

# Get admin user ID
echo ""
echo -e "${BLUE}👤 Enter your Telegram User ID:${NC}"
echo "   (Get this from @userinfobot - format: 176007160)"
read -p "User ID: " USER_ID

if [ -z "$USER_ID" ]; then
    echo -e "${RED}❌ User ID cannot be empty!${NC}"
    exit 1
fi

# Validate token format
if [[ ! "$BOT_TOKEN" =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
    echo -e "${RED}❌ Invalid bot token format!${NC}"
    echo "   Expected format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890"
    exit 1
fi

# Validate user ID format
if [[ ! "$USER_ID" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}❌ Invalid user ID format!${NC}"
    echo "   Expected format: 176007160"
    exit 1
fi

# Create backup
echo -e "${YELLOW}💾 Creating backup of current .env file...${NC}"
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Update .env file
echo -e "${YELLOW}📝 Updating .env file...${NC}"
sed -i.tmp "s/telegram_bot_token=.*/telegram_bot_token=$BOT_TOKEN/" .env
sed -i.tmp "s/admin_telegram_ids=.*/admin_telegram_ids=$USER_ID/" .env
rm .env.tmp

echo -e "${GREEN}✅ Configuration updated successfully!${NC}"
echo ""

# Show updated configuration
echo -e "${YELLOW}📋 Updated Telegram Configuration:${NC}"
echo "----------------------------------------"
grep -E "telegram_bot_token|admin_telegram_ids" .env
echo ""

echo -e "${BLUE}🔄 Next steps:${NC}"
echo "1. Restart the bot service:"
echo "   pkill -f 'app.bot.bot_dev'"
echo "   python -m app.bot.bot &"
echo ""
echo "2. Test the bot by sending a message to your bot in Telegram"
echo ""
echo "3. Check bot logs:"
echo "   tail -f logs/bot.log"
echo ""

echo -e "${GREEN}🎉 Telegram bot configuration complete!${NC}"
