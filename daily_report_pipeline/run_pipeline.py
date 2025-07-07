#!/usr/bin/env python3
"""
Daily Report Pipeline Runner
===========================

Executes the daily report pipeline with comprehensive monitoring and error handling.
"""

import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from daily_report_pipeline.specialists.cv_matching import CVMatchingSpecialist
from daily_report_pipeline.specialists.monitoring import (
    PerformanceMonitoringSpecialist,
    LLMPerformanceSpecialist
)

class PipelineRunner:
    """Manages the execution of the daily report pipeline."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize pipeline components."""
        self.start_time = datetime.now()
        self.setup_logging()
        
        # Initialize specialists
        self.cv_matcher = CVMatchingSpecialist()
        self.perf_monitor = PerformanceMonitoringSpecialist(config_path)
        self.llm_monitor = LLMPerformanceSpecialist(config_path)
        
        self.logger = logging.getLogger(__name__)
        self.stats: Dict[str, Any] = {
            "total_jobs": 0,
            "processed_jobs": 0,
            "failed_jobs": 0,
            "processing_time": 0.0
        }

    def setup_logging(self) -> None:
        """Configure logging with proper formatting."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def run(self) -> bool:
        """Execute the daily report pipeline with monitoring."""
        try:
            self.logger.info("Starting daily report pipeline")
            
            # Start monitoring
            resource_metrics = self.perf_monitor.collect_resource_metrics()
            self.logger.info(f"Initial resource metrics: CPU {resource_metrics.cpu_percent}%, "
                           f"Memory {resource_metrics.memory_percent}%")

            # Process CVs and jobs
            success = self._process_matching()
            if not success:
                return False

            # Collect final metrics
            pipeline_metrics = self.perf_monitor.collect_pipeline_metrics(self.stats)
            llm_metrics = self.llm_monitor.collect_hourly_metrics()
            
            # Generate reports
            self._generate_reports(pipeline_metrics, llm_metrics)
            
            # Check for any critical alerts
            if self._check_alerts():
                self.logger.warning("Completed with alerts - check monitoring logs")
                return False

            self.logger.info("Pipeline completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            return False

    def _process_matching(self) -> bool:
        """Process CV matching with monitoring."""
        try:
            # TODO: Implement actual CV and job processing logic
            self.logger.info("Processing CVs and jobs")
            return True
        except Exception as e:
            self.logger.error(f"Matching process failed: {str(e)}", exc_info=True)
            return False

    def _generate_reports(self, pipeline_metrics, llm_metrics) -> None:
        """Generate pipeline execution reports."""
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        
        # TODO: Implement report generation
        self.logger.info("Generating reports")

    def _check_alerts(self) -> bool:
        """Check for any critical monitoring alerts."""
        perf_alerts = self.perf_monitor.get_active_alerts()
        llm_alerts = self.llm_monitor.get_active_alerts()
        
        critical_alerts = [
            alert for alert in perf_alerts + llm_alerts
            if alert.severity in ("error", "critical")
        ]
        
        for alert in critical_alerts:
            self.logger.error(f"Critical alert: {alert.message}")
        
        return bool(critical_alerts)

def main() -> int:
    """Main entry point for the pipeline."""
    config_path = Path("config/pipeline_config.json")
    runner = PipelineRunner(config_path)
    
    success = runner.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
