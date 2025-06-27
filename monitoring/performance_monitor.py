#!/usr/bin/env python3
"""
Phase 4 Continuous Performance Monitoring System
===============================================

Real-time performance monitoring and regression detection system for 
Project Sunset's Phase 3 architecture optimization.

Features:
- Real-time performance tracking
- Automated regression detection
- Performance alerts and notifications
- Historical trend analysis
"""

import sys
import os
import time
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import statistics
import logging

# Add sandy to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/performance_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PerformanceMonitor")

@dataclass
class PerformanceThreshold:
    """Performance threshold configuration"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    unit: str
    trend_window: int = 10  # Number of measurements for trend analysis

@dataclass
class PerformanceAlert:
    """Performance alert data structure"""
    alert_id: str
    timestamp: str
    metric_name: str
    current_value: float
    threshold_value: float
    severity: str  # "warning" or "critical"
    message: str

class PerformanceMonitor:
    """Continuous performance monitoring system"""
    
    def __init__(self):
        self.monitoring_dir = Path("monitoring")
        self.monitoring_dir.mkdir(exist_ok=True)
        
        self.performance_data: List[Dict[str, Any]] = []
        self.alerts: List[PerformanceAlert] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Define performance thresholds
        self.thresholds = {
            "initialization_time": PerformanceThreshold(
                metric_name="initialization_time",
                warning_threshold=0.050,  # 50ms
                critical_threshold=0.100,  # 100ms
                unit="seconds"
            ),
            "evaluation_time": PerformanceThreshold(
                metric_name="evaluation_time",
                warning_threshold=30.0,  # 30 seconds
                critical_threshold=60.0,  # 60 seconds
                unit="seconds"
            ),
            "memory_usage": PerformanceThreshold(
                metric_name="memory_usage",
                warning_threshold=500 * 1024 * 1024,  # 500MB
                critical_threshold=1024 * 1024 * 1024,  # 1GB
                unit="bytes"
            ),
            "error_rate": PerformanceThreshold(
                metric_name="error_rate",
                warning_threshold=0.05,  # 5%
                critical_threshold=0.10,  # 10%
                unit="percentage"
            )
        }
        
        logger.info("🔍 Performance Monitor initialized")
    
    def measure_performance_metrics(self) -> Dict[str, Any]:
        """Measure current performance metrics"""
        try:
            from run_pipeline.core.direct_specialist_manager import get_job_matching_specialists
            import psutil
            import tracemalloc
            
            # Start memory tracing
            tracemalloc.start()
            process = psutil.Process()
            
            # Measure initialization time
            init_start = time.perf_counter()
            specialists = get_job_matching_specialists()
            init_time = time.perf_counter() - init_start
            
            # Measure evaluation time
            cv_data = {"text": "Performance monitoring test CV"}
            job_data = {"description": "Performance monitoring test job"}
            
            eval_start = time.perf_counter()
            result = specialists.evaluate_job_fitness(cv_data, job_data)
            eval_time = time.perf_counter() - eval_start
            
            # Memory metrics
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            memory_info = process.memory_info()
            
            # CPU metrics
            cpu_percent = process.cpu_percent()
            
            tracemalloc.stop()
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "initialization_time": init_time,
                "evaluation_time": eval_time,
                "memory_usage": peak_memory,
                "rss_memory": memory_info.rss,
                "cpu_percent": cpu_percent,
                "evaluation_success": result.success,
                "specialist_used": result.specialist_used,
                "error_occurred": False
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error measuring performance: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error_occurred": True,
                "error_message": str(e)
            }
    
    def check_thresholds(self, metrics: Dict[str, Any]) -> List[PerformanceAlert]:
        """Check if metrics exceed defined thresholds"""
        alerts = []
        
        for metric_name, threshold in self.thresholds.items():
            if metric_name in metrics and not metrics.get("error_occurred", False):
                current_value = metrics[metric_name]
                
                # Check critical threshold
                if current_value > threshold.critical_threshold:
                    alert = PerformanceAlert(
                        alert_id=f"{metric_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        timestamp=datetime.now().isoformat(),
                        metric_name=metric_name,
                        current_value=current_value,
                        threshold_value=threshold.critical_threshold,
                        severity="critical",
                        message=f"Critical: {metric_name} exceeded threshold: {current_value:.6f} > {threshold.critical_threshold} {threshold.unit}"
                    )
                    alerts.append(alert)
                    logger.critical(alert.message)
                
                # Check warning threshold
                elif current_value > threshold.warning_threshold:
                    alert = PerformanceAlert(
                        alert_id=f"{metric_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        timestamp=datetime.now().isoformat(),
                        metric_name=metric_name,
                        current_value=current_value,
                        threshold_value=threshold.warning_threshold,
                        severity="warning",
                        message=f"Warning: {metric_name} exceeded threshold: {current_value:.6f} > {threshold.warning_threshold} {threshold.unit}"
                    )
                    alerts.append(alert)
                    logger.warning(alert.message)
        
        return alerts
    
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if len(self.performance_data) < 5:
            return {"status": "insufficient_data", "message": "Need at least 5 data points for trend analysis"}
        
        # Get recent data points
        recent_data = self.performance_data[-10:]  # Last 10 measurements
        
        trends = {}
        
        for metric_name in ["initialization_time", "evaluation_time", "memory_usage"]:
            values = [data[metric_name] for data in recent_data if metric_name in data and not data.get("error_occurred")]
            
            if len(values) >= 3:
                # Calculate trend
                recent_avg = statistics.mean(values[-3:])  # Last 3 values
                earlier_avg = statistics.mean(values[:-3])  # Earlier values
                
                trend_direction = "increasing" if recent_avg > earlier_avg else "decreasing"
                trend_magnitude = abs(recent_avg - earlier_avg) / earlier_avg * 100
                
                trends[metric_name] = {
                    "direction": trend_direction,
                    "magnitude_percent": trend_magnitude,
                    "recent_average": recent_avg,
                    "earlier_average": earlier_avg,
                    "current_value": values[-1]
                }
        
        return trends
    
    def save_monitoring_data(self):
        """Save monitoring data to disk"""
        # Save performance data
        data_file = self.monitoring_dir / "performance_data.json"
        with open(data_file, 'w') as f:
            json.dump(self.performance_data, f, indent=2)
        
        # Save alerts
        alerts_file = self.monitoring_dir / "performance_alerts.json"
        alerts_data = [asdict(alert) for alert in self.alerts]
        with open(alerts_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        if not self.performance_data:
            return {"status": "no_data", "message": "No performance data available"}
        
        # Calculate summary statistics
        recent_data = [d for d in self.performance_data if not d.get("error_occurred")]
        
        if not recent_data:
            return {"status": "no_valid_data", "message": "No valid performance data available"}
        
        summary = {
            "monitoring_period": {
                "start": self.performance_data[0]["timestamp"],
                "end": self.performance_data[-1]["timestamp"],
                "total_measurements": len(self.performance_data),
                "valid_measurements": len(recent_data)
            },
            "performance_summary": {},
            "alerts_summary": {
                "total_alerts": len(self.alerts),
                "critical_alerts": len([a for a in self.alerts if a.severity == "critical"]),
                "warning_alerts": len([a for a in self.alerts if a.severity == "warning"])
            },
            "trends": self.analyze_performance_trends()
        }
        
        # Calculate performance statistics
        for metric_name in ["initialization_time", "evaluation_time", "memory_usage"]:
            values = [d[metric_name] for d in recent_data if metric_name in d]
            
            if values:
                summary["performance_summary"][metric_name] = {
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values),
                    "current": values[-1]
                }
        
        return summary
    
    def start_monitoring(self, interval: int = 60):
        """Start continuous performance monitoring"""
        if self.is_monitoring:
            logger.warning("⚠️ Monitoring already running")
            return
        
        self.is_monitoring = True
        logger.info(f"🚀 Starting continuous performance monitoring (interval: {interval}s)")
        
        def monitor_loop():
            while self.is_monitoring:
                try:
                    # Measure performance
                    metrics = self.measure_performance_metrics()
                    self.performance_data.append(metrics)
                    
                    # Check thresholds
                    new_alerts = self.check_thresholds(metrics)
                    self.alerts.extend(new_alerts)
                    
                    # Log current status
                    if not metrics.get("error_occurred"):
                        logger.info(f"📊 Performance check: "
                                  f"init={metrics['initialization_time']:.6f}s, "
                                  f"eval={metrics['evaluation_time']:.3f}s, "
                                  f"mem={metrics['memory_usage']/1024/1024:.1f}MB")
                    
                    # Save data periodically
                    if len(self.performance_data) % 10 == 0:
                        self.save_monitoring_data()
                    
                    # Wait for next measurement
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"❌ Monitoring error: {e}")
                    time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop continuous performance monitoring"""
        if not self.is_monitoring:
            logger.warning("⚠️ Monitoring not running")
            return
        
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        # Save final data
        self.save_monitoring_data()
        
        # Generate final report
        report = self.generate_monitoring_report()
        report_file = self.monitoring_dir / f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"🛑 Performance monitoring stopped. Report saved: {report_file}")
        return report

def main():
    """Main execution function for testing"""
    monitor = PerformanceMonitor()
    
    print("🔍 Performance Monitor Test Run")
    print("=" * 40)
    
    # Run a few measurements
    for i in range(3):
        print(f"📊 Measurement {i+1}/3")
        metrics = monitor.measure_performance_metrics()
        monitor.performance_data.append(metrics)
        
        alerts = monitor.check_thresholds(metrics)
        monitor.alerts.extend(alerts)
        
        if not metrics.get("error_occurred"):
            print(f"⚡ Init: {metrics['initialization_time']:.6f}s")
            print(f"⚡ Eval: {metrics['evaluation_time']:.3f}s")
            print(f"🧠 Memory: {metrics['memory_usage']/1024/1024:.1f}MB")
        
        time.sleep(2)
    
    # Generate report
    report = monitor.generate_monitoring_report()
    print("\n📋 Monitoring Report Generated")
    print(f"✅ Valid measurements: {report.get('monitoring_period', {}).get('valid_measurements', 0)}")
    print(f"⚠️ Total alerts: {report.get('alerts_summary', {}).get('total_alerts', 0)}")
    
    return report

if __name__ == "__main__":
    results = main()
