#!/usr/bin/env python3
"""
Beautiful CLI interface for Project Sunset using Rich.
Makes the terminal experience delightful and informative.
"""
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.prompt import Confirm, Prompt
from rich.layout import Layout
from rich.live import Live
from rich import box
from typing import Optional, List
import time
from datetime import datetime
from pathlib import Path

# Initialize rich console
console = Console()

def print_sunset_banner():
    """Display beautiful Project Sunset banner"""
    banner_text = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  🌅  PROJECT SUNSET - INTELLIGENT JOB MATCHING PIPELINE  🌅   ║
    ║                                                               ║
    ║  "Automating the job application process with AI precision"   ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    
    console.print(Panel(
        banner_text,
        style="bold magenta",
        border_style="bright_yellow",
        expand=False
    ))

def print_phase_status():
    """Display current phase status"""
    table = Table(title="🚀 Phase 7 - Pipeline Restoration Status", box=box.ROUNDED)
    
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Last Updated", style="green")
    
    table.add_row("Job Fetching", "✅ Working", "Just now")
    table.add_row("LLM Processing", "✅ Working", "Just now") 
    table.add_row("Excel Export", "✅ Working", "Just now")
    table.add_row("Cover Letters", "🔧 In Progress", "Pending")
    table.add_row("Email Delivery", "⏳ Waiting", "Pending")
    
    console.print(table)

def show_progress_spinner(task_name: str, duration: float = 2.0):
    """Show a beautiful progress spinner"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description=task_name, total=None)
        time.sleep(duration)

def show_progress_bar(task_name: str, total_items: int, current: int = 0):
    """Show a beautiful progress bar"""
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(description=task_name, total=total_items, completed=current)
        return progress, task

def display_job_summary(jobs_data: List[dict]):
    """Display a beautiful summary of jobs"""
    if not jobs_data:
        console.print("No jobs to display", style="yellow")
        return
    
    table = Table(title="📋 Job Analysis Summary", box=box.HEAVY_EDGE)
    
    table.add_column("Job ID", style="cyan", no_wrap=True)
    table.add_column("Position", style="bright_white")
    table.add_column("Match Level", style="magenta")
    table.add_column("Location", style="green")
    table.add_column("Domain Gap", style="yellow")
    
    for job in jobs_data:
        # Use Beautiful JSON Architecture format
        job_id = str(job.get('job_metadata', {}).get('job_id') or job.get('job_id', 'Unknown'))
        position = job.get('job_content', {}).get('title') or job.get('web_details', {}).get('position_title', 'Unknown')[:30]
        match_level = job.get('evaluation_results', {}).get('cv_to_role_match', 'Unknown')
        
        # Location extraction from Beautiful JSON Architecture
        location = 'Unknown'
        job_content = job.get('job_content', {})
        location_data = job_content.get('location', {})
        if location_data:
            city = location_data.get('city', '')
            country = location_data.get('country', '')
            location = f"{city}, {country}".strip(', ')
        
        # Fallback to legacy format if Beautiful JSON not available
        if location == 'Unknown' or location == ', ':
            search_details = job.get('search_details', {})
            if search_details.get('PositionLocation'):
                loc_data = search_details['PositionLocation'][0]
                city = loc_data.get('CityName', '')
                country = loc_data.get('CountryName', '')
                location = f"{city}, {country}".strip(', ')
        
        # Domain gap assessment using Beautiful JSON Architecture
        domain_gap = "Unknown"
        eval_data = job.get('evaluation_results', {})
        if eval_data:
            domain_assessment = (eval_data.get('domain_knowledge_assessment') or '').lower()
            decision_rationale = (eval_data.get('decision', {}).get('rationale') or '').lower()
            gap_indicators = ['lacks', 'missing', 'no experience', 'gap', 'would take', 'years to acquire']
            has_gap = any(indicator in domain_assessment or indicator in decision_rationale 
                         for indicator in gap_indicators)
            domain_gap = 'Yes' if has_gap else 'No'
        
        # Color coding for match level
        if match_level.lower() == 'good':
            match_style = "bold green"
        elif match_level.lower() == 'moderate':
            match_style = "bold yellow"
        elif match_level.lower() == 'low':
            match_style = "bold red"
        else:
            match_style = "dim white"
        
        table.add_row(
            job_id,
            position,
            Text(match_level, style=match_style),
            location,
            domain_gap
        )
    
    console.print(table)

def confirm_action(message: str, default: bool = True) -> bool:
    """Beautiful confirmation prompt"""
    return Confirm.ask(
        f"[bold yellow]🤔 {message}[/bold yellow]",
        default=default
    )

def get_user_input(prompt: str, default: str = "") -> str:
    """Beautiful input prompt"""
    return Prompt.ask(
        f"[bold cyan]✨ {prompt}[/bold cyan]",
        default=default
    )

def print_success(message: str):
    """Print success message with style"""
    console.print(f"✅ {message}", style="bold green")

def print_warning(message: str):
    """Print warning message with style"""
    console.print(f"⚠️  {message}", style="bold yellow")

def print_error(message: str):
    """Print error message with style"""
    console.print(f"❌ {message}", style="bold red")

def print_info(message: str):
    """Print info message with style"""
    console.print(f"ℹ️  {message}", style="bold blue")

def display_file_info(file_path: Path):
    """Display beautiful file information"""
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return
    
    stats = file_path.stat()
    size = stats.st_size
    modified = datetime.fromtimestamp(stats.st_mtime)
    
    table = Table(title=f"📄 File Information: {file_path.name}", box=box.SIMPLE)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Full Path", str(file_path))
    table.add_row("Size", f"{size:,} bytes")
    table.add_row("Modified", modified.strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row("Type", file_path.suffix or "No extension")
    
    console.print(table)

def create_status_dashboard(data: dict):
    """Create a live status dashboard"""
    layout = Layout()
    
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
    
    # Header
    header_text = Text("🌅 PROJECT SUNSET - LIVE DASHBOARD 🌅", justify="center")
    header_text.stylize("bold magenta")
    layout["header"].update(Panel(header_text))
    
    # Body - main content
    body_content = f"""
Pipeline Status: {data.get('status', 'Unknown')}
Jobs Processed: {data.get('jobs_processed', 0)}
Current Phase: {data.get('current_phase', 'Unknown')}
Last Update: {datetime.now().strftime('%H:%M:%S')}
    """
    layout["body"].update(Panel(body_content, title="Status"))
    
    # Footer
    footer_text = Text("Press Ctrl+C to stop monitoring", justify="center")
    footer_text.stylize("dim")
    layout["footer"].update(Panel(footer_text))
    
    return layout

if __name__ == "__main__":
    # Demo the CLI components
    print_sunset_banner()
    print_phase_status()
    
    # Demo progress
    show_progress_spinner("Initializing beautiful CLI...")
    print_success("CLI components loaded successfully!")
    
    # Demo user interaction
    if confirm_action("Would you like to see a job summary demo?"):
        # Demo job summary with sample data using Beautiful JSON Architecture
        sample_jobs = [
            {
                'job_metadata': {'job_id': '64050'},
                'job_content': {
                    'title': 'SAP Basis Administrator',
                    'location': {'city': 'Frankfurt', 'country': 'Germany'}
                },
                'evaluation_results': {'cv_to_role_match': 'Good'}
            }
        ]
        display_job_summary(sample_jobs)
