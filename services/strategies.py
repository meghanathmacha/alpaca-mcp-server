"""0DTE Trading strategies for SPY options."""

import asyncio
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple
import logging

from alpaca.trading.requests import MarketOrderRequest, OptionLegRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, OrderClass, OrderType, TimeInForce
from alpaca.common.exceptions import APIError
from alpaca.data.requests import OptionSnapshotRequest, StockLatestQuoteRequest

from .config import config
from .alpaca_client import client_manager
from .option_chain_cache import option_cache, OptionData
from .risk_manager import risk_manager, TradePreview
from .audit_logger import audit_logger

logger = logging.getLogger(__name__)


class StrategyError(Exception):
    """Custom exception for strategy errors."""
    pass


class ZDTEStrategies:
    """Zero Days to Expiration trading strategies."""
    
    def __init__(self):
        """Initialize strategy engine."""
        self._market_data_cache = {}
        self._order_tracking = {}
    
    async def execute_strategy(self, trade_preview: TradePreview) -> str:
        """Execute a validated trade from preview.
        
        Args:
            trade_preview: Validated trade preview object
            
        Returns:
            Execution result message
        """
        try:
            if trade_preview.strategy == 'orb_long_call':
                return await self._execute_orb_long_call(trade_preview)
            elif trade_preview.strategy == 'orb_long_put':
                return await self._execute_orb_long_put(trade_preview)
            elif trade_preview.strategy == 'iron_condor_30_delta':
                return await self._execute_iron_condor(trade_preview)
            elif trade_preview.strategy == 'lotto_play_5_delta':
                return await self._execute_lotto_play(trade_preview)
            else:
                return f"Unknown strategy: {trade_preview.strategy}"
                
        except Exception as e:
            logger.error(f"Error executing {trade_preview.strategy}: {e}")
            return f"Trade execution failed: {str(e)}"
    
    async def _execute_orb_long_call(self, trade_preview: TradePreview) -> str:
        """Execute ORB long call strategy."""
        try:
            leg = trade_preview.legs[0]
            option_symbol = leg['symbol']
            quantity = leg['quantity']
            
            # Create and submit market order
            order_request = MarketOrderRequest(
                symbol=option_symbol,
                qty=quantity,
                side=OrderSide.BUY
            )
            
            order = client_manager.trading_client.submit_order(order_request)
            
            # Track order
            self._order_tracking[order.id] = {
                'strategy': 'orb_long_call',
                'timestamp': datetime.now(),
                'symbol': option_symbol,
                'quantity': quantity
            }
            
            # Audit log the execution
            await audit_logger.log_trade_event(
                event_type="execution",
                trade_data={
                    'strategy': 'orb_long_call',
                    'order_id': order.id,
                    'symbol': option_symbol,
                    'quantity': quantity,
                    'order_type': 'market',
                    'side': 'buy',
                    'estimated_cost': trade_preview.cost,
                    'max_loss': trade_preview.max_loss,
                    'delta_exposure': trade_preview.delta_exposure,
                    'confirmation_token': trade_preview.confirmation_token
                }
            )
            
            return f"""
            ORB Long Call - Order Executed:
            ==============================
            Order ID: {order.id}
            Symbol: {option_symbol}
            Quantity: {quantity} contracts
            Side: BUY
            Order Type: MARKET
            Status: {order.status}
            
            Estimated Cost: ${trade_preview.cost:.2f}
            Max Loss: ${trade_preview.max_loss:.2f}
            Delta Exposure: {trade_preview.delta_exposure:+.0f}
            
            Monitor order status for fills and updates.
            """
            
        except APIError as e:
            logger.error(f"API error in ORB long call execution: {e}")
            return f"Order submission failed - API Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in ORB long call execution: {e}")
            return f"Order execution failed: {str(e)}"
    
    async def _execute_orb_long_put(self, trade_preview: TradePreview) -> str:
        """Execute ORB long put strategy."""
        try:
            leg = trade_preview.legs[0]
            option_symbol = leg['symbol']
            quantity = leg['quantity']
            
            # Create and submit market order
            order_request = MarketOrderRequest(
                symbol=option_symbol,
                qty=quantity,
                side=OrderSide.BUY
            )
            
            order = client_manager.trading_client.submit_order(order_request)
            
            # Track order
            self._order_tracking[order.id] = {
                'strategy': 'orb_long_put',
                'timestamp': datetime.now(),
                'symbol': option_symbol,
                'quantity': quantity
            }
            
            return f"""
            ORB Long Put - Order Executed:
            =============================
            Order ID: {order.id}
            Symbol: {option_symbol}
            Quantity: {quantity} contracts
            Side: BUY
            Order Type: MARKET
            Status: {order.status}
            
            Estimated Cost: ${trade_preview.cost:.2f}
            Max Loss: ${trade_preview.max_loss:.2f}
            Delta Exposure: {trade_preview.delta_exposure:+.0f}
            
            Monitor order status for fills and updates.
            """
            
        except APIError as e:
            logger.error(f"API error in ORB long put execution: {e}")
            return f"Order submission failed - API Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in ORB long put execution: {e}")
            return f"Order execution failed: {str(e)}"
    
    async def _execute_iron_condor(self, trade_preview: TradePreview) -> str:
        """Execute Iron Condor strategy."""
        try:
            # Multi-leg order for Iron Condor
            legs = []
            for leg_data in trade_preview.legs:
                leg = OptionLegRequest(
                    symbol=leg_data['symbol'],
                    side=OrderSide.SELL if leg_data['side'] == 'sell' else OrderSide.BUY,
                    qty=leg_data['quantity']
                )
                legs.append(leg)
            
            # Submit multi-leg order
            order_request = LimitOrderRequest(
                symbol="SPY",  # Base symbol for multi-leg options
                qty=0,  # Not used for multi-leg
                side=OrderSide.BUY,  # Default side for multi-leg
                type=OrderType.MARKET,
                time_in_force=TimeInForce.DAY,
                legs=legs
            )
            
            order = client_manager.trading_client.submit_order(order_request)
            
            # Track order
            self._order_tracking[order.id] = {
                'strategy': 'iron_condor_30_delta',
                'timestamp': datetime.now(),
                'legs': len(legs)
            }
            
            return f"""
            Iron Condor - Multi-leg Order Executed:
            ======================================
            Order ID: {order.id}
            Strategy: 30-Delta Iron Condor
            Legs: {len(legs)}
            Order Type: MARKET
            Status: {order.status}
            
            Net Credit: ${trade_preview.cost:.2f}
            Max Loss: ${trade_preview.max_loss:.2f}
            Max Profit: ${trade_preview.max_profit:.2f}
            
            Multi-leg order submitted successfully.
            """
            
        except APIError as e:
            logger.error(f"API error in Iron Condor execution: {e}")
            return f"Multi-leg order submission failed - API Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in Iron Condor execution: {e}")
            return f"Order execution failed: {str(e)}"
    
    async def _execute_lotto_play(self, trade_preview: TradePreview) -> str:
        """Execute Lotto Play strategy."""
        try:
            leg = trade_preview.legs[0]
            option_symbol = leg['symbol']
            quantity = leg['quantity']
            
            # Create and submit market order
            order_request = MarketOrderRequest(
                symbol=option_symbol,
                qty=quantity,
                side=OrderSide.BUY
            )
            
            order = client_manager.trading_client.submit_order(order_request)
            
            # Track order
            self._order_tracking[order.id] = {
                'strategy': 'lotto_play_5_delta',
                'timestamp': datetime.now(),
                'symbol': option_symbol,
                'quantity': quantity
            }
            
            return f"""
            Lotto Play - Order Executed:
            ===========================
            Order ID: {order.id}
            Symbol: {option_symbol}
            Quantity: {quantity} contracts
            Side: BUY
            Delta: ~5 (High risk/reward)
            Status: {order.status}
            
            Cost: ${trade_preview.cost:.2f}
            Max Loss: ${trade_preview.max_loss:.2f} (100% of premium)
            Potential Upside: Unlimited
            
            Lottery ticket purchased successfully!
            """
            
        except APIError as e:
            logger.error(f"API error in Lotto Play execution: {e}")
            return f"Order submission failed - API Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in Lotto Play execution: {e}")
            return f"Order execution failed: {str(e)}"
    
    async def get_order_status(self, order_id: str) -> Dict:
        """Get order status and fill information.
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Dictionary with order status details
        """
        try:
            order = client_manager.trading_client.get_order_by_id(order_id)
            
            return {
                'order_id': order.id,
                'status': order.status,
                'symbol': order.symbol,
                'qty': order.qty,
                'filled_qty': order.filled_qty or 0,
                'filled_avg_price': order.filled_avg_price or 0,
                'created_at': order.created_at,
                'updated_at': order.updated_at,
                'strategy': self._order_tracking.get(order_id, {}).get('strategy', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Error getting order status for {order_id}: {e}")
            return {'error': str(e)}

    async def orb_long_call(self, strike_delta: float = 30.0, preview: bool = True) -> str:
        """Opening Range Breakout - Long Call Strategy.
        
        Buys a call option at the specified delta when SPY breaks above opening range high.
        
        Args:
            strike_delta: Target delta for the call option (default: 30.0)
            preview: If True, return preview; if False, execute trade
            
        Returns:
            Formatted string with strategy result
        """
        try:
            strategy_name = "orb_long_call"
            
            # Get current SPY price and opening range
            spy_price = await self._get_spy_price()
            opening_range = await self._get_opening_range()
            
            # Check if we're above opening range high
            if spy_price <= opening_range['high']:
                return f"""
                ORB Long Call - Conditions Not Met:
                ----------------------------------
                Current SPY Price: ${spy_price:.2f}
                Opening Range High: ${opening_range['high']:.2f}
                
                Strategy triggers when SPY breaks above opening range high.
                """
            
            # Find appropriate call option
            target_delta = strike_delta / 100.0  # Convert to decimal
            call_option = await option_cache.get_by_delta(target_delta, 'call')
            
            if not call_option:
                return f"""
                ORB Long Call - No Suitable Option Found:
                ----------------------------------------
                Target Delta: {target_delta:.2f}
                
                No call option found matching target delta.
                Ensure 0DTE SPY option chain is loaded.
                """
            
            # Calculate trade details
            mid_price = (call_option.bid + call_option.ask) / 2
            trade_cost = mid_price * 100  # Option contract multiplier
            
            # Create trade legs
            legs = [{
                'symbol': call_option.symbol,
                'side': 'buy',
                'quantity': 1,
                'ratio_qty': 1,
                'estimated_cost': trade_cost,
                'delta': call_option.delta,
                'max_profit': float('inf'),  # Unlimited upside
                'max_loss': trade_cost,
                'strike': call_option.strike,
                'expiration': call_option.expiration
            }]
            
            if preview:
                # Generate preview
                trade_preview = await risk_manager.generate_preview(strategy_name, legs, trade_cost)
                
                return f"""
                ORB Long Call - Trade Preview:
                ----------------------------
                Strategy: Opening Range Breakout Call
                Current SPY: ${spy_price:.2f}
                OR High: ${opening_range['high']:.2f} ✓ (Breakout confirmed)
                
                Option Details:
                - Symbol: {call_option.symbol}
                - Strike: ${call_option.strike:.2f}
                - Delta: {call_option.delta:.3f}
                - Mid Price: ${mid_price:.2f}
                - Total Cost: ${trade_cost:.2f}
                
                Risk Analysis:
                - Max Profit: Unlimited
                - Max Loss: ${trade_cost:.2f}
                - Delta Exposure: +{call_option.delta * 100:.0f}
                - Warnings: {', '.join(trade_preview.risk_warnings) if trade_preview.risk_warnings else 'None'}
                
                To execute: Confirm with token '{trade_preview.confirmation_token}'
                """
            else:
                # This would be the execution path
                return "Execution not yet implemented - use preview mode"
                
        except Exception as e:
            logger.error(f"Error in orb_long_call: {e}")
            return f"Error executing ORB Long Call strategy: {str(e)}"
    
    async def orb_long_put(self, strike_delta: float = 30.0, preview: bool = True) -> str:
        """Opening Range Breakout - Long Put Strategy.
        
        Buys a put option at the specified delta when SPY breaks below opening range low.
        
        Args:
            strike_delta: Target delta for the put option (default: 30.0)
            preview: If True, return preview; if False, execute trade
            
        Returns:
            Formatted string with strategy result
        """
        try:
            strategy_name = "orb_long_put"
            
            # Get current SPY price and opening range
            spy_price = await self._get_spy_price()
            opening_range = await self._get_opening_range()
            
            # Check if we're below opening range low
            if spy_price >= opening_range['low']:
                return f"""
                ORB Long Put - Conditions Not Met:
                ---------------------------------
                Current SPY Price: ${spy_price:.2f}
                Opening Range Low: ${opening_range['low']:.2f}
                
                Strategy triggers when SPY breaks below opening range low.
                """
            
            # Find appropriate put option
            target_delta = strike_delta / 100.0  # Convert to decimal
            put_option = await option_cache.get_by_delta(target_delta, 'put')
            
            if not put_option:
                return f"""
                ORB Long Put - No Suitable Option Found:
                ---------------------------------------
                Target Delta: {target_delta:.2f}
                
                No put option found matching target delta.
                Ensure 0DTE SPY option chain is loaded.
                """
            
            # Calculate trade details
            mid_price = (put_option.bid + put_option.ask) / 2
            trade_cost = mid_price * 100  # Option contract multiplier
            
            # Create trade legs
            legs = [{
                'symbol': put_option.symbol,
                'side': 'buy',
                'quantity': 1,
                'ratio_qty': 1,
                'estimated_cost': trade_cost,
                'delta': put_option.delta,
                'max_profit': (put_option.strike * 100) - trade_cost,  # Strike price minus premium
                'max_loss': trade_cost,
                'strike': put_option.strike,
                'expiration': put_option.expiration
            }]
            
            if preview:
                # Generate preview
                trade_preview = await risk_manager.generate_preview(strategy_name, legs, trade_cost)
                
                return f"""
                ORB Long Put - Trade Preview:
                ---------------------------
                Strategy: Opening Range Breakout Put
                Current SPY: ${spy_price:.2f}
                OR Low: ${opening_range['low']:.2f} ✓ (Breakdown confirmed)
                
                Option Details:
                - Symbol: {put_option.symbol}
                - Strike: ${put_option.strike:.2f}
                - Delta: {put_option.delta:.3f}
                - Mid Price: ${mid_price:.2f}
                - Total Cost: ${trade_cost:.2f}
                
                Risk Analysis:
                - Max Profit: ${legs[0]['max_profit']:.2f}
                - Max Loss: ${trade_cost:.2f}
                - Delta Exposure: {put_option.delta * 100:.0f}
                - Warnings: {', '.join(trade_preview.risk_warnings) if trade_preview.risk_warnings else 'None'}
                
                To execute: Confirm with token '{trade_preview.confirmation_token}'
                """
            else:
                # This would be the execution path
                return "Execution not yet implemented - use preview mode"
                
        except Exception as e:
            logger.error(f"Error in orb_long_put: {e}")
            return f"Error executing ORB Long Put strategy: {str(e)}"
    
    async def iron_condor_30_delta(self, width: int = 10, preview: bool = True) -> str:
        """30-Delta Iron Condor Strategy.
        
        Sells a call spread and put spread both at ~30 delta for neutral income strategy.
        
        Args:
            width: Strike width for each spread (default: 10)
            preview: If True, return preview; if False, execute trade
            
        Returns:
            Formatted string with strategy result
        """
        try:
            strategy_name = "iron_condor_30_delta"
            
            # Get 30-delta options
            target_delta = 0.30
            call_option = await option_cache.get_by_delta(target_delta, 'call')
            put_option = await option_cache.get_by_delta(target_delta, 'put')
            
            if not call_option or not put_option:
                return """
                Iron Condor - Options Not Available:
                ------------------------------------
                Could not find suitable 30-delta call and put options.
                Ensure 0DTE SPY option chain is loaded.
                """
            
            # Find options for the spreads (width points away)
            call_strike_long = call_option.strike + width
            put_strike_long = put_option.strike - width
            
            call_long = await self._find_option_by_strike(call_strike_long, 'call')
            put_long = await self._find_option_by_strike(put_strike_long, 'put')
            
            if not call_long or not put_long:
                return f"""
                Iron Condor - Spread Options Not Available:
                ------------------------------------------
                Could not find options for {width}-point spreads.
                Call Long Strike: ${call_strike_long:.2f}
                Put Long Strike: ${put_strike_long:.2f}
                """
            
            # Calculate trade details
            call_spread_credit = (call_option.bid - call_long.ask) * 100
            put_spread_credit = (put_option.bid - put_long.ask) * 100
            total_credit = call_spread_credit + put_spread_credit
            max_loss = (width * 100) - total_credit
            
            # Create trade legs
            legs = [
                {  # Short call
                    'symbol': call_option.symbol,
                    'side': 'sell',
                    'quantity': 1,
                    'ratio_qty': 1,
                    'delta': call_option.delta,
                    'strike': call_option.strike
                },
                {  # Long call
                    'symbol': call_long.symbol,
                    'side': 'buy',
                    'quantity': 1,
                    'ratio_qty': 1,
                    'delta': call_long.delta,
                    'strike': call_long.strike
                },
                {  # Short put
                    'symbol': put_option.symbol,
                    'side': 'sell',
                    'quantity': 1,
                    'ratio_qty': 1,
                    'delta': put_option.delta,
                    'strike': put_option.strike
                },
                {  # Long put
                    'symbol': put_long.symbol,
                    'side': 'buy',
                    'quantity': 1,
                    'ratio_qty': 1,
                    'delta': put_long.delta,
                    'strike': put_long.strike
                }
            ]
            
            if preview:
                trade_preview = await risk_manager.generate_preview(strategy_name, legs, -total_credit)
                
                spy_price = await self._get_spy_price()
                
                return f"""
                Iron Condor 30-Delta - Trade Preview:
                ------------------------------------
                Strategy: Neutral income strategy
                Current SPY: ${spy_price:.2f}
                
                Call Spread: ${call_option.strike:.2f}/${call_long.strike:.2f}
                Put Spread: ${put_option.strike:.2f}/${put_long.strike:.2f}
                
                Trade Details:
                - Call Spread Credit: ${call_spread_credit:.2f}
                - Put Spread Credit: ${put_spread_credit:.2f}
                - Total Credit: ${total_credit:.2f}
                - Max Profit: ${total_credit:.2f} (at expiration between strikes)
                - Max Loss: ${max_loss:.2f}
                - Breakeven Range: ${put_option.strike - total_credit/100:.2f} to ${call_option.strike + total_credit/100:.2f}
                
                To execute: Confirm with token '{trade_preview.confirmation_token}'
                """
            else:
                return "Execution not yet implemented - use preview mode"
                
        except Exception as e:
            logger.error(f"Error in iron_condor_30_delta: {e}")
            return f"Error executing Iron Condor strategy: {str(e)}"
    
    async def lotto_play_5_delta(self, side: str = "call", preview: bool = True) -> str:
        """Late-day 5-Delta Lottery Play Strategy.
        
        Buys very low delta options (5-delta) in the last hour of trading
        for potential large moves into close. High risk, high reward strategy.
        
        Args:
            side: 'call' or 'put' (default: 'call')
            preview: If True, return preview; if False, execute trade
            
        Returns:
            Formatted string with strategy result
        """
        try:
            strategy_name = "lotto_play_5_delta"
            
            # Check if we're in the last hour of trading
            current_time = datetime.now().time()
            market_close = time(16, 0)  # 4:00 PM ET
            lotto_start = time(15, 0)   # 3:00 PM ET
            
            if current_time < lotto_start:
                return f"""
                Lotto Play 5-Delta - Too Early:
                -------------------------------
                Current Time: {current_time}
                Strategy Window: 3:00 PM - 4:00 PM ET
                
                This strategy is designed for the final hour of trading
                when volatility and potential for large moves increases.
                """
            
            if current_time > market_close:
                return """
                Lotto Play 5-Delta - Market Closed:
                -----------------------------------
                Market has closed. This strategy targets the final hour
                of trading for maximum time decay and volatility potential.
                """
            
            # Validate side parameter
            if side.lower() not in ['call', 'put']:
                return f"Invalid side '{side}'. Must be 'call' or 'put'."
            
            # Find 5-delta option
            target_delta = 0.05
            option = await option_cache.get_by_delta(target_delta, side.lower())
            
            if not option:
                return f"""
                Lotto Play 5-Delta - No Suitable Option Found:
                ---------------------------------------------
                Target Delta: {target_delta:.2f}
                Side: {side.title()}
                
                No {side.lower()} option found matching 5-delta target.
                Ensure 0DTE SPY option chain is loaded.
                """
            
            # Calculate trade details
            mid_price = (option.bid + option.ask) / 2
            
            # For lotto plays, we typically risk a small fixed amount
            risk_amount = 100.0  # Risk $100 per lotto play
            quantity = max(1, int(risk_amount / (mid_price * 100)))  # How many contracts we can buy
            total_cost = mid_price * 100 * quantity
            
            # Calculate potential profits (simplified)
            if side.lower() == 'call':
                # For calls, potential is theoretically unlimited
                max_profit = float('inf')
                breakeven = option.strike + (total_cost / (quantity * 100))
            else:
                # For puts, max profit is strike price minus premium
                max_profit = (option.strike * quantity * 100) - total_cost
                breakeven = option.strike - (total_cost / (quantity * 100))
            
            # Create trade legs
            legs = [{
                'symbol': option.symbol,
                'side': 'buy',
                'quantity': quantity,
                'ratio_qty': quantity,
                'estimated_cost': total_cost,
                'delta': option.delta,
                'max_profit': max_profit,
                'max_loss': total_cost,
                'strike': option.strike,
                'expiration': option.expiration,
                'iv': option.iv
            }]
            
            if preview:
                # Generate preview
                trade_preview = await risk_manager.generate_preview(strategy_name, legs, total_cost)
                
                spy_price = await self._get_spy_price()
                time_to_close = (datetime.combine(datetime.now().date(), market_close) - 
                                datetime.now()).total_seconds() / 60  # Minutes
                
                return f"""
                Lotto Play 5-Delta {side.title()} - Trade Preview:
                ================================================
                Strategy: High-risk lottery play for end-of-day moves
                Current SPY: ${spy_price:.2f}
                Time to Close: {time_to_close:.0f} minutes
                
                Option Details:
                - Symbol: {option.symbol}
                - Strike: ${option.strike:.2f}
                - Delta: {option.delta:.3f} (Very low probability)
                - Mid Price: ${mid_price:.2f}
                - Implied Vol: {option.iv:.1%}
                - Quantity: {quantity} contracts
                - Total Cost: ${total_cost:.2f}
                
                Risk Analysis:
                - Max Profit: {'Unlimited' if max_profit == float('inf') else f'${max_profit:.2f}'}
                - Max Loss: ${total_cost:.2f} (100% of premium)
                - Breakeven: ${breakeven:.2f}
                - Delta Exposure: {option.delta * quantity * 100:+.0f}
                
                ⚠️  HIGH RISK LOTTERY PLAY ⚠️
                - Very low probability of profit
                - High time decay (theta risk)
                - Suitable only for small speculative amounts
                
                To execute: Confirm with token '{trade_preview.confirmation_token}'
                """
            else:
                # This would be the execution path
                return "Execution not yet implemented - use preview mode"
                
        except Exception as e:
            logger.error(f"Error in lotto_play_5_delta: {e}")
            return f"Error executing Lotto Play 5-Delta strategy: {str(e)}"
    
    async def straddle_scan(self, max_iv: float = 0.8, min_volume: int = 100) -> str:
        """Scan for Profitable Straddle Opportunities.
        
        Scans 0DTE SPY options for straddle opportunities based on 
        implied volatility and volume criteria.
        
        Args:
            max_iv: Maximum implied volatility threshold (default: 0.8 = 80%)
            min_volume: Minimum volume requirement (default: 100)
            
        Returns:
            Formatted string with straddle opportunities
        """
        try:
            # Get all current options
            all_calls = await option_cache.get_all_options('call')
            all_puts = await option_cache.get_all_options('put')
            
            if not all_calls or not all_puts:
                return """
                Straddle Scan - No Options Data:
                --------------------------------
                No option chain data available for scanning.
                Ensure 0DTE SPY option chain is loaded.
                """
            
            # Group options by strike price to find straddle pairs
            strike_pairs = {}
            
            # Index calls by strike
            for call in all_calls:
                strike = call.strike
                if call.volume >= min_volume and call.iv <= max_iv:
                    if strike not in strike_pairs:
                        strike_pairs[strike] = {}
                    strike_pairs[strike]['call'] = call
            
            # Index puts by strike
            for put in all_puts:
                strike = put.strike
                if (strike in strike_pairs and 
                    put.volume >= min_volume and 
                    put.iv <= max_iv):
                    strike_pairs[strike]['put'] = put
            
            # Find complete straddle pairs (both call and put available)
            straddle_opportunities = []
            
            for strike, options in strike_pairs.items():
                if 'call' in options and 'put' in options:
                    call = options['call']
                    put = options['put']
                    
                    # Calculate straddle metrics
                    call_mid = (call.bid + call.ask) / 2
                    put_mid = (put.bid + put.ask) / 2
                    straddle_cost = (call_mid + put_mid) * 100
                    
                    # Calculate breakeven points
                    upper_breakeven = strike + (call_mid + put_mid)
                    lower_breakeven = strike - (call_mid + put_mid)
                    
                    # Calculate implied move
                    spy_price = await self._get_spy_price()
                    implied_move_pct = ((call_mid + put_mid) / spy_price) * 100
                    
                    # Average IV of the straddle
                    avg_iv = (call.iv + put.iv) / 2
                    
                    straddle_opportunities.append({
                        'strike': strike,
                        'call': call,
                        'put': put,
                        'cost': straddle_cost,
                        'upper_breakeven': upper_breakeven,
                        'lower_breakeven': lower_breakeven,
                        'implied_move_pct': implied_move_pct,
                        'avg_iv': avg_iv,
                        'total_volume': call.volume + put.volume
                    })
            
            if not straddle_opportunities:
                return f"""
                Straddle Scan - No Opportunities Found:
                --------------------------------------
                Scan Criteria:
                - Max IV: {max_iv:.1%}
                - Min Volume: {min_volume}
                
                No straddle pairs found meeting these criteria.
                Consider relaxing the filters or checking option chain data.
                """
            
            # Sort by implied move percentage (lower is generally better for sellers)
            straddle_opportunities.sort(key=lambda x: x['implied_move_pct'])
            
            # Format results
            spy_price = await self._get_spy_price()
            result = f"""
            Straddle Scan Results:
            =====================
            Current SPY: ${spy_price:.2f}
            Scan Criteria: Max IV {max_iv:.0%}, Min Volume {min_volume}
            Found {len(straddle_opportunities)} opportunities:
            
            """
            
            for i, straddle in enumerate(straddle_opportunities[:10], 1):  # Show top 10
                result += f"""
            {i}. ${straddle['strike']:.2f} Strike Straddle:
               Cost: ${straddle['cost']:.2f}
               Implied Move: {straddle['implied_move_pct']:.1f}%
               Breakevens: ${straddle['lower_breakeven']:.2f} - ${straddle['upper_breakeven']:.2f}
               Avg IV: {straddle['avg_iv']:.1%}
               Volume: {straddle['total_volume']} (C:{straddle['call'].volume}, P:{straddle['put'].volume})
               Call: {straddle['call'].symbol} (δ={straddle['call'].delta:.3f})
               Put: {straddle['put'].symbol} (δ={straddle['put'].delta:.3f})
               ---
                """
            
            if len(straddle_opportunities) > 10:
                result += f"\n            ... and {len(straddle_opportunities) - 10} more opportunities"
            
            result += f"""
            
            💡 Strategy Notes:
            - Lower implied move % generally better for straddle sellers
            - Higher volume provides better liquidity
            - Consider current market volatility vs. implied volatility
            - 0DTE straddles have high time decay risk
            """
            
            return result
            
        except Exception as e:
            logger.error(f"Error in straddle_scan: {e}")
            return f"Error scanning for straddle opportunities: {str(e)}"
    
    async def _get_spy_price(self) -> float:
        """Get current SPY price."""
        try:
            from alpaca.data.requests import StockLatestQuoteRequest
            request = StockLatestQuoteRequest(symbol_or_symbols='SPY')
            quotes = client_manager.stock_data_client.get_stock_latest_quote(request)
            
            if 'SPY' in quotes:
                quote = quotes['SPY']
                return (quote.ask_price + quote.bid_price) / 2
            else:
                raise StrategyError("Could not get SPY price")
                
        except Exception as e:
            logger.error(f"Error getting SPY price: {e}")
            raise StrategyError(f"Error getting SPY price: {e}")
    
    async def _get_opening_range(self) -> Dict[str, float]:
        """Get SPY opening range (first 30 minutes of trading)."""
        try:
            # This is a simplified version - would need to calculate from actual bars
            # For now, return mock data
            spy_price = await self._get_spy_price()
            
            return {
                'high': spy_price + 2.0,  # Mock: current price + $2
                'low': spy_price - 2.0,   # Mock: current price - $2
                'range': 4.0
            }
            
        except Exception as e:
            logger.error(f"Error getting opening range: {e}")
            raise StrategyError(f"Error getting opening range: {e}")
    
    async def _find_option_by_strike(self, strike: float, option_type: str) -> Optional[OptionData]:
        """Find option by exact strike price."""
        all_options = await option_cache.get_all_options(option_type)
        
        for option in all_options:
            if abs(option.strike - strike) < 0.01:  # Allow small floating point differences
                return option
        
        return None


# Global strategies instance
strategies = ZDTEStrategies()