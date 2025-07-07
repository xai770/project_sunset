"""
Data models for monitoring system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(Enum):
    """Severity levels for alerts."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class MetricValue:
    """A single metric value."""
    value: Union[int, float]
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class Metric:
    """A metric with its metadata and values."""
    name: str
    type: MetricType
    description: str
    values: List[MetricValue] = field(default_factory=list)
    unit: Optional[str] = None

@dataclass
class Alert:
    """An alert generated from monitoring."""
    message: str
    severity: AlertSeverity
    metric_name: str
    threshold: float
    current_value: float
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class MonitoringConfig:
    """Configuration for monitoring thresholds and alerts."""
    metric_name: str
    warning_threshold: Optional[float] = None
    error_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    aggregation_window: int = 300  # 5 minutes in seconds
    alert_cooldown: int = 3600  # 1 hour in seconds

@dataclass
class ResourceMetrics:
    """Resource utilization metrics."""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_received: int
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PipelineMetrics:
    """Pipeline performance metrics."""
    total_jobs: int
    processed_jobs: int
    failed_jobs: int
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class LLMMetrics:
    """LLM-specific performance metrics."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_latency: float
    total_tokens: int
    total_cost: float
    timestamp: datetime = field(default_factory=datetime.now)
