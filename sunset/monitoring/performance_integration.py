#!/usr/bin/env python3
"""
LLM Factory Performance Monitoring Integration

Provides decorators and utilities to automatically track performance
of all LLM Factory specialist calls throughout the sunset system.
"""
import time
import logging
from functools import wraps
from typing import Any, Callable, Optional
from datetime import datetime
import inspect

# Import the monitoring system
try:
    from monitoring.llm_factory_performance_monitor import LLMFactoryPerformanceMonitor, QualityMetric  # type: ignore
except ImportError:
    # Fallback if monitoring is not available
    LLMFactoryPerformanceMonitor = None  # type: ignore
    QualityMetric = None  # type: ignore

logger = logging.getLogger('llm_factory_integration')

class PerformanceTracker:
    """Tracks performance of LLM Factory operations"""
    
    def __init__(self):
        try:
            self.monitor = LLMFactoryPerformanceMonitor()
            self.enabled = True
        except Exception:
            self.monitor = None
            self.enabled = False
        
        if not self.enabled:
            logger.warning("Performance monitoring not available - metrics will not be tracked")
    
    def track_specialist_call(self, component: str, operation: str = "process"):
        """Decorator to track LLM Factory specialist calls"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                if not self.enabled:
                    return func(*args, **kwargs)
                
                start_time = time.time()
                success = False
                error_message = None
                quality_score = 0.0
                specialist_used = None
                model_used = "unknown"
                output_length = None
                
                try:
                    # Execute the function
                    result = func(*args, **kwargs)
                    success = True
                    
                    # Extract metrics from result
                    if isinstance(result, dict):
                        # Try to extract quality metrics from LLM Factory response
                        quality_score = result.get('quality_score', 0.8)  # Default good score
                        specialist_used = result.get('specialist_id', func.__name__)
                        model_used = result.get('model_used', model_used)
                        
                        # Calculate output length
                        if 'content' in result:
                            output_length = len(str(result['content']))
                        elif 'response' in result:
                            output_length = len(str(result['response']))
                    
                    elif hasattr(result, '__len__'):
                        output_length = len(str(result))
                        quality_score = 0.8  # Default for successful operations
                    
                    return result
                
                except Exception as e:
                    error_message = str(e)
                    logger.error(f"Error in {component}/{operation}: {e}")
                    raise
                
                finally:
                    # Record metrics
                    response_time = time.time() - start_time
                    
                    if self.enabled:
                        metric = QualityMetric(
                            timestamp=datetime.now().isoformat(),
                            component=component,
                            operation=operation,
                            quality_score=quality_score,
                            response_time=response_time,
                            success=success,
                            model_used=model_used,
                            specialist_used=specialist_used,
                            error_message=error_message,
                            output_length=output_length
                        )
                        
                        self.monitor.record_metric(metric)
            
            return wrapper
        return decorator
    
    def track_quality_score(self, component: str, operation: str, 
                           quality_score: float, response_time: float,
                           specialist_used: Optional[str] = None, model_used: str = "unknown",
                           output_length: Optional[int] = None, user_satisfaction: Optional[int] = None):
        """Manually track a quality score"""
        if not self.enabled:
            return
        
        metric = QualityMetric(
            timestamp=datetime.now().isoformat(),
            component=component,
            operation=operation,
            quality_score=quality_score,
            response_time=response_time,
            success=True,
            model_used=model_used,
            specialist_used=specialist_used,
            output_length=output_length,
            user_satisfaction=user_satisfaction
        )
        
        self.monitor.record_metric(metric)

# Global performance tracker instance
performance_tracker = PerformanceTracker()

# Convenient decorators for each component
def track_job_matching(operation: str = "evaluate"):
    """Track job matching operations"""
    return performance_tracker.track_specialist_call("job_matching", operation)

def track_cover_letter(operation: str = "generate"):
    """Track cover letter generation operations"""
    return performance_tracker.track_specialist_call("cover_letter_generation", operation)

def track_feedback_processing(operation: str = "analyze"):
    """Track feedback processing operations"""
    return performance_tracker.track_specialist_call("feedback_processing", operation)

def track_skill_analysis(operation: str = "analyze"):
    """Track skill analysis operations"""
    return performance_tracker.track_specialist_call("skill_analysis", operation)

def track_document_analysis(operation: str = "analyze"):
    """Track document analysis operations"""
    return performance_tracker.track_specialist_call("document_analysis", operation)

# Utility functions for easy integration
def log_user_satisfaction(component: str, operation: str, satisfaction_rating: int):
    """Log user satisfaction rating (1-5)"""
    if performance_tracker.enabled:
        # Find the most recent metric for this component/operation and update it
        # This is a simplified version - in production you'd want to match by session ID
        logger.info(f"User satisfaction for {component}/{operation}: {satisfaction_rating}/5")

def generate_daily_report():
    """Generate and display daily performance report"""
    if performance_tracker.enabled:
        performance_tracker.monitor.print_performance_summary(days_back=1)
    else:
        logger.warning("Performance monitoring not available")

def generate_weekly_report():
    """Generate and display weekly performance report"""
    if performance_tracker.enabled:
        performance_tracker.monitor.print_performance_summary(days_back=7)
    else:
        logger.warning("Performance monitoring not available")
