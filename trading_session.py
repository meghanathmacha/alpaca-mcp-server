#!/usr/bin/env python3
"""
Quick Trading Session Launcher
=============================

Run this to start your trading session with all tools ready.
Usage: python trading_session.py
"""

import asyncio
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

from services.alpaca_client import client_manager
from services.risk_manager import risk_manager
from services.strategies import strategies
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.requests import OptionChainRequest, OptionSnapshotRequest, StockLatestQuoteRequest


class TradingSession:
    """Main trading session interface."""
    
    def __init__(self):
        self.session_start = datetime.now()
        self.session_trades = []
        self.watchlist = []
        
    async def start(self):
        """Initialize trading session."""
        print("🚀 TRADING SESSION STARTING")
        print("=" * 80)
        print(f"Session Time: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Quick status check
        await self.status()
        print()
        
        # Show available commands
        self.show_commands()
        
        return self
    
    async def status(self):
        """Quick account and market status."""
        try:
            # Account info
            account = client_manager.trading_client.get_account()
            positions = client_manager.trading_client.get_all_positions()
            
            print("📊 ACCOUNT STATUS")
            print("-" * 40)
            print(f"Buying Power: ${float(account.buying_power):,.0f}")
            print(f"Portfolio Value: ${float(account.portfolio_value):,.0f}")
            print(f"Positions: {len(positions)}")
            
            # P&L
            daily_pnl = await risk_manager.get_daily_pnl()
            portfolio_delta = await risk_manager.get_portfolio_delta()
            print(f"Daily P&L: ${daily_pnl:+.2f}")
            print(f"Portfolio Delta: {portfolio_delta:+.1f}")
            
            # SPY price
            spy_price = await self.get_spy_price()
            print(f"SPY: ${spy_price:.2f}")
            
            # Pending orders
            orders = client_manager.trading_client.get_orders()
            pending = [o for o in orders if o.status in ['new', 'accepted', 'pending_new']]
            print(f"Pending Orders: {len(pending)}")
            
            if positions:
                print("\n📍 Current Positions:")
                for pos in positions:
                    pnl = float(pos.unrealized_pl or 0)
                    print(f"  {pos.symbol}: {pos.qty} | P&L: ${pnl:+.0f}")
            
        except Exception as e:
            print(f"❌ Status error: {e}")
    
    async def get_spy_price(self) -> float:
        """Get current SPY price."""
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols='SPY')
            quotes = client_manager.stock_data_client.get_stock_latest_quote(request)
            if 'SPY' in quotes:
                quote = quotes['SPY']
                return (quote.ask_price + quote.bid_price) / 2
            return 0.0
        except:
            return 0.0
    
    async def scan_options(self, days_ahead: int = 1, around_price: Optional[float] = None, max_price: float = 5.0):
        """Scan for trading opportunities."""
        try:
            print(f"🔍 SCANNING SPY OPTIONS")
            print("-" * 40)
            
            target_date = date.today() + timedelta(days=days_ahead)
            spy_price = await self.get_spy_price()
            
            if around_price is None:
                around_price = spy_price
            
            # Get options near target price
            request = OptionChainRequest(
                underlying_symbol='SPY',
                expiration_date=target_date,
                strike_price_gte=around_price - 30,
                strike_price_lte=around_price + 30
            )
            
            option_chain = client_manager.option_data_client.get_option_chain(request)
            print(f"Found {len(option_chain)} contracts expiring {target_date}")
            print(f"SPY: ${spy_price:.2f}")
            
            # Sample good options
            good_options = []
            for symbol in list(option_chain.keys())[:30]:
                try:
                    snapshot_request = OptionSnapshotRequest(symbol_or_symbols=[symbol])
                    snapshots = client_manager.option_data_client.get_option_snapshot(snapshot_request)
                    
                    if symbol in snapshots:
                        quote = snapshots[symbol].latest_quote
                        option_type = 'CALL' if 'C' in symbol else 'PUT'
                        strike_str = symbol.split('C' if option_type == 'CALL' else 'P')[1]
                        strike = float(strike_str) / 1000
                        
                        bid = quote.bid_price or 0.0
                        ask = quote.ask_price or 0.01
                        mid = (bid + ask) / 2
                        
                        if 0.10 <= mid <= max_price and bid > 0:
                            distance = abs(spy_price - strike)
                            good_options.append({
                                'symbol': symbol,
                                'type': option_type,
                                'strike': strike,
                                'bid': bid,
                                'ask': ask,
                                'mid': mid,
                                'cost': mid * 100,
                                'distance': distance
                            })
                except:
                    continue
            
            # Sort by distance from current price
            good_options.sort(key=lambda x: x['distance'])
            
            print(f"\n📊 TRADING OPPORTUNITIES (Under ${max_price:.2f}):")
            print("Symbol               Type Strike   Mid    Cost   Distance")
            print("-" * 65)
            
            for i, opt in enumerate(good_options[:15], 1):
                print(f"{i:2}. {opt['symbol']:<15} {opt['type']:<4} {opt['strike']:<8.1f} "
                      f"{opt['mid']:<6.2f} ${opt['cost']:<5.0f} {opt['distance']:<8.1f}")
            
            return good_options
            
        except Exception as e:
            print(f"❌ Scan error: {e}")
            return []
    
    async def quick_buy(self, symbol: str, quantity: int = 1, limit_price: Optional[float] = None):
        """Quick buy with minimal friction."""
        try:
            print(f"💰 QUICK BUY: {symbol}")
            print("-" * 40)
            
            # Get quote
            snapshot_request = OptionSnapshotRequest(symbol_or_symbols=[symbol])
            snapshots = client_manager.option_data_client.get_option_snapshot(snapshot_request)
            
            if symbol not in snapshots:
                print("❌ Cannot get quote")
                return None
            
            quote = snapshots[symbol].latest_quote
            bid = quote.bid_price or 0.0
            ask = quote.ask_price or 0.01
            mid = (bid + ask) / 2
            
            # Auto-set limit price if not provided
            if limit_price is None:
                limit_price = round(mid + 0.05, 2)  # Slightly above mid
            
            cost = limit_price * 100 * quantity
            
            print(f"Symbol: {symbol}")
            print(f"Quantity: {quantity}")
            print(f"Bid/Ask: ${bid:.2f}/${ask:.2f}")
            print(f"Limit Price: ${limit_price:.2f}")
            print(f"Total Cost: ${cost:.2f}")
            
            # Risk check
            daily_pnl = await risk_manager.get_daily_pnl()
            print(f"Current P&L: ${daily_pnl:+.2f}")
            
            # Submit order
            order_request = LimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price
            )
            
            order = client_manager.trading_client.submit_order(order_request)
            
            print(f"\n✅ ORDER PLACED!")
            print(f"Order ID: {order.id}")
            print(f"Status: {order.status}")
            
            # Track in session
            self.session_trades.append({
                'time': datetime.now(),
                'symbol': symbol,
                'side': 'BUY',
                'qty': quantity,
                'limit_price': limit_price,
                'order_id': order.id,
                'cost': cost
            })
            
            return order.id
            
        except Exception as e:
            print(f"❌ Order error: {e}")
            return None
    
    async def quick_sell(self, symbol: str, quantity: int = 1, limit_price: Optional[float] = None):
        """Quick sell position."""
        try:
            print(f"💸 QUICK SELL: {symbol}")
            print("-" * 40)
            
            # Check if we have position
            positions = client_manager.trading_client.get_all_positions()
            position = next((p for p in positions if p.symbol == symbol), None)
            
            if not position:
                print(f"❌ No position found for {symbol}")
                return None
            
            available_qty = int(position.qty)
            if quantity > available_qty:
                print(f"❌ Only have {available_qty} contracts, requested {quantity}")
                return None
            
            # Get quote
            snapshot_request = OptionSnapshotRequest(symbol_or_symbols=[symbol])
            snapshots = client_manager.option_data_client.get_option_snapshot(snapshot_request)
            
            if symbol not in snapshots:
                print("❌ Cannot get quote")
                return None
            
            quote = snapshots[symbol].latest_quote
            bid = quote.bid_price or 0.0
            ask = quote.ask_price or 0.01
            
            # Auto-set limit price if not provided (slightly below bid)
            if limit_price is None:
                limit_price = round(bid - 0.05, 2)
            
            proceeds = limit_price * 100 * quantity
            
            print(f"Position: {available_qty} contracts")
            print(f"Selling: {quantity}")
            print(f"Bid/Ask: ${bid:.2f}/${ask:.2f}")
            print(f"Limit Price: ${limit_price:.2f}")
            print(f"Proceeds: ${proceeds:.2f}")
            
            # Submit sell order
            order_request = LimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price
            )
            
            order = client_manager.trading_client.submit_order(order_request)
            
            print(f"\n✅ SELL ORDER PLACED!")
            print(f"Order ID: {order.id}")
            print(f"Status: {order.status}")
            
            # Track in session
            self.session_trades.append({
                'time': datetime.now(),
                'symbol': symbol,
                'side': 'SELL',
                'qty': quantity,
                'limit_price': limit_price,
                'order_id': order.id,
                'proceeds': proceeds
            })
            
            return order.id
            
        except Exception as e:
            print(f"❌ Sell error: {e}")
            return None
    
    async def check_orders(self):
        """Check all order statuses."""
        try:
            print("📋 ORDER STATUS")
            print("-" * 40)
            
            orders = client_manager.trading_client.get_orders()
            
            if not orders:
                print("No orders today")
                return
            
            for order in orders[:10]:  # Last 10 orders
                status_emoji = {
                    'filled': '✅',
                    'accepted': '⏳',
                    'new': '🟡',
                    'cancelled': '❌',
                    'rejected': '🚫'
                }.get(str(order.status).lower(), '❓')
                
                print(f"{status_emoji} {order.symbol}: {order.side} {order.qty} @ ${order.limit_price or 'MKT'} - {order.status}")
                
                if order.filled_qty and order.filled_avg_price:
                    print(f"   Filled: {order.filled_qty} @ ${float(order.filled_avg_price):.2f}")
                    
        except Exception as e:
            print(f"❌ Orders error: {e}")
    
    def session_summary(self):
        """Show session trading summary."""
        print("\n📈 SESSION SUMMARY")
        print("-" * 40)
        print(f"Session Duration: {datetime.now() - self.session_start}")
        print(f"Trades Executed: {len(self.session_trades)}")
        
        if self.session_trades:
            total_cost = sum(t.get('cost', 0) for t in self.session_trades if t['side'] == 'BUY')
            total_proceeds = sum(t.get('proceeds', 0) for t in self.session_trades if t['side'] == 'SELL')
            
            print(f"Total Bought: ${total_cost:.0f}")
            print(f"Total Sold: ${total_proceeds:.0f}")
            
            print("\nTrade Log:")
            for i, trade in enumerate(self.session_trades, 1):
                time_str = trade['time'].strftime('%H:%M')
                print(f"{i}. {time_str} - {trade['side']} {trade['qty']} {trade['symbol']} @ ${trade['limit_price']:.2f}")
    
    def show_commands(self):
        """Show available commands."""
        print("🎯 AVAILABLE COMMANDS")
        print("-" * 40)
        print("Strategy & Analysis:")
        print("  await session.scan_options()               # Find opportunities")
        print("  await session.scan_options(max_price=2.0)  # Cheap options only")
        print("  await session.get_spy_price()              # Current SPY price")
        print()
        print("Quick Trading:")
        print("  await session.quick_buy('SYMBOL')          # Buy with auto-limit")
        print("  await session.quick_buy('SYMBOL', 2, 3.50) # Buy 2 at $3.50 limit")
        print("  await session.quick_sell('SYMBOL')         # Sell position")
        print()
        print("Monitoring:")
        print("  await session.status()                     # Account status")
        print("  await session.check_orders()               # Order status")
        print("  session.session_summary()                  # Session summary")
        print()
        print("Strategy Tools:")
        print("  await strategies.orb_long_call(preview=True)   # ORB strategy")
        print("  await strategies.iron_condor_30_delta()       # Iron Condor")
        print("  await strategies.lotto_play_5_delta()         # Lottery play")
        print()
        print("💡 TIP: Use 'await session.scan_options()' to start!")


async def main():
    """Start trading session."""
    session = TradingSession()
    return await session.start()


if __name__ == "__main__":
    print("🚀 Quick start with: python trading_session.py")
    session = asyncio.run(main())