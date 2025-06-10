#!/usr/bin/env python3
"""
Phase 4 Automated Regression Detection System
============================================

Automated system for detecting performance regressions and quality degradation
in Project Sunset's Phase 3 optimized architecture.

Features:
- Baseline performance establishment
- Automated regression detection
- Quality comparison analysis
- Alert generation for regressions
"""

import sys
import os
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Add sunset to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class PerformanceBaseline:
    """Performance baseline data structure"""
    baseline_id: str
    created_date: str
    architecture_version: str
    initialization_time_avg: float
    evaluation_time_avg: float
    memory_usage_avg: float
    success_rate: float
    measurements_count: int

@dataclass
class RegressionDetection:
    """Regression detection result"""
    regression_id: str
    detection_date: str
    metric_name: str
    baseline_value: float
    current_value: float
    regression_percent: float
    severity: str  # "minor", "moderate", "severe"
    is_regression: bool

class RegressionDetector:
    """Automated regression detection system"""
    
    def __init__(self):
        self.regression_dir = Path("testing/regression_analysis")
        self.regression_dir.mkdir(exist_ok=True)
        
        # Regression thresholds (percentage increase from baseline)
        self.regression_thresholds = {
            "initialization_time": {"minor": 20, "moderate": 50, "severe": 100},
            "evaluation_time": {"minor": 15, "moderate": 30, "severe": 60},
            "memory_usage": {"minor": 25, "moderate": 50, "severe": 100},
            "success_rate": {"minor": 5, "moderate": 10, "severe": 20}  # percentage decrease
        }
        
        print("🔍 Regression Detector initialized")
    
    def establish_baseline(self, measurements: List[Dict[str, Any]]) -> PerformanceBaseline:
        """Establish performance baseline from measurements"""
        print("📊 Establishing Performance Baseline")
        print("-" * 40)
        
        # Filter valid measurements
        valid_measurements = [m for m in measurements if not m.get("error_occurred", False)]
        
        if len(valid_measurements) < 3:
            raise ValueError("Need at least 3 valid measurements to establish baseline")
        
        # Calculate averages
        init_times = [m["initialization_time"] for m in valid_measurements if "initialization_time" in m]
        eval_times = [m["evaluation_time"] for m in valid_measurements if "evaluation_time" in m]
        memory_usages = [m["memory_usage"] for m in valid_measurements if "memory_usage" in m]
        success_count = len([m for m in valid_measurements if m.get("evaluation_success", False)])
        
        baseline = PerformanceBaseline(
            baseline_id=f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            created_date=datetime.now().isoformat(),
            architecture_version="Phase3_DirectSpecialist_v3",
            initialization_time_avg=statistics.mean(init_times) if init_times else 0,
            evaluation_time_avg=statistics.mean(eval_times) if eval_times else 0,
            memory_usage_avg=statistics.mean(memory_usages) if memory_usages else 0,
            success_rate=(success_count / len(valid_measurements)) * 100,
            measurements_count=len(valid_measurements)
        )
        
        # Save baseline
        baseline_file = self.regression_dir / f"{baseline.baseline_id}.json"
        with open(baseline_file, 'w') as f:
            json.dump(asdict(baseline), f, indent=2)
        
        print(f"✅ Baseline established: {baseline.baseline_id}")
        print(f"📊 Init time avg: {baseline.initialization_time_avg:.6f}s")
        print(f"📊 Eval time avg: {baseline.evaluation_time_avg:.3f}s")
        print(f"🧠 Memory avg: {baseline.memory_usage_avg / 1024 / 1024:.1f}MB")
        print(f"✅ Success rate: {baseline.success_rate:.1f}%")
        
        return baseline
    
    def load_latest_baseline(self) -> Optional[PerformanceBaseline]:
        """Load the most recent performance baseline"""
        baseline_files = list(self.regression_dir.glob("baseline_*.json"))
        
        if not baseline_files:
            return None
        
        # Get the most recent baseline
        latest_file = max(baseline_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            baseline_data = json.load(f)
        
        return PerformanceBaseline(**baseline_data)
    
    def detect_regressions(self, current_measurements: List[Dict[str, Any]], 
                          baseline: Optional[PerformanceBaseline] = None) -> List[RegressionDetection]:
        """Detect performance regressions against baseline"""
        print("🔍 Detecting Performance Regressions")
        print("-" * 40)
        
        if baseline is None:
            baseline = self.load_latest_baseline()
            if baseline is None:
                print("⚠️ No baseline found. Establishing new baseline...")
                baseline = self.establish_baseline(current_measurements)
                return []
        
        # Filter valid current measurements
        valid_current = [m for m in current_measurements if not m.get("error_occurred", False)]
        
        if not valid_current:
            print("❌ No valid current measurements for regression detection")
            return []
        
        # Calculate current metrics
        current_metrics = {}
        
        init_times = [m["initialization_time"] for m in valid_current if "initialization_time" in m]
        if init_times:
            current_metrics["initialization_time"] = statistics.mean(init_times)
        
        eval_times = [m["evaluation_time"] for m in valid_current if "evaluation_time" in m]
        if eval_times:
            current_metrics["evaluation_time"] = statistics.mean(eval_times)
        
        memory_usages = [m["memory_usage"] for m in valid_current if "memory_usage" in m]
        if memory_usages:
            current_metrics["memory_usage"] = statistics.mean(memory_usages)
        
        success_count = len([m for m in valid_current if m.get("evaluation_success", False)])
        current_metrics["success_rate"] = (success_count / len(valid_current)) * 100
        
        # Detect regressions
        regressions = []
        
        baseline_values = {
            "initialization_time": baseline.initialization_time_avg,
            "evaluation_time": baseline.evaluation_time_avg,
            "memory_usage": baseline.memory_usage_avg,
            "success_rate": baseline.success_rate
        }
        
        for metric_name, current_value in current_metrics.items():
            baseline_value = baseline_values[metric_name]
            
            if baseline_value == 0:
                continue
            
            # Calculate regression percentage
            if metric_name == "success_rate":
                # For success rate, regression is a decrease
                regression_percent = ((baseline_value - current_value) / baseline_value) * 100
            else:
                # For other metrics, regression is an increase
                regression_percent = ((current_value - baseline_value) / baseline_value) * 100
            
            # Determine severity
            thresholds = self.regression_thresholds[metric_name]
            is_regression = False
            severity = "none"
            
            if regression_percent > thresholds["severe"]:
                is_regression = True
                severity = "severe"
            elif regression_percent > thresholds["moderate"]:
                is_regression = True
                severity = "moderate"
            elif regression_percent > thresholds["minor"]:
                is_regression = True
                severity = "minor"
            
            regression = RegressionDetection(
                regression_id=f"regression_{metric_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                detection_date=datetime.now().isoformat(),
                metric_name=metric_name,
                baseline_value=baseline_value,
                current_value=current_value,
                regression_percent=regression_percent,
                severity=severity,
                is_regression=is_regression
            )
            
            regressions.append(regression)
            
            # Log results
            if is_regression:
                print(f"🚨 REGRESSION DETECTED: {metric_name}")
                print(f"   Severity: {severity.upper()}")
                print(f"   Baseline: {baseline_value:.6f}")
                print(f"   Current: {current_value:.6f}")
                print(f"   Change: +{regression_percent:.1f}%")
            else:
                print(f"✅ {metric_name}: No regression (change: {regression_percent:+.1f}%)")
        
        # Save regression results
        if regressions:
            regression_file = self.regression_dir / f"regression_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            regression_data = [asdict(r) for r in regressions]
            with open(regression_file, 'w') as f:
                json.dump(regression_data, f, indent=2)
        
        return regressions
    
    def run_regression_test(self) -> Dict[str, Any]:
        """Run a complete regression test"""
        print("🔍 AUTOMATED REGRESSION DETECTION TEST")
        print("=" * 50)
        
        try:
            # Collect current performance measurements
            current_measurements = []
            
            print("📊 Collecting current performance measurements...")
            
            for i in range(5):  # Take 5 measurements
                print(f"🔄 Measurement {i+1}/5")
                
                from run_pipeline.core.direct_specialist_manager import get_job_matching_specialists
                import time
                import tracemalloc
                
                tracemalloc.start()
                
                # Measure initialization
                init_start = time.perf_counter()
                specialists = get_job_matching_specialists()
                init_time = time.perf_counter() - init_start
                
                # Measure evaluation
                cv_data = {"text": f"Regression test CV {i+1}"}
                job_data = {"description": f"Regression test job {i+1}"}
                
                eval_start = time.perf_counter()
                result = specialists.evaluate_job_fitness(cv_data, job_data)
                eval_time = time.perf_counter() - eval_start
                
                current_memory, peak_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                measurement = {
                    "timestamp": datetime.now().isoformat(),
                    "initialization_time": init_time,
                    "evaluation_time": eval_time,
                    "memory_usage": peak_memory,
                    "evaluation_success": result.success,
                    "error_occurred": False
                }
                
                current_measurements.append(measurement)
                time.sleep(1)  # Brief pause between measurements
            
            # Detect regressions
            regressions = self.detect_regressions(current_measurements)
            
            # Generate summary
            regression_summary = {
                "test_date": datetime.now().isoformat(),
                "measurements_taken": len(current_measurements),
                "regressions_detected": len([r for r in regressions if r.is_regression]),
                "total_checks": len(regressions),
                "severity_breakdown": {
                    "severe": len([r for r in regressions if r.severity == "severe"]),
                    "moderate": len([r for r in regressions if r.severity == "moderate"]),
                    "minor": len([r for r in regressions if r.severity == "minor"])
                },
                "regressions": [asdict(r) for r in regressions]
            }
            
            print("\n" + "=" * 50)
            print("📋 REGRESSION TEST SUMMARY")
            print("=" * 50)
            print(f"✅ Measurements taken: {regression_summary['measurements_taken']}")
            print(f"🔍 Regression checks: {regression_summary['total_checks']}")
            print(f"🚨 Regressions detected: {regression_summary['regressions_detected']}")
            
            if regression_summary['regressions_detected'] == 0:
                print("🎉 NO REGRESSIONS DETECTED - System performing within baseline!")
            else:
                print(f"⚠️ Severe: {regression_summary['severity_breakdown']['severe']}")
                print(f"⚠️ Moderate: {regression_summary['severity_breakdown']['moderate']}")
                print(f"⚠️ Minor: {regression_summary['severity_breakdown']['minor']}")
            
            return regression_summary
            
        except Exception as e:
            print(f"❌ Regression test failed: {e}")
            return {"error": str(e), "test_date": datetime.now().isoformat()}

def main():
    """Main execution function"""
    detector = RegressionDetector()
    results = detector.run_regression_test()
    return results

if __name__ == "__main__":
    results = main()
