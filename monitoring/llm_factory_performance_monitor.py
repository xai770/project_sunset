#!/usr/bin/env python3
"""
LLM Factory Performance Monitoring System

Tracks quality improvements and performance metrics after LLM Factory integration.
This system establishes baseline metrics for ongoing improvement tracking.
"""
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('llm_factory_monitor')

@dataclass
class QualityMetric:
    """Quality metrics for LLM interactions"""
    timestamp: str
    component: str
    operation: str
    quality_score: float
    response_time: float
    success: bool
    model_used: str
    specialist_used: Optional[str] = None
    error_message: Optional[str] = None
    output_length: Optional[int] = None
    user_satisfaction: Optional[int] = None  # 1-5 rating if available

@dataclass
class PerformanceReport:
    """Performance report summary"""
    component: str
    total_operations: int
    success_rate: float
    avg_quality_score: float
    avg_response_time: float
    quality_improvement: Optional[float] = None
    speed_improvement: Optional[float] = None

class LLMFactoryPerformanceMonitor:
    """Monitor and track LLM Factory performance improvements"""
    
    def __init__(self, data_dir: str = "monitoring/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.data_dir / "llm_factory_metrics.jsonl"
        self.baseline_file = self.data_dir / "baseline_metrics.json"
        self.reports_file = self.data_dir / "performance_reports.json"
        
        self.baseline_metrics = self._load_baseline_metrics()
        
    def _load_baseline_metrics(self) -> Dict[str, Any]:
        """Load baseline metrics from before LLM Factory integration"""
        if self.baseline_file.exists():
            with open(self.baseline_file) as f:
                return json.load(f)  # type: ignore
        
        # Default baseline metrics (estimated from legacy system)
        return {
            "job_matching": {
                "quality_score": 0.65,  # 65% estimated quality
                "response_time": 15.0,  # 15 seconds average
                "success_rate": 0.85    # 85% success rate
            },
            "cover_letter_generation": {
                "quality_score": 0.40,  # 40% due to AI artifacts
                "response_time": 20.0,  # 20 seconds average
                "success_rate": 0.70    # 70% due to broken outputs
            },
            "feedback_processing": {
                "quality_score": 0.55,  # 55% basic analysis
                "response_time": 8.0,   # 8 seconds average
                "success_rate": 0.90    # 90% simple success
            },
            "skill_analysis": {
                "quality_score": 0.60,  # 60% accuracy
                "response_time": 12.0,  # 12 seconds average
                "success_rate": 0.80    # 80% success rate
            }
        }
    
    def record_metric(self, metric: QualityMetric) -> None:
        """Record a new quality metric"""
        try:
            with open(self.metrics_file, 'a') as f:
                f.write(json.dumps(asdict(metric)) + '\n')
            
            logger.info(f"Recorded metric: {metric.component}/{metric.operation} - "
                       f"Quality: {metric.quality_score:.2f}, Time: {metric.response_time:.2f}s")
        
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
    
    def load_metrics(self, days_back: int = 30) -> List[QualityMetric]:
        """Load metrics from the last N days"""
        if not self.metrics_file.exists():
            return []
        
        cutoff_time = datetime.now().timestamp() - (days_back * 24 * 3600)
        metrics = []
        
        try:
            with open(self.metrics_file) as f:
                for line in f:
                    data = json.loads(line.strip())
                    metric_time = datetime.fromisoformat(data['timestamp']).timestamp()
                    
                    if metric_time >= cutoff_time:
                        metrics.append(QualityMetric(**data))
            
            logger.info(f"Loaded {len(metrics)} metrics from last {days_back} days")
            return metrics
        
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
            return []
    
    def analyze_component_performance(self, component: str, days_back: int = 30) -> PerformanceReport:
        """Analyze performance for a specific component"""
        metrics = [m for m in self.load_metrics(days_back) if m.component == component]
        
        if not metrics:
            logger.warning(f"No metrics found for component: {component}")
            return PerformanceReport(
                component=component,
                total_operations=0,
                success_rate=0.0,
                avg_quality_score=0.0,
                avg_response_time=0.0
            )
        
        successful_metrics = [m for m in metrics if m.success]
        
        total_operations = len(metrics)
        success_rate = len(successful_metrics) / total_operations
        avg_quality_score = statistics.mean([m.quality_score for m in successful_metrics]) if successful_metrics else 0.0
        avg_response_time = statistics.mean([m.response_time for m in metrics])
        
        # Calculate improvements vs baseline
        baseline = self.baseline_metrics.get(component, {})
        quality_improvement = None
        speed_improvement = None
        
        if baseline:
            if baseline.get('quality_score'):
                quality_improvement = ((avg_quality_score - baseline['quality_score']) / baseline['quality_score']) * 100
            if baseline.get('response_time'):
                speed_improvement = ((baseline['response_time'] - avg_response_time) / baseline['response_time']) * 100
        
        return PerformanceReport(
            component=component,
            total_operations=total_operations,
            success_rate=success_rate,
            avg_quality_score=avg_quality_score,
            avg_response_time=avg_response_time,
            quality_improvement=quality_improvement,
            speed_improvement=speed_improvement
        )
    
    def generate_comprehensive_report(self, days_back: int = 30) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        components = ['job_matching', 'cover_letter_generation', 'feedback_processing', 'skill_analysis']
        
        report: Dict[str, Any] = {
            'generated_at': datetime.now().isoformat(),
            'period_days': days_back,
            'components': {},
            'summary': {}
        }
        
        total_operations = 0
        total_improvements = []
        
        for component in components:
            perf_report = self.analyze_component_performance(component, days_back)
            report['components'][component] = asdict(perf_report)
            
            total_operations += perf_report.total_operations
            if perf_report.quality_improvement:
                total_improvements.append(perf_report.quality_improvement)
        
        # Calculate summary statistics
        report['summary'] = {
            'total_operations': total_operations,
            'avg_quality_improvement': statistics.mean(total_improvements) if total_improvements else 0.0,
            'components_improved': len([i for i in total_improvements if i > 0]),
            'overall_status': 'excellent' if statistics.mean(total_improvements or [0]) > 50 else 'good' if statistics.mean(total_improvements or [0]) > 20 else 'baseline'
        }
        
        # Save report
        try:
            with open(self.reports_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Generated comprehensive report: {total_operations} operations analyzed")
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        return report
    
    def print_performance_summary(self, days_back: int = 30) -> None:
        """Print a human-readable performance summary"""
        report = self.generate_comprehensive_report(days_back)
        
        print(f"\n{'='*60}")
        print(f"🎯 LLM FACTORY PERFORMANCE REPORT")
        print(f"{'='*60}")
        print(f"📅 Period: Last {days_back} days")
        print(f"🔢 Total Operations: {report['summary']['total_operations']}")
        print(f"📈 Average Quality Improvement: {report['summary']['avg_quality_improvement']:.1f}%")
        print(f"✅ Components Improved: {report['summary']['components_improved']}/4")
        print(f"🏆 Overall Status: {report['summary']['overall_status'].upper()}")
        
        print(f"\n{'='*60}")
        print(f"📊 COMPONENT BREAKDOWN")
        print(f"{'='*60}")
        
        for component, data in report['components'].items():
            print(f"\n🔧 {component.replace('_', ' ').title()}")
            print(f"   Operations: {data['total_operations']}")
            print(f"   Success Rate: {data['success_rate']:.1%}")
            print(f"   Quality Score: {data['avg_quality_score']:.2f}")
            print(f"   Response Time: {data['avg_response_time']:.1f}s")
            
            if data['quality_improvement']:
                improvement_emoji = "📈" if data['quality_improvement'] > 0 else "📉"
                print(f"   Quality Improvement: {improvement_emoji} {data['quality_improvement']:+.1f}%")
            
            if data['speed_improvement']:
                speed_emoji = "⚡" if data['speed_improvement'] > 0 else "🐌"
                print(f"   Speed Improvement: {speed_emoji} {data['speed_improvement']:+.1f}%")

def create_sample_metrics():
    """Create sample metrics to demonstrate the monitoring system"""
    monitor = LLMFactoryPerformanceMonitor()
    
    # Sample metrics showing LLM Factory improvements
    sample_metrics = [
        QualityMetric(
            timestamp=datetime.now().isoformat(),
            component="job_matching",
            operation="evaluate_fitness",
            quality_score=0.85,  # Improved from 0.65 baseline
            response_time=12.0,  # Improved from 15.0 baseline
            success=True,
            model_used="llama3.2:latest",
            specialist_used="JobFitnessEvaluatorV2",
            output_length=1200
        ),
        QualityMetric(
            timestamp=datetime.now().isoformat(),
            component="cover_letter_generation",
            operation="generate_letter",
            quality_score=0.90,  # Dramatically improved from 0.40 baseline
            response_time=18.0,  # Improved from 20.0 baseline
            success=True,
            model_used="llama3.2:latest",
            specialist_used="CoverLetterGeneratorV2",
            output_length=1800,
            user_satisfaction=5
        ),
        QualityMetric(
            timestamp=datetime.now().isoformat(),
            component="feedback_processing",
            operation="analyze_feedback",
            quality_score=0.80,  # Improved from 0.55 baseline
            response_time=6.0,   # Improved from 8.0 baseline
            success=True,
            model_used="llama3.2:latest",
            specialist_used="FeedbackProcessorSpecialist",
            output_length=600
        )
    ]
    
    # Record sample metrics
    for metric in sample_metrics:
        monitor.record_metric(metric)
    
    return monitor

def main():
    """Main function to demonstrate the monitoring system"""
    print("🎯 Setting up LLM Factory Performance Monitoring...")
    
    # Create sample metrics
    monitor = create_sample_metrics()
    
    # Generate and display report
    monitor.print_performance_summary()
    
    print("\n" + "="*60)
    print("✅ Performance monitoring system is ready!")
    print("📝 Use this system to track LLM Factory quality improvements")
    print("🔍 Monitor quality scores, response times, and user satisfaction")
    print("📊 Generate regular reports to demonstrate ROI")
    print("="*60)

if __name__ == "__main__":
    main()
