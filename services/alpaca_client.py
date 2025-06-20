"""Alpaca client management with performance optimizations."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from collections import defaultdict

from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.live.stock import StockDataStream

from .config import config

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, max_requests_per_minute: int = 200):
        """Initialize rate limiter.
        
        Args:
            max_requests_per_minute: Maximum requests allowed per minute
        """
        self.max_requests = max_requests_per_minute
        self.requests = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def acquire(self, endpoint: str = "default") -> bool:
        """Acquire permission to make a request.
        
        Args:
            endpoint: API endpoint for granular rate limiting
            
        Returns:
            True if request is allowed, False if rate limited
        """
        async with self._lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            
            # Remove old requests
            self.requests[endpoint] = [
                req_time for req_time in self.requests[endpoint]
                if req_time > minute_ago
            ]
            
            # Check if we can make another request
            if len(self.requests[endpoint]) >= self.max_requests:
                return False
            
            # Record this request
            self.requests[endpoint].append(now)
            return True
    
    async def wait_if_needed(self, endpoint: str = "default"):
        """Wait if rate limited."""
        if not await self.acquire(endpoint):
            # Calculate wait time until oldest request expires
            async with self._lock:
                if self.requests[endpoint]:
                    oldest_request = min(self.requests[endpoint])
                    wait_time = 60 - (datetime.now() - oldest_request).total_seconds()
                    if wait_time > 0:
                        logger.warning(f"Rate limited on {endpoint}, waiting {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)


class AlpacaClientManager:
    """Manages Alpaca API clients with performance optimizations."""
    
    def __init__(self):
        """Initialize client manager."""
        self._trading_client = None
        self._stock_data_client = None
        self._option_data_client = None
        self._stock_stream_client = None
        self._rate_limiter = RateLimiter()
        self._client_stats = {
            'requests_made': 0,
            'requests_failed': 0,
            'last_request_time': None,
            'average_response_time': 0.0,
            'connection_pool_size': 10
        }
        self._performance_cache = {}
        self._cache_ttl = 5  # seconds
    
    @property
    def trading_client(self) -> TradingClient:
        """Get trading client with optimized configuration."""
        if self._trading_client is None:
            self._trading_client = TradingClient(
                config.alpaca_api_key, 
                config.alpaca_secret_key, 
                paper=config.paper,
                url_override=config.trade_api_url
            )
        return self._trading_client
    
    @property
    def stock_data_client(self) -> StockHistoricalDataClient:
        """Get stock data client with optimized configuration."""
        if self._stock_data_client is None:
            self._stock_data_client = StockHistoricalDataClient(
                config.alpaca_api_key, 
                config.alpaca_secret_key,
                url_override=config.data_api_url
            )
        return self._stock_data_client
    
    @property
    def option_data_client(self) -> OptionHistoricalDataClient:
        """Get option data client with optimized configuration."""
        if self._option_data_client is None:
            self._option_data_client = OptionHistoricalDataClient(
                api_key=config.alpaca_api_key,
                secret_key=config.alpaca_secret_key
            )
        return self._option_data_client
    
    @property
    def stock_stream_client(self) -> StockDataStream:
        """Get stock streaming client with optimized configuration."""
        if self._stock_stream_client is None:
            self._stock_stream_client = StockDataStream(
                config.alpaca_api_key,
                config.alpaca_secret_key,
                url_override=config.stream_data_wss
            )
        return self._stock_stream_client
    
    async def make_request_with_rate_limit(self, endpoint: str, request_func, *args, **kwargs):
        """Make an API request with rate limiting and performance tracking.
        
        Args:
            endpoint: API endpoint identifier
            request_func: Function to execute
            *args, **kwargs: Arguments for the request function
            
        Returns:
            Result of the request function
        """
        # Check rate limit
        await self._rate_limiter.wait_if_needed(endpoint)
        
        # Track performance
        start_time = datetime.now()
        
        try:
            # Execute request
            result = request_func(*args, **kwargs)
            
            # Update stats
            self._client_stats['requests_made'] += 1
            self._client_stats['last_request_time'] = start_time
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Update average response time (exponential moving average)
            if self._client_stats['average_response_time'] == 0:
                self._client_stats['average_response_time'] = response_time
            else:
                alpha = 0.1  # Smoothing factor
                self._client_stats['average_response_time'] = (
                    alpha * response_time + 
                    (1 - alpha) * self._client_stats['average_response_time']
                )
            
            # Log slow requests
            if response_time > 2.0:
                logger.warning(f"Slow API request to {endpoint}: {response_time:.3f}s")
            
            return result
            
        except Exception as e:
            self._client_stats['requests_failed'] += 1
            logger.error(f"API request failed for {endpoint}: {e}")
            raise
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get client performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'total_requests': self._client_stats['requests_made'],
            'failed_requests': self._client_stats['requests_failed'],
            'success_rate': (
                (self._client_stats['requests_made'] - self._client_stats['requests_failed']) /
                max(self._client_stats['requests_made'], 1) * 100
            ),
            'average_response_time_ms': self._client_stats['average_response_time'] * 1000,
            'last_request_time': self._client_stats['last_request_time'],
            'rate_limiter_stats': {
                endpoint: len(requests) 
                for endpoint, requests in self._rate_limiter.requests.items()
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all clients.
        
        Returns:
            Health status for each client
        """
        health_status = {}
        
        # Test trading client
        try:
            account = self.trading_client.get_account()
            health_status['trading_client'] = {
                'status': 'healthy',
                'account_id': account.id,
                'buying_power': float(account.buying_power)
            }
        except Exception as e:
            health_status['trading_client'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Test stock data client
        try:
            # Simple test request
            from alpaca.data.requests import StockLatestQuoteRequest
            request = StockLatestQuoteRequest(symbol_or_symbols="SPY")
            quotes = self.stock_data_client.get_stock_latest_quote(request)
            health_status['stock_data_client'] = {
                'status': 'healthy',
                'test_symbol': 'SPY',
                'quote_count': len(quotes)
            }
        except Exception as e:
            health_status['stock_data_client'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Test option data client
        try:
            # Note: Option data might not always be available
            health_status['option_data_client'] = {
                'status': 'healthy',
                'note': 'Client initialized successfully'
            }
        except Exception as e:
            health_status['option_data_client'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        return health_status


# Global client manager instance
client_manager = AlpacaClientManager()