# Templates Directory

This directory contains template files used by the document generation scripts.

## Templates

- `cover_letter_template.md` - Template for cover letters with placeholder variables

## Cover Letter Template

The cover letter template contains placeholders wrapped in curly braces that are replaced by the `generate_cover_letter.py` script:

- `{company}` - Company name
- `{company_address}` - Company address
- `{date}` - Current date (automatically generated)
- `{job_title}` - Position title
- `{reference_number}` - Job reference number
- `{department}` - Department or team name
- `{primary_expertise_area}` - Primary area of expertise
- `{skill_area_1}` - First skill area
- `{skill_area_2}` - Second skill area
- `{skill_bullets}` - Bullet points of skills
- `{specific_interest}` - Specific interest in the position
- `{relevant_experience}` - Relevant experience
- `{relevant_understanding}` - Relevant understanding
- `{potential_contribution}` - Potential contribution
- `{value_proposition}` - Value proposition

## Usage

The templates are used by the document generation scripts in `scripts/doc_generator/`. 

To modify the cover letter format, edit the template file and the changes will apply to all future generated cover letters.
