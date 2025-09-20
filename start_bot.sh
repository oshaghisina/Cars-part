#!/bin/bash

# Telegram Bot Startup Script
# This script ensures only one bot instance is running

echo "🧹 **CLEANING UP EXISTING BOT PROCESSES**"

# Kill all existing bot processes
pkill -f "python.*app.bot.bot" 2>/dev/null
sleep 2

# Verify cleanup
REMAINING=$(ps aux | grep "python.*app.bot.bot" | grep -v grep | wc -l)
echo "📊 Bot processes remaining: $REMAINING"

if [ $REMAINING -gt 0 ]; then
    echo "⚠️  Some processes still running, using force kill..."
    ps aux | grep "python.*app.bot.bot" | grep -v grep | awk '{print $2}' | xargs -I {} kill -9 {} 2>/dev/null
    sleep 2
fi

# Final verification
FINAL_COUNT=$(ps aux | grep "python.*app.bot.bot" | grep -v grep | wc -l)
echo "✅ Final cleanup: $FINAL_COUNT bot processes remaining"

if [ $FINAL_COUNT -eq 0 ]; then
    echo "🤖 **STARTING CLEAN BOT INSTANCE**"
    cd "/Users/sinaoshaghi/Projects/China Car Parts"
    source venv/bin/activate
    python -m app.bot.bot
else
    echo "❌ **FAILED TO CLEAN UP ALL PROCESSES**"
    echo "Please manually kill remaining processes and try again"
    exit 1
fi
