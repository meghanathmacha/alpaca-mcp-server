"""Alpaca client management for MCP server."""

from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.live.stock import StockDataStream

from .config import config


class AlpacaClientManager:
    """Manages all Alpaca API clients."""
    
    def __init__(self):
        """Initialize all Alpaca clients."""
        self._trading_client = None
        self._stock_data_client = None
        self._option_data_client = None
        self._stock_stream_client = None
    
    @property
    def trading_client(self) -> TradingClient:
        """Get trading client (lazy initialization)."""
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
        """Get stock historical data client (lazy initialization)."""
        if self._stock_data_client is None:
            self._stock_data_client = StockHistoricalDataClient(
                config.alpaca_api_key, 
                config.alpaca_secret_key,
                url_override=config.data_api_url
            )
        return self._stock_data_client
    
    @property
    def option_data_client(self) -> OptionHistoricalDataClient:
        """Get option historical data client (lazy initialization)."""
        if self._option_data_client is None:
            self._option_data_client = OptionHistoricalDataClient(
                api_key=config.alpaca_api_key,
                secret_key=config.alpaca_secret_key
            )
        return self._option_data_client
    
    @property
    def stock_stream_client(self) -> StockDataStream:
        """Get stock streaming client (lazy initialization)."""
        if self._stock_stream_client is None:
            self._stock_stream_client = StockDataStream(
                config.alpaca_api_key,
                config.alpaca_secret_key,
                url_override=config.stream_data_wss
            )
        return self._stock_stream_client


# Global client manager instance
client_manager = AlpacaClientManager()