#!/bin/bash

# Start Telegram bot

set -e

echo "🤖 Starting Telegram Bot"

# Activate virtual environment
source venv/bin/activate

# Load environment variables
export $(cat env/.env | grep -v '^#' | xargs)

# Start bot
echo "📱 Starting Telegram bot..."
python -m app.bot.bot
