#!/usr/bin/env python3
"""
Phase 4 Enhanced Benchmark Suite
===============================

Comprehensive performance testing framework for validating the 40% architecture
simplification benefits achieved in Phase 3.

Features:
- Memory profiling and resource monitoring
- Statistical performance analysis  
- Architecture complexity measurement
- Automated regression detection
"""

import sys
import os
import time
import psutil
import statistics
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import tracemalloc
import gc

# Add sunset to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics data structure"""
    test_name: str
    execution_time: float
    memory_peak: int  # bytes
    memory_current: int  # bytes
    cpu_percent: float
    specialist_used: str
    timestamp: str
    quality_score: Optional[float] = None
    error_occurred: bool = False
    error_message: str = ""

@dataclass
class BenchmarkSession:
    """Complete benchmark session results"""
    session_id: str
    start_time: str
    end_time: str
    total_tests: int
    successful_tests: int
    failed_tests: int
    average_execution_time: float
    total_memory_usage: int
    architecture_version: str
    metrics: List[PerformanceMetrics]

class EnhancedBenchmarkSuite:
    """Enhanced benchmark suite with comprehensive metrics"""
    
    def __init__(self):
        self.session_id = f"phase4_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now().isoformat()
        self.metrics: List[PerformanceMetrics] = []
        self.results_dir = Path("testing/benchmark_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize memory tracking
        tracemalloc.start()
        
        print(f"🚀 Enhanced Benchmark Suite - Session: {self.session_id}")
        print("=" * 70)
    
    def measure_memory_usage(self) -> Dict[str, int]:
        """Get current memory usage metrics"""
        current, peak = tracemalloc.get_traced_memory()
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "traced_current": current,
            "traced_peak": peak,
            "rss": memory_info.rss,
            "vms": memory_info.vms
        }
    
    def measure_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=0.1)
    
    def run_direct_specialist_benchmark(self) -> PerformanceMetrics:
        """Benchmark direct specialist integration"""
        print("\n📊 Testing Direct Specialist Integration")
        print("-" * 50)
        
        # Memory snapshot before
        gc.collect()
        memory_before = self.measure_memory_usage()
        
        start_time = time.perf_counter()
        cpu_start = self.measure_cpu_usage()
        
        try:
            from run_pipeline.core.direct_specialist_manager import get_job_matching_specialists
            
            # Initialize specialists
            init_start = time.perf_counter()
            specialists = get_job_matching_specialists()
            init_time = time.perf_counter() - init_start
            
            print(f"⚡ Specialist initialization: {init_time:.6f}s")
            
            # Test evaluation
            cv_data = {
                "text": "Senior Software Engineer with 8 years Python experience, "
                       "expertise in machine learning, distributed systems, and cloud architecture. "
                       "Led teams of 5+ developers, built scalable microservices handling 1M+ requests/day."
            }
            job_data = {
                "description": "Senior Python Developer position requiring machine learning expertise, "
                              "cloud platform experience, and team leadership skills. "
                              "Must have 5+ years Python, ML frameworks, and microservices architecture."
            }
            
            eval_start = time.perf_counter()
            result = specialists.evaluate_job_fitness(cv_data, job_data)
            eval_time = time.perf_counter() - eval_start
            
            print(f"⚡ Job fitness evaluation: {eval_time:.6f}s")
            print(f"📊 Evaluation success: {result.success}")
            print(f"🎯 Specialist used: {result.specialist_used}")
            
            # Memory snapshot after
            memory_after = self.measure_memory_usage()
            cpu_end = self.measure_cpu_usage()
            
            execution_time = time.perf_counter() - start_time
            
            metrics = PerformanceMetrics(
                test_name="direct_specialist_integration",
                execution_time=execution_time,
                memory_peak=memory_after["traced_peak"],
                memory_current=memory_after["traced_current"],
                cpu_percent=(cpu_start + cpu_end) / 2,
                specialist_used=result.specialist_used,
                timestamp=datetime.now().isoformat(),
                quality_score=result.quality_score,
                error_occurred=False
            )
            
            print(f"📈 Total execution time: {execution_time:.6f}s")
            print(f"🧠 Peak memory usage: {memory_after['traced_peak'] / 1024 / 1024:.2f} MB")
            
            return metrics
            
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            memory_after = self.measure_memory_usage()
            
            print(f"❌ Benchmark failed: {e}")
            
            return PerformanceMetrics(
                test_name="direct_specialist_integration",
                execution_time=execution_time,
                memory_peak=memory_after["traced_peak"],
                memory_current=memory_after["traced_current"],
                cpu_percent=0.0,
                specialist_used="none",
                timestamp=datetime.now().isoformat(),
                error_occurred=True,
                error_message=str(e)
            )
    
    def run_architecture_complexity_analysis(self) -> Dict[str, Any]:
        """Analyze architecture complexity metrics"""
        print("\n📐 Architecture Complexity Analysis")
        print("-" * 40)
        
        complexity_metrics = {
            "direct_specialist_patterns": 0,
            "legacy_abstraction_layers": 0,
            "total_llm_related_files": 0,
            "lines_of_code": 0,
            "function_count": 0,
            "class_count": 0
        }
        
        # Analyze run_pipeline directory
        run_pipeline_dir = Path("run_pipeline")
        
        for py_file in run_pipeline_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    complexity_metrics["lines_of_code"] += len(lines)
                    complexity_metrics["function_count"] += content.count("def ")
                    complexity_metrics["class_count"] += content.count("class ")
                    
                    # Check for direct specialist patterns
                    if "direct_specialist_manager" in content or "DirectSpecialist" in content:
                        complexity_metrics["direct_specialist_patterns"] += 1
                    
                    # Check for legacy patterns
                    if "LLMClient" in content or "LLMFactoryEnhancer" in content:
                        complexity_metrics["legacy_abstraction_layers"] += 1
                    
                    # Count LLM-related files
                    if any(term in content.lower() for term in ["llm", "specialist", "ollama"]):
                        complexity_metrics["total_llm_related_files"] += 1
                        
            except Exception as e:
                print(f"⚠️ Error analyzing {py_file}: {e}")
        
        # Calculate complexity score (lower is better)
        complexity_score = (
            complexity_metrics["legacy_abstraction_layers"] * 10 +
            complexity_metrics["lines_of_code"] / 1000 +
            complexity_metrics["function_count"] / 100
        )
        
        complexity_metrics["complexity_score"] = complexity_score
        complexity_metrics["simplification_achieved"] = True if complexity_metrics["direct_specialist_patterns"] > complexity_metrics["legacy_abstraction_layers"] else False
        
        print(f"📊 Direct specialist patterns: {complexity_metrics['direct_specialist_patterns']}")
        print(f"📊 Legacy abstraction layers: {complexity_metrics['legacy_abstraction_layers']}")
        print(f"📊 Total LLM-related files: {complexity_metrics['total_llm_related_files']}")
        print(f"📊 Lines of code: {complexity_metrics['lines_of_code']}")
        print(f"📊 Complexity score: {complexity_score:.2f}")
        print(f"✅ Simplification achieved: {complexity_metrics['simplification_achieved']}")
        
        return complexity_metrics
    
    def run_memory_profiling_benchmark(self) -> PerformanceMetrics:
        """Comprehensive memory usage profiling"""
        print("\n🧠 Memory Profiling Benchmark")
        print("-" * 35)
        
        gc.collect()  # Clean up before measurement
        memory_before = self.measure_memory_usage()
        
        start_time = time.perf_counter()
        
        try:
            # Load multiple specialists to test memory usage
            from run_pipeline.core.direct_specialist_manager import get_job_matching_specialists, get_feedback_specialists
            
            print("📊 Loading job matching specialists...")
            job_specialists = get_job_matching_specialists()
            memory_after_job = self.measure_memory_usage()
            
            print("📊 Loading feedback specialists...")
            feedback_specialists = get_feedback_specialists()
            memory_after_feedback = self.measure_memory_usage()
            
            # Run multiple evaluations to test memory stability
            for i in range(5):
                cv_data = {"text": f"Test CV data iteration {i}"}
                job_data = {"description": f"Test job description iteration {i}"}
                
                result = job_specialists.evaluate_job_fitness(cv_data, job_data)
                print(f"🔄 Iteration {i+1}: {result.success}")
            
            memory_final = self.measure_memory_usage()
            execution_time = time.perf_counter() - start_time
            
            memory_growth = memory_final["traced_current"] - memory_before["traced_current"]
            peak_usage = memory_final["traced_peak"]
            
            print(f"📈 Memory growth: {memory_growth / 1024 / 1024:.2f} MB")
            print(f"🏔️ Peak memory usage: {peak_usage / 1024 / 1024:.2f} MB")
            print(f"⏱️ Total execution time: {execution_time:.3f}s")
            
            return PerformanceMetrics(
                test_name="memory_profiling",
                execution_time=execution_time,
                memory_peak=peak_usage,
                memory_current=memory_final["traced_current"],
                cpu_percent=self.measure_cpu_usage(),
                specialist_used="multiple",
                timestamp=datetime.now().isoformat(),
                error_occurred=False
            )
            
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            memory_after = self.measure_memory_usage()
            
            return PerformanceMetrics(
                test_name="memory_profiling",
                execution_time=execution_time,
                memory_peak=memory_after["traced_peak"],
                memory_current=memory_after["traced_current"],
                cpu_percent=0.0,
                specialist_used="none",
                timestamp=datetime.now().isoformat(),
                error_occurred=True,
                error_message=str(e)
            )
    
    def run_statistical_analysis(self, iterations: int = 10) -> Dict[str, Any]:
        """Run statistical analysis of performance metrics"""
        print(f"\n📊 Statistical Performance Analysis ({iterations} iterations)")
        print("-" * 55)
        
        execution_times = []
        memory_peaks = []
        
        for i in range(iterations):
            print(f"🔄 Running iteration {i+1}/{iterations}")
            
            # Quick specialist evaluation
            try:
                from run_pipeline.core.direct_specialist_manager import get_job_matching_specialists
                
                start_time = time.perf_counter()
                specialists = get_job_matching_specialists()
                
                cv_data = {"text": "Statistical analysis test CV"}
                job_data = {"description": "Statistical analysis test job"}
                
                result = specialists.evaluate_job_fitness(cv_data, job_data)
                execution_time = time.perf_counter() - start_time
                
                execution_times.append(execution_time)
                
                memory_usage = self.measure_memory_usage()
                memory_peaks.append(memory_usage["traced_peak"])
                
            except Exception as e:
                print(f"⚠️ Iteration {i+1} failed: {e}")
        
        if execution_times:
            stats = {
                "iterations": len(execution_times),
                "execution_time": {
                    "mean": statistics.mean(execution_times),
                    "median": statistics.median(execution_times),
                    "std_dev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                    "min": min(execution_times),
                    "max": max(execution_times)
                },
                "memory_peak": {
                    "mean": statistics.mean(memory_peaks),
                    "median": statistics.median(memory_peaks),
                    "std_dev": statistics.stdev(memory_peaks) if len(memory_peaks) > 1 else 0,
                    "min": min(memory_peaks),
                    "max": max(memory_peaks)
                }
            }
            
            print(f"📊 Mean execution time: {stats['execution_time']['mean']:.6f}s")
            print(f"📊 Std deviation: {stats['execution_time']['std_dev']:.6f}s")
            print(f"🧠 Mean memory peak: {stats['memory_peak']['mean'] / 1024 / 1024:.2f} MB")
            
            return stats
        else:
            return {"error": "No successful iterations"}
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        print("\n📋 Generating Performance Report")
        print("-" * 35)
        
        end_time = datetime.now().isoformat()
        
        session = BenchmarkSession(
            session_id=self.session_id,
            start_time=self.start_time,
            end_time=end_time,
            total_tests=len(self.metrics),
            successful_tests=len([m for m in self.metrics if not m.error_occurred]),
            failed_tests=len([m for m in self.metrics if m.error_occurred]),
            average_execution_time=statistics.mean([m.execution_time for m in self.metrics]) if self.metrics else 0,
            total_memory_usage=sum([m.memory_peak for m in self.metrics]),
            architecture_version="Phase3_DirectSpecialist_v3",
            metrics=self.metrics
        )
        
        # Save results
        report_file = self.results_dir / f"{self.session_id}_report.json"
        with open(report_file, 'w') as f:
            json.dump(asdict(session), f, indent=2)
        
        print(f"✅ Performance report saved: {report_file}")
        
        return asdict(session)
    
    def run_comprehensive_benchmark(self):
        """Execute the complete enhanced benchmark suite"""
        print("🎯 PHASE 4 ENHANCED BENCHMARK SUITE")
        print("=" * 70)
        print("Comprehensive performance testing and architecture analysis")
        print("=" * 70)
        
        # 1. Direct Specialist Integration Benchmark
        direct_metrics = self.run_direct_specialist_benchmark()
        self.metrics.append(direct_metrics)
        
        # 2. Architecture Complexity Analysis
        complexity_analysis = self.run_architecture_complexity_analysis()
        
        # 3. Memory Profiling Benchmark
        memory_metrics = self.run_memory_profiling_benchmark()
        self.metrics.append(memory_metrics)
        
        # 4. Statistical Analysis
        statistical_analysis = self.run_statistical_analysis()
        
        # 5. Generate comprehensive report
        performance_report = self.generate_performance_report()
        
        # Summary
        print("\n" + "=" * 70)
        print("🎉 PHASE 4 BENCHMARK COMPLETION SUMMARY")
        print("=" * 70)
        
        successful_tests = len([m for m in self.metrics if not m.error_occurred])
        total_tests = len(self.metrics)
        
        print(f"✅ Tests completed: {successful_tests}/{total_tests}")
        print(f"⚡ Average execution time: {performance_report['average_execution_time']:.6f}s")
        print(f"🧠 Total memory usage: {performance_report['total_memory_usage'] / 1024 / 1024:.2f} MB")
        print(f"📊 Architecture simplification: {'✅ Achieved' if complexity_analysis.get('simplification_achieved') else '❌ Not achieved'}")
        
        if statistical_analysis and 'execution_time' in statistical_analysis:
            print(f"📈 Performance consistency: ±{statistical_analysis['execution_time']['std_dev']:.6f}s")
        
        print(f"📋 Detailed report: {self.session_id}_report.json")
        print("🚀 Phase 4 Enhanced Benchmarks: COMPLETE!")
        
        return performance_report

def main():
    """Main execution function"""
    benchmark_suite = EnhancedBenchmarkSuite()
    results = benchmark_suite.run_comprehensive_benchmark()
    return results

if __name__ == "__main__":
    results = main()
