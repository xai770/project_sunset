"""
Performance monitoring specialist for tracking system metrics and generating alerts.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psutil
import json
from pathlib import Path

from .data_models import (
    Alert, AlertSeverity, Metric, MetricType, MetricValue,
    MonitoringConfig, ResourceMetrics, PipelineMetrics, LLMMetrics
)

class PerformanceMonitoringSpecialist:
    """Specialist for monitoring system and pipeline performance."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the monitoring specialist."""
        self.metrics: Dict[str, Metric] = {}
        self.alerts: List[Alert] = []
        self.configs: Dict[str, MonitoringConfig] = {}
        self.last_alert_times: Dict[str, datetime] = {}
        
        # Load configurations
        if config_path:
            self._load_config(config_path)
        else:
            self._setup_default_config()

    def _load_config(self, config_path: Path) -> None:
        """Load monitoring configuration from file."""
        with open(config_path) as f:
            config_data = json.load(f)
        
        for metric_config in config_data["metrics"]:
            self.configs[metric_config["name"]] = MonitoringConfig(**metric_config)

    def _setup_default_config(self) -> None:
        """Set up default monitoring configuration."""
        self.configs["cpu_usage"] = MonitoringConfig(
            metric_name="cpu_usage",
            warning_threshold=70.0,
            error_threshold=85.0,
            critical_threshold=95.0
        )
        self.configs["memory_usage"] = MonitoringConfig(
            metric_name="memory_usage",
            warning_threshold=70.0,
            error_threshold=85.0,
            critical_threshold=95.0
        )
        self.configs["pipeline_error_rate"] = MonitoringConfig(
            metric_name="pipeline_error_rate",
            warning_threshold=5.0,
            error_threshold=10.0,
            critical_threshold=20.0
        )

    def collect_resource_metrics(self) -> ResourceMetrics:
        """Collect system resource metrics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()

        metrics = ResourceMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_usage_percent=disk.percent,
            network_bytes_sent=net_io.bytes_sent,
            network_bytes_received=net_io.bytes_recv
        )

        self._check_resource_thresholds(metrics)
        return metrics

    def collect_pipeline_metrics(self, stats: Dict[str, int]) -> PipelineMetrics:
        """Collect pipeline performance metrics."""
        metrics = PipelineMetrics(
            total_jobs=stats.get("total_jobs", 0),
            processed_jobs=stats.get("processed_jobs", 0),
            failed_jobs=stats.get("failed_jobs", 0),
            processing_time=stats.get("processing_time", 0.0)
        )

        self._check_pipeline_thresholds(metrics)
        return metrics

    def collect_llm_metrics(self, stats: Dict[str, float]) -> LLMMetrics:
        """Collect LLM-specific metrics."""
        metrics = LLMMetrics(
            total_requests=stats.get("total_requests", 0),
            successful_requests=stats.get("successful_requests", 0),
            failed_requests=stats.get("failed_requests", 0),
            average_latency=stats.get("average_latency", 0.0),
            total_tokens=stats.get("total_tokens", 0),
            total_cost=stats.get("total_cost", 0.0)
        )

        self._check_llm_thresholds(metrics)
        return metrics

    def _check_resource_thresholds(self, metrics: ResourceMetrics) -> None:
        """Check resource metrics against thresholds and generate alerts."""
        # CPU Usage
        self._check_threshold(
            "cpu_usage",
            metrics.cpu_percent,
            "CPU usage is high",
            timestamp=metrics.timestamp
        )

        # Memory Usage
        self._check_threshold(
            "memory_usage",
            metrics.memory_percent,
            "Memory usage is high",
            timestamp=metrics.timestamp
        )

        # Disk Usage
        if metrics.disk_usage_percent > 90:
            self._create_alert(
                "Disk usage above 90%",
                AlertSeverity.ERROR,
                "disk_usage",
                90.0,
                metrics.disk_usage_percent,
                metrics.timestamp
            )

    def _check_pipeline_thresholds(self, metrics: PipelineMetrics) -> None:
        """Check pipeline metrics against thresholds and generate alerts."""
        if metrics.total_jobs > 0:
            error_rate = (metrics.failed_jobs / metrics.total_jobs) * 100
            self._check_threshold(
                "pipeline_error_rate",
                error_rate,
                "Pipeline error rate is high",
                timestamp=metrics.timestamp
            )

        if metrics.processing_time > 300:  # 5 minutes
            self._create_alert(
                "Pipeline processing time exceeds 5 minutes",
                AlertSeverity.WARNING,
                "processing_time",
                300.0,
                metrics.processing_time,
                metrics.timestamp
            )

    def _check_llm_thresholds(self, metrics: LLMMetrics) -> None:
        """Check LLM metrics against thresholds and generate alerts."""
        if metrics.total_requests > 0:
            error_rate = (metrics.failed_requests / metrics.total_requests) * 100
            if error_rate > 10:
                self._create_alert(
                    "LLM error rate above 10%",
                    AlertSeverity.ERROR,
                    "llm_error_rate",
                    10.0,
                    error_rate,
                    metrics.timestamp
                )

        if metrics.average_latency > 2.0:  # 2 seconds
            self._create_alert(
                "LLM average latency above 2 seconds",
                AlertSeverity.WARNING,
                "llm_latency",
                2.0,
                metrics.average_latency,
                metrics.timestamp
            )

    def _check_threshold(
        self,
        metric_name: str,
        value: float,
        message_prefix: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Check a value against configured thresholds."""
        if metric_name not in self.configs:
            return

        config = self.configs[metric_name]
        timestamp = timestamp or datetime.now()

        if (config.critical_threshold is not None and 
            value >= config.critical_threshold):
            self._create_alert(
                f"{message_prefix} (CRITICAL)",
                AlertSeverity.CRITICAL,
                metric_name,
                config.critical_threshold,
                value,
                timestamp
            )
        elif (config.error_threshold is not None and 
              value >= config.error_threshold):
            self._create_alert(
                f"{message_prefix} (ERROR)",
                AlertSeverity.ERROR,
                metric_name,
                config.error_threshold,
                value,
                timestamp
            )
        elif (config.warning_threshold is not None and 
              value >= config.warning_threshold):
            self._create_alert(
                f"{message_prefix} (WARNING)",
                AlertSeverity.WARNING,
                metric_name,
                config.warning_threshold,
                value,
                timestamp
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
