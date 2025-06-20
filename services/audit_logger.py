"""Local audit logging service for trade records and system events."""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import asyncio
import aiofiles

from .config import config

logger = logging.getLogger(__name__)


@dataclass
class AuditEvent:
    """Audit event data structure."""
    timestamp: str
    event_type: str
    user_id: str
    session_id: str
    event_data: Dict[str, Any]
    risk_level: str = "low"
    source: str = "alpaca_mcp_server"


class LocalAuditLogger:
    """Local file-based audit logging for trade records and system events."""
    
    def __init__(self, log_directory: str = "audit_logs"):
        """Initialize audit logger.
        
        Args:
            log_directory: Directory to store audit logs
        """
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)
        
        # Create subdirectories for different log types
        (self.log_directory / "trades").mkdir(exist_ok=True)
        (self.log_directory / "risk_events").mkdir(exist_ok=True)
        (self.log_directory / "system_events").mkdir(exist_ok=True)
        (self.log_directory / "performance").mkdir(exist_ok=True)
        
        self._write_lock = asyncio.Lock()
        
        logger.info(f"Audit logger initialized: {self.log_directory}")
    
    async def log_trade_event(self, event_type: str, trade_data: Dict[str, Any], 
                             user_id: str = "system", session_id: str = "default") -> None:
        """Log trade-related events.
        
        Args:
            event_type: Type of trade event (preview, confirmation, execution, etc.)
            trade_data: Trade details and metadata
            user_id: User identifier
            session_id: Session identifier
        """
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type=f"trade.{event_type}",
            user_id=user_id,
            session_id=session_id,
            event_data=trade_data,
            risk_level=self._assess_trade_risk(trade_data)
        )
        
        await self._write_audit_log(event, "trades")
    
    async def log_risk_event(self, event_type: str, risk_data: Dict[str, Any],
                            user_id: str = "system", session_id: str = "default") -> None:
        """Log risk management events.
        
        Args:
            event_type: Type of risk event (violation, warning, limit_breach, etc.)
            risk_data: Risk details and metrics
            user_id: User identifier
            session_id: Session identifier
        """
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type=f"risk.{event_type}",
            user_id=user_id,
            session_id=session_id,
            event_data=risk_data,
            risk_level=self._assess_risk_level(risk_data)
        )
        
        await self._write_audit_log(event, "risk_events")
    
    async def log_system_event(self, event_type: str, system_data: Dict[str, Any],
                              user_id: str = "system", session_id: str = "default") -> None:
        """Log system events.
        
        Args:
            event_type: Type of system event (startup, shutdown, error, etc.)
            system_data: System details and metadata
            user_id: User identifier
            session_id: Session identifier
        """
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type=f"system.{event_type}",
            user_id=user_id,
            session_id=session_id,
            event_data=system_data,
            risk_level="low"
        )
        
        await self._write_audit_log(event, "system_events")
    
    async def log_performance_event(self, event_type: str, perf_data: Dict[str, Any],
                                   user_id: str = "system", session_id: str = "default") -> None:
        """Log performance events.
        
        Args:
            event_type: Type of performance event (latency, throughput, error_rate, etc.)
            perf_data: Performance metrics and details
            user_id: User identifier
            session_id: Session identifier
        """
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type=f"performance.{event_type}",
            user_id=user_id,
            session_id=session_id,
            event_data=perf_data,
            risk_level="low"
        )
        
        await self._write_audit_log(event, "performance")
    
    async def _write_audit_log(self, event: AuditEvent, log_type: str) -> None:
        """Write audit event to appropriate log file.
        
        Args:
            event: Audit event to log
            log_type: Type of log (trades, risk_events, system_events, performance)
        """
        try:
            async with self._write_lock:
                # Create filename with date for log rotation
                date_str = datetime.now().strftime("%Y-%m-%d")
                log_file = self.log_directory / log_type / f"{log_type}_{date_str}.jsonl"
                
                # Write event as JSON line
                event_json = json.dumps(asdict(event), default=str)
                
                async with aiofiles.open(log_file, mode='a') as f:
                    await f.write(event_json + '\n')
                
                # Log high-risk events to main logger as well
                if event.risk_level == "high":
                    logger.warning(f"High-risk audit event: {event.event_type} - {event.event_data}")
                    
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def _assess_trade_risk(self, trade_data: Dict[str, Any]) -> str:
        """Assess risk level of trade event.
        
        Args:
            trade_data: Trade data to assess
            
        Returns:
            Risk level: low, medium, high
        """
        try:
            cost = trade_data.get('cost', 0)
            max_loss = trade_data.get('max_loss', 0)
            
            # High risk criteria
            if cost > 1000 or abs(max_loss) > 500:
                return "high"
            elif cost > 500 or abs(max_loss) > 200:
                return "medium"
            else:
                return "low"
                
        except Exception:
            return "medium"  # Default to medium if we can't assess
    
    def _assess_risk_level(self, risk_data: Dict[str, Any]) -> str:
        """Assess risk level of risk event.
        
        Args:
            risk_data: Risk data to assess
            
        Returns:
            Risk level: low, medium, high
        """
        violations = risk_data.get('violations', [])
        daily_loss = risk_data.get('daily_loss', 0)
        
        if violations or abs(daily_loss) > config.max_daily_loss * 0.8:
            return "high"
        elif abs(daily_loss) > config.max_daily_loss * 0.5:
            return "medium"
        else:
            return "low"
    
    async def get_audit_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get audit log summary for the last N days.
        
        Args:
            days: Number of days to summarize
            
        Returns:
            Summary statistics
        """
        try:
            summary = {
                'period_days': days,
                'total_events': 0,
                'events_by_type': {},
                'events_by_risk': {'low': 0, 'medium': 0, 'high': 0},
                'trade_summary': {
                    'total_trades': 0,
                    'total_cost': 0.0,
                    'strategies_used': set()
                }
            }
            
            # Read recent log files
            end_date = datetime.now()
            for i in range(days):
                check_date = end_date - timedelta(days=i)
                date_str = check_date.strftime("%Y-%m-%d")
                
                # Check all log types
                for log_type in ['trades', 'risk_events', 'system_events', 'performance']:
                    log_file = self.log_directory / log_type / f"{log_type}_{date_str}.jsonl"
                    
                    if log_file.exists():
                        async with aiofiles.open(log_file, mode='r') as f:
                            async for line in f:
                                try:
                                    event_data = json.loads(line.strip())
                                    summary['total_events'] += 1
                                    
                                    event_type = event_data.get('event_type', 'unknown')
                                    risk_level = event_data.get('risk_level', 'low')
                                    
                                    summary['events_by_type'][event_type] = summary['events_by_type'].get(event_type, 0) + 1
                                    summary['events_by_risk'][risk_level] += 1
                                    
                                    # Trade-specific summary
                                    if event_type.startswith('trade.'):
                                        summary['trade_summary']['total_trades'] += 1
                                        trade_data = event_data.get('event_data', {})
                                        cost = trade_data.get('cost', 0)
                                        summary['trade_summary']['total_cost'] += cost
                                        
                                        strategy = trade_data.get('strategy')
                                        if strategy:
                                            summary['trade_summary']['strategies_used'].add(strategy)
                                            
                                except json.JSONDecodeError:
                                    continue
            
            # Convert set to list for JSON serialization
            summary['trade_summary']['strategies_used'] = list(summary['trade_summary']['strategies_used'])
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating audit summary: {e}")
            return {'error': str(e)}
    
    async def cleanup_old_logs(self, days_to_keep: int = 30) -> Dict[str, int]:
        """Clean up audit logs older than specified days.
        
        Args:
            days_to_keep: Number of days of logs to retain
            
        Returns:
            Cleanup statistics
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cleanup_stats = {'files_removed': 0, 'total_size_freed': 0}
            
            for log_type in ['trades', 'risk_events', 'system_events', 'performance']:
                log_dir = self.log_directory / log_type
                
                for log_file in log_dir.glob("*.jsonl"):
                    try:
                        # Extract date from filename
                        date_part = log_file.stem.split('_')[-1]
                        file_date = datetime.strptime(date_part, "%Y-%m-%d")
                        
                        if file_date < cutoff_date:
                            file_size = log_file.stat().st_size
                            log_file.unlink()
                            cleanup_stats['files_removed'] += 1
                            cleanup_stats['total_size_freed'] += file_size
                            
                    except (ValueError, OSError) as e:
                        logger.warning(f"Could not process log file {log_file}: {e}")
            
            logger.info(f"Cleaned up {cleanup_stats['files_removed']} old log files, freed {cleanup_stats['total_size_freed']} bytes")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Error during log cleanup: {e}")
            return {'error': str(e)}


# Global audit logger instance
audit_logger = LocalAuditLogger()