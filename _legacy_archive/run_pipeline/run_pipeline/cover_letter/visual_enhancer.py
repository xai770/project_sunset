#!/usr/bin/env python3
"""
Visual Enhancer for Cover Letter Generation

This module adds visual enhancements to cover letters,
including formatting, ASCII charts, and structural improvements.
"""

import re
import os
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Import the professional chart generator if available
try:
    from professional_timeline_generator import ProfessionalSkillTimelineGenerator  # type: ignore
    has_professional_charts = True
except ImportError:
    has_professional_charts = False
    logger.warning("Professional chart generator not available. Using ASCII charts only.")

class VisualEnhancer:
    """
    Enhances cover letters with visual elements and improved formatting.
    """
    
    def __init__(self):
        """Initialize the VisualEnhancer."""
        self.horizontal_line = "─" * 60
        self.separator = "•••"
        
        # Set up output directory for professional charts
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), "output", "charts")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def enhance_cover_letter(self, content):
        """
        Enhance a cover letter with visual improvements.
        
        Args:
            content (str): The original cover letter content
            
        Returns:
            str: Enhanced cover letter content
        """
        # Only enhance Markdown content
        if not self._is_markdown(content):
            logger.warning("Content does not appear to be Markdown. Skipping enhancement.")
            return content
            
        # Apply enhancements
        enhanced = content
        enhanced = self._enhance_header(enhanced)
        enhanced = self._enhance_sections(enhanced)
        enhanced = self._enhance_skills(enhanced)
        
        # Look for placeholder markers to insert charts and summaries
        if "{{SKILL_MATCH_CHART}}" in enhanced:
            logger.info("Found skill match chart placeholder.")
        
        if "{{QUALIFICATION_SUMMARY}}" in enhanced:
            logger.info("Found qualification summary placeholder.")
        
        # Add the footer last so it doesn't interfere with other enhancements
        enhanced = self._add_footer(enhanced)
        
        return enhanced
    
    def _is_markdown(self, content):
        """Check if content appears to be in Markdown format."""
        # Look for common Markdown elements like headers, emphasis, etc.
        markdown_patterns = [
            r'^#\s+.+$',           # Headers
            r'^\*\*.+\*\*$',       # Bold text
            r'^\*.+\*$',           # Italics
            r'^-\s+.+$',           # List items
            r'^\d+\.\s+.+$',       # Numbered list
            r'^>\s+.+$',           # Blockquotes
        ]
        
        for pattern in markdown_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True
        
        # Check for common Markdown cover letter elements
        if "# " in content and "## " in content:
            return True
            
        return False
    
    def _enhance_header(self, content):
        """Enhance the header section of the cover letter."""
        # Find the header section (first H1)
        header_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if not header_match:
            return content
            
        header_text = header_match.group(1)
        
        # Create an enhanced header with a decorative line
        enhanced_header = f"""# {header_text}

{self.horizontal_line}

"""
        
        # Replace the original header
        return content.replace(header_match.group(0), enhanced_header)
    
    def _enhance_sections(self, content):
        """Enhance section headings in the cover letter."""
        # Find all section headings (H2)
        sections = re.finditer(r'^##\s+(.+)$', content, re.MULTILINE)
        
        # Process each section heading
        result = content
        for section in sections:
            section_text = section.group(1)
            
            # Create enhanced section heading
            enhanced_section = f"""

{self.separator} **{section_text}** {self.separator}

"""
            
            # Replace the original section heading
            result = result.replace(section.group(0), enhanced_section)
            
        return result
    
    def _enhance_skills(self, content):
        """Enhance skill bullet points in the cover letter."""
        # Find skill bullet points (typically starting with "- **")
        skill_pattern = r'(-\s+\*\*.*?\*\*:.*?)(?=\n\n|\n-|\Z)'
        
        def enhance_skill_bullet(match):
            skill_bullet = match.group(1)
            # Add indentation and a special character
            enhanced_bullet = f"  ► {skill_bullet[2:]}"
            return enhanced_bullet
            
        # Replace skill bullets with enhanced format
        enhanced_content = re.sub(skill_pattern, enhance_skill_bullet, content, flags=re.DOTALL)
        
        return enhanced_content
    
    def _add_footer(self, content):
        """Add a professional footer to the cover letter."""
        # Check if there's already an attachments section
        if "**Attachments:**" in content:
            # Add horizontal line above attachments
            attachments_pattern = r'(\n\*\*Attachments:\*\*)'
            content = re.sub(attachments_pattern, f"\n\n{self.horizontal_line}\n\\1", content)
        else:
            # Add footer with horizontal line
            footer = f"""

{self.horizontal_line}

**Attachments:**
- Curriculum Vitae
- Certificates and References
"""
            content = content + footer
            
        # Insert skilled match charts and qualification summaries before footer if present
        if "##SKILL_MATCH_CHART##" in content:
            chart_pattern = r'##SKILL_MATCH_CHART##'
            content = re.sub(chart_pattern, "", content)
            
        if "##QUALIFICATION_SUMMARY##" in content:
            summary_pattern = r'##QUALIFICATION_SUMMARY##'
            content = re.sub(summary_pattern, "", content)
            
        # Add skill match and qualification sections if they exist in the content
        # Either as Markdown code blocks or as variables to be replaced
        match = re.search(r'<!-- SKILL_CHART:(.*?)-->', content, re.DOTALL)
        if match:
            chart_data = match.group(1).strip()
            content = content.replace(match.group(0), chart_data)
            
        match = re.search(r'<!-- QUAL_SUMMARY:(.*?)-->', content, re.DOTALL)
        if match:
            summary_data = match.group(1).strip()
            content = content.replace(match.group(0), summary_data)
            
        return content
    
    def create_skill_match_chart(self, skill_matches, job_id=None):
        """
        Create a professional PNG chart representing skill match percentage.
        
        Args:
            skill_matches (dict): Dictionary of skills and their match percentages
            job_id (str): Optional job ID for unique filename
            
        Returns:
            str: Markdown with embedded PNG image reference
        """
        if not skill_matches:
            return ""
        
        try:
            # Import here to avoid import issues
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Create professional chart
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Prepare data
            skills = list(skill_matches.keys())
            percentages = list(skill_matches.values())
            
            # Create horizontal bar chart
            y_pos = np.arange(len(skills))
            bars = ax.barh(y_pos, percentages, color='#2E4A66', alpha=0.8)
            
            # Customize chart
            ax.set_yticks(y_pos)
            ax.set_yticklabels(skills)
            ax.set_xlabel('Match Percentage (%)')
            ax.set_title('Skill Match Analysis', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlim(0, 100)
            
            # Add percentage labels on bars
            for i, (bar, pct) in enumerate(zip(bars, percentages)):
                width = bar.get_width()
                ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                       f'{pct}%', ha='left', va='center', fontweight='bold')
            
            # Style the chart
            ax.grid(axis='x', alpha=0.3)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            
            # Save chart
            timestamp = str(int(datetime.now().timestamp()))
            filename = f"skill_match_{job_id or timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Return markdown with image reference
            return f"""
## Skill Match Analysis

![Skill Match Chart]({filepath})

*Professional skill alignment analysis showing percentage match for key competencies.*
"""
            
        except ImportError:
            logger.warning("Matplotlib not available, falling back to text summary")
            # Fallback to simple text summary
            summary = "\n## Skill Match Analysis\n\n"
            for skill, percentage in skill_matches.items():
                summary += f"• **{skill}**: {percentage}% match\n"
            return summary
        except Exception as e:
            logger.error(f"Error creating skill match chart: {e}")
            # Fallback to simple text summary  
            summary = "\n## Skill Match Analysis\n\n"
            for skill, percentage in skill_matches.items():
                summary += f"• **{skill}**: {percentage}% match\n"
            return summary
        
    def create_professional_skill_timeline(self, starting_skill_pct, skill_improvements, 
                                         title="Skill Progression Timeline", output_format="ascii"):
        """
        Create a professional skill progression timeline chart.
        
        Args:
            starting_skill_pct (int): Starting skill percentage (0-100)
            skill_improvements (list): List of tuples (months_from_start, pct_increase, skill_name)
            title (str): Title for the chart
            output_format (str): Output format - 'ascii', 'image', or 'latex'
            
        Returns:
            str: Chart as a string (ASCII or markdown with image reference)
        """
        if output_format == "ascii" or not has_professional_charts:
            # Use ASCII chart generator
            return self._create_ascii_skill_timeline(starting_skill_pct, skill_improvements, title)
        
        # Use professional chart generator
        try:
            # Initialize with output directory
            generator = ProfessionalSkillTimelineGenerator(self.output_dir)
            
            if output_format == "latex":
                # Generate LaTeX code
                latex_code = generator.generate_latex_code(starting_skill_pct, skill_improvements, title)
                return f"```latex\n{latex_code}\n```"
            else:
                # Generate image chart and return markdown
                job_id = str(int(datetime.now().timestamp()))
                filename = f"skill_timeline_{job_id}.png"
                image_path, markdown = generator.generate_chart(
                    starting_skill_pct, 
                    skill_improvements,
                    title=title,
                    save_as=filename
                )
                return markdown
        except Exception as e:
            logger.error(f"Error generating professional chart: {e}")
            # Fall back to ASCII chart
            return self._create_ascii_skill_timeline(starting_skill_pct, skill_improvements, title)
            
    def create_qualification_summary(self, qualifications, rating="★★★☆☆"):
        """
        Create a formatted qualification summary.
        
        Args:
            qualifications (list): List of qualification items
            rating (str): Optional rating to display
            
        Returns:
            str: Formatted qualification summary
        """
        if not qualifications:
            return ""
            
        summary = """
## Qualification Summary

```
"""
        
        # Add rating if provided
        if rating:
            summary += f"Overall match: {rating}\n\n"
        
        for qual in qualifications:
            if isinstance(qual, dict) and "area" in qual and "description" in qual:
                # Format as area: description
                summary += f"• {qual['area']}: {qual['description']}\n"
            else:
                # Simple bullet point
                summary += f"• {qual}\n"
                
        summary += "```\n"
        return summary
        
    def create_skill_progression_timeline(self, starting_skill_pct, skill_improvements, 
                                        title="Skill Progression Timeline", format_type="ascii"):
        """
        Create a skill progression timeline showing future skill acquisition.
        
        Args:
            starting_skill_pct (int): Starting skill percentage (0-100)
            skill_improvements (list): List of tuples (months_from_start, pct_increase, skill_name)
            title (str): Title for the chart
            format_type (str): Format type - 'ascii', 'image', or 'latex'
            
        Returns:
            str: Chart as a string (ASCII or markdown with image reference)
        """
        # Check if we should use professional charts
        if format_type != "ascii" and has_professional_charts:
            try:
                # Use professional chart generator
                generator = ProfessionalSkillTimelineGenerator(self.output_dir)
                
                if format_type == "latex":
                    # Generate LaTeX code
                    latex_code = generator.generate_latex_code(starting_skill_pct, skill_improvements, title)
                    return f"""
## {title}

```latex
{latex_code}
```
"""
                else:
                    # Generate image chart and return markdown
                    job_id = str(int(datetime.now().timestamp()))
                    filename = f"skill_timeline_{job_id}.png"
                    image_path, markdown = generator.generate_chart(
                        starting_skill_pct, 
                        skill_improvements,
                        title=title,
                        save_as=filename
                    )
                    return f"""
## {title}

{markdown}
"""
            except Exception as e:
                logger.error(f"Error generating professional chart: {e}")
                logger.info("Falling back to ASCII chart")
                # Fall back to ASCII chart on error
        
        # Use ASCII chart
        return self._create_ascii_skill_timeline(starting_skill_pct, skill_improvements, title)
            
    def _create_ascii_skill_timeline(self, starting_skill_pct, skill_improvements, title="Skill Progression Timeline"):
        """
        Create an ASCII chart representing skill progression over time.
        
        Args:
            starting_skill_pct (int): Starting skill percentage (0-100)
            skill_improvements (list): List of tuples (months_from_start, pct_increase, skill_name)
            title (str): Title for the chart
            
        Returns:
            str: ASCII chart as a string
        """
        # Prepare data
        now = datetime.now()
        months = []
        percentages = {}
        
        # Start with current percentage
        current_date = now.strftime("%b'%y")
        months.append(current_date)
        percentages[current_date] = starting_skill_pct
        
        # Sort skill improvements by month
        sorted_improvements = sorted(skill_improvements, key=lambda x: x[0])
        
        # Add future months based on skill improvements
        for months_from_now, percentage, skill_name in sorted_improvements:
            future_date = datetime(
                now.year + ((now.month - 1 + months_from_now) // 12), 
                ((now.month - 1 + months_from_now) % 12) + 1, 
                1
            )
            future_month = future_date.strftime("%b'%y")
            months.append(future_month)
            percentages[future_month] = percentage
        
        # Generate chart
        chart = f"""
## {title}

```
Skill Match %
"""
        # Draw percentage lines
        max_pct = 100
        min_pct = max(0, starting_skill_pct - 20)
        
        # Chart height and width
        chart_height = 6
        month_width = 7
        chart_width = len(months) * month_width
        
        # Generate chart grid
        grid_lines = []
        
        # Top line with percentage
        grid_lines.append(f"{max_pct}% │" + " " * chart_width)
        
        # Middle percentage lines
        for i in range(4, 0, -1):
            pct = min_pct + (i * (max_pct - min_pct) // 5)
            grid_lines.append(f"{pct:3d}% │" + " " * chart_width)
        
        # Bottom line with percentage
        month_headers = "".join([f"{m:^{month_width}}" for m in months])
        grid_lines.append(f"{min_pct:3d}% ┼" + "─" * chart_width)
        grid_lines.append("     │" + month_headers)
        
        # Add vertical separators between months
        for i, line in enumerate(grid_lines[:-2]):
            for m in range(1, len(months)):
                pos = 6 + m * month_width
                chars = list(line)
                if pos < len(chars):
                    chars[pos] = "│"
                grid_lines[i] = "".join(chars)
        
        # Add the progression line
        prev_pct = starting_skill_pct
        prev_pos = (0, self._pct_to_y_pos(prev_pct, max_pct, min_pct, chart_height))
        
        # Draw the lines for each skill improvement
        for i, (months_from_now, pct, _) in enumerate(sorted_improvements):
            # Calculate x position
            x_pos = (i+1) * month_width + 3
            
            # Calculate y position based on percentage (reverse scale)
            y_pos = self._pct_to_y_pos(pct, max_pct, min_pct, chart_height)
            
            # Connect the points
            self._draw_line(grid_lines, prev_pos, (x_pos, y_pos))
            
            # Mark the point
            if y_pos < len(grid_lines):
                chars = list(grid_lines[y_pos])
                if x_pos < len(chars):
                    chars[x_pos] = "●"
                    grid_lines[y_pos] = "".join(chars)
            
            prev_pos = (x_pos, y_pos)
        
        # Add chart to output
        chart += "\n".join(grid_lines)
        
        # Add annotations
        chart += "\n     │"
        for i, (months_from_now, pct, skill_name) in enumerate(sorted_improvements):
            chart += f"\n     │{' ' * ((i+1) * month_width - 1)}│"
            chart += f"\n     │{' ' * ((i+1) * month_width - 1)}└── {skill_name} ({pct}%)"
        
        chart += f"\n     │\n     └── Starting Qualification ({starting_skill_pct}%)"
        chart += "\n```\n"
        
        return chart
        
    def _pct_to_y_pos(self, pct, max_pct, min_pct, chart_height):
        """Convert percentage to y position on chart (higher percentage = lower y position)"""
        if max_pct == min_pct:
            return 0
        normalized = (pct - min_pct) / (max_pct - min_pct)
        return max(0, min(chart_height - 1, chart_height - 1 - int(normalized * (chart_height - 1))))
    
    def _draw_line(self, grid_lines, start, end):
        """Draw a line between two points on the grid"""
        x1, y1 = start
        x2, y2 = end
        
        # If horizontal line
        if y1 == y2:
            line = list(grid_lines[y1])
            for x in range(x1 + 1, x2):
                if 0 <= x < len(line):
                    line[x] = "─"
            grid_lines[y1] = "".join(line)
            return
            
        # If vertical line
        if x1 == x2:
            for y in range(min(y1, y2) + 1, max(y1, y2)):
                if 0 <= y < len(grid_lines):
                    line = list(grid_lines[y])
                    if 0 <= x1 < len(line):
                        line[x1] = "│"
                        grid_lines[y] = "".join(line)
            return
            
        # Diagonal line
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        x_inc = dx / steps
        y_inc = dy / steps
        
        x, y = x1, y1
        for _ in range(steps):
            x += x_inc
            y += y_inc
            ix, iy = int(round(x)), int(round(y))
            if 0 <= iy < len(grid_lines):
                line = list(grid_lines[iy])
                if 0 <= ix < len(line):
                    if y_inc < 0 and x_inc > 0:
                        line[ix] = "/"
                    elif y_inc > 0 and x_inc > 0:
                        line[ix] = "\\"
                    else:
                        line[ix] = "─"
                    grid_lines[iy] = "".join(line)
