#!/usr/bin/env python3
"""
Specialist Types and Data Structures
==================================
Core data structures for specialist operations.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SpecialistResult:
    """Standardized result format for all specialist operations"""
    success: bool
    result: Any
    specialist_used: str
    execution_time: float
    quality_score: Optional[float] = None
    error: Optional[str] = None
