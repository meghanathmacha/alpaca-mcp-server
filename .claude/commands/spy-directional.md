# SPY 0DTE Directional Trading Command

Research and recommend 0DTE SPY options based on market direction bias: $ARGUMENTS

## Direction-Specific Research:

### If $ARGUMENTS contains "bullish" or "calls":
- Focus on call options and bullish strategies
- Use `orb_long_call()` to check breakout conditions
- Identify near-the-money and slightly OTM calls
- Consider call spreads for defined risk

### If $ARGUMENTS contains "bearish" or "puts":
- Focus on put options and bearish strategies  
- Use `orb_long_put()` to check breakdown conditions
- Identify near-the-money and slightly OTM puts
- Consider put spreads for defined risk

### If $ARGUMENTS contains "neutral" or "sideways":
- Focus on neutral strategies
- Use `iron_condor_30_delta()` for income generation
- Use `straddle_scan()` for volatility plays
- Consider short straddles/strangles if appropriate

### If $ARGUMENTS contains "volatile" or "breakout":
- Focus on long straddles and strangles
- Use `lotto_play_5_delta()` for lottery tickets
- Look for wide bid-ask spreads indicating uncertainty
- Consider both calls and puts for explosive moves

## Analysis Framework:

1. **Current Market Context**
   - Use `get_spy_price()` and recent price action
   - Identify key technical levels (support/resistance)
   - Assess current implied volatility environment

2. **Option Selection Criteria**
   - Liquidity: Minimum volume and open interest
   - Spreads: Tight bid-ask spreads for better execution
   - Time decay: Optimize for remaining time value
   - Delta exposure: Match directional bias

3. **Risk Assessment**
   - Use `risk_check()` to verify account limits
   - Calculate appropriate position sizing
   - Set stop-loss levels and profit targets
   - Consider portfolio correlation and diversification

## Output Format:

### **SPY 0DTE $ARGUMENTS STRATEGY RECOMMENDATIONS**

**Market Setup for $ARGUMENTS Bias:**
- Current SPY: $XXX.XX
- Direction rationale: [Why this direction makes sense]
- Key catalysts: [Events/levels that could drive movement]
- Risk factors: [What could go wrong]

**Recommended Trades (ranked by probability):**

**1. PRIMARY PLAY - [Strategy Name]**
- **Setup**: [Entry conditions]
- **Option**: [Symbol and details]
- **Entry**: $X.XX
- **Target**: $X.XX (+XX% gain)
- **Stop**: $X.XX (-XX% loss)
- **Probability**: XX%

[Continue for 2-4 additional recommendations]

**Position Sizing:**
- Recommended allocation per trade
- Maximum total risk exposure
- Account percentage limits

**Execution Plan:**
1. Monitor for entry conditions
2. Use limit orders for better fills
3. Set stop-losses immediately after entry
4. Take profits at predetermined levels

Would you like me to execute any of these trades using the MCP tools?