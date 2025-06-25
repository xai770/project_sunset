"""
Project Sunset - Phase 5 Modern Core Architecture
==============================================

Clean, production-ready core module for AI-powered job matching.
"""

from .direct_specialist_manager import DirectSpecialistManager
from .job_matching_api import JobMatchingAPI

__all__ = [
    'DirectSpecialistManager',
    'JobMatchingAPI'
]

__version__ = "5.0.0"
__status__ = "Production Ready"
