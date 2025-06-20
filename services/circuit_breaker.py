"""Circuit breaker implementation for API failure protection."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Circuit is open, failing fast
    HALF_OPEN = "half_open" # Testing if service has recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5          # Number of failures to trigger open
    recovery_timeout: int = 60          # Seconds before trying half-open
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout_duration: float = 30.0     # Request timeout in seconds


class CircuitBreaker:
    """Circuit breaker for protecting against cascading failures."""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        """Initialize circuit breaker.
        
        Args:
            name: Identifier for this circuit breaker
            config: Configuration settings
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        
        self._lock = asyncio.Lock()
        
        logger.info(f"Circuit breaker '{name}' initialized")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpen: When circuit is open
            Exception: Original function exceptions
        """
        async with self._lock:
            await self._update_state()
            
            if self.state == CircuitState.OPEN:
                raise CircuitBreakerOpen(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Last failure: {self.last_failure_time}"
                )
        
        # Execute the function with timeout
        try:
            result = await asyncio.wait_for(
                self._execute_function(func, *args, **kwargs),
                timeout=self.config.timeout_duration
            )
            
            await self._record_success()
            return result
            
        except asyncio.TimeoutError:
            await self._record_failure("Timeout")
            raise CircuitBreakerTimeout(
                f"Function call timed out after {self.config.timeout_duration}s"
            )
        except Exception as e:
            await self._record_failure(str(e))
            raise
    
    async def _execute_function(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function, handling both sync and async functions."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    
    async def _update_state(self):
        """Update circuit breaker state based on current conditions."""
        now = datetime.now()
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if (self.last_failure_time and 
                now - self.last_failure_time >= timedelta(seconds=self.config.recovery_timeout)):
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info(f"Circuit breaker '{self.name}' moved to HALF_OPEN")
    
    async def _record_success(self):
        """Record a successful operation."""
        async with self._lock:
            self.last_success_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    logger.info(f"Circuit breaker '{self.name}' CLOSED after recovery")
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0
    
    async def _record_failure(self, error_msg: str):
        """Record a failed operation.
        
        Args:
            error_msg: Error message describing the failure
        """
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            logger.warning(
                f"Circuit breaker '{self.name}' failure {self.failure_count}: {error_msg}"
            )
            
            if (self.state == CircuitState.CLOSED and 
                self.failure_count >= self.config.failure_threshold):
                self.state = CircuitState.OPEN
                logger.error(
                    f"Circuit breaker '{self.name}' OPENED after {self.failure_count} failures"
                )
            elif self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open state reopens the circuit
                self.state = CircuitState.OPEN
                logger.error(f"Circuit breaker '{self.name}' reopened during recovery test")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics.
        
        Returns:
            Dictionary with current statistics
        """
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'last_success_time': self.last_success_time.isoformat() if self.last_success_time else None,
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout,
                'success_threshold': self.config.success_threshold,
                'timeout_duration': self.config.timeout_duration
            }
        }
    
    async def reset(self):
        """Manually reset circuit breaker to closed state."""
        async with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            logger.info(f"Circuit breaker '{self.name}' manually reset")


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreakerTimeout(Exception):
    """Exception raised when function call times out."""
    pass


class CircuitBreakerManager:
    """Manages multiple circuit breakers for different services."""
    
    def __init__(self):
        """Initialize circuit breaker manager."""
        self.breakers: Dict[str, CircuitBreaker] = {}
        
        # Create default circuit breakers for different services
        self._create_default_breakers()
    
    def _create_default_breakers(self):
        """Create default circuit breakers for API endpoints."""
        # Trading API circuit breaker
        self.breakers['trading_api'] = CircuitBreaker(
            'trading_api',
            CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30,
                success_threshold=2,
                timeout_duration=15.0
            )
        )
        
        # Market data API circuit breaker
        self.breakers['market_data'] = CircuitBreaker(
            'market_data',
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=20,
                success_threshold=3,
                timeout_duration=10.0
            )
        )
        
        # Option data API circuit breaker
        self.breakers['option_data'] = CircuitBreaker(
            'option_data',
            CircuitBreakerConfig(
                failure_threshold=4,
                recovery_timeout=25,
                success_threshold=2,
                timeout_duration=12.0
            )
        )
    
    def get_breaker(self, name: str) -> CircuitBreaker:
        """Get circuit breaker by name.
        
        Args:
            name: Circuit breaker name
            
        Returns:
            CircuitBreaker instance
        """
        if name not in self.breakers:
            # Create new circuit breaker with default config
            self.breakers[name] = CircuitBreaker(name)
        
        return self.breakers[name]
    
    async def protected_call(self, breaker_name: str, func: Callable, *args, **kwargs) -> Any:
        """Make a protected API call using specified circuit breaker.
        
        Args:
            breaker_name: Name of circuit breaker to use
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
        """
        breaker = self.get_breaker(breaker_name)
        return await breaker.call(func, *args, **kwargs)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers.
        
        Returns:
            Dictionary mapping breaker names to their statistics
        """
        return {name: breaker.get_stats() for name, breaker in self.breakers.items()}
    
    async def reset_all(self):
        """Reset all circuit breakers."""
        for breaker in self.breakers.values():
            await breaker.reset()
        logger.info("All circuit breakers reset")


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()