"""
Excel Report Generator
====================

Generates Excel reports following Sandy's Golden Rules.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class ExcelReportGenerator:
    """Generates Excel reports with proper formatting"""
    
    def __init__(self, reports_path: Path):
        """Initialize the Excel report generator
        
        Args:
            reports_path: Directory where reports will be saved
        """
        self.reports_path = reports_path
        self.reports_path.mkdir(exist_ok=True)
    
    def generate_report(self, report_data: List[Dict[str, Any]]) -> Path:
        """Generate an Excel report from the provided data
        
        Args:
            report_data: List of job report entries
            
        Returns:
            Path to the generated Excel file
        """
        if not report_data:
            raise ValueError("No data provided for report generation")
        
        # Create DataFrame
        df = pd.DataFrame(report_data)
        
        # Generate Excel file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = self.reports_path / f"daily_report_{timestamp}.xlsx"
        
        print(f"\nCreating Excel report: {excel_path}")
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Daily Report', index=False)
            
            # Format worksheet
            self._format_worksheet(writer.book['Daily Report'])
        
        print(f"Excel report created: {excel_path}")
        print(f"Report contains {len(report_data)} jobs with job matching format (28 columns)")
        
        return excel_path
    
    def _format_worksheet(self, worksheet):
        """Apply formatting to worksheet"""
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            # Find maximum content length
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            # Set column width (capped at 50 characters)
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
