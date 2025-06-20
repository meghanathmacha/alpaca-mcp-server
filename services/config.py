"""Configuration management for Alpaca MCP Server."""

import os
from typing import Optional
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TradingConfig(BaseSettings):
    """Trading configuration with environment variable support."""
    
    # Alpaca API Configuration
    alpaca_api_key: str
    alpaca_secret_key: str
    paper: bool = True
    trade_api_url: Optional[str] = None
    trade_api_wss: Optional[str] = None
    data_api_url: Optional[str] = None
    stream_data_wss: Optional[str] = None
    
    # Risk Management
    max_daily_loss: float = 500.0
    portfolio_delta_cap: float = 50.0
    confirmation_timeout: int = 30
    
    # 0DTE Specific Configuration
    spy_chain_update_interval: int = 2
    auto_expire_time: str = "16:15"
    cache_cleanup_interval: int = 300
    
    # Monitoring
    prometheus_port: int = 9090
    s3_audit_bucket: Optional[str] = None
    pagerduty_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False
        
        # Map environment variables
        fields = {
            'alpaca_api_key': {'env': 'ALPACA_API_KEY'},
            'alpaca_secret_key': {'env': 'ALPACA_SECRET_KEY'},
            'paper': {'env': 'PAPER'},
            'trade_api_url': {'env': 'TRADE_API_URL'},
            'trade_api_wss': {'env': 'TRADE_API_WSS'},
            'data_api_url': {'env': 'DATA_API_URL'},
            'stream_data_wss': {'env': 'STREAM_DATA_WSS'},
            'max_daily_loss': {'env': 'MAX_DAILY_LOSS'},
            'portfolio_delta_cap': {'env': 'PORTFOLIO_DELTA_CAP'},
            'confirmation_timeout': {'env': 'CONFIRMATION_TIMEOUT'},
            'spy_chain_update_interval': {'env': 'SPY_CHAIN_UPDATE_INTERVAL'},
            'auto_expire_time': {'env': 'AUTO_EXPIRE_TIME'},
            'cache_cleanup_interval': {'env': 'CACHE_CLEANUP_INTERVAL'},
            'prometheus_port': {'env': 'PROMETHEUS_PORT'},
            's3_audit_bucket': {'env': 'S3_AUDIT_BUCKET'},
            'pagerduty_api_key': {'env': 'PAGERDUTY_API_KEY'},
        }

    def validate_required_fields(self):
        """Validate that required fields are present."""
        if not self.alpaca_api_key or not self.alpaca_secret_key:
            raise ValueError("Alpaca API credentials not found in environment variables.")


# Global config instance
config = TradingConfig()
config.validate_required_fields()