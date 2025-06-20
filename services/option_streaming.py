"""Real-time option chain streaming for 0DTE SPY options."""

import asyncio
import logging
from datetime import datetime, time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

from alpaca.data.requests import OptionSnapshotRequest
from alpaca.data.live.option import OptionDataStream

from .config import config
from .alpaca_client import client_manager
from .option_chain_cache import option_cache, OptionData

logger = logging.getLogger(__name__)


@dataclass
class StreamingConfig:
    """Configuration for option chain streaming."""
    update_interval: float = 0.5  # seconds - optimized for <1s latency
    batch_size: int = 50  # smaller batches for faster processing
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    auto_reconnect: bool = True
    concurrent_requests: int = 3  # parallel API calls
    cache_warmup_enabled: bool = True


class OptionChainStreamer:
    """Real-time streaming of 0DTE SPY option chains."""
    
    def __init__(self, streaming_config: StreamingConfig = None):
        """Initialize the option chain streamer.
        
        Args:
            streaming_config: Configuration for streaming behavior
        """
        self.config = streaming_config or StreamingConfig()
        self._stream_client = None
        self._is_streaming = False
        self._stream_task = None
        self._current_symbols = set()
        self._last_update = datetime.now()
        self._retry_count = 0
        
        # Callbacks for real-time updates
        self._update_callbacks: List[Callable] = []
    
    def add_update_callback(self, callback: Callable[[List[OptionData]], None]):
        """Add a callback function to be called on option updates.
        
        Args:
            callback: Function to call with updated option data
        """
        self._update_callbacks.append(callback)
    
    def remove_update_callback(self, callback: Callable):
        """Remove a callback function."""
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)
    
    async def start_streaming(self, symbols: List[str] = None) -> bool:
        """Start streaming 0DTE SPY option chain data.
        
        Args:
            symbols: Optional list of specific option symbols to stream.
                    If None, will auto-discover 0DTE SPY options.
        
        Returns:
            bool: True if streaming started successfully
        """
        if self._is_streaming:
            logger.info("Option streaming already active")
            return True
        
        try:
            # Get symbols to stream
            if symbols is None:
                symbols = await self._discover_0dte_spy_symbols()
            
            if not symbols:
                logger.warning("No 0DTE SPY option symbols found for streaming")
                return False
            
            self._current_symbols = set(symbols)
            logger.info(f"Starting option streaming for {len(symbols)} symbols")
            
            # Start the streaming task
            self._stream_task = asyncio.create_task(self._streaming_loop())
            self._is_streaming = True
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start option streaming: {e}")
            return False
    
    async def stop_streaming(self):
        """Stop the option chain streaming."""
        if not self._is_streaming:
            return
        
        logger.info("Stopping option chain streaming")
        self._is_streaming = False
        
        if self._stream_task:
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass
        
        if self._stream_client:
            await self._stream_client.close()
            self._stream_client = None
        
        logger.info("Option streaming stopped")
    
    async def _streaming_loop(self):
        """Main streaming loop that fetches and updates option data."""
        while self._is_streaming:
            try:
                await self._update_option_chain()
                self._retry_count = 0  # Reset retry count on success
                
                # Wait for next update
                await asyncio.sleep(self.config.update_interval)
                
            except asyncio.CancelledError:
                logger.info("Streaming loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in streaming loop: {e}")
                
                # Handle retries
                self._retry_count += 1
                if self._retry_count >= self.config.max_retries:
                    if self.config.auto_reconnect:
                        logger.warning(f"Max retries reached, attempting reconnect in {self.config.retry_delay}s")
                        await asyncio.sleep(self.config.retry_delay)
                        self._retry_count = 0  # Reset for reconnection attempt
                    else:
                        logger.error("Max retries reached, stopping streaming")
                        self._is_streaming = False
                        break
                else:
                    await asyncio.sleep(self.config.retry_delay)
    
    async def _update_option_chain(self):
        """Fetch latest option data and update cache with optimized performance."""
        if not self._current_symbols:
            return
        
        start_time = datetime.now()
        
        try:
            # Use smaller batches for faster processing
            symbol_batches = [
                list(self._current_symbols)[i:i+self.config.batch_size] 
                for i in range(0, len(self._current_symbols), self.config.batch_size)
            ]
            
            # Process batches concurrently for better performance
            all_updates = []
            
            # Limit concurrent requests to avoid overwhelming API
            semaphore = asyncio.Semaphore(self.config.concurrent_requests)
            
            async def process_batch(symbols_batch):
                async with semaphore:
                    return await self._fetch_batch_data(symbols_batch)
            
            # Execute batches concurrently
            tasks = [process_batch(batch) for batch in symbol_batches]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect results and handle exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {result}")
                    continue
                all_updates.extend(result)
            
            if all_updates:
                # Update cache efficiently
                await option_cache.update_chain(all_updates)
                
                # Notify callbacks asynchronously
                callback_tasks = []
                for callback in self._update_callbacks:
                    callback_tasks.append(self._safe_callback(callback, all_updates))
                
                if callback_tasks:
                    await asyncio.gather(*callback_tasks, return_exceptions=True)
                
                self._last_update = datetime.now()
                
                # Performance monitoring
                update_duration = (self._last_update - start_time).total_seconds()
                logger.debug(f"Updated {len(all_updates)} contracts in {update_duration:.3f}s")
                
                # Warn if update takes too long
                if update_duration > 0.8:  # 800ms warning threshold
                    logger.warning(f"Slow option chain update: {update_duration:.3f}s")
            
        except Exception as e:
            logger.error(f"Error updating option chain: {e}")
            raise
    
    async def _fetch_batch_data(self, symbols_batch: List[str]) -> List[OptionData]:
        """Fetch option data for a batch of symbols."""
        try:
            # Get option snapshots
            request = OptionSnapshotRequest(symbol_or_symbols=symbols_batch)
            snapshots = client_manager.option_data_client.get_option_snapshot(request)
            
            # Convert to OptionData objects
            batch_updates = []
            for symbol, snapshot in snapshots.items():
                if snapshot and snapshot.latest_quote:
                    quote = snapshot.latest_quote
                    greeks = snapshot.greeks
                    
                    # Parse option symbol to get strike and type
                    strike, option_type = self._parse_option_symbol(symbol)
                    
                    option_data = OptionData(
                        symbol=symbol,
                        bid=quote.bid_price,
                        ask=quote.ask_price,
                        delta=greeks.delta if greeks else 0.0,
                        gamma=greeks.gamma if greeks else 0.0,
                        theta=greeks.theta if greeks else 0.0,
                        vega=greeks.vega if greeks else 0.0,
                        rho=greeks.rho if greeks else 0.0,
                        iv=snapshot.implied_volatility or 0.0,
                        volume=snapshot.latest_trade.size if snapshot.latest_trade else 0,
                        open_interest=getattr(snapshot, 'open_interest', 0),
                        strike=strike,
                        expiration=datetime.now().replace(hour=16, minute=0, second=0, microsecond=0),  # 0DTE
                        option_type=option_type,
                        timestamp=datetime.now()
                    )
                    
                    batch_updates.append(option_data)
            
            return batch_updates
            
        except Exception as e:
            logger.error(f"Error fetching batch data: {e}")
            return []
    
    async def _safe_callback(self, callback: Callable, data: List[OptionData]):
        """Safely execute callback without blocking main update loop."""
        try:
            await callback(data)
        except Exception as e:
            logger.error(f"Error in update callback: {e}")
    
    async def _discover_0dte_spy_symbols(self) -> List[str]:
        """Discover 0DTE SPY option symbols for streaming.
        
        Returns:
            List of option symbols expiring today
        """
        try:
            # Get 0DTE option contracts for SPY
            from alpaca.trading.requests import GetOptionContractsRequest
            from datetime import date
            
            today = date.today()
            request = GetOptionContractsRequest(
                underlying_symbols=['SPY'],
                expiration_date=today,
                status='active'
            )
            
            response = client_manager.trading_client.get_option_contracts(request)
            
            symbols = []
            if response and response.option_contracts:
                for contract in response.option_contracts:
                    symbols.append(contract.symbol)
                
                logger.info(f"Discovered {len(symbols)} 0DTE SPY option symbols")
            else:
                logger.warning("No 0DTE SPY option contracts found")
            
            return symbols
            
        except Exception as e:
            logger.error(f"Error discovering 0DTE symbols: {e}")
            return []
    
    def _parse_option_symbol(self, symbol: str) -> tuple[float, str]:
        """Parse option symbol to extract strike price and type.
        
        Args:
            symbol: Option symbol (e.g., 'SPY250620C00450000')
            
        Returns:
            Tuple of (strike_price, option_type)
        """
        try:
            # SPY option symbol format: SPY[YYMMDD][C/P][00000000]
            # Last 8 digits are strike price * 1000
            if 'C' in symbol:
                option_type = 'call'
                strike_part = symbol.split('C')[1]
            elif 'P' in symbol:
                option_type = 'put'
                strike_part = symbol.split('P')[1]
            else:
                return 0.0, 'unknown'
            
            # Convert strike price (last 8 digits / 1000)
            strike_price = float(strike_part) / 1000
            
            return strike_price, option_type
            
        except Exception as e:
            logger.warning(f"Error parsing option symbol {symbol}: {e}")
            return 0.0, 'unknown'
    
    def get_streaming_status(self) -> Dict[str, any]:
        """Get current streaming status and statistics.
        
        Returns:
            Dictionary with streaming status information
        """
        return {
            'is_streaming': self._is_streaming,
            'symbols_count': len(self._current_symbols),
            'last_update': self._last_update.isoformat() if self._last_update else None,
            'retry_count': self._retry_count,
            'callbacks_count': len(self._update_callbacks),
            'update_interval': self.config.update_interval,
            'auto_reconnect': self.config.auto_reconnect
        }


# Global streaming instance
option_streamer = OptionChainStreamer()


# Convenience functions
async def start_spy_0dte_streaming() -> bool:
    """Start streaming 0DTE SPY options.
    
    Returns:
        bool: True if streaming started successfully
    """
    return await option_streamer.start_streaming()


async def stop_spy_0dte_streaming():
    """Stop streaming 0DTE SPY options."""
    await option_streamer.stop_streaming()


def add_streaming_callback(callback: Callable[[List[OptionData]], None]):
    """Add a callback for option updates."""
    option_streamer.add_update_callback(callback)


def get_streaming_status() -> Dict[str, any]:
    """Get current streaming status."""
    return option_streamer.get_streaming_status()