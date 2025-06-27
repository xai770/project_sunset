#!/usr/bin/env python3
"""
Professional Skill Timeline Generator for Cover Letters

This module generates professional timeline visualizations showing skill progression
over time as training and learning activities are completed.
"""

import os
import matplotlib
# Use Agg backend which doesn't require a display (good for servers)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

class ProfessionalSkillTimelineGenerator:
    """
    Generates professional visualizations of skill progression timelines for cover letters.
    """
    
    def __init__(self, output_dir=None, start_date=None):
        """Initialize the timeline generator.
        
        Args:
            output_dir (str): Directory to save generated charts (default: output/charts)
            start_date (datetime): Starting date for the timeline (default: 14 days from now)
        """
        # Set up default output directory
        if output_dir is None:
            # Try to find the project root
            script_dir = os.path.dirname(os.path.abspath(__file__))
            possible_project_roots = [
                os.path.dirname(os.path.dirname(os.path.dirname(script_dir))),
                os.path.dirname(os.path.dirname(script_dir))
            ]
            
            project_root = None
            for root in possible_project_roots:
                if os.path.exists(os.path.join(root, "output")):
                    project_root = root
                    break
                    
            if project_root:
                self.output_dir = os.path.join(project_root, "output", "charts")
            else:
                self.output_dir = os.path.join(script_dir, "charts")
        else:
            self.output_dir = output_dir
            
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up default start date
        if start_date is None:
            self.start_date = datetime.now() + timedelta(days=14)
        else:
            self.start_date = start_date
            
        # Set up figure params
        self.fig_width = 10
        self.fig_height = 6
        self.dpi = 300
        self.color_palette = {
            'line': '#1f77b4',        # Blue line
            'background': '#f8f9fa',  # Light gray background
            'grid': '#e0e0e0',        # Lighter gray grid
            'point': '#ff7f0e',       # Orange points
            'text': '#333333'         # Dark gray text
        }
        
    def generate_chart(self, starting_skill_pct, skill_improvements, 
                      title="Projected Skill Development Timeline", 
                      save_as="skill_timeline.png",
                      show_annotations=True):
        """
        Generate a professional timeline chart showing skill progression.
        
        Args:
            starting_skill_pct (int): Starting skill match percentage (0-100)
            skill_improvements (list): List of tuples (months_from_start, pct_increase, skill_name)
            title (str): Title for the chart
            save_as (str): Filename to save the chart as
            show_annotations (bool): Whether to show text annotations for each point
                
        Returns:
            tuple: (path_to_saved_image, markdown_code_to_embed)
        """
        # Create figure with professional look
        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=(self.fig_width, self.fig_height), dpi=self.dpi)
        
        # Set background color
        fig.patch.set_facecolor(self.color_palette['background'])
        ax.set_facecolor(self.color_palette['background'])
        
        # Calculate dates for each point
        dates = [self.start_date]
        percentages = [starting_skill_pct]
        labels = ["Starting Qualification"]
        
        # Sort skill improvements by month
        sorted_improvements = sorted(skill_improvements, key=lambda x: x[0])
        
        for months_from_start, percentage, skill_name in sorted_improvements:
            # Calculate the date for this improvement
            improvement_date = self.start_date + timedelta(days=months_from_start*30)  # Approximate
            dates.append(improvement_date)
            percentages.append(percentage)
            labels.append(skill_name)
        
        # Plot the line
        ax.plot(dates, percentages, 'o-', linewidth=2.5, 
                color=self.color_palette['line'], 
                markerfacecolor=self.color_palette['point'],
                markeredgecolor='white',
                markersize=10)
        
        # Format x-axis to show dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.xticks(rotation=45)
        
        # Set y-axis range
        min_pct = max(0, min(percentages) - 10)
        max_pct = min(100, max(percentages) + 5)
        ax.set_ylim(min_pct, max_pct)
        
        # Y-axis should show percentage
        ax.set_ylabel('Skill Match Percentage')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}%'))
        
        # Add grid lines
        ax.grid(True, linestyle='--', alpha=0.7, color=self.color_palette['grid'])
        
        # Add title and labels
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20, color=self.color_palette['text'])
        ax.set_xlabel('Timeline', fontsize=12, labelpad=10)
        
        # Annotate points if requested
        if show_annotations:
            for i, (date, pct, label) in enumerate(zip(dates, percentages, labels)):
                offset_x = 10 if i > 0 else -10
                ha = 'left' if i > 0 else 'right'
                
                # Create box around text
                bbox_props = dict(
                    boxstyle="round,pad=0.5", 
                    edgecolor=self.color_palette['line'],
                    facecolor='white',
                    alpha=0.9
                )
                
                ax.annotate(
                    f"{label}\n{pct}%",
                    (date, pct),
                    xytext=(offset_x, 10),
                    textcoords='offset points',
                    ha=ha, 
                    va='center',
                    fontsize=9,
                    bbox=bbox_props,
                    arrowprops=dict(
                        arrowstyle="-|>",
                        color=self.color_palette['line'],
                        connectionstyle="arc3,rad=0.2" if i > 0 else "arc3,rad=-0.2"
                    )
                )
                
        # Add watermark in bottom right (optional)
        ax.text(
            0.98, 0.02, "Generated by JFMS",
            ha='right', va='bottom',
            transform=ax.transAxes,
            fontsize=8, alpha=0.5,
            color=self.color_palette['text']
        )
        
        # Tight layout
        plt.tight_layout()
        
        # Save the figure
        filepath = os.path.join(self.output_dir, save_as)
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        
        # Create markdown code for embedding the image
        markdown_code = f"![Skill Progression Timeline]({filepath})"
        
        # Close the figure to free memory
        plt.close(fig)
        
        return filepath, markdown_code
        
    def generate_latex_code(self, starting_skill_pct, skill_improvements,
                           title="Projected Skill Development Timeline"):
        """
        Generate LaTeX code for a pgfplots timeline chart showing skill progression.
        
        This generates LaTeX code that can be used in a LaTeX document.
        
        Args:
            starting_skill_pct (int): Starting skill match percentage (0-100)
            skill_improvements (list): List of tuples (months_from_start, pct_increase, skill_name)
            title (str): Title for the chart
                
        Returns:
            str: LaTeX code for the chart
        """
        # Calculate dates for each point
        dates = [self.start_date]
        percentages = [starting_skill_pct]
        labels = ["Starting Qualification"]
        
        # Sort skill improvements by month
        sorted_improvements = sorted(skill_improvements, key=lambda x: x[0])
        
        for months_from_start, percentage, skill_name in sorted_improvements:
            # Calculate the date for this improvement
            improvement_date = self.start_date + timedelta(days=months_from_start*30)  # Approximate
            dates.append(improvement_date)
            percentages.append(percentage)
            labels.append(skill_name)
        
        # Create LaTeX code for the chart
        latex_code = []
        latex_code.append("\\begin{figure}[htb]")
        latex_code.append("  \\centering")
        latex_code.append("  \\begin{tikzpicture}")
        latex_code.append("    \\begin{axis}[")
        latex_code.append(f"      title={{{title}}},")
        latex_code.append("      xlabel={Timeline},")
        latex_code.append("      ylabel={Skill Match Percentage},")
        latex_code.append("      xmin=" + self.start_date.strftime("%Y-%m-%d") + ",")
        latex_code.append("      xmax=" + dates[-1].strftime("%Y-%m-%d") + ",")
        latex_code.append(f"      ymin={max(0, min(percentages) - 5)},")
        latex_code.append(f"      ymax={min(100, max(percentages) + 5)},")
        latex_code.append("      xticklabel style={rotate=45, anchor=east},")
        latex_code.append("      grid=both,")
        latex_code.append("      grid style={line width=.1pt, draw=gray!10},")
        latex_code.append("      major grid style={line width=.2pt,draw=gray!50},")
        latex_code.append("      axis lines=left,")
        latex_code.append("      width=0.8\\textwidth,")
        latex_code.append("      height=0.5\\textwidth,")
        latex_code.append("      legend pos=north west")
        latex_code.append("    ]")
        
        # Add the plot
        latex_code.append("    \\addplot[")
        latex_code.append("      color=blue,")
        latex_code.append("      mark=*,")
        latex_code.append("      line width=1.5pt,")
        latex_code.append("      mark size=3pt")
        latex_code.append("    ]")
        latex_code.append("    coordinates {")
        
        # Add coordinates
        for date, pct in zip(dates, percentages):
            latex_code.append(f"      ({date.strftime('%Y-%m-%d')},{pct})")
        
        latex_code.append("    };")
        
        # Add annotations
        for i, (date, pct, label) in enumerate(zip(dates, percentages, labels)):
            latex_code.append(f"    \\node[anchor=west, xshift=5pt, yshift=5pt] at (axis cs:{date.strftime('%Y-%m-%d')},{pct}) {{{label} ({pct}\\%)}};")
        
        latex_code.append("    \\end{axis}")
        latex_code.append("  \\end{tikzpicture}")
        latex_code.append(f"  \\caption{{{title}}}")
        latex_code.append("\\end{figure}")
        
        return "\n".join(latex_code)
    
    def get_markdown_for_image(self, image_path, alt_text="Skill Progression Timeline"):
        """Get markdown code to embed the image in a document."""
        return f"![{alt_text}]({image_path})"


# Testing functionality when run directly
if __name__ == "__main__":
    # Create a generator
    generator = ProfessionalSkillTimelineGenerator()
    
    # Define starting skill match and improvements
    starting_skill_match = 80
    skill_improvements = [
        (6, 90, "Google Cloud"),   # After 6 months, reach 90% with Google Cloud
        (9, 95, "Advanced DB")     # After 9 months, reach 95% with Advanced DB
    ]
    
    # Generate and save the chart
    image_path, markdown = generator.generate_chart(
        starting_skill_match, 
        skill_improvements,
        title="Projected Skill Development Timeline",
        save_as="skill_timeline_demo.png"
    )
    
    print(f"Chart saved to: {image_path}")
    print("Markdown for embedding:")
    print(markdown)
    
    # Generate LaTeX code
    latex_code = generator.generate_latex_code(
        starting_skill_match,
        skill_improvements
    )
    
    print("\nLaTeX code for the chart:")
    print(latex_code)
