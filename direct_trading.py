#!/usr/bin/env python3
"""
Direct Trading Interface for SPY Options
========================================

Use this script to trade directly from the terminal without MCP.
Run: python direct_trading.py
"""

import asyncio
import sys
from datetime import date, timedelta, datetime
from services.alpaca_client import client_manager
from services.risk_manager import risk_manager
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide
from alpaca.data.requests import OptionChainRequest, OptionSnapshotRequest, StockLatestQuoteRequest


class DirectTrader:
    """Direct trading interface for terminal use."""
    
    def __init__(self):
        self.session_trades = []
    
    async def show_account(self):
        """Show account information."""
        try:
            account = client_manager.trading_client.get_account()
            positions = client_manager.trading_client.get_all_positions()
            
            print("📊 ACCOUNT STATUS")
            print("=" * 50)
            print(f"Account ID: {account.id}")
            print(f"Status: {account.status}")
            print(f"Buying Power: ${float(account.buying_power):,.2f}")
            print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
            print(f"Day Trade Count: {account.daytrade_count}")
            print(f"Paper Trading: {account.pattern_day_trader == False}")
            print(f"Positions: {len(positions)}")
            
            if positions:
                print("\nCurrent Positions:")
                for pos in positions:
                    pnl = float(pos.unrealized_pl or 0)
                    pnl_pct = float(pos.unrealized_plpc or 0) * 100
                    print(f"  {pos.symbol}: {pos.qty} @ ${pos.avg_entry_price} | P&L: ${pnl:.2f} ({pnl_pct:+.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error getting account info: {e}")
            return False
    
    async def get_spy_price(self):
        """Get current SPY price."""
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols='SPY')
            quotes = client_manager.stock_data_client.get_stock_latest_quote(request)
            
            if 'SPY' in quotes:
                quote = quotes['SPY']
                spy_price = (quote.ask_price + quote.bid_price) / 2
                print(f"📈 SPY Current Price: ${spy_price:.2f}")
                print(f"   Bid: ${quote.bid_price:.2f} | Ask: ${quote.ask_price:.2f}")
                return spy_price
            else:
                print("❌ Could not get SPY price")
                return None
                
        except Exception as e:
            print(f"❌ Error getting SPY price: {e}")
            return None
    
    async def scan_spy_options(self, days_ahead=1, show_count=10):
        """Scan available SPY options."""
        try:
            target_date = date.today() + timedelta(days=days_ahead)
            
            print(f"🔍 SCANNING SPY OPTIONS for {target_date}")
            print("=" * 50)
            
            # Get option chain
            request = OptionChainRequest(
                underlying_symbol='SPY',
                expiration_date=target_date
            )
            
            option_chain = client_manager.option_data_client.get_option_chain(request)
            
            if not option_chain:
                print(f"❌ No options found for {target_date}")
                return []
            
            print(f"✓ Found {len(option_chain)} total contracts")
            
            # Separate calls and puts
            calls = [symbol for symbol in option_chain.keys() if 'C' in symbol]
            puts = [symbol for symbol in option_chain.keys() if 'P' in symbol]
            
            print(f"   Calls: {len(calls)} | Puts: {len(puts)}")
            
            # Get current SPY price for reference
            spy_price = await self.get_spy_price()
            
            # Sample some options near the money
            sample_options = []
            
            for symbol in list(option_chain.keys())[:show_count]:
                try:
                    # Get quote
                    snapshot_request = OptionSnapshotRequest(symbol_or_symbols=[symbol])
                    snapshots = client_manager.option_data_client.get_option_snapshot(snapshot_request)
                    
                    if symbol in snapshots:
                        snapshot = snapshots[symbol]
                        quote = snapshot.latest_quote
                        
                        # Parse strike from symbol
                        option_type = 'CALL' if 'C' in symbol else 'PUT'
                        strike_str = symbol.split('C' if option_type == 'CALL' else 'P')[1]
                        strike = float(strike_str) / 1000
                        
                        bid = quote.bid_price or 0.0
                        ask = quote.ask_price or 0.01
                        mid = (bid + ask) / 2
                        
                        # Calculate moneyness
                        if spy_price:
                            if option_type == 'CALL':
                                moneyness = spy_price - strike
                            else:
                                moneyness = strike - spy_price
                        else:
                            moneyness = 0
                        
                        sample_options.append({
                            'symbol': symbol,
                            'type': option_type,
                            'strike': strike,
                            'bid': bid,
                            'ask': ask,
                            'mid': mid,
                            'moneyness': moneyness
                        })
                        
                except Exception:
                    continue
            
            # Sort by moneyness (closest to at-the-money first)
            sample_options.sort(key=lambda x: abs(x['moneyness']))
            
            print(f"\n📋 Sample Options (closest to ATM):")
            print(f"{'Symbol':<20} {'Type':<4} {'Strike':<8} {'Bid':<6} {'Ask':<6} {'Mid':<6} {'Moneyness':<10}")
            print("-" * 70)
            
            for opt in sample_options[:show_count]:
                print(f"{opt['symbol']:<20} {opt['type']:<4} {opt['strike']:<8.1f} "
                      f"{opt['bid']:<6.2f} {opt['ask']:<6.2f} {opt['mid']:<6.2f} {opt['moneyness']:<+10.1f}")
            
            return sample_options
            
        except Exception as e:
            print(f"❌ Error scanning options: {e}")
            return []
    
    async def buy_option(self, symbol, quantity=1, dry_run=True):
        """Buy an option contract."""
        try:
            print(f"💰 {'[DRY RUN] ' if dry_run else ''}BUYING OPTION")
            print("=" * 50)
            print(f"Symbol: {symbol}")
            print(f"Quantity: {quantity} contracts")
            
            # Get current quote
            snapshot_request = OptionSnapshotRequest(symbol_or_symbols=[symbol])
            snapshots = client_manager.option_data_client.get_option_snapshot(snapshot_request)
            
            if symbol not in snapshots:
                print("❌ Could not get option quote")
                return False
            
            snapshot = snapshots[symbol]
            quote = snapshot.latest_quote
            
            ask_price = quote.ask_price or 0.01
            estimated_cost = ask_price * 100 * quantity  # Option multiplier
            
            print(f"Current Ask: ${ask_price:.2f}")
            print(f"Estimated Cost: ${estimated_cost:.2f}")
            
            # Risk check
            daily_pnl = await risk_manager.get_daily_pnl()
            print(f"Current Daily P&L: ${daily_pnl:.2f}")
            
            if dry_run:
                print("🚨 DRY RUN - No actual order submitted")
                print("To execute for real, call: buy_option(symbol, quantity, dry_run=False)")
                return True
            
            # Confirm before real execution
            response = input(f"\n⚠️  Execute REAL order for ${estimated_cost:.2f}? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Order cancelled")
                return False
            
            # Submit market order
            order_request = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=OrderSide.BUY
            )
            
            order = client_manager.trading_client.submit_order(order_request)
            
            print(f"✅ ORDER SUBMITTED")
            print(f"Order ID: {order.id}")
            print(f"Status: {order.status}")
            
            # Track in session
            self.session_trades.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'side': 'BUY',
                'quantity': quantity,
                'order_id': order.id,
                'estimated_cost': estimated_cost
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Error buying option: {e}")
            return False
    
    async def show_session_summary(self):
        """Show summary of this session's activity."""
        print("\n📈 SESSION SUMMARY")
        print("=" * 50)
        
        if not self.session_trades:
            print("No trades executed this session")
            return
        
        total_cost = sum(trade['estimated_cost'] for trade in self.session_trades)
        
        print(f"Trades Executed: {len(self.session_trades)}")
        print(f"Total Estimated Cost: ${total_cost:.2f}")
        print("\nTrade Details:")
        
        for i, trade in enumerate(self.session_trades, 1):
            print(f"{i}. {trade['timestamp'].strftime('%H:%M:%S')} - "
                  f"{trade['side']} {trade['quantity']} {trade['symbol']} "
                  f"(${trade['estimated_cost']:.2f}) [Order: {trade['order_id']}]")


async def main():
    """Main trading interface."""
    trader = DirectTrader()
    
    print("🚀 DIRECT SPY OPTIONS TRADING TERMINAL")
    print("=" * 60)
    print("Available commands:")
    print("1. trader.show_account() - Account info")
    print("2. trader.get_spy_price() - Current SPY price")
    print("3. trader.scan_spy_options() - Scan available options")
    print("4. trader.buy_option('SYMBOL', quantity, dry_run=True) - Buy option")
    print("5. trader.show_session_summary() - Session summary")
    print("\nExample workflow:")
    print("await trader.show_account()")
    print("await trader.scan_spy_options()")
    print("await trader.buy_option('SPY250620C00600000', 1, dry_run=True)")
    print("\n" + "=" * 60)
    
    # Quick demo
    await trader.show_account()
    await trader.get_spy_price()
    options = await trader.scan_spy_options(days_ahead=1, show_count=5)
    
    if options:
        print(f"\n💡 To buy the first option:")
        print(f"await trader.buy_option('{options[0]['symbol']}', 1, dry_run=True)")
    
    return trader


if __name__ == "__main__":
    # Run the main interface
    trader = asyncio.run(main())
    
    print(f"\n🎯 Trader object created! Use 'trader' to execute commands.")
    print(f"Example: asyncio.run(trader.buy_option('SPY250620C00600000', 1, dry_run=True))")