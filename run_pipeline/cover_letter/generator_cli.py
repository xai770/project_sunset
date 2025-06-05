"""
CLI Interface for Cover Letter Generator

This module provides command-line interface functionality for the cover letter generator,
including interactive input collection and argument parsing.
"""

import argparse
import logging
import sys
import os

# Configure logger
logger = logging.getLogger(__name__)

def get_input_with_default(prompt, default=None):
    """
    Get user input with a default value
    
    Args:
        prompt (str): Prompt to display to the user
        default (str, optional): Default value to use if no input is provided
        
    Returns:
        str: User input or default value
    """
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    else:
        return input(f"{prompt}: ").strip()

def interactive_mode(profile):
    """
    Run in interactive mode to collect job details from the user
    
    Args:
        profile (dict): User profile data for default values
        
    Returns:
        dict: Job details collected from the user
    """
    print("=== Anschreiben-Generator ===")
    
    # Collect job details
    job_details = {}
    
    # Basic job information
    job_details["job_id"] = get_input_with_default("Job ID (z.B. 62765)", 
                                                 profile.get("job_id", ""))
    job_details["job_title"] = get_input_with_default("Stellenbezeichnung (z.B. Senior Business Functional Analyst)",
                                                    profile.get("job_title", ""))
    job_details["reference_number"] = get_input_with_default("Referenznummer (z.B. R0385120)",
                                                          profile.get("reference_number", ""))
    
    # Company information
    job_details["company"] = get_input_with_default("Unternehmen (z.B. Deutsche Bank AG)",
                                                  profile.get("company", "Deutsche Bank AG"))
    job_details["company_address"] = get_input_with_default("Unternehmensadresse (z.B. 60262 Frankfurt)",
                                                          profile.get("company_address", "60262 Frankfurt"))
    
    # Job details
    job_details["department"] = get_input_with_default("Abteilung/Team (z.B. im Innovation Team)",
                                                     profile.get("department", ""))
    
    # Expertise and skills
    job_details["primary_expertise_area"] = get_input_with_default(
        "Primärer Expertisenbereich (z.B. der Analyse von Geschäftsprozessen und der Entwicklung von innovativen Lösungen)",
        profile.get("primary_expertise_area", "der Analyse von Geschäftsprozessen und der Entwicklung von innovativen Lösungen"))
    
    job_details["skill_area_1"] = get_input_with_default(
        "Kompetenzbereich 1 (z.B. Prozessoptimierung)",
        profile.get("skill_area_1", "Prozessoptimierung"))
    
    job_details["skill_area_2"] = get_input_with_default(
        "Kompetenzbereich 2 (z.B. Plattformentwicklung)",
        profile.get("skill_area_2", "Plattformentwicklung"))
    
    # Skills selection
    print("\nWählen Sie relevante Fähigkeiten für diese Position aus:")
    job_details["skill_bullets"] = skill_library.select_skills_interactive(skill_library.get_available_skills())
    
    # Position specific details
    job_details["specific_interest"] = get_input_with_default(
        "Was reizt besonders an der Position? (z.B. die Möglichkeit, an der Gestaltung der Innovationskultur mitzuwirken...)",
        profile.get("specific_interest", "die Möglichkeit, an der Gestaltung der Innovationskultur der Deutschen Bank mitzuwirken und durch die Optimierung der Prozesse einen direkten Beitrag zur digitalen Transformation der Bank zu leisten"))
    
    job_details["relevant_experience"] = get_input_with_default(
        "Relevante Erfahrung (z.B. der Implementierung von technischen Lösungen)",
        profile.get("relevant_experience", "der Implementierung von technischen Lösungen"))
    
    job_details["relevant_understanding"] = get_input_with_default(
        "Relevantes Verständnis (z.B. Geschäftsprozesse und Benutzeranforderungen)",
        profile.get("relevant_understanding", "Geschäftsprozesse und Benutzeranforderungen"))
    
    job_details["potential_contribution"] = get_input_with_default(
        "Möglicher Beitrag (z.B. Prozesse erfolgreich zu optimieren)",
        profile.get("potential_contribution", "die Prozesse erfolgreich zu optimieren und zu einem wertvollen Werkzeug für alle Teams zu machen"))
    
    job_details["value_proposition"] = get_input_with_default(
        "Wertversprechen (z.B. erfolgreiche Schulungen durchzuführen)",
        profile.get("value_proposition", "erfolgreiche Schulungen durchzuführen und neue Teams effektiv einzuarbeiten"))
    
    return job_details

def parse_arguments(default_template_path, default_output_dir):
    """
    Parse command-line arguments for the cover letter generator
    
    Args:
        default_template_path (str): Default template path to use
        default_output_dir (str): Default output directory to use
        
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Anschreiben-Generator für Bewerbungen")
    parser.add_argument("-t", "--template", default=default_template_path,
                        help="Pfad zur Anschreiben-Vorlage")
    parser.add_argument("-o", "--output", default=default_output_dir,
                        help="Ausgabeverzeichnis für das generierte Anschreiben")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Interaktiver Modus für die Eingabe der Stellendetails")
    parser.add_argument("-j", "--job-id", help="Job ID")
    parser.add_argument("--job-title", help="Stellenbezeichnung")
    parser.add_argument("--reference", help="Referenznummer")
    
    return parser.parse_args()

def handle_output_display(filepath, content):
    """
    Handle displaying the output to the user
    
    Args:
        filepath (str): Path where the file was saved
        content (str): Content of the cover letter
        
    Returns:
        None
    """
    print(f"\nAnschreiben erfolgreich gespeichert: {filepath}")
    print("\nMöchten Sie das generierte Anschreiben anzeigen? (j/n)")
    if input("> ").lower().startswith("j"):
        print("\n" + "="*50 + "\n")
        print(content)
        print("\n" + "="*50)

if __name__ == "__main__":
    # Allow running as a script for testing
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from run_pipeline.cover_letter import skill_library