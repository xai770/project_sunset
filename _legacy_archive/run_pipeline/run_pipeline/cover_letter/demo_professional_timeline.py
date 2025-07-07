#!/usr/bin/env python3
"""
Demo script to showcase the Professional Skill Timeline Generator
"""

import os
import sys
from datetime import datetime, timedelta

# Add project root to the Python path to make imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from run_pipeline.cover_letter.professional_timeline_generator import ProfessionalSkillTimelineGenerator

def generate_demo_timeline():
    """Generate a sample professional skill progression timeline chart."""
    
    # Create the generator with default settings
    start_date = datetime.now() + timedelta(days=14)
    generator = ProfessionalSkillTimelineGenerator(start_date=start_date)
    
    # Define starting skill match and improvements
    starting_skill_match = 80
    skill_improvements = [
        (6, 90, "Google Cloud"),  # After 6 months, reach 90% with Google Cloud
        (9, 95, "Advanced DB")    # After 9 months, reach 95% with Advanced DB
    ]
    
    # Generate the chart
    image_path, markdown = generator.generate_chart(
        starting_skill_match, 
        skill_improvements,
        title="Projected Skill Development Timeline",
        save_as="skill_timeline_demo.png"
    )
    
    # Generate LaTeX code as well
    latex_code = generator.generate_latex_code(
        starting_skill_match,
        skill_improvements
    )
    
    return image_path, markdown, latex_code

def save_demo_files():
    """Save demo files for the timeline chart."""
    image_path, markdown, latex_code = generate_demo_timeline()
    
    # Output to the examples directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                             "output", "examples")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save Markdown demo
    md_output_path = os.path.join(output_dir, "professional_timeline_demo.md")
    with open(md_output_path, 'w', encoding='utf-8') as f:
        f.write("# Professional Skill Progression Timeline Demo\n\n")
        f.write("This demonstrates how the professional skill progression timeline would appear in a cover letter.\n\n")
        f.write("## Skill Timeline Visualization\n\n")
        f.write(markdown)
        f.write("\n\n## How This Helps Employers\n\n")
        f.write("This timeline visualization provides employers with:\n\n")
        f.write("1. Clear visibility into skill development plans\n")
        f.write("2. Realistic expectations about time-to-productivity\n")
        f.write("3. Demonstration of commitment to learn required skills\n")
        f.write("4. Transparent communication about current capabilities and future potential\n")
    
    # Save LaTeX demo
    latex_output_path = os.path.join(output_dir, "skill_timeline_latex.tex")
    with open(latex_output_path, 'w', encoding='utf-8') as f:
        f.write("\\documentclass{article}\n")
        f.write("\\usepackage{tikz}\n")
        f.write("\\usepackage{pgfplots}\n")
        f.write("\\pgfplotsset{compat=1.17}\n\n")
        f.write("\\begin{document}\n\n")
        f.write("\\section{Skill Progression Timeline}\n\n")
        f.write("The following chart demonstrates projected skill development over time:\n\n")
        f.write(latex_code)
        f.write("\n\n\\end{document}\n")
    
    print(f"PNG image saved to: {image_path}")
    print(f"Markdown demo saved to: {md_output_path}")
    print(f"LaTeX code saved to: {latex_output_path}")
    
    return image_path, md_output_path, latex_output_path

if __name__ == "__main__":
    # Get the current directory to handle imports correctly
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    # Try to install matplotlib if it's not available
    try:
        import matplotlib
    except ImportError:
        print("Installing matplotlib...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
        import matplotlib
    
    # Generate and save the timeline files
    try:
        image_path, md_path, latex_path = save_demo_files()
        print("\nSuccessfully generated professional timeline chart!")
        print(f"Image: {image_path}")
        print(f"Markdown: {md_path}")
        print(f"LaTeX: {latex_path}")
    except Exception as e:
        print(f"Error generating timeline: {e}")
