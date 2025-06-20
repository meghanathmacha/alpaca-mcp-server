"""In-memory option chain cache for 0DTE trading."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, time
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class OptionData:
    """Option contract data structure."""
    symbol: str
    bid: float
    ask: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    iv: float
    volume: int
    open_interest: int
    strike: float
    expiration: datetime
    option_type: str  # 'call' or 'put'
    timestamp: datetime


class OptionChainCache:
    """Thread-safe in-memory cache for 0DTE SPY option chains."""
    
    def __init__(self, auto_expire_time: str = "16:15"):
        """Initialize the option chain cache.
        
        Args:
            auto_expire_time: Time to auto-expire data (e.g., "16:15" for 4:15 PM ET)
        """
        self._cache: Dict[str, OptionData] = {}
        self._lock = asyncio.Lock()
        self._last_update = datetime.now()
        self._auto_expire_time = time.fromisoformat(auto_expire_time)
        
    async def update_chain(self, spy_options: List[OptionData]) -> None:
        """Thread-safe cache update.
        
        Args:
            spy_options: List of option data to update in cache
        """
        async with self._lock:
            # Check if we should auto-expire (past 4:15 PM ET)
            now = datetime.now()
            if now.time() > self._auto_expire_time:
                logger.info("Auto-expiring 0DTE option chain data")
                self._cache.clear()
                return
                
            # Update cache with new data
            for option in spy_options:
                self._cache[option.symbol] = option
                
            self._last_update = now
            logger.debug(f"Updated option chain cache with {len(spy_options)} contracts")
    
    async def get_by_symbol(self, symbol: str) -> Optional[OptionData]:
        """Get option data by symbol.
        
        Args:
            symbol: Option symbol
            
        Returns:
            Option data if found, None otherwise
        """
        async with self._lock:
            return self._cache.get(symbol)
    
    async def get_by_delta(self, target_delta: float, option_type: str, tolerance: float = 0.05) -> Optional[OptionData]:
        """Find option by target delta.
        
        Args:
            target_delta: Target delta value (e.g., 0.30 for 30-delta)
            option_type: 'call' or 'put'
            tolerance: Delta tolerance for matching (default: 0.05)
            
        Returns:
            Option data closest to target delta within tolerance
        """
        async with self._lock:
            best_match = None
            best_diff = float('inf')
            
            for option in self._cache.values():
                if option.option_type.lower() != option_type.lower():
                    continue
                    
                # For puts, use absolute delta for comparison
                option_delta = abs(option.delta) if option_type.lower() == 'put' else option.delta
                diff = abs(option_delta - target_delta)
                
                if diff <= tolerance and diff < best_diff:
                    best_diff = diff
                    best_match = option
                    
            return best_match
    
    async def get_by_strike_range(self, min_strike: float, max_strike: float, option_type: str) -> List[OptionData]:
        """Get options within a strike price range.
        
        Args:
            min_strike: Minimum strike price
            max_strike: Maximum strike price
            option_type: 'call' or 'put'
            
        Returns:
            List of options within the strike range
        """
        async with self._lock:
            matches = []
            for option in self._cache.values():
                if (option.option_type.lower() == option_type.lower() and
                    min_strike <= option.strike <= max_strike):
                    matches.append(option)
            
            # Sort by strike price
            matches.sort(key=lambda x: x.strike)
            return matches
    
    async def get_all_options(self, option_type: Optional[str] = None) -> List[OptionData]:
        """Get all cached options, optionally filtered by type.
        
        Args:
            option_type: Optional filter for 'call' or 'put'
            
        Returns:
            List of all cached options
        """
        async with self._lock:
            if option_type:
                return [opt for opt in self._cache.values() 
                       if opt.option_type.lower() == option_type.lower()]
            return list(self._cache.values())
    
    async def get_cache_stats(self) -> Dict[str, any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        async with self._lock:
            calls = sum(1 for opt in self._cache.values() if opt.option_type.lower() == 'call')
            puts = sum(1 for opt in self._cache.values() if opt.option_type.lower() == 'put')
            
            return {
                'total_contracts': len(self._cache),
                'calls': calls,
                'puts': puts,
                'last_update': self._last_update,
                'cache_age_seconds': (datetime.now() - self._last_update).total_seconds()
            }
    
    async def clear_expired(self) -> None:
        """Clear expired data (called automatically or manually)."""
        async with self._lock:
            now = datetime.now()
            if now.time() > self._auto_expire_time:
                expired_count = len(self._cache)
                self._cache.clear()
                logger.info(f"Cleared {expired_count} expired 0DTE contracts")


# Global cache instance
option_cache = OptionChainCache()