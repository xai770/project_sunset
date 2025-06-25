"""
Skill Library for Cover Letter Generator

This module provides a library of skill bullet points that can be included in cover letters.
Each skill bullet is formatted with a heading and description of expertise.
"""

# Common skill bullet templates that can be selected and customized
SKILL_BULLETS = {
    "platform_management": "- **Plattform-Management und -Entwicklung**: Ich habe erfolgreich eine unternehmensweite Plattform für Software License Management aufgebaut und kontinuierlich weiterentwickelt. Dabei habe ich eng mit Benutzern zusammengearbeitet, um die Plattform an ihre Bedürfnisse anzupassen und Prozesse zu optimieren.",
    
    "data_analysis": "- **Datenanalyse und Reporting**: Ich habe umfassende Erfahrung in der Analyse komplexer Datenstrukturen und der Erstellung aussagekräftiger Reports für das Senior Management. Dabei habe ich verschiedene Datenquellen integriert und Prozesse zur automatisierten Berichterstattung entwickelt.",
    
    "banking_processes": "- **Banking-Prozesse und Innovation**: Als langjähriger Mitarbeiter der Deutschen Bank verfüge ich über ein tiefes Verständnis der Bankprozesse und der Herausforderungen, mit denen die Organisation im Bereich Digitalisierung und Innovation konfrontiert ist. Ich habe in verschiedenen Projekten innovative Lösungen entwickelt, um Prozesse effizienter zu gestalten und Compliance-Anforderungen zu erfüllen.",
    
    "stakeholder_management": "- **Netzwerkaufbau und Stakeholder-Management**: In meinen bisherigen Rollen habe ich erfolgreich bereichsübergreifende Netzwerke aufgebaut und gepflegt. Ich arbeite regelmäßig mit Vertretern aus Technology, Business und Infrastructure zusammen und verstehe die Bedeutung eines effektiven Stakeholder-Managements für den Erfolg von Innovationsinitiativen.",
    
    "it_audit": "- **IT-Audit und Risikomanagement**: Als Team Lead für Proof of Entitlement/Contractual Provisions Management habe ich Prozesse entwickelt, die sicherstellen, dass die Software-Nutzung den vertraglichen Vereinbarungen entspricht. Dies beinhaltete die Analyse von Daten aus Beschaffungssystemen, die Automatisierung von Berichtsprozessen und die Implementierung von KPI-Überwachungen.",
    
    "it_infrastructure": "- **IT-Infrastruktur und Betrieb**: Während meiner Zeit bei Novartis und der Deutschen Bank war ich verantwortlich für das Management der globalen IT-Kategorie, was ein fundiertes Verständnis von IT-Infrastruktur, Betriebssystemen und Datenbanken erforderte.",
    
    "information_security": "- **Information Security und Compliance**: Als Global Lead für Software License Management bei Novartis und Compliance Manager bei der Deutschen Bank war ich für die Einhaltung von Lizenzvereinbarungen und die Identifizierung von Compliance-Risiken verantwortlich.",
    
    "it_controls": "- **Prüfung von IT-Kontrollen**: In meinen verschiedenen Rollen habe ich umfangreiche Erfahrungen in der Bewertung von IT-Kontrollen und der Identifizierung von Schwachstellen gesammelt, insbesondere im Zusammenhang mit Software-Lizenzierung und Vendor Management."
}

def get_available_skills():
    """
    Get the dictionary of available skill bullets
    
    Returns:
        dict: Dictionary of skill bullets with keys and formatted text
    """
    return SKILL_BULLETS

def get_skill_categories():
    """
    Get list of skill categories in a human-readable format
    
    Returns:
        list: List of tuples (key, display_name) for each skill category
    """
    return [(key, key.replace('_', ' ').title()) for key in SKILL_BULLETS.keys()]

def format_custom_skill(skill_text):
    """
    Format custom skill text with proper bullet and formatting
    
    Args:
        skill_text (str): User-provided skill text
        
    Returns:
        str: Formatted skill bullet point
    """
    if not skill_text.startswith("- **"):
        skill_text = f"- **Eigene Expertise**: {skill_text}"
    return skill_text

def select_skills_interactive(available_skills):
    """
    Interactive skill selection from the available skills dictionary
    
    Args:
        available_skills (dict): Dictionary of skill bullets
        
    Returns:
        str: Selected skills formatted as bullet points
    """
    print("\nVerfügbare Skill-Kategorien:")
    for i, (key, value) in enumerate(available_skills.items(), 1):
        print(f"{i}. {key.replace('_', ' ').title()}")
    
    print("\nWählen Sie bis zu 4 Skills (durch Kommas getrennt, z.B. '1,3,4'):")
    selection = input("> ").strip().split(",")
    
    selected_skills = []
    keys = list(available_skills.keys())
    
    for choice in selection:
        try:
            index = int(choice.strip()) - 1
            if 0 <= index < len(keys):
                selected_skills.append(available_skills[keys[index]])
        except ValueError:
            continue
    
    # Allow custom skill entry
    print("\nMöchten Sie einen eigenen Skill-Punkt hinzufügen? (j/n)")
    if input("> ").lower().startswith("j"):
        print("Geben Sie Ihren eigenen Skill-Punkt ein (mit '- **Überschrift**:' beginnen):")
        custom_skill = input("> ").strip()
        selected_skills.append(format_custom_skill(custom_skill))
    
    return "\n\n".join(selected_skills)

# Use absolute imports for all internal modules if needed
# Example: from run_pipeline.cover_letter import template_manager