# SPY 0DTE Options Research & Strategy Command

Please conduct comprehensive research on tomorrow's 0DTE SPY options and provide 5 strategic trading recommendations.

## Research Process:

### 1. Market Analysis
- Use `get_spy_price()` to get current SPY price and recent movement
- Check `market_status()` to understand current market conditions
- Analyze SPY recent price action and volatility patterns

### 2. Options Chain Analysis
- Scan available 0DTE SPY options expiring tomorrow
- Identify liquid options with reasonable bid-ask spreads
- Calculate implied volatility and time decay factors
- Focus on strikes within 2-3% of current SPY price for best liquidity

### 3. Strategy Assessment
Use the built-in strategy tools to evaluate opportunities:
- **Opening Range Breakout**: Check `orb_long_call()` and `orb_long_put()` conditions
- **Iron Condor**: Evaluate `iron_condor_30_delta()` for neutral income
- **Lottery Plays**: Assess `lotto_play_5_delta()` for high-risk/reward
- **Straddle Opportunities**: Use `straddle_scan()` for volatility plays

### 4. Risk Analysis
- Check current account status with `get_account()`
- Verify risk limits with `risk_check()`
- Calculate position sizing based on account balance
- Assess portfolio delta exposure with `portfolio_delta()`

## Required Output Format:

Provide exactly 5 trading recommendations in this format:

### **SPY 0DTE TRADING RECOMMENDATIONS FOR [DATE]**

**Market Context:**
- Current SPY: $XXX.XX
- Market conditions: [Open/Closed, volatility assessment]
- Key levels to watch: [Support/resistance]

**Top 5 Opportunities:**

**1. [Strategy Name] - [Risk Level]**
- **Option**: [Symbol] ([Strike] [Call/Put])
- **Current Price**: $X.XX (Bid: $X.XX / Ask: $X.XX)
- **Cost**: $XXX for 1 contract
- **Strategy**: [Brief description]
- **Trigger**: [When to enter]
- **Target**: [Profit target]
- **Risk**: [Max loss]
- **Probability**: [Success likelihood]

[Repeat for options 2-5]

**Account Status:**
- Available buying power: $XXX,XXX
- Current P&L: $XXX
- Portfolio delta: XXX

**Risk Management:**
- Maximum recommended position size per trade
- Stop-loss recommendations
- Portfolio diversification notes

## Execution Instructions:

After presenting the 5 options, ask: **"Which option would you like me to execute? I can place the order immediately using the MCP trading tools."**

If the user selects an option:
1. Use the appropriate MCP tool to execute the trade
2. Confirm order details before submission
3. Provide order confirmation and tracking information

**Important Safety Notes:**
- All trades execute on paper trading account
- Use preview mode first for all strategies
- Emergency stop available via `emergency_stop(True)`
- Monitor positions with real-time P&L tracking