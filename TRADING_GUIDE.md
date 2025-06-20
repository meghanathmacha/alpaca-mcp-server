# SPY Options Trading Quick Reference

## 🚀 Getting Started (Every Session)

```bash
# Option 1: Quick start script
./start_trading.sh

# Option 2: Manual start
source .venv/bin/activate
python trading_session.py
```

## 🎯 Basic Trading Workflow

### 1. Start Session & Check Status
```python
# Session auto-starts, or manually:
from trading_session import main
session = await main()

# Check account status
await session.status()
```

### 2. Find Trading Opportunities
```python
# Scan for options under $5
await session.scan_options(max_price=5.0)

# Scan tomorrow's options
await session.scan_options(days_ahead=1)

# Get current SPY price
spy_price = await session.get_spy_price()
```

### 3. Execute Trades
```python
# Quick buy with auto-limit pricing
await session.quick_buy('SPY250620C00596000')

# Buy with specific limit price
await session.quick_buy('SPY250620C00596000', quantity=2, limit_price=3.50)

# Quick sell position
await session.quick_sell('SPY250620C00596000')
```

### 4. Monitor & Manage
```python
# Check order status
await session.check_orders()

# Account status update
await session.status()

# Session summary
session.session_summary()
```

## 📊 Strategy Tools

### Opening Range Breakout
```python
from services.strategies import strategies

# Preview ORB long call (30-delta)
await strategies.orb_long_call(strike_delta=30, preview=True)

# Preview ORB long put (30-delta)  
await strategies.orb_long_put(strike_delta=30, preview=True)
```

### Iron Condor (Neutral Strategy)
```python
# Preview 30-delta Iron Condor
await strategies.iron_condor_30_delta(width=10, preview=True)
```

### Lottery Plays (High Risk/Reward)
```python
# Preview 5-delta lottery call
await strategies.lotto_play_5_delta(side='call', preview=True)

# Preview 5-delta lottery put
await strategies.lotto_play_5_delta(side='put', preview=True)
```

### Straddle Scanner
```python
# Scan for straddle opportunities
await strategies.straddle_scan(max_iv=0.8, min_volume=100)
```

## 🛡️ Risk Management

### Check Risk Metrics
```python
from services.risk_manager import risk_manager

# Daily P&L
daily_pnl = await risk_manager.get_daily_pnl()

# Portfolio delta exposure
portfolio_delta = await risk_manager.get_portfolio_delta()

# Risk metrics
risk_metrics = await risk_manager.get_risk_metrics()
```

### Emergency Controls
```python
# Emergency stop all trading
await risk_manager.emergency_stop(True)

# Resume trading
await risk_manager.emergency_stop(False)
```

## 📈 Direct API Access

### Account Info
```python
from services.alpaca_client import client_manager

# Get account details
account = client_manager.trading_client.get_account()
positions = client_manager.trading_client.get_all_positions()
orders = client_manager.trading_client.get_orders()
```

### Market Data
```python
from alpaca.data.requests import StockLatestQuoteRequest, OptionSnapshotRequest

# SPY quote
request = StockLatestQuoteRequest(symbol_or_symbols='SPY')
quotes = client_manager.stock_data_client.get_stock_latest_quote(request)

# Option quote
request = OptionSnapshotRequest(symbol_or_symbols=['SPY250620C00596000'])
snapshots = client_manager.option_data_client.get_option_snapshot(request)
```

## 🎯 Quick Trading Examples

### Example 1: Buy ATM Call
```python
# Start session
session = await main()

# Find ATM options
options = await session.scan_options(max_price=5.0)

# Buy the first good option
if options:
    await session.quick_buy(options[0]['symbol'])
```

### Example 2: Scalp Trade
```python
# Buy
await session.quick_buy('SPY250620C00596000', limit_price=3.00)

# Check if filled
await session.check_orders()

# Sell for profit
await session.quick_sell('SPY250620C00596000', limit_price=3.20)
```

### Example 3: Strategy-Based Trade
```python
# Check if ORB conditions are met
result = await strategies.orb_long_call(preview=True)
print(result)

# If conditions look good, scan for the right option
options = await session.scan_options()

# Execute trade
await session.quick_buy('BEST_OPTION_SYMBOL')
```

## ⚡ Power User Tips

1. **Alias for quick start**: Add to your shell profile:
   ```bash
   alias trade='cd /path/to/alpaca-mcp-server && ./start_trading.sh'
   ```

2. **Custom price alerts**: Set up watchlist and check periodically:
   ```python
   session.watchlist = ['SPY250620C00596000', 'SPY250620P00590000']
   # Check periodically with session.status()
   ```

3. **Batch operations**: Execute multiple commands:
   ```python
   # Multiple scans
   calls = await session.scan_options(max_price=3.0)
   puts = await session.scan_options(max_price=3.0)
   
   # Multiple orders
   await session.quick_buy(calls[0]['symbol'])
   await session.quick_buy(puts[0]['symbol'])
   ```

4. **Risk-first trading**: Always check P&L before trading:
   ```python
   await session.status()  # Shows current P&L
   # Only trade if within risk limits
   ```

## 🔧 Troubleshooting

### Common Issues
- **Market closed**: Use limit orders instead of market orders
- **No options found**: Try different expiration dates or price ranges
- **Order rejected**: Check buying power and option availability
- **Connection issues**: Restart session and check API keys

### Debug Commands
```python
# Test API connection
from services.alpaca_client import client_manager
account = client_manager.trading_client.get_account()

# Check environment
from services.config import config
print(f"Paper trading: {config.paper}")
print(f"API key: {config.alpaca_api_key[:10]}...")
```

## 🎯 Claude Code Slash Commands

### Custom Trading Commands
When using Claude Code, three specialized slash commands are available:

#### `/stock-spy0dte`
Comprehensive 0DTE SPY options research and recommendations:
```
/stock-spy0dte
```
**Output**: 5 detailed trade recommendations with full analysis
- Market conditions assessment
- Options chain analysis  
- Risk/reward calculations
- Immediate execution capability

#### `/spy-directional [bias]`
Direction-specific strategy recommendations:
```
/spy-directional bullish
/spy-directional bearish  
/spy-directional neutral
/spy-directional volatile
```
**Output**: Tailored strategies matching your market outlook
- Bullish: Focus on calls and breakout strategies
- Bearish: Focus on puts and breakdown strategies
- Neutral: Iron condors and income strategies
- Volatile: Straddles and breakout plays

#### `/market-scan`
Quick 30-second market and opportunity scanner:
```
/market-scan
```
**Output**: Rapid market assessment
- Current SPY price and movement
- Account status check
- Immediate trading opportunities
- Risk alerts and time-sensitive setups

### Example Claude Code Workflow
```
1. Start: /market-scan
2. Research: /stock-spy0dte  
3. Execute: "Execute option #2 from the recommendations"
4. Monitor: Check account status
5. Manage: Set stops and targets
```

## 📞 Support

- **Alpaca API Docs**: https://docs.alpaca.markets/
- **Paper Trading Dashboard**: https://app.alpaca.markets/paper/dashboard
- **Risk Management**: All trades use paper money for safety
- **Claude Code Best Practices**: https://www.anthropic.com/engineering/claude-code-best-practices