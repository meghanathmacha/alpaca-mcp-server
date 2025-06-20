# Quick Market & Options Scanner

Perform a rapid scan of current market conditions and highlight immediate trading opportunities.

## Scanning Protocol:

### 1. Market Snapshot (30 seconds)
- Execute `get_spy_price()` for current SPY level
- Check `market_status()` for trading hours
- Quick assessment of recent price movement and volatility

### 2. Account Quick Check
- Run `get_account()` for buying power
- Execute `risk_check()` for current risk exposure
- Check `portfolio_delta()` for position bias

### 3. Opportunity Scanner
- Run `straddle_scan(max_iv=0.8, min_volume=100)` for volatility plays
- Quick check of all strategy tools for immediate setups:
  - `orb_long_call(preview=True)` - Bullish breakout ready?
  - `orb_long_put(preview=True)` - Bearish breakdown ready?
  - `iron_condor_30_delta(preview=True)` - Neutral income opportunity?
  - `lotto_play_5_delta(side="call", preview=True)` - Lottery ticket potential?

## Output Format:

### **🔍 MARKET SCAN RESULTS - [TIMESTAMP]**

**📊 Market Status:**
- SPY: $XXX.XX ([+/-]$X.XX, [+/-]X.XX%)
- Market: [Open/Closed/Pre-market/After-hours]
- Volatility: [High/Medium/Low based on recent movement]

**💰 Account Status:**
- Buying Power: $XXX,XXX
- Current P&L: $[+/-]XXX
- Portfolio Delta: [+/-]XX
- Risk Status: ✅ Green / ⚠️ Yellow / 🔴 Red

**⚡ Immediate Opportunities:**

**🎯 HIGH PROBABILITY:**
- [List any strategies showing strong setup signals]

**📈 BREAKOUT WATCH:**
- [ORB conditions and key levels]

**🎲 LOTTERY TICKETS:**
- [5-delta options for explosive moves]

**⚖️ NEUTRAL INCOME:**
- [Iron condor and similar opportunities]

**🚨 ALERTS:**
- [Any risk warnings or market conditions to watch]

**⏰ TIME SENSITIVE:**
- [Any setups that need immediate attention]

---

**Next Steps:**
1. Use `/stock-spy0dte` for detailed 0DTE research
2. Use `/spy-directional [bias]` for direction-specific strategies
3. Ask me to execute any specific trade that interests you

**Quick Execute:**
"Execute [strategy name]" for immediate trade execution with MCP tools.