# TODO: SPY 0DTE Trading Bot - Extensions to Existing MCP Server

**Current State**: Comprehensive 1,589-line `alpaca_mcp_server.py` with 26 MCP tools already implemented.  
**Goal**: Extend existing implementation to add 0DTE-specific trading strategies and optimizations.

## 📊 Progress Status

**✅ COMPLETED:**
- Week 1: Strategic Trading Tools (5/5 tools) ✅
- Modular architecture refactoring (`services/` modules)
- Strategic tools: `orb_long_call()`, `orb_long_put()`, `iron_condor_30_delta()`, `lotto_play_5_delta()`, `straddle_scan()`
- Risk management framework with preview-confirm pattern
- Utility tools: `show_pnl()`, `portfolio_delta()`, `risk_check()`, `kill_switch()`, `flatten_all()`
- In-memory option chain cache with auto-expiry
- Configuration management with Pydantic
- Enhanced error handling and user-friendly responses

**🔄 IN PROGRESS:**
- Week 2: Risk & utility tools implementation

**📋 NEXT UP:**
- W2.1-W2.5: Risk management and utility tools
- Week 3: Preview-confirm pattern completion

---

## 🎯 What's Already Working

✅ **26 MCP Tools**: Account, positions, stock/options trading, market data, watchlists  
✅ **Options Support**: Multi-leg orders, Greeks, snapshots, contract search  
✅ **Order Management**: All order types (market, limit, stop, trailing), cancellation  
✅ **Risk Features**: Position sizing, account validation, error handling  
✅ **FastMCP Framework**: Proper async tools, environment config, client setup  

---

## 🚀 Extensions Needed (6-Week Roadmap)

### Week 1: Strategic Trading Tools ✅ COMPLETED
- [x] **W1.1** `orb_long_call()` - Opening Range Breakout call strategy ✅
- [x] **W1.2** `orb_long_put()` - Opening Range Breakout put strategy ✅
- [x] **W1.3** `iron_condor_30_delta()` - 30-Delta Iron Condor builder ✅
- [x] **W1.4** `lotto_play_5_delta()` - Late-day 5-Delta lottery plays ✅
- [x] **W1.5** `straddle_scan()` - Profitable straddle finder ✅

### Week 2: Risk & Utility Tools
- [ ] **W2.1** `flatten_all()` - Enhanced version of existing `close_all_positions`
- [ ] **W2.2** `show_pnl()` - Real-time P&L summary with Greeks
- [ ] **W2.3** `kill_switch()` - Emergency trading halt toggle
- [ ] **W2.4** `portfolio_delta()` - Real-time portfolio delta monitoring
- [ ] **W2.5** `risk_check()` - Pre-trade risk validation

### Week 3: Preview-Confirm Pattern
- [ ] **W3.1** Add `preview` parameter to all strategy tools
- [ ] **W3.2** Trade preview with cost/risk analysis
- [ ] **W3.3** Two-step confirmation enforcement
- [ ] **W3.4** Confirmation timeout handling (30s default)
- [ ] **W3.5** Enhanced error messages for failed confirmations

### Week 4: 0DTE Optimizations
- [ ] **W4.1** In-memory SPY option chain cache (`OptionChainCache` class)
- [ ] **W4.2** Real-time WebSocket streaming integration
- [ ] **W4.3** Auto-expiry at 4:15pm ET daily
- [ ] **W4.4** Thread-safe concurrent access for multiple MCP clients
- [ ] **W4.5** <1s latency option chain updates

### Week 5: Production Features
- [ ] **W5.1** Enhanced risk validation layer with configurable limits
- [ ] **W5.2** Immutable trade logging to S3
- [ ] **W5.3** Prometheus metrics endpoint (`/metrics`)
- [ ] **W5.4** Health check endpoint (`/health`)
- [ ] **W5.5** PagerDuty alert integration

### Week 6: Testing & Deployment
- [ ] **W6.1** Unit tests for new strategy tools
- [ ] **W6.2** Integration tests with paper trading
- [ ] **W6.3** Performance testing (100-session burn-in)
- [ ] **W6.4** Docker optimization for production
- [ ] **W6.5** Documentation updates

---

## 🛠️ New MCP Tools to Add

### Strategic Tools
```python
@mcp.tool()
async def orb_long_call(strike_delta: float = 30, preview: bool = True) -> str:
    """Opening Range Breakout - Long Call Strategy"""

@mcp.tool()
async def orb_long_put(strike_delta: float = 30, preview: bool = True) -> str:
    """Opening Range Breakout - Long Put Strategy"""

@mcp.tool()
async def iron_condor_30_delta(width: int = 10, preview: bool = True) -> str:
    """30-Delta Iron Condor Strategy"""

@mcp.tool()
async def lotto_play_5_delta(side: str = "call", preview: bool = True) -> str:
    """Late-day 5-Delta Lottery Play"""

@mcp.tool()
async def straddle_scan(max_iv: float = 0.8, min_volume: int = 100) -> str:
    """Scan for Profitable Straddle Opportunities"""
```

### Utility Tools
```python
@mcp.tool()
async def flatten_all() -> str:
    """Close all positions immediately"""

@mcp.tool()
async def show_pnl() -> str:
    """Display real-time P&L with Greeks breakdown"""

@mcp.tool()
async def kill_switch(enable: bool = True) -> str:
    """Emergency trading halt toggle"""

@mcp.tool()
async def portfolio_delta() -> str:
    """Real-time portfolio delta exposure"""

@mcp.tool()
async def risk_check() -> str:
    """Pre-trade risk validation summary"""
```

---

## 🏗️ Code Additions Required

### 1. Risk Management Layer
```python
# Add to alpaca_mcp_server.py
class RiskManager:
    def __init__(self, max_daily_loss: float = 500, delta_cap: float = 50):
        self.max_daily_loss = max_daily_loss
        self.delta_cap = delta_cap
    
    async def validate_trade(self, order_preview: dict) -> bool:
        """Pre-trade risk validation"""
        
    async def check_daily_loss(self) -> bool:
        """Check if daily loss cap exceeded"""
```

### 2. Option Chain Cache
```python
# Add to alpaca_mcp_server.py
import asyncio
from dataclasses import dataclass
from typing import Dict

@dataclass
class OptionData:
    symbol: str
    bid: float
    ask: float
    delta: float
    gamma: float
    theta: float
    vega: float
    iv: float
    volume: int
    timestamp: datetime

class OptionChainCache:
    def __init__(self):
        self._cache: Dict[str, OptionData] = {}
        self._lock = asyncio.Lock()
        self._last_update = datetime.now()
    
    async def update_chain(self, spy_options: List[OptionData]):
        """Thread-safe cache update"""
        
    async def get_by_delta(self, target_delta: float, option_type: str) -> OptionData:
        """Find option by target delta"""
```

### 3. Preview-Confirm Pattern
```python
# Add to existing tool functions
class TradePreview:
    def __init__(self, strategy: str, cost: float, max_loss: float, max_profit: float):
        self.strategy = strategy
        self.cost = cost
        self.max_loss = max_loss
        self.max_profit = max_profit
        self.confirmation_token = f"confirm_{int(time.time())}"

async def generate_preview(strategy_name: str, legs: List[dict]) -> TradePreview:
    """Generate trade preview with risk metrics"""
```

### 4. WebSocket Integration
```python
# Extend existing stock_data_stream_client usage
async def start_option_stream():
    """Start real-time option data streaming"""
    
async def handle_option_update(data):
    """Update in-memory cache with real-time data"""
```

---

## 📊 Configuration Extensions

### Environment Variables to Add
```bash
# Risk Management
MAX_DAILY_LOSS=500
PORTFOLIO_DELTA_CAP=50
CONFIRMATION_TIMEOUT=30

# 0DTE Specific
SPY_CHAIN_UPDATE_INTERVAL=2
AUTO_EXPIRE_TIME="16:15"
CACHE_CLEANUP_INTERVAL=300

# Monitoring
PROMETHEUS_PORT=9090
S3_AUDIT_BUCKET=trading-audit-logs
PAGERDUTY_API_KEY=your_key
```

### Config Class Extension
```python
# Add to common/config.py (new file)
from pydantic import BaseSettings

class TradingConfig(BaseSettings):
    # Existing Alpaca config
    alpaca_api_key: str
    alpaca_secret_key: str
    paper: bool = True
    
    # New risk config
    max_daily_loss: float = 500
    delta_cap: float = 50
    confirmation_timeout: int = 30
    
    # 0DTE config
    spy_update_interval: int = 2
    auto_expire_time: str = "16:15"
    
    class Config:
        env_file = ".env"
```

---

## 🧪 Testing Strategy

### Unit Tests (New)
- [ ] **TEST.1** Strategy tool logic (ORB, Iron Condor, Lotto)
- [ ] **TEST.2** Risk validation scenarios
- [ ] **TEST.3** Preview-confirm flow
- [ ] **TEST.4** Option chain cache operations
- [ ] **TEST.5** WebSocket data handling

### Integration Tests (Extend)
- [ ] **INT.1** End-to-end strategy execution in paper account
- [ ] **INT.2** Risk limit breach scenarios
- [ ] **INT.3** Concurrent MCP client access
- [ ] **INT.4** Market data streaming reliability
- [ ] **INT.5** Emergency kill-switch functionality

---

## 🚀 Deployment Updates

### Docker Extensions
```dockerfile
# Update existing Dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

# Add new dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080 9090
CMD ["python", "alpaca_mcp_server.py"]
```

### New Dependencies
```txt
# Add to requirements.txt
prometheus-client==0.20.0
asyncio-mqtt==0.16.1
boto3==1.34.144
pydantic==2.7.4
```

---

## 🎯 Success Metrics

### Performance Targets
- [ ] **PERF.1** Option chain update latency ≤ 1s p95
- [ ] **PERF.2** Strategy tool response time ≤ 500ms
- [ ] **PERF.3** Preview generation ≤ 200ms
- [ ] **PERF.4** Risk validation ≤ 100ms
- [ ] **PERF.5** Concurrent client support ≥ 3

### Operational Targets
- [ ] **OPS.1** Zero unintended trades (preview-confirm enforcement)
- [ ] **OPS.2** Daily loss cap: 0 breaches
- [ ] **OPS.3** Portfolio delta within limits: 100% compliance
- [ ] **OPS.4** Kill-switch activation: ≤ 1s response time
- [ ] **OPS.5** Data expiry: automatic at 4:15pm ET

---

## 📝 Implementation Notes

**Extend, Don't Replace**: Build on the solid 1,589-line foundation
**Minimal Dependencies**: Leverage existing Alpaca SDK and FastMCP framework  
**0DTE Focus**: Optimize for same-day expiry with in-memory caching
**Risk First**: All new tools must implement preview-confirm pattern
**Production Ready**: Include monitoring, logging, and health checks from day one

---

*Based on existing alpaca_mcp_server.py analysis - Focus on strategic extensions*