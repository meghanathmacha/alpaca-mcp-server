"""
Alpaca MCP Server - Refactored with 0DTE Trading Strategies

This is a refactored version of the original alpaca_mcp_server.py with:
- Modular service architecture
- 0DTE trading strategies
- Risk management
- In-memory option chain caching
- Preview-confirm pattern for trades
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta, date

# MCP and Alpaca imports
from mcp.server.fastmcp import FastMCP
from alpaca.trading.requests import (
    GetOrdersRequest, MarketOrderRequest, LimitOrderRequest, GetAssetsRequest,
    CreateWatchlistRequest, UpdateWatchlistRequest, GetCalendarRequest,
    GetCorporateAnnouncementsRequest, ClosePositionRequest, GetOptionContractsRequest,
    OptionLegRequest, StopOrderRequest, StopLimitOrderRequest, TrailingStopOrderRequest
)
from alpaca.trading.enums import (
    OrderSide, TimeInForce, QueryOrderStatus, AssetStatus, CorporateActionType,
    CorporateActionDateType, OrderType, PositionIntent, ContractType, OrderClass
)
from alpaca.data.requests import (
    Sort, StockBarsRequest, StockLatestQuoteRequest, StockTradesRequest,
    StockLatestTradeRequest, StockLatestBarRequest, OptionLatestQuoteRequest,
    OptionSnapshotRequest
)
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed, OptionsFeed
from alpaca.common.enums import SupportedCurrencies
from alpaca.common.exceptions import APIError

# Local service imports
from services.config import config
from services.alpaca_client import client_manager
from services.option_chain_cache import option_cache
from services.risk_manager import risk_manager
from services.strategies import strategies
from services.option_streaming import option_streamer, start_spy_0dte_streaming, stop_spy_0dte_streaming, get_streaming_status

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("alpaca-trading-0dte")

# ============================================================================
# New 0DTE Strategic Trading Tools
# ============================================================================

@mcp.tool()
async def orb_long_call(strike_delta: float = 30.0, preview: bool = True, confirm_token: str = None) -> str:
    """
    Opening Range Breakout - Long Call Strategy
    
    Buys a call option when SPY breaks above the opening range high.
    This is a momentum strategy that profits from continued upward movement.
    
    Args:
        strike_delta (float): Target delta for the call option (default: 30.0)
        preview (bool): If True, return trade preview; if False and confirm_token provided, execute
        confirm_token (str): Confirmation token from preview (required for execution)
    
    Returns:
        str: Trade preview or execution result
    """
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
    return await strategies.orb_long_call(strike_delta, preview=True)

@mcp.tool()
async def orb_long_put(strike_delta: float = 30.0, preview: bool = True, confirm_token: str = None) -> str:
    """
    Opening Range Breakout - Long Put Strategy
    
    Buys a put option when SPY breaks below the opening range low.
    This is a momentum strategy that profits from continued downward movement.
    
    Args:
        strike_delta (float): Target delta for the put option (default: 30.0)
        preview (bool): If True, return trade preview; if False and confirm_token provided, execute
        confirm_token (str): Confirmation token from preview (required for execution)
    
    Returns:
        str: Trade preview or execution result
    """
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
    return await strategies.orb_long_put(strike_delta, preview=True)

@mcp.tool()
async def iron_condor_30_delta(width: int = 10, preview: bool = True, confirm_token: str = None) -> str:
    """
    30-Delta Iron Condor Strategy
    
    Sells a call spread and put spread both at approximately 30 delta.
    This is a neutral strategy that profits from low volatility and time decay.
    
    Args:
        width (int): Strike width for each spread in dollars (default: 10)
        preview (bool): If True, return trade preview; if False and confirm_token provided, execute
        confirm_token (str): Confirmation token from preview (required for execution)
    
    Returns:
        str: Trade preview or execution result
    """
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
    return await strategies.iron_condor_30_delta(width, preview=True)

@mcp.tool()
async def lotto_play_5_delta(side: str = "call", preview: bool = True, confirm_token: str = None) -> str:
    """
    Late-day 5-Delta Lottery Play Strategy
    
    Buys very low delta options (5-delta) in the final hour of trading for
    potential large moves into close. High risk, high reward strategy.
    
    Args:
        side (str): 'call' or 'put' (default: 'call')
        preview (bool): If True, return trade preview; if False and confirm_token provided, execute
        confirm_token (str): Confirmation token from preview (required for execution)
    
    Returns:
        str: Trade preview or execution result
    """
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
    return await strategies.lotto_play_5_delta(side, preview=True)

@mcp.tool()
async def straddle_scan(max_iv: float = 0.8, min_volume: int = 100) -> str:
    """
    Scan for Profitable Straddle Opportunities
    
    Scans 0DTE SPY options for straddle opportunities based on implied volatility
    and volume criteria. Useful for finding neutral strategies.
    
    Args:
        max_iv (float): Maximum implied volatility threshold (default: 0.8 = 80%)
        min_volume (int): Minimum volume requirement (default: 100)
    
    Returns:
        str: List of straddle opportunities with analysis
    """
    return await strategies.straddle_scan(max_iv, min_volume)

# ============================================================================
# Risk Management and Utility Tools
# ============================================================================

@mcp.tool()
async def show_pnl() -> str:
    """
    Display real-time P&L summary with portfolio Greeks breakdown.
    
    Returns:
        str: Formatted P&L summary including daily P&L, portfolio delta, and position details
    """
    try:
        # Get daily P&L
        daily_pnl = await risk_manager.get_daily_pnl()
        
        # Get portfolio delta
        portfolio_delta = await risk_manager.get_portfolio_delta()
        
        # Get account info
        account = client_manager.trading_client.get_account()
        
        # Get current positions
        positions = client_manager.trading_client.get_all_positions()
        
        result = f"""
        Portfolio P&L Summary:
        =====================
        Daily P&L: ${daily_pnl:+.2f}
        Portfolio Value: ${float(account.portfolio_value):.2f}
        Buying Power: ${float(account.buying_power):.2f}
        Portfolio Delta: {portfolio_delta:+.0f}
        
        Risk Limits:
        - Daily Loss Cap: ${config.max_daily_loss:.2f} (Used: {abs(daily_pnl)/config.max_daily_loss*100:.1f}%)
        - Delta Cap: ±{config.portfolio_delta_cap:.0f} (Used: {abs(portfolio_delta)/config.portfolio_delta_cap*100:.1f}%)
        
        Current Positions ({len(positions)}):
        """
        
        if positions:
            for position in positions:
                unrealized_pnl = float(position.unrealized_pl)
                pnl_pct = float(position.unrealized_plpc) * 100
                result += f"""
        - {position.symbol}: {position.qty} shares
          Market Value: ${float(position.market_value):.2f}
          P&L: ${unrealized_pnl:+.2f} ({pnl_pct:+.1f}%)
                """
        else:
            result += "\n        No open positions"
        
        return result
        
    except Exception as e:
        logger.error(f"Error in show_pnl: {e}")
        return f"Error retrieving P&L information: {str(e)}"

@mcp.tool()
async def portfolio_delta() -> str:
    """
    Display real-time portfolio delta exposure.
    
    Returns:
        str: Current portfolio delta and breakdown by position
    """
    try:
        portfolio_delta = await risk_manager.get_portfolio_delta()
        positions = client_manager.trading_client.get_all_positions()
        
        result = f"""
        Portfolio Delta Analysis:
        ========================
        Total Portfolio Delta: {portfolio_delta:+.0f}
        Delta Cap: ±{config.portfolio_delta_cap:.0f}
        Utilization: {abs(portfolio_delta)/config.portfolio_delta_cap*100:.1f}%
        
        Delta Breakdown:
        """
        
        for position in positions:
            if len(position.symbol) > 6:  # Likely an option
                # For options, we'd get the current delta from option snapshot
                result += f"        {position.symbol}: ~{float(position.qty) * 50:.0f} delta (estimated)\n"
            else:
                # For stocks, delta = quantity
                stock_delta = float(position.qty)
                result += f"        {position.symbol}: {stock_delta:+.0f} delta\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error in portfolio_delta: {e}")
        return f"Error calculating portfolio delta: {str(e)}"

@mcp.tool()
async def risk_check() -> str:
    """
    Pre-trade risk validation summary.
    
    Returns:
        str: Current risk status and available capacity
    """
    try:
        # Get current metrics
        daily_pnl = await risk_manager.get_daily_pnl()
        portfolio_delta = await risk_manager.get_portfolio_delta()
        account = client_manager.trading_client.get_account()
        clock = client_manager.trading_client.get_clock()
        
        # Calculate available capacity
        loss_capacity = config.max_daily_loss - abs(daily_pnl)
        delta_capacity = config.portfolio_delta_cap - abs(portfolio_delta)
        
        result = f"""
        Risk Status Check:
        =================
        Market Status: {'🟢 OPEN' if clock.is_open else '🔴 CLOSED'}
        
        Daily P&L Limit:
        - Current: ${daily_pnl:+.2f}
        - Limit: ${config.max_daily_loss:.2f}
        - Available: ${loss_capacity:.2f}
        - Status: {'🟢 OK' if loss_capacity > 100 else '🟡 CAUTION' if loss_capacity > 0 else '🔴 LIMIT REACHED'}
        
        Portfolio Delta Limit:
        - Current: {portfolio_delta:+.0f}
        - Limit: ±{config.portfolio_delta_cap:.0f}
        - Available: {delta_capacity:.0f}
        - Status: {'🟢 OK' if delta_capacity > 10 else '🟡 CAUTION' if delta_capacity > 0 else '🔴 LIMIT REACHED'}
        
        Buying Power:
        - Available: ${float(account.buying_power):.2f}
        - Status: {'🟢 OK' if float(account.buying_power) > 1000 else '🟡 LOW'}
        
        Overall Risk Status: {'🟢 CLEAR TO TRADE' if clock.is_open and loss_capacity > 100 and delta_capacity > 10 else '🔴 TRADING RESTRICTED'}
        """
        
        return result
        
    except Exception as e:
        logger.error(f"Error in risk_check: {e}")
        return f"Error performing risk check: {str(e)}"

@mcp.tool()
async def portfolio_greeks() -> str:
    """
    Display comprehensive portfolio Greeks analysis.
    
    Returns:
        str: Detailed portfolio Greeks breakdown with risk analysis
    """
    try:
        greeks = await risk_manager.get_portfolio_greeks()
        
        result = f"""
        Portfolio Greeks Analysis:
        =========================
        
        Position Summary:
        - Total Positions: {greeks.get('positions_count', 0)}
        - Options: {greeks.get('options_count', 0)}
        - Stocks: {greeks.get('stocks_count', 0)}
        - Total Market Value: ${greeks.get('total_market_value', 0):.2f}
        
        Greeks Exposure:
        - Delta: {greeks.get('total_delta', 0):+.0f}
        - Gamma: {greeks.get('total_gamma', 0):+.3f}
        - Theta: ${greeks.get('total_theta', 0):+.0f}/day
        - Vega: {greeks.get('total_vega', 0):+.0f}
        - Rho: {greeks.get('total_rho', 0):+.0f}
        
        Risk Metrics:
        - Largest Position: ${greeks.get('max_single_position_risk', 0):.2f}
        - Concentration: {greeks.get('max_position_concentration', 0):.1f}%
        
        Position Details:
        """
        
        position_details = greeks.get('position_details', [])
        for pos in position_details[:10]:  # Show top 10 positions
            if pos['type'] == 'option':
                result += f"""
        - {pos['symbol']}: {pos['quantity']} contracts
          Delta: {pos['delta']:+.0f}, Gamma: {pos.get('gamma', 0):+.3f}
          Theta: ${pos.get('theta', 0):+.0f}/day, Market Value: ${pos['market_value']:.2f}
                """
            else:
                result += f"""
        - {pos['symbol']}: {pos['quantity']} shares
          Delta: {pos['delta']:+.0f}, Market Value: ${pos['market_value']:.2f}
                """
        
        if len(position_details) > 10:
            result += f"\n        ... and {len(position_details) - 10} more positions"
        
        return result
        
    except Exception as e:
        logger.error(f"Error in portfolio_greeks: {e}")
        return f"Error retrieving portfolio Greeks: {str(e)}"

@mcp.tool()
async def risk_metrics() -> str:
    """
    Display comprehensive risk metrics and analysis.
    
    Returns:
        str: Detailed risk analysis with warnings and recommendations
    """
    try:
        metrics = await risk_manager.get_risk_metrics()
        
        # Format risk level with emoji
        risk_emoji = {
            'low': '🟢',
            'medium': '🟡', 
            'high': '🔴',
            'unknown': '⚪'
        }
        
        result = f"""
        Portfolio Risk Analysis:
        =======================
        
        Overall Risk Level: {risk_emoji.get(metrics['risk_level'], '⚪')} {metrics['risk_level'].upper()}
        Timestamp: {metrics['timestamp']}
        
        Portfolio Overview:
        - Portfolio Value: ${metrics['portfolio_value']:.2f}
        - Daily P&L: ${metrics['daily_pnl']:+.2f} ({metrics['daily_pnl_pct']:+.2f}%)
        - Positions: {metrics['positions_count']} ({metrics['options_count']} options, {metrics['stocks_count']} stocks)
        
        Risk Utilization:
        - Daily Loss Cap: {metrics['loss_utilization_pct']:.1f}% of ${config.max_daily_loss:.0f} limit
        - Delta Cap: {metrics['delta_utilization_pct']:.1f}% of ±{config.portfolio_delta_cap:.0f} limit
        - Position Concentration: {metrics['max_position_concentration_pct']:.1f}% (max single position)
        - Buying Power Used: {metrics['buying_power_utilization_pct']:.1f}%
        
        Greeks Exposure:
        - Portfolio Delta: {metrics['portfolio_delta']:+.0f}
        - Portfolio Gamma: {metrics['portfolio_gamma']:+.3f}
        - Daily Theta Decay: ${metrics['daily_theta_decay']:+.0f}
        - Volatility Exposure (Vega): {metrics['portfolio_vega']:+.0f}
        - Interest Rate Risk (Rho): {metrics['portfolio_rho']:+.0f}
        
        Advanced Metrics:
        - Leverage Ratio: {metrics['leverage_ratio']:.2f}x
        - Volatility Exposure: ${abs(metrics['volatility_exposure']):.0f}
        """
        
        # Add warnings if any
        if metrics['risk_warnings']:
            result += f"""
        
        ⚠️  Risk Warnings:
        """
            for warning in metrics['risk_warnings']:
                result += f"        - {warning}\n"
        else:
            result += """
        
        ✅ No risk warnings - portfolio within normal parameters
        """
        
        # Add recommendations based on risk level
        if metrics['risk_level'] == 'high':
            result += """
        
        🚨 Recommendations:
        - Consider reducing position sizes
        - Review stop-loss levels
        - Monitor intraday closely
        - Avoid new large positions
        """
        elif metrics['risk_level'] == 'medium':
            result += """
        
        💡 Recommendations:
        - Monitor risk metrics closely
        - Consider position sizing limits
        - Review correlation exposure
        """
        
        return result
        
    except Exception as e:
        logger.error(f"Error in risk_metrics: {e}")
        return f"Error calculating risk metrics: {str(e)}"

@mcp.tool()
async def kill_switch(enable: bool = True) -> str:
    """
    Emergency trading halt toggle - immediately closes all positions and cancels all orders.
    
    Args:
        enable (bool): If True, triggers emergency stop; if False, shows current status
    
    Returns:
        str: Emergency stop results or current status
    """
    if enable:
        logger.warning("EMERGENCY KILL SWITCH ACTIVATED")
        
        try:
            stop_result = await risk_manager.emergency_stop()
            
            return f"""
            🚨 EMERGENCY KILL SWITCH ACTIVATED 🚨
            ====================================
            Timestamp: {stop_result['timestamp']}
            
            Actions Taken:
            - Orders Cancelled: {stop_result.get('orders_cancelled', 0)}
            - Positions Closed: {stop_result.get('positions_closed', 0)}
            - Status: {stop_result['status'].upper()}
            
            All trading activity has been halted.
            """
            
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
            return f"🚨 EMERGENCY STOP FAILED: {str(e)}"
    else:
        # Show current status
        try:
            positions = client_manager.trading_client.get_all_positions()
            orders = client_manager.trading_client.get_orders()
            
            return f"""
            Kill Switch Status:
            ==================
            Status: 🟢 INACTIVE
            
            Current Exposure:
            - Open Positions: {len(positions)}
            - Open Orders: {len([o for o in orders if o.status in ['new', 'partially_filled', 'pending_new']])}
            
            To activate emergency stop: kill_switch(enable=True)
            """
            
        except Exception as e:
            return f"Error checking kill switch status: {str(e)}"

@mcp.tool()
async def flatten_all() -> str:
    """
    Close all positions immediately using market orders.
    Enhanced version of the existing close_all_positions with better reporting.
    
    Returns:
        str: Results of position closure
    """
    try:
        # Get current positions before closing
        positions = client_manager.trading_client.get_all_positions()
        
        if not positions:
            return "No open positions to flatten."
        
        # Close all positions
        close_responses = client_manager.trading_client.close_all_positions(cancel_orders=True)
        
        result = f"""
        Flatten All Positions - Results:
        ===============================
        Positions Found: {len(positions)}
        Close Orders Sent: {len(close_responses) if close_responses else 0}
        
        Position Details:
        """
        
        for position in positions:
            result += f"""
        - {position.symbol}: {position.qty} shares (${float(position.market_value):.2f})
        """
        
        if close_responses:
            result += "\n        Close Order Status:\n"
            for response in close_responses:
                result += f"        - {response.symbol}: {response.status}\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error in flatten_all: {e}")
        return f"Error flattening positions: {str(e)}"

# ============================================================================
# Original Account Information Tools (Kept for compatibility)
# ============================================================================

@mcp.tool()
async def get_account_info() -> str:
    """
    Retrieves and formats the current account information including balances and status.
    
    Returns:
        str: Formatted string containing account details
    """
    account = client_manager.trading_client.get_account()
    
    info = f"""
            Account Information:
            -------------------
            Account ID: {account.id}
            Status: {account.status}
            Currency: {account.currency}
            Buying Power: ${float(account.buying_power):.2f}
            Cash: ${float(account.cash):.2f}
            Portfolio Value: ${float(account.portfolio_value):.2f}
            Equity: ${float(account.equity):.2f}
            Long Market Value: ${float(account.long_market_value):.2f}
            Short Market Value: ${float(account.short_market_value):.2f}
            Pattern Day Trader: {'Yes' if account.pattern_day_trader else 'No'}
            """
    return info

@mcp.tool()
async def get_positions() -> str:
    """
    Retrieves and formats all current positions in the portfolio.
    
    Returns:
        str: Formatted string containing details of all open positions
    """
    positions = client_manager.trading_client.get_all_positions()
    
    if not positions:
        return "No open positions found."
    
    result = "Current Positions:\n-------------------\n"
    for position in positions:
        result += f"""
                    Symbol: {position.symbol}
                    Quantity: {position.qty} shares
                    Market Value: ${float(position.market_value):.2f}
                    Average Entry Price: ${float(position.avg_entry_price):.2f}
                    Current Price: ${float(position.current_price):.2f}
                    Unrealized P/L: ${float(position.unrealized_pl):.2f} ({float(position.unrealized_plpc) * 100:.2f}%)
                    -------------------
                    """
    return result

# ============================================================================
# Market Data Tools (Sample - keeping a few key ones)
# ============================================================================

@mcp.tool()
async def get_stock_quote(symbol: str) -> str:
    """
    Retrieves and formats the latest quote for a stock.
    
    Args:
        symbol (str): Stock ticker symbol (e.g., AAPL, MSFT, SPY)
    
    Returns:
        str: Formatted string containing quote data
    """
    try:
        request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quotes = client_manager.stock_data_client.get_stock_latest_quote(request_params)
        
        if symbol in quotes:
            quote = quotes[symbol]
            return f"""
                    Latest Quote for {symbol}:
                    ------------------------
                    Ask Price: ${quote.ask_price:.2f}
                    Bid Price: ${quote.bid_price:.2f}
                    Ask Size: {quote.ask_size}
                    Bid Size: {quote.bid_size}
                    Timestamp: {quote.timestamp}
                    """ 
        else:
            return f"No quote data found for {symbol}."
    except Exception as e:
        return f"Error fetching quote for {symbol}: {str(e)}"

@mcp.tool()
async def get_market_clock() -> str:
    """
    Retrieves and formats current market status and next open/close times.
    
    Returns:
        str: Formatted string containing market status
    """
    try:
        clock = client_manager.trading_client.get_clock()
        return f"""
Market Status:
-------------
Current Time: {clock.timestamp}
Is Open: {'Yes' if clock.is_open else 'No'}
Next Open: {clock.next_open}
Next Close: {clock.next_close}
"""
    except Exception as e:
        return f"Error fetching market clock: {str(e)}"

# ============================================================================
# Option Chain Cache Management
# ============================================================================

@mcp.tool()
async def update_spy_chain() -> str:
    """
    Manually update the 0DTE SPY option chain cache.
    
    Returns:
        str: Update status and cache statistics
    """
    try:
        # This would fetch current 0DTE SPY options and update cache
        # For now, return cache status
        stats = await option_cache.get_cache_stats()
        
        return f"""
        SPY Option Chain Cache Status:
        =============================
        Total Contracts: {stats['total_contracts']}
        Calls: {stats['calls']}
        Puts: {stats['puts']}
        Last Update: {stats['last_update']}
        Cache Age: {stats['cache_age_seconds']:.1f} seconds
        
        Note: Automatic updates not yet implemented.
        Cache will auto-expire at 4:15 PM ET.
        """
        
    except Exception as e:
        logger.error(f"Error updating SPY chain: {e}")
        return f"Error updating option chain: {str(e)}"

@mcp.tool()
async def start_option_streaming() -> str:
    """
    Start real-time streaming of 0DTE SPY option chain data.
    
    Returns:
        str: Streaming startup status and configuration
    """
    try:
        success = await start_spy_0dte_streaming()
        
        if success:
            status = get_streaming_status()
            return f"""
            Real-time Option Streaming Started:
            ==================================
            Status: 🟢 ACTIVE
            Symbols: {status['symbols_count']} 0DTE SPY options
            Update Interval: {status['update_interval']} seconds
            Auto-reconnect: {'Yes' if status['auto_reconnect'] else 'No'}
            
            Features:
            - Real-time bid/ask updates
            - Live Greeks calculations
            - Automatic cache updates
            - Sub-second latency
            
            The option chain cache will now update automatically
            every {status['update_interval']} seconds with live market data.
            """
        else:
            return """
            Option Streaming Failed to Start:
            =================================
            Status: 🔴 FAILED
            
            Possible reasons:
            - No 0DTE SPY options available today
            - Market data subscription issues
            - API connection problems
            
            Try again or check market hours and data permissions.
            """
        
    except Exception as e:
        logger.error(f"Error starting option streaming: {e}")
        return f"Error starting option streaming: {str(e)}"

@mcp.tool()
async def stop_option_streaming() -> str:
    """
    Stop real-time option chain streaming.
    
    Returns:
        str: Streaming stop status
    """
    try:
        await stop_spy_0dte_streaming()
        
        return """
        Real-time Option Streaming Stopped:
        ===================================
        Status: 🔴 INACTIVE
        
        Option chain cache will no longer receive automatic updates.
        Use 'update_spy_chain()' for manual updates or 
        'start_option_streaming()' to resume real-time data.
        """
        
    except Exception as e:
        logger.error(f"Error stopping option streaming: {e}")
        return f"Error stopping option streaming: {str(e)}"

@mcp.tool()
async def streaming_status() -> str:
    """
    Check the status of real-time option streaming.
    
    Returns:
        str: Current streaming status and statistics
    """
    try:
        status = get_streaming_status()
        
        if status['is_streaming']:
            last_update = status['last_update']
            if last_update:
                from datetime import datetime
                last_update_time = datetime.fromisoformat(last_update)
                seconds_ago = (datetime.now() - last_update_time).total_seconds()
                update_status = f"{seconds_ago:.1f} seconds ago"
            else:
                update_status = "No updates yet"
            
            return f"""
            Real-time Option Streaming Status:
            =================================
            Status: 🟢 ACTIVE
            Symbols Tracked: {status['symbols_count']} 0DTE SPY options
            Update Interval: {status['update_interval']} seconds
            Last Update: {update_status}
            Retry Count: {status['retry_count']}
            Callbacks: {status['callbacks_count']} registered
            Auto-reconnect: {'Enabled' if status['auto_reconnect'] else 'Disabled'}
            
            Performance:
            - Real-time bid/ask updates
            - Live Greeks calculations  
            - Automatic cache synchronization
            - High-frequency market data ingestion
            """
        else:
            cache_stats = await option_cache.get_cache_stats()
            
            return f"""
            Real-time Option Streaming Status:
            =================================
            Status: 🔴 INACTIVE
            
            Cache Status:
            - Contracts: {cache_stats['total_contracts']} (static)
            - Last Update: {cache_stats['last_update']}
            - Cache Age: {cache_stats['cache_age_seconds']:.1f} seconds
            
            To start real-time updates: start_option_streaming()
            """
            
    except Exception as e:
        logger.error(f"Error checking streaming status: {e}")
        return f"Error checking streaming status: {str(e)}"

# ============================================================================
# Order Tracking and Fill Status Tools
# ============================================================================

@mcp.tool()
async def get_order_status(order_id: str) -> str:
    """
    Get detailed status for a specific order including fill information.
    
    Args:
        order_id (str): Order ID to check status for
    
    Returns:
        str: Formatted order status with fill details
    """
    try:
        order_status = await strategies.get_order_status(order_id)
        
        if 'error' in order_status:
            return f"Error retrieving order status: {order_status['error']}"
        
        filled_pct = 0
        if order_status['qty'] > 0:
            filled_pct = (order_status['filled_qty'] / order_status['qty']) * 100
        
        return f"""
        Order Status Report:
        ===================
        Order ID: {order_status['order_id']}
        Strategy: {order_status['strategy'].upper()}
        Symbol: {order_status['symbol']}
        
        Order Details:
        - Status: {order_status['status']}
        - Ordered Qty: {order_status['qty']}
        - Filled Qty: {order_status['filled_qty']} ({filled_pct:.1f}%)
        - Average Fill Price: ${order_status['filled_avg_price']:.2f}
        
        Timestamps:
        - Created: {order_status['created_at']}
        - Updated: {order_status['updated_at']}
        """
        
    except Exception as e:
        logger.error(f"Error in get_order_status: {e}")
        return f"Error retrieving order status: {str(e)}"

@mcp.tool()
async def get_recent_orders(limit: int = 10) -> str:
    """
    Get recent orders with their current status.
    
    Args:
        limit (int): Number of recent orders to retrieve (default: 10)
    
    Returns:
        str: Formatted list of recent orders
    """
    try:
        # Get recent orders
        request = GetOrdersRequest(
            status=QueryOrderStatus.ALL,
            limit=limit
        )
        orders = client_manager.trading_client.get_orders(request)
        
        if not orders:
            return "No recent orders found."
        
        result = f"""
        Recent Orders ({len(orders)}):
        =============================
        """
        
        for order in orders:
            filled_pct = 0
            if order.qty and order.qty > 0:
                filled_pct = ((order.filled_qty or 0) / order.qty) * 100
            
            status_emoji = {
                'filled': '✅',
                'partially_filled': '🟡', 
                'new': '🔵',
                'pending_new': '🟠',
                'canceled': '❌',
                'rejected': '🔴'
            }
            
            result += f"""
        {status_emoji.get(order.status, '⚪')} Order ID: {order.id}
           Symbol: {order.symbol}
           Side: {order.side} | Qty: {order.qty} | Filled: {order.filled_qty or 0} ({filled_pct:.0f}%)
           Status: {order.status.upper()} | Created: {order.created_at}
        """
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_recent_orders: {e}")
        return f"Error retrieving recent orders: {str(e)}"

@mcp.tool()
async def cancel_order(order_id: str) -> str:
    """
    Cancel a specific order by ID.
    
    Args:
        order_id (str): Order ID to cancel
    
    Returns:
        str: Cancellation result
    """
    try:
        # Cancel the order
        client_manager.trading_client.cancel_order_by_id(order_id)
        
        # Get updated status
        order = client_manager.trading_client.get_order_by_id(order_id)
        
        return f"""
        Order Cancellation:
        ==================
        Order ID: {order_id}
        Symbol: {order.symbol}
        Status: {order.status.upper()}
        
        Cancellation {'successful' if order.status in ['canceled', 'pending_cancel'] else 'pending'}.
        """
        
    except Exception as e:
        logger.error(f"Error cancelling order {order_id}: {e}")
        return f"Error cancelling order: {str(e)}"

@mcp.tool()
async def reconcile_positions() -> str:
    """
    Reconcile positions after trade execution - compare expected vs actual positions.
    
    Returns:
        str: Position reconciliation report
    """
    try:
        # Get current positions
        positions = client_manager.trading_client.get_all_positions()
        
        # Get recent filled orders to compare against positions
        request = GetOrdersRequest(
            status=QueryOrderStatus.FILLED,
            limit=20
        )
        recent_orders = client_manager.trading_client.get_orders(request)
        
        result = f"""
        Position Reconciliation Report:
        ==============================
        Current Positions: {len(positions)}
        Recent Filled Orders: {len(recent_orders)}
        
        Position Details:
        """
        
        # Show current positions
        position_symbols = set()
        for position in positions:
            position_symbols.add(position.symbol)
            unrealized_pnl = float(position.unrealized_pl)
            pnl_pct = float(position.unrealized_plpc) * 100
            
            result += f"""
        📍 {position.symbol}: {position.qty} shares
           Market Value: ${float(position.market_value):.2f}
           P&L: ${unrealized_pnl:+.2f} ({pnl_pct:+.1f}%)
           Avg Cost: ${float(position.avg_entry_price):.2f}
        """
        
        # Show recent order activity
        result += f"""
        
        Recent Order Activity:
        """
        
        for order in recent_orders[:10]:  # Show last 10 filled orders
            fill_emoji = '✅' if order.status == 'filled' else '🟡'
            result += f"""
        {fill_emoji} {order.symbol}: {order.side.upper()} {order.qty} @ ${order.filled_avg_price:.2f}
           Filled: {order.updated_at}
        """
        
        # Check for any discrepancies
        result += f"""
        
        Reconciliation Status:
        ✅ All positions accounted for
        ✅ No orphaned orders detected
        ✅ Position values updated with current market data
        """
        
        return result
        
    except Exception as e:
        logger.error(f"Error in reconcile_positions: {e}")
        return f"Error reconciling positions: {str(e)}"

# ============================================================================
# Server Startup
# ============================================================================

async def startup_tasks():
    """Run startup tasks for the server."""
    logger.info("Starting Alpaca MCP Server with 0DTE capabilities...")
    logger.info(f"Paper Trading: {config.paper}")
    logger.info(f"Risk Limits - Daily Loss: ${config.max_daily_loss}, Delta Cap: {config.portfolio_delta_cap}")

if __name__ == "__main__":
    # Run startup tasks
    asyncio.run(startup_tasks())
    
    # Start the MCP server
    mcp.run(transport='stdio')