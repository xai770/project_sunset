#!/usr/bin/env python3
"""
Markdown report generator for Project Sunset.
Creates human-readable reports parallel to Excel exports.
"""
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from .config_manager import get_config, SunsetConfig

class MarkdownExporter:
    """Handles the export of job matches to Markdown format"""
    
    def __init__(self, config: Optional[SunsetConfig] = None):
        """Initialize the exporter with configuration"""
        self.config = config or get_config()
    
    def export_matches(self, 
                      matches: List[Dict[str, Any]], 
                      output_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Export job matches to a markdown file.
        
        Args:
            matches: List of job match dictionaries
            output_path: Optional specific output path
            
        Returns:
            Path to the created markdown file
        """
        if not matches:
            raise ValueError("No matches to export")

        # Convert output_path to Path if it's a string
        if isinstance(output_path, str):
            output_path = Path(output_path)
            
        # If no output path specified, create one based on timestamp
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(self.config.output_dir) / "reports" / f"job_matches_{timestamp}.md"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write("# Job Matches Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write each job
            for match in matches:
                job_id = match.get('Job ID', 'Unknown')
                f.write(f"## Job {job_id}\n\n")
                
                # Write all fields except Job ID (already in heading)
                for key, value in match.items():
                    if key != 'Job ID':
                        if value and str(value).strip():  # Only write non-empty fields
                            f.write(f"### {key}\n")
                            f.write(f"{value}\n\n")

        return output_path
