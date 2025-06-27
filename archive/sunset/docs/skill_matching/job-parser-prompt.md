	# Prompt for Job Description Skill Parsing
	
	You are a specialized skill extraction system designed to parse job descriptions and categorize skills according to predefined categories.
	
	## Task
	
	1. Analyze the provided job description
	2. Extract all skills required or preferred for the position
	3. Categorize each skill into one of the predefined skill categories
	4. Rate the required level for each skill on a scale of 1-5 (1=basic, 5=expert)
	5. Indicate if each skill is essential or desirable
	6. Format the result as a JSON object
	
	## Skill Categories to Use
	
	Use ONLY these exact skill categories for categorization:
	- IT_Technical: Technical IT skills like programming, database development, system architecture
	- IT_Management: IT governance, project management, software lifecycle management skills
	- Sourcing_and_Procurement: Skills related to vendor management, contracts, procurement
	- Leadership_and_Management: Team leadership, process management, stakeholder engagement
	- Analysis_and_Reporting: Analytical skills, data processing, reporting, decision frameworks
	- Domain_Knowledge: Industry-specific knowledge and expertise
	
	## Output Format
	
	Format your output as a JSON object with the following structure:
	
	```json
	{
	  "position": "Job title from the description",
	  "company": "Company name if available, otherwise 'Not specified'",
	  "skill_requirements": {
	    "IT_Technical": [
	      {
	        "name": "Name of the skill",
	        "level": 1-5 rating of required expertise,
	        "importance": "Essential or Desirable"
	      }
	    ],
	    "IT_Management": [
	      {
	        "name": "Name of the skill",
	        "level": 1-5 rating of required expertise,
	        "importance": "Essential or Desirable"
	      }
	    ],
	    "Sourcing_and_Procurement": [
	      {
	        "name": "Name of the skill",
	        "level": 1-5 rating of required expertise,
	        "importance": "Essential or Desirable"
	      }
	    ],
	    "Leadership_and_Management": [
	      {
	        "name": "Name of the skill",
	        "level": 1-5 rating of required expertise,
	        "importance": "Essential or Desirable"
	      }
	    ],
	    "Analysis_and_Reporting": [
	      {
	        "name": "Name of the skill",
	        "level": 1-5 rating of required expertise,
	        "importance": "Essential or Desirable"
	      }
	    ],
	    "Domain_Knowledge": [
	      {
	        "name": "Name of the skill",
	        "level": 1-5 rating of required expertise,
	        "importance": "Essential or Desirable"
	      }
	    ]
	  }
	}
	```
	
	If no skills belong to a category, include that category with an empty array.
	
	## Job Description
	
	{ "structured_description": {
	      "title": "Alternative Products Manager",
	      "responsibilities": [
	        "Guidance and project management of the conception, development, structuring, and introduction of new Alternative Products with a focus on Germany, including internal approval procedures.",
	        "Advancement of the product strategy, identification of opportunities for product innovations, and creation of business cases for new product developments or product modifications.",
	        "Staying up-to-date with the introduction of new products by competitors, market trends, structural innovations, and evolving regulatory changes.",
	        "Support for Alternative Product Development Team worldwide in structuring and introducing new products, particularly UK Product Development Team.",
	        "Close collaboration with stakeholders at Deutsche Bank and DWS, including senior management, portfolio managers, alternative product management teams, sales teams, fund operations, finance department, tax department, legal department, and compliance department.",
	        "Central point of contact for Alternative Products within the Alternative Organization for products launched and sold in Germany.",
	        "Management and support of stakeholder relationships in the Alternative area as well as throughout the entire DWS organization.",
	        "Management and support of multiple projects worldwide that impact on the Alternative Business, with a focus on Germany.",
	        "Administration of the global product pipeline, with emphasis on Germany, and reporting on new initiatives status.",
	        "Preparation of materials, templates, and input into databases.",
	        "Support for local and global ad-hoc projects in conjunction with product development activities."
	      ],
	      "requirements": [
	        "Bachelor's degree or equivalent qualification/relevant work experience.",
	        "8-10 years of experience in an investment-related or product development function.",
	        "Comprehensive understanding of alternative asset classes (real estate, infrastructure, private credit) and structures (AIFs in Germany, including special funds, open funds, partnerships, AIF structures).",
	        "Excellent project management and organizational skills with attention to detail and prioritization abilities.",
	        "Results-oriented self-motivation with the ability to work independently and as part of a team.",
	        "Ability to build close relationships with various teams and individuals and influence results.",
	        "Solution-oriented, creative, and proactive in suggesting new strategies/lifestyles.",
	        "Openness to new challenges with acute engagement and self-development approach.",
	        "Mastery of Microsoft Office applications.",
	        "Excellent communication skills in German and English (written and verbal)."
	      ]
	    }}


---
## olmo2:latest output

{
  "position": "Alternative Products Manager",
  "company": "Deutsche Bank or DWS"
  "skill_requirements": {
    "IT_Technical": [
      {
        "name": "Microsoft Office Applications",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "IT_Management": [
      {
        "name": "Project Management",
        "level": 5,
        "importance": "Essential"
      },
      {
        "name": "Organizational Leadership",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "Sourcing_and_Procurement": [
      {
        "name": "Vendor Management",
        "level": 4,
        "importance": "Desirable"
      }
    ],
    "Leadership_and_Management": [
      {
        "name": "Team Leadership",
        "level": 5,
        "importance": "Essential"
      },
      {
        "name": "Stakeholder Engagement",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "Analysis_and_Reportin": [
      {
        "name": "Data Analysis",
        "level": 4,
        "importance": "Desirable"
      },
      {
        "name": "Decision Frameworks",
        "level": 4,
        "importance": "Desirable"
      }
    ],
    "Domain_Knowledge": [
      {
        "name": "Alternative Asset Classes",
        "level": 5,
        "importance": "Essential"
      },
      {
        "name": "Regulatory Changes",
        "level": 4,
        "importance": "Desirable"
      }
    ]
  }
}