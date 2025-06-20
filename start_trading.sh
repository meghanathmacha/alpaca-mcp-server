#!/bin/bash

# Trading Session Startup Script
# ==============================

echo "🚀 Starting SPY Options Trading Session..."

# Activate virtual environment
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import alpaca" &> /dev/null; then
    echo "📦 Installing dependencies..."
    uv pip install -r requirements.txt
fi

# Check API connection
echo "🔌 Testing API connection..."
if python -c "
import asyncio
from services.alpaca_client import client_manager
try:
    account = client_manager.trading_client.get_account()
    print(f'✅ Connected to account: {account.id}')
    print(f'📊 Buying power: \${account.buying_power}')
except Exception as e:
    print(f'❌ Connection failed: {e}')
    exit(1)
"; then
    echo "✅ API connection successful"
else
    echo "❌ API connection failed"
    exit 1
fi

echo ""
echo "🎯 TRADING SESSION READY"
echo "======================="
echo "Quick commands:"
echo "  python trading_session.py    # Start interactive session"
echo "  python direct_trading.py     # Direct trading interface"
echo ""
echo "Or start Python and run:"
echo "  from trading_session import main"
echo "  session = await main()"
echo ""

# Option to auto-start Python session
read -p "Start Python trading session now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🐍 Starting Python session..."
    python -c "
import asyncio
from trading_session import main

print('🚀 Loading trading session...')
session = asyncio.run(main())
print()
print('💡 Session object created as \"session\"')
print('💡 Try: await session.scan_options()')
print()

# Keep session alive for interactive use
import code
code.interact(local=locals())
"
fi