#!/usr/bin/env python3
"""
Specialist Version Monitor - Prevent LLM vs Hardcoded Confusion
==============================================================

This utility helps detect when specialists are not using expected LLM processing.
"""

import time
from typing import Dict, Any
import logging

class SpecialistMonitor:
    """Monitor specialist performance to detect version mismatches"""
    
    def __init__(self):
        self.expected_times = {
            "domain_classification_v1_0": (0.001, 0.050),  # Hardcoded
            "domain_classification_v1_1": (3.0, 15.0),     # LLM
            "location_validation_v1_0": (0.001, 0.050),    # Hardcoded  
            "location_validation_v1_1": (2.0, 10.0)        # LLM
        }
    
    def monitor_specialist_call(self, specialist_name: str, version: str, 
                              processing_time: float, result: Dict[Any, Any]):
        """Monitor a specialist call for suspicious timing"""
        
        key = f"{specialist_name}_{version}"
        expected_min, expected_max = self.expected_times.get(key, (0, float('inf')))
        
        # Check for version mismatch
        if version.endswith("v1_1") and processing_time < 1.0:
            logging.warning(f"🚨 SUSPICIOUS: {key} processed in {processing_time:.4f}s - Expected LLM processing!")
            logging.warning(f"   This may indicate v1_1 is not using Ollama correctly")
            return False
            
        elif version.endswith("v1_0") and processing_time > 1.0:
            logging.warning(f"🐌 UNEXPECTED: {key} processed in {processing_time:.4f}s - Slower than expected for hardcoded")
            
        # Check if within expected range
        if not (expected_min <= processing_time <= expected_max):
            logging.warning(f"⚠️  TIMING ANOMALY: {key} took {processing_time:.4f}s (expected {expected_min}-{expected_max}s)")
            
        # Add metadata to result
        if isinstance(result, dict):
            result['_monitor'] = {
                'version_used': version,
                'processing_time': processing_time,
                'timing_normal': expected_min <= processing_time <= expected_max,
                'ollama_likely_used': processing_time > 1.0 if version.endswith('v1_1') else None
            }
            
        return True

# Usage example:
monitor = SpecialistMonitor()

def monitored_specialist_call(specialist_func, specialist_name, version, *args, **kwargs):
    """Wrapper to monitor specialist calls"""
    start_time = time.time()
    result = specialist_func(*args, **kwargs)
    processing_time = time.time() - start_time
    
    monitor.monitor_specialist_call(specialist_name, version, processing_time, result)
    return result
