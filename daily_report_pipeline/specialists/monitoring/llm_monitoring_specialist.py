"""
LLM performance monitoring specialist for tracking LLM-specific metrics.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path

from .data_models import (
    Alert, AlertSeverity, LLMMetrics, Metric, MetricType,
    MetricValue, MonitoringConfig
)

class LLMPerformanceSpecialist:
    """Specialist for monitoring LLM performance and costs."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the LLM monitoring specialist."""
        self.metrics: Dict[str, Metric] = {}
        self.alerts: List[Alert] = []
        self.configs: Dict[str, MonitoringConfig] = {}
        self.last_alert_times: Dict[str, datetime] = {}
        
        # Initialize metrics
        self._initialize_metrics()
        
        # Load configurations
        if config_path:
            self._load_config(config_path)
        else:
            self._setup_default_config()

    def _initialize_metrics(self) -> None:
        """Initialize LLM metrics tracking."""
        self.metrics["llm_requests"] = Metric(
            name="llm_requests",
            type=MetricType.COUNTER,
            description="Total number of LLM requests"
        )
        self.metrics["llm_latency"] = Metric(
            name="llm_latency",
            type=MetricType.HISTOGRAM,
            description="LLM request latency in seconds"
        )
        self.metrics["llm_tokens"] = Metric(
            name="llm_tokens",
            type=MetricType.COUNTER,
            description="Total tokens used"
        )
        self.metrics["llm_cost"] = Metric(
            name="llm_cost",
            type=MetricType.COUNTER,
            description="Total cost in USD",
            unit="USD"
        )

    def _load_config(self, config_path: Path) -> None:
        """Load LLM monitoring configuration from file."""
        with open(config_path) as f:
            config_data = json.load(f)
        
        for metric_config in config_data.get("llm_metrics", []):
            self.configs[metric_config["name"]] = MonitoringConfig(**metric_config)

    def _setup_default_config(self) -> None:
        """Set up default LLM monitoring configuration."""
        self.configs["llm_error_rate"] = MonitoringConfig(
            metric_name="llm_error_rate",
            warning_threshold=5.0,
            error_threshold=10.0,
            critical_threshold=20.0
        )
        self.configs["llm_latency"] = MonitoringConfig(
            metric_name="llm_latency",
            warning_threshold=2.0,  # 2 seconds
            error_threshold=5.0,    # 5 seconds
            critical_threshold=10.0  # 10 seconds
        )
        self.configs["daily_cost"] = MonitoringConfig(
            metric_name="daily_cost",
            warning_threshold=50.0,   # $50
            error_threshold=100.0,    # $100
            critical_threshold=200.0   # $200
        )

    def track_request(
        self,
        success: bool,
        latency: float,
        tokens: int,
        cost: float,
        model: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Track an individual LLM request."""
        timestamp = timestamp or datetime.now()
        labels = {"model": model, "success": str(success)}

        # Update requests metric
        self.metrics["llm_requests"].values.append(
            MetricValue(1, timestamp, labels)
        )

        # Update latency metric
        self.metrics["llm_latency"].values.append(
            MetricValue(latency, timestamp, labels)
        )

        # Update tokens metric
        self.metrics["llm_tokens"].values.append(
            MetricValue(tokens, timestamp, labels)
        )

        # Update cost metric
        self.metrics["llm_cost"].values.append(
            MetricValue(cost, timestamp, labels)
        )

        # Check thresholds
        if latency > self.configs["llm_latency"].warning_threshold:
            self._create_alert(
                f"High LLM latency ({latency:.2f}s) for model {model}",
                AlertSeverity.WARNING,
                "llm_latency",
                self.configs["llm_latency"].warning_threshold,
                latency,
                timestamp
            )

    def collect_hourly_metrics(self) -> LLMMetrics:
        """Collect hourly LLM performance metrics."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)

        # Filter metrics for the last hour
        hourly_requests = [
            v for v in self.metrics["llm_requests"].values
            if v.timestamp > hour_ago
        ]
        hourly_latencies = [
            v for v in self.metrics["llm_latency"].values
            if v.timestamp > hour_ago
        ]
        hourly_tokens = [
            v for v in self.metrics["llm_tokens"].values
            if v.timestamp > hour_ago
        ]
        hourly_costs = [
            v for v in self.metrics["llm_cost"].values
            if v.timestamp > hour_ago
        ]

        # Calculate metrics
        total_requests = len(hourly_requests)
        successful_requests = len([
            r for r in hourly_requests
            if r.labels.get("success") == "True"
        ])
        failed_requests = total_requests - successful_requests
        
        average_latency = (
            sum(v.value for v in hourly_latencies) / len(hourly_latencies)
            if hourly_latencies else 0.0
        )
        
        total_tokens = sum(v.value for v in hourly_tokens)
        total_cost = sum(v.value for v in hourly_costs)

        metrics = LLMMetrics(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_latency=average_latency,
            total_tokens=total_tokens,
            total_cost=total_cost
        )

        self._check_hourly_thresholds(metrics)
        return metrics

    def _check_hourly_thresholds(self, metrics: LLMMetrics) -> None:
        """Check hourly metrics against thresholds."""
        if metrics.total_requests > 0:
            error_rate = (metrics.failed_requests / metrics.total_requests) * 100
            if error_rate > self.configs["llm_error_rate"].warning_threshold:
                self._create_alert(
                    f"High LLM error rate: {error_rate:.1f}%",
                    AlertSeverity.WARNING,
                    "llm_error_rate",
                    self.configs["llm_error_rate"].warning_threshold,
                    error_rate,
                    datetime.now()
                )

        if metrics.total_cost > self.configs["daily_cost"].warning_threshold / 24:
            self._create_alert(
                f"High hourly LLM cost: ${metrics.total_cost:.2f}",
                AlertSeverity.WARNING,
                "hourly_cost",
                self.configs["daily_cost"].warning_threshold / 24,
                metrics.total_cost,
                datetime.now()
            )

    def _create_alert(
        self,
        message: str,
        severity: AlertSeverity,
        metric_name: str,
        threshold: float,
        current_value: float,
        timestamp: datetime
    ) -> None:
        """Create and store an alert if cooldown period has passed."""
        # Check alert cooldown
        last_alert = self.last_alert_times.get(f"{metric_name}_{severity.value}")
        if last_alert:
            config = self.configs.get(metric_name)
            cooldown = config.alert_cooldown if config else 3600
            if (timestamp - last_alert).total_seconds() < cooldown:
                return

        # Create and store alert
        alert = Alert(
            message=message,
            severity=severity,
            metric_name=metric_name,
            threshold=threshold,
            current_value=current_value,
            timestamp=timestamp
        )
        self.alerts.append(alert)
        self.last_alert_times[f"{metric_name}_{severity.value}"] = timestamp

    def get_active_alerts(self) -> List[Alert]:
        """Get all unresolved alerts."""
        return [alert for alert in self.alerts if not alert.resolved]

    def resolve_alert(self, alert: Alert) -> None:
        """Mark an alert as resolved."""
        alert.resolved = True
        alert.resolved_at = datetime.now()

    def export_metrics(self, export_path: Path) -> None:
        """Export collected metrics to file."""
        metrics_data = {
            name: {
                "type": metric.type.value,
                "description": metric.description,
                "unit": metric.unit,
                "values": [
                    {
                        "value": val.value,
                        "timestamp": val.timestamp.isoformat(),
                        "labels": val.labels
                    }
                    for val in metric.values
                ]
            }
            for name, metric in self.metrics.items()
        }

        with open(export_path, 'w') as f:
            json.dump(metrics_data, f, indent=2)
