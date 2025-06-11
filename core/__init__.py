"""
Project Sunset - Phase 5 Modern Core Architecture
==============================================

Clean, production-ready core module for AI-powered job matching.
"""

from .direct_specialist_manager import DirectSpecialistManager
from .job_matching_api import JobMatchingAPI
from .job_fetcher_p5 import JobFetcherP5

__all__ = [
    'DirectSpecialistManager',
    'JobMatchingAPI',
    'JobFetcherP5'
]

__version__ = "5.0.0"
__status__ = "Production Ready"
