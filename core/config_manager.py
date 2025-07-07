#!/usr/bin/env python3
"""
Centralized configuration management for Project Sunset.
Beautiful, type-safe, and environment-aware configuration.
"""
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import json
import os
from datetime import datetime

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "sunset"
    username: str = ""
    password: str = ""

@dataclass
class LLMConfig:
    """LLM configuration for different models"""
    default_model: str = "llama3.2"
    timeout: int = 300
    max_retries: int = 3
    temperature: float = 0.7
    available_models: list = field(default_factory=lambda: ["llama3.2", "gpt-4", "claude-3"])

@dataclass
class JobSearchConfig:
    """Job search and fetching configuration"""
    max_jobs_per_search: int = 50
    search_delay_seconds: float = 2.0
    max_concurrent_requests: int = 5
    user_agent: str = "Project-Sunset-Job-Fetcher/1.0"
    quick_mode_limit: int = 5

@dataclass
class ExcelConfig:
    """Excel export configuration"""
    output_directory: str = "output/excel"
    template_columns: Dict[str, str] = field(default_factory=lambda: {
        'A': 'Job ID',
        'B': 'Full Content',
        'C': 'Concise Job Description',
        'D': 'Position title',
        'E': 'Location',
        'F': 'Location Validation Details',
        'G': 'Job domain',
        'H': 'Match level',
        'I': 'Evaluation date',
        'J': 'Has domain gap',
        'K': 'Domain assessment',
        'L': 'No-go rationale',
        'M': 'Application narrative',
        'N': 'export_job_matches_log',
        'O': 'generate_cover_letters_log',
        'P': 'reviewer_feedback',
        'Q': 'mailman_log',
        'R': 'process_feedback_log',
        'S': 'reviewer_support_log',
        'T': 'workflow_status',
        'U': 'Technical Evaluation',
        'V': 'Human Story Interpretation',
        'W': 'Opportunity Bridge Assessment',
        'X': 'Growth Path Illumination',
        'Y': 'Encouragement Synthesis',
        'Z': 'Confidence Score',
        'AA': 'Joy Level'
    })
    row_height_max: int = 200
    row_height_min: int = 30

@dataclass
class SunsetConfig:
    """Main configuration class for Project Sunset"""
    # Core paths
    root_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data")
    job_data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data" / "postings")
    output_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "output")
    
    # Environment
    environment: str = "development"  # development, testing, production
    debug: bool = True
    log_level: str = "INFO"
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    job_search: JobSearchConfig = field(default_factory=JobSearchConfig)
    excel: ExcelConfig = field(default_factory=ExcelConfig)
    
    # Runtime info
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0-phase7"
    
    def __post_init__(self):
        """Ensure directories exist and validate configuration"""
        # Create necessary directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.job_data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "excel").mkdir(parents=True, exist_ok=True)
        
        # Validate paths
        if not self.root_dir.exists():
            raise ValueError(f"Root directory does not exist: {self.root_dir}")
    
    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> 'SunsetConfig':
        """Load configuration from JSON file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "sunset_config.json"
        
        if not config_path.exists():
            print(f"Configuration file not found at {config_path}, using defaults")
            return cls()
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Create the configuration instance with loaded data
            instance = cls()
            
            # Update environment settings
            instance.environment = config_data.get("environment", instance.environment)
            instance.debug = config_data.get("debug", instance.debug)
            instance.log_level = config_data.get("log_level", instance.log_level)
            instance.version = config_data.get("version", instance.version)
            
            # Update LLM configuration
            if "llm" in config_data:
                llm_data = config_data["llm"]
                instance.llm.default_model = llm_data.get("default_model", instance.llm.default_model)
                instance.llm.timeout = llm_data.get("timeout", instance.llm.timeout)
                instance.llm.max_retries = llm_data.get("max_retries", instance.llm.max_retries)
            
            # Update job search configuration
            if "job_search" in config_data:
                job_search_data = config_data["job_search"]
                instance.job_search.max_jobs_per_search = job_search_data.get(
                    "max_jobs_per_search", instance.job_search.max_jobs_per_search)
                instance.job_search.quick_mode_limit = job_search_data.get(
                    "quick_mode_limit", instance.job_search.quick_mode_limit)
            
            # Update Excel configuration
            if "excel" in config_data:
                excel_data = config_data["excel"]
                instance.excel.output_directory = excel_data.get(
                    "output_directory", instance.excel.output_directory)
                instance.excel.template_columns = excel_data.get(
                    "template_columns", instance.excel.template_columns)
                instance.excel.row_height_max = excel_data.get(
                    "row_height_max", instance.excel.row_height_max)
                instance.excel.row_height_min = excel_data.get(
                    "row_height_min", instance.excel.row_height_min)
            
            return instance
            
        except Exception as e:
            print(f"Error loading configuration: {e}, using defaults")
            return cls()
    
    def save_to_file(self, config_path: Optional[Path] = None) -> None:
        """Save current configuration to JSON file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "sunset_config.json"
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dictionary (simplified for now)
        config_dict = {
            "environment": self.environment,
            "debug": self.debug,
            "log_level": self.log_level,
            "version": self.version,
            "llm": {
                "default_model": self.llm.default_model,
                "timeout": self.llm.timeout,
                "max_retries": self.llm.max_retries
            },
            "job_search": {
                "max_jobs_per_search": self.job_search.max_jobs_per_search,
                "quick_mode_limit": self.job_search.quick_mode_limit
            },
            "excel": {
                "output_directory": self.excel.output_directory,
                "template_columns": self.excel.template_columns,
                "row_height_max": self.excel.row_height_max,
                "row_height_min": self.excel.row_height_min
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def get_job_file_path(self, job_id: int) -> Path:
        """Get the file path for a specific job"""
        return self.job_data_dir / f"job{job_id}.json"
    
    def get_excel_output_path(self, timestamp: Optional[str] = None) -> Path:
        """Get path for Excel output file"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / "excel" / f"job_matches_{timestamp}.xlsx"

# Global configuration instance
_config_instance: Optional[SunsetConfig] = None

def get_config() -> SunsetConfig:
    """Get the global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = SunsetConfig.from_file()
    return _config_instance

def reload_config() -> SunsetConfig:
    """Reload configuration from file"""
    global _config_instance
    _config_instance = SunsetConfig.from_file()
    return _config_instance

# Beautiful ASCII art for configuration display
def display_config_banner():
    """Display a beautiful configuration banner"""
    config = get_config()
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    🌅 PROJECT SUNSET CONFIGURATION 🌅        ║
╠══════════════════════════════════════════════════════════════╣
║ Version: {config.version:<47} ║
║ Environment: {config.environment:<43} ║
║ Debug Mode: {str(config.debug):<44} ║
║ LLM Model: {config.llm.default_model:<45} ║
║ Job Data Dir: {str(config.job_data_dir):<40} ║
╚══════════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    # Test the configuration system
    display_config_banner()
    config = get_config()
    print(f"Configuration loaded successfully!")
    print(f"Job data directory: {config.job_data_dir}")
    print(f"Excel output directory: {config.excel.output_directory}")
