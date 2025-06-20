# TODO: SPY 0DTE Trading Bot - Extensions to Existing MCP Server

**Current State**: Comprehensive 1,589-line `alpaca_mcp_server.py` with 26 MCP tools already implemented.  
**Goal**: Extend existing implementation to add 0DTE-specific trading strategies and optimizations.

## 📊 Progress Status

**✅ COMPLETED:**
- Week 1: Strategic Trading Tools (5/5 tools) ✅
- Week 2: Risk & Utility Tools + Enhancements (9/9 tools) ✅
- Modular architecture refactoring (`services/` modules)
- Strategic tools: `orb_long_call()`, `orb_long_put()`, `iron_condor_30_delta()`, `lotto_play_5_delta()`, `straddle_scan()`
- Risk management framework with preview-confirm pattern
- Utility tools: `show_pnl()`, `portfolio_delta()`, `risk_check()`, `kill_switch()`, `flatten_all()`
- Advanced analytics: `portfolio_greeks()`, `risk_metrics()` with comprehensive warnings
- Real-time streaming: `start_option_streaming()`, `stop_option_streaming()`, `streaming_status()`
- In-memory option chain cache with auto-expiry
- Configuration management with Pydantic
- Enhanced error handling and user-friendly responses

**🔄 IN PROGRESS:**
- Week 4: Performance optimization and latency improvements

**📋 NEXT UP:**
- W4.5-W4.9: <1s latency optimization and benchmarking
- W5.2-W5.9: Production deployment features
- W6.1-W6.5: Testing and deployment pipeline

## 📈 Development Velocity

**Weeks 1-3 Accomplished (Ahead of Schedule):**
- ✅ 18 MCP tools implemented (5 strategic + 9 risk/utility + 4 execution/tracking)
- ✅ Complete trade execution pipeline with real order submission
- ✅ Advanced risk analytics with portfolio Greeks
- ✅ Real-time option streaming capability
- ✅ Preview-confirm pattern with full execution
- ✅ Order tracking and position reconciliation
- ✅ Modular architecture with comprehensive error handling

**Current Status:** 75% of 6-week roadmap completed in 3 weeks

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

### Week 2: Risk & Utility Tools ✅ COMPLETED
- [x] **W2.1** `flatten_all()` - Enhanced version of existing `close_all_positions` ✅
- [x] **W2.2** `show_pnl()` - Real-time P&L summary with Greeks ✅
- [x] **W2.3** `kill_switch()` - Emergency trading halt toggle ✅
- [x] **W2.4** `portfolio_delta()` - Real-time portfolio delta monitoring ✅
- [x] **W2.5** `risk_check()` - Pre-trade risk validation ✅

**Week 2 Enhancements:**
- [x] **W2.6** Advanced portfolio Greeks analysis (`portfolio_greeks()`) ✅
- [x] **W2.7** Comprehensive risk metrics (`risk_metrics()`) ✅
- [x] **W2.8** Real-time option streaming (`start_option_streaming()`, `stop_option_streaming()`) ✅
- [x] **W2.9** Streaming status monitoring (`streaming_status()`) ✅

### Week 3: Trade Execution Pipeline ✅ COMPLETED
- [x] **W3.1** Add `preview` parameter to all strategy tools ✅
- [x] **W3.2** Trade preview with cost/risk analysis ✅
- [x] **W3.3** Two-step confirmation enforcement ✅
- [x] **W3.4** Confirmation timeout handling (30s default) ✅
- [x] **W3.5** Enhanced error messages for failed confirmations ✅
- [x] **W3.6** Complete trade execution logic with real API calls ✅
- [x] **W3.7** Order validation and submission pipeline ✅
- [x] **W3.8** Fill status tracking and reporting ✅
- [x] **W3.9** Post-trade position reconciliation ✅

**Week 3 New Tools:**
- [x] **W3.10** `get_order_status(order_id)` - Individual order tracking ✅
- [x] **W3.11** `get_recent_orders(limit)` - Order history viewer ✅
- [x] **W3.12** `cancel_order(order_id)` - Order cancellation ✅
- [x] **W3.13** `reconcile_positions()` - Post-trade validation ✅

### Week 4: 0DTE Optimizations ✅ Partially Complete
- [x] **W4.1** In-memory SPY option chain cache (`OptionChainCache` class) ✅ (Already implemented)
- [x] **W4.2** Real-time WebSocket streaming integration ✅ (Already implemented)
- [x] **W4.3** Auto-expiry at 4:15pm ET daily ✅ (Already implemented)
- [x] **W4.4** Thread-safe concurrent access for multiple MCP clients ✅ (Already implemented)
- [ ] **W4.5** <1s latency option chain updates (currently 2s) 🔄
- [ ] **W4.6** Performance optimization and memory management
- [ ] **W4.7** Connection pooling and API rate limiting
- [ ] **W4.8** Caching strategy optimization for high-frequency updates
- [ ] **W4.9** Load testing and performance benchmarking

### Week 5: Production Features ✅ Partially Complete
- [x] **W5.1** Enhanced risk validation layer with configurable limits ✅ (Already implemented)
- [ ] **W5.2** Immutable trade logging to S3
- [ ] **W5.3** Prometheus metrics endpoint (`/metrics`)
- [ ] **W5.4** Health check endpoint (`/health`)
- [ ] **W5.5** PagerDuty alert integration
- [ ] **W5.6** Circuit breaker implementation for API failures
- [ ] **W5.7** Automated backup and disaster recovery
- [ ] **W5.8** Production deployment pipeline
- [ ] **W5.9** Security audit and penetration testing

### Week 6: Testing & Deployment
- [ ] **W6.1** Unit tests for new strategy tools
- [ ] **W6.2** Integration tests with paper trading
- [ ] **W6.3** Performance testing (100-session burn-in)
- [ ] **W6.4** Docker optimization for production
- [ ] **W6.5** Documentation updates

---

## 🛠️ Implemented MCP Tools (18 Total)

### ✅ Strategic Trading Tools (Week 1)
```python
@mcp.tool()
async def orb_long_call(strike_delta: float = 30, preview: bool = True, confirm_token: str = None) -> str:
    """Opening Range Breakout - Long Call Strategy with execution"""

@mcp.tool()
async def orb_long_put(strike_delta: float = 30, preview: bool = True, confirm_token: str = None) -> str:
    """Opening Range Breakout - Long Put Strategy with execution"""

@mcp.tool()
async def iron_condor_30_delta(width: int = 10, preview: bool = True, confirm_token: str = None) -> str:
    """30-Delta Iron Condor Strategy with execution"""

@mcp.tool()
async def lotto_play_5_delta(side: str = "call", preview: bool = True, confirm_token: str = None) -> str:
    """Late-day 5-Delta Lottery Play with execution"""

@mcp.tool()
async def straddle_scan(max_iv: float = 0.8, min_volume: int = 100) -> str:
    """Scan for Profitable Straddle Opportunities"""
```

### ✅ Risk & Utility Tools (Week 2)
```python
@mcp.tool()
async def show_pnl() -> str:
    """Display real-time P&L with Greeks breakdown"""

@mcp.tool()
async def portfolio_delta() -> str:
    """Real-time portfolio delta exposure"""

@mcp.tool()
async def portfolio_greeks() -> str:
    """Comprehensive portfolio Greeks analysis"""

@mcp.tool()
async def risk_check() -> str:
    """Pre-trade risk validation summary"""

@mcp.tool()
async def risk_metrics() -> str:
    """Advanced risk analytics with warnings"""

@mcp.tool()
async def kill_switch(enable: bool = True) -> str:
    """Emergency trading halt toggle"""

@mcp.tool()
async def flatten_all() -> str:
    """Enhanced position closure"""
```

### ✅ Real-time Streaming Tools (Week 2)
```python
@mcp.tool()
async def start_option_streaming() -> str:
    """Start real-time 0DTE SPY option streaming"""

@mcp.tool()
async def stop_option_streaming() -> str:
    """Stop real-time option streaming"""

@mcp.tool()
async def streaming_status() -> str:
    """Check streaming status and performance"""
```

### ✅ Order Execution & Tracking Tools (Week 3)
```python
@mcp.tool()
async def get_order_status(order_id: str) -> str:
    """Get detailed order status and fill information"""

@mcp.tool()
async def get_recent_orders(limit: int = 10) -> str:
    """View recent orders with current status"""

@mcp.tool()
async def cancel_order(order_id: str) -> str:
    """Cancel a specific order by ID"""

@mcp.tool()
async def reconcile_positions() -> str:
    """Post-trade position reconciliation and validation"""
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