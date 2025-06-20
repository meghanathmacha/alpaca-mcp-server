# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server for Alpaca Trading API that enables natural language interaction with stock and options trading. The server has been extended with 0DTE (zero days to expiration) trading strategies and enhanced risk management.

## Architecture Overview

### Current Structure (Refactored)
- **Modular Design**: Code is now organized into service modules for better maintainability
- **Two Server Files**: 
  - `alpaca_mcp_server.py` - Original monolithic implementation (1,589 lines, 26 tools)
  - `alpaca_mcp_server_new.py` - Refactored modular implementation with 0DTE features
- **Service Layer**: Separate modules for configuration, clients, caching, risk management, and strategies

### Service Modules

#### `services/config.py`
- Pydantic-based configuration management
- Environment variable validation
- Risk management parameters
- 0DTE-specific settings

#### `services/alpaca_client.py`
- Centralized Alpaca client management
- Lazy initialization of clients
- Support for trading, market data, and options clients

#### `services/option_chain_cache.py`
- In-memory caching for 0DTE SPY option chains
- Thread-safe operations with asyncio locks
- Auto-expiry at 4:15 PM ET daily
- Delta-based option lookup

#### `services/risk_manager.py`
- Pre-trade risk validation
- Preview-confirm pattern implementation
- Daily P&L and portfolio delta monitoring
- Emergency stop functionality

#### `services/strategies.py`
- 0DTE trading strategies implementation
- Opening Range Breakout (ORB) strategies
- Iron Condor and other neutral strategies
- Strategy-specific risk analysis

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment file
cp .env.example .env
# Edit .env with your Alpaca API credentials and risk parameters
```

### Running the Servers
```bash
# Original server (legacy compatibility)
python alpaca_mcp_server.py

# New refactored server with 0DTE features
python alpaca_mcp_server_new.py

# Test with Claude Desktop or VS Code
# Configuration files in .vscode/mcp.json for VS Code
```

### Testing New Features
```bash
# Test 0DTE strategies (in paper trading mode)
# Use Claude to interact with implemented tools:

# Strategic Tools (Week 1 ✅)
# - orb_long_call(strike_delta=30, preview=True)
# - orb_long_put(strike_delta=30, preview=True) 
# - iron_condor_30_delta(width=10, preview=True)
# - lotto_play_5_delta(side="call", preview=True)
# - straddle_scan(max_iv=0.8, min_volume=100)

# Risk & Utility Tools (Week 1 ✅)
# - show_pnl()
# - portfolio_delta()
# - risk_check()
# - kill_switch(enable=False)
# - flatten_all()

# Option Chain Management
# - update_spy_chain()
```

## New 0DTE Features (Weeks 1-4 ✅ COMPLETED)

### Strategic Trading Tools (All Implemented with Full Execution)
1. **Opening Range Breakout**: `orb_long_call()`, `orb_long_put()` ✅
2. **Iron Condor**: `iron_condor_30_delta()` ✅
3. **Lottery Plays**: `lotto_play_5_delta()` ✅
4. **Straddle Scanner**: `straddle_scan()` ✅
5. **Risk Management**: `show_pnl()`, `portfolio_delta()`, `risk_check()` ✅
6. **Emergency Controls**: `kill_switch()`, `flatten_all()` ✅

### Order Execution & Tracking Tools (Week 3 ✅ COMPLETED)
7. **Order Status**: `get_order_status(order_id)` ✅
8. **Order History**: `get_recent_orders(limit)` ✅
9. **Order Management**: `cancel_order(order_id)` ✅
10. **Position Reconciliation**: `reconcile_positions()` ✅

### Performance & Monitoring Tools (Week 4 ✅ COMPLETED)
11. **Performance Dashboard**: `performance_stats()` ✅
12. **Health Monitoring**: `system_health_check()` ✅
13. **Load Testing**: `benchmark_performance(duration)` ✅

### Preview-Confirm-Execute Pattern
All strategic tools implement a complete three-step process:
1. **Preview Mode**: Shows trade details, cost, risk analysis, and confirmation token
2. **Validation**: Pre-execution risk checks and violation reporting
3. **Execution Mode**: Real API order submission with comprehensive error handling

### Risk Management
- **Daily Loss Cap**: Configurable maximum daily loss (default: $500)
- **Portfolio Delta Cap**: Maximum absolute delta exposure (default: 50)
- **Pre-trade Validation**: All trades validated against risk limits
- **Real-time Monitoring**: Continuous P&L and delta tracking

### Performance Optimization (Week 4 ✅)
- **Sub-Second Latency**: Option chain updates optimized to 0.5s (from 2s)
- **Rate Limiting**: 200 requests/minute with endpoint-specific tracking
- **Connection Pooling**: Optimized API client management
- **Performance Monitoring**: Real-time metrics and benchmarking
- **Load Testing**: Comprehensive performance analysis tools

### In-Memory Caching
- **0DTE Optimization**: SPY option chains cached in memory
- **Auto-Expiry**: Data automatically expires at 4:15 PM ET
- **Thread-Safe**: Concurrent access from multiple MCP clients
- **Delta Lookup**: Fast option selection by target delta
- **Concurrent Processing**: Async batch processing with semaphores

## Configuration

### Environment Variables
```bash
# Risk Management
MAX_DAILY_LOSS=500.0          # Maximum daily loss in dollars
PORTFOLIO_DELTA_CAP=50.0      # Maximum absolute portfolio delta
CONFIRMATION_TIMEOUT=30       # Trade confirmation timeout in seconds

# 0DTE Trading
SPY_CHAIN_UPDATE_INTERVAL=2   # Option chain update interval in seconds
AUTO_EXPIRE_TIME="16:15"      # Auto-expire time for 0DTE data
CACHE_CLEANUP_INTERVAL=300    # Cache cleanup interval in seconds
```

## Adding New Tools

### For Strategic Tools
1. Add strategy logic to `services/strategies.py`
2. Implement preview-confirm-execute pattern
3. Include risk analysis in previews
4. Add execution logic in `execute_strategy()` method
5. Add tool decorator in main server file
6. Test with paper trading first

### For Utility Tools
1. Add business logic to appropriate service module
2. Use `@mcp.tool()` decorator in main server file
3. Include comprehensive error handling
4. Follow established formatting patterns

## Code Patterns

### Strategy Tool Template
```python
@mcp.tool()
async def strategy_name(param1: float = default, preview: bool = True, confirm_token: str = None) -> str:
    """Strategy description with preview-confirm-execute pattern."""
    
    if not preview and confirm_token:
        # Execution path
        trade_preview = await risk_manager.confirm_trade(confirm_token)
        if not trade_preview:
            return f"""
            ❌ Confirmation Failed:
            ======================
            Invalid or expired confirmation token.
            
            Possible reasons:
            - Token has expired (30-second timeout)
            - Token was already used
            - Invalid token format
            
            Please generate a new preview with preview=True to get a fresh confirmation token.
            """
        
        # Validate trade one more time
        is_valid, violations = await risk_manager.validate_trade(trade_preview)
        if not is_valid:
            return f"""
            ⚠️ Trade Validation Failed:
            ==========================
            The following risk violations were detected:
            
            {chr(10).join(f'• {violation}' for violation in violations)}
            
            Please resolve these issues before attempting to execute the trade.
            Use risk_check() to review your current risk status.
            """
        
        # Execute the trade
        return await strategies.execute_strategy(trade_preview)
        
    # Preview path
    return await strategies.strategy_implementation(param1, preview=True)
```

### Error Handling
```python
try:
    # Business logic
    result = await some_operation()
    return formatted_result
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    return user_friendly_error_message
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return f"Unexpected error: {str(e)}"
```

## Testing Strategy

### Unit Testing (Not Yet Implemented)
- Service module testing
- Risk validation testing
- Cache operations testing
- Strategy logic testing

### Integration Testing
- Paper trading validation
- Risk limit enforcement
- Preview-confirm flow
- Emergency stop procedures

### Manual Testing
- Claude Desktop integration
- VS Code MCP testing
- Paper account validation
- Risk scenario testing

## Common Development Tasks

### Adding a New Strategy
1. Implement strategy in `services/strategies.py`
2. Add risk analysis logic
3. Create MCP tool wrapper in main server
4. Add to TODO.md and test thoroughly
5. Update documentation

### Modifying Risk Parameters
1. Update `services/config.py` configuration
2. Modify validation logic in `services/risk_manager.py`
3. Test with various scenarios
4. Update environment variable documentation

### Debugging Issues
1. Check server logs for detailed errors
2. Validate environment configuration
3. Test with paper trading first
4. Use `risk_check()` tool for status validation

## Trade Execution Pipeline (Week 3 ✅)

### Order Execution Flow
1. **Preview Generation**: Strategy creates detailed trade preview with risk analysis
2. **Risk Validation**: Pre-trade checks against daily loss and delta limits
3. **Confirmation Token**: Secure token generated with 30-second expiry
4. **Order Submission**: Real API calls to Alpaca with market/multi-leg orders
5. **Order Tracking**: Automatic tracking with fill status monitoring
6. **Position Reconciliation**: Post-trade validation and position updates

### Order Management Tools
- **`get_order_status(order_id)`**: Track individual order fills and status
- **`get_recent_orders(limit)`**: View recent order history with emoji status indicators
- **`cancel_order(order_id)`**: Cancel pending orders with confirmation
- **`reconcile_positions()`**: Compare expected vs actual positions after trades

### Execution Error Handling
- **API Errors**: Comprehensive error catching with user-friendly messages
- **Order Failures**: Detailed failure reasons and retry guidance
- **Risk Violations**: Clear explanations of limit breaches with resolution steps
- **Token Expiry**: Enhanced error messages with specific timeout information

## Security and Risk Notes

- **Three-Step Confirmation**: All strategy trades require preview → validation → execution
- **Risk Limits**: Enforced before any trade execution with detailed violation reporting
- **Paper Trading**: Always test with paper account first
- **Emergency Stop**: `kill_switch()` immediately halts all trading
- **Order Tracking**: All orders tracked with strategy attribution
- **Audit Trail**: All trade previews, confirmations, and executions are logged
- **Auto-Expiry**: 0DTE data automatically expires to prevent stale trades

## Migration Notes

- **Legacy Compatibility**: Original `alpaca_mcp_server.py` remains functional
- **Gradual Migration**: Can gradually move to `alpaca_mcp_server_new.py`
- **Feature Parity**: All original tools available in refactored version
- **Enhanced Features**: New server adds 0DTE strategies and risk management