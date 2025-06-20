"""Risk management service for trading operations."""

import asyncio
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from .config import config
from .alpaca_client import client_manager

logger = logging.getLogger(__name__)


@dataclass
class TradePreview:
    """Trade preview with risk analysis."""
    strategy: str
    cost: float
    max_loss: float
    max_profit: float
    delta_exposure: float
    confirmation_token: str
    legs: List[Dict]
    risk_warnings: List[str]
    expires_at: datetime


class RiskManager:
    """Manages trading risk and validation."""
    
    def __init__(self):
        """Initialize risk manager."""
        self._confirmation_cache: Dict[str, TradePreview] = {}
        self._daily_pnl_start: Optional[float] = None
        self._cache_lock = asyncio.Lock()
        
    async def validate_trade(self, preview: TradePreview) -> Tuple[bool, List[str]]:
        """Validate a trade against risk parameters.
        
        Args:
            preview: Trade preview to validate
            
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []
        
        # Check daily loss limit
        current_daily_pnl = await self.get_daily_pnl()
        projected_loss = current_daily_pnl + preview.max_loss
        
        if abs(projected_loss) > config.max_daily_loss:
            violations.append(f"Trade would exceed daily loss limit of ${config.max_daily_loss}")
        
        # Check portfolio delta exposure
        current_delta = await self.get_portfolio_delta()
        projected_delta = current_delta + preview.delta_exposure
        
        if abs(projected_delta) > config.portfolio_delta_cap:
            violations.append(f"Trade would exceed portfolio delta cap of {config.portfolio_delta_cap}")
        
        # Check buying power
        account = client_manager.trading_client.get_account()
        if preview.cost > float(account.buying_power):
            violations.append(f"Insufficient buying power. Required: ${preview.cost:.2f}, Available: ${account.buying_power}")
        
        # Check market hours
        clock = client_manager.trading_client.get_clock()
        if not clock.is_open:
            violations.append("Market is currently closed")
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    async def generate_preview(self, strategy: str, legs: List[Dict], cost: float = None) -> TradePreview:
        """Generate a trade preview with risk analysis.
        
        Args:
            strategy: Strategy name
            legs: List of option legs
            cost: Optional cost override
            
        Returns:
            Trade preview object
        """
        # Calculate cost if not provided
        if cost is None:
            cost = await self._calculate_trade_cost(legs)
        
        # Calculate max profit/loss
        max_profit, max_loss = await self._calculate_profit_loss(legs)
        
        # Calculate delta exposure
        delta_exposure = await self._calculate_delta_exposure(legs)
        
        # Generate confirmation token
        confirmation_token = f"confirm_{strategy}_{int(datetime.now().timestamp())}"
        
        # Check for risk warnings
        risk_warnings = await self._generate_risk_warnings(legs, cost)
        
        preview = TradePreview(
            strategy=strategy,
            cost=cost,
            max_loss=max_loss,
            max_profit=max_profit,
            delta_exposure=delta_exposure,
            confirmation_token=confirmation_token,
            legs=legs,
            risk_warnings=risk_warnings,
            expires_at=datetime.now().timestamp() + config.confirmation_timeout
        )
        
        # Cache the preview
        async with self._cache_lock:
            self._confirmation_cache[confirmation_token] = preview
        
        return preview
    
    async def confirm_trade(self, confirmation_token: str) -> Optional[TradePreview]:
        """Confirm a trade using the confirmation token.
        
        Args:
            confirmation_token: Token from preview
            
        Returns:
            Trade preview if valid, None if expired/invalid
        """
        async with self._cache_lock:
            preview = self._confirmation_cache.get(confirmation_token)
            
            if not preview:
                return None
                
            # Check if confirmation has expired
            if datetime.now().timestamp() > preview.expires_at:
                del self._confirmation_cache[confirmation_token]
                return None
            
            # Remove from cache after confirmation
            del self._confirmation_cache[confirmation_token]
            return preview
    
    async def get_daily_pnl(self) -> float:
        """Get current daily P&L.
        
        Returns:
            Daily P&L in dollars
        """
        try:
            # Get today's start portfolio value if not cached
            if self._daily_pnl_start is None:
                # This would ideally be cached at market open
                # For now, we'll use current equity as baseline
                account = client_manager.trading_client.get_account()
                self._daily_pnl_start = float(account.equity)
            
            # Get current portfolio value
            account = client_manager.trading_client.get_account()
            current_equity = float(account.equity)
            
            return current_equity - self._daily_pnl_start
            
        except Exception as e:
            logger.error(f"Error calculating daily P&L: {e}")
            return 0.0
    
    async def get_portfolio_delta(self) -> float:
        """Get current portfolio delta exposure.
        
        Returns:
            Total portfolio delta
        """
        try:
            positions = client_manager.trading_client.get_all_positions()
            total_delta = 0.0
            
            for position in positions:
                # For options, we'd need to get the current delta
                # For stocks, delta = quantity (simplified)
                if len(position.symbol) > 6:  # Likely an option
                    # Get option snapshot for current delta
                    try:
                        from .alpaca_client import client_manager
                        from alpaca.data.requests import OptionSnapshotRequest
                        
                        request = OptionSnapshotRequest(symbol_or_symbols=position.symbol)
                        snapshots = client_manager.option_data_client.get_option_snapshot(request)
                        
                        if position.symbol in snapshots and snapshots[position.symbol].greeks:
                            greeks = snapshots[position.symbol].greeks
                            option_delta = greeks.delta * float(position.qty) * 100  # Contract multiplier
                            total_delta += option_delta
                            
                    except Exception as e:
                        logger.warning(f"Could not get delta for {position.symbol}: {e}")
                else:
                    # Stock position - delta = quantity
                    total_delta += float(position.qty)
            
            return total_delta
            
        except Exception as e:
            logger.error(f"Error calculating portfolio delta: {e}")
            return 0.0
    
    async def emergency_stop(self) -> Dict[str, any]:
        """Emergency stop - close all positions and cancel all orders.
        
        Returns:
            Summary of emergency stop actions
        """
        try:
            # Cancel all orders
            cancel_responses = client_manager.trading_client.cancel_orders()
            
            # Close all positions
            close_responses = client_manager.trading_client.close_all_positions(cancel_orders=False)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'orders_cancelled': len(cancel_responses) if cancel_responses else 0,
                'positions_closed': len(close_responses) if close_responses else 0,
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    async def _calculate_trade_cost(self, legs: List[Dict]) -> float:
        """Calculate estimated trade cost."""
        # Simplified cost calculation
        # In practice, you'd get current option prices
        total_cost = 0.0
        for leg in legs:
            # This is a placeholder - would need real option pricing
            total_cost += abs(leg.get('estimated_cost', 0.0))
        return total_cost
    
    async def _calculate_profit_loss(self, legs: List[Dict]) -> Tuple[float, float]:
        """Calculate max profit and loss for strategy."""
        # Simplified P&L calculation
        # This would depend on the specific strategy
        max_profit = sum(leg.get('max_profit', 0.0) for leg in legs)
        max_loss = sum(leg.get('max_loss', 0.0) for leg in legs)
        return max_profit, max_loss
    
    async def _calculate_delta_exposure(self, legs: List[Dict]) -> float:
        """Calculate total delta exposure for the trade."""
        total_delta = 0.0
        for leg in legs:
            delta = leg.get('delta', 0.0)
            quantity = leg.get('quantity', 0)
            side_multiplier = 1 if leg.get('side') == 'buy' else -1
            total_delta += delta * quantity * side_multiplier * 100  # Contract multiplier
        return total_delta
    
    async def _generate_risk_warnings(self, legs: List[Dict], cost: float) -> List[str]:
        """Generate risk warnings for the trade."""
        warnings = []
        
        # High cost warning
        if cost > 1000:
            warnings.append(f"High cost trade: ${cost:.2f}")
        
        # Multiple legs warning
        if len(legs) > 2:
            warnings.append("Complex multi-leg strategy")
        
        # Close to expiration warning
        for leg in legs:
            if 'expiration' in leg:
                # Add logic to check if close to expiration
                warnings.append("Trading 0DTE options - high time decay risk")
                break
        
        return warnings


# Global risk manager instance
risk_manager = RiskManager()