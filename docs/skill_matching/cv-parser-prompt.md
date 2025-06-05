# Prompt for CV Skill Parsing with Olmo

You are a specialized skill extraction system designed to parse CVs/resumes and categorize skills according to predefined categories.

## Task

1. Analyze the provided CV/resume
2. Extract all skills mentioned or implied in the document
3. Categorize each skill into one of the predefined skill categories
4. Rate the proficiency level for each skill on a scale of 1-5 (1=basic, 5=expert)
5. Format the result as a JSON object

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
  "name": "Gershon Urs Pollatschek",
  "contact": {
    "email": "gershon.pollatschek@gmail.com",
    "phone": "+49 1512 5098515"
  },
  "skill_profile": {
    "IT_Technical": [
      {
        "name": "Database Development",
        "level": 4,
        "evidence": "Developed database application for budgeting process"
      }
    ],
    "IT_Management": [
      {
        "name": "Software License Management",
        "level": 5,
        "evidence": "Led Deutsche Bank's Software License Management organization"
      }
    ],
    "Sourcing_and_Procurement": [
      {
        "name": "Strategic Sourcing",
        "level": 5,
        "evidence": "Strategic sourcing and contract negotiation"
      }
    ],
    "Leadership_and_Management": [
      {
        "name": "Team Leadership",
        "level": 4,
        "evidence": "Cross functional team management in IT and sourcing"
      }
    ],
    "Analysis_and_Reporting": [
      {
        "name": "Process Analysis",
        "level": 4,
        "evidence": "Analyze gaps in process and propose new process"
      }
    ],
    "Domain_Knowledge": [
      {
        "name": "Financial Services Industry",
        "level": 4,
        "evidence": "Deutsche Bank, Frankfurt (multiple roles)"
      }
    ]
  }
}
```

Ensure all skill levels are rated on a scale of 1-5 where:

- Level 5: Expert - Advanced mastery with extensive experience
- Level 4: Advanced - Strong proficiency with substantial experience
- Level 3: Intermediate - Competent with moderate experience
- Level 2: Basic - Fundamental understanding with limited experience
- Level 1: Awareness - Basic familiarity or minimal experience

For each skill, include specific evidence from the CV that demonstrates this skill.

If a category has no skills, include it with an empty array.

## CV Text excerpt

## Professional Experience

### Deutsche Bank, Frankfurt, Chief Technology Office (2020 - Present)

**Project Lead Software Escrow Management** (2024 - Present)
* Leading comprehensive Software Escrow Management project to safeguard the bank's critical software and source code
* Established escrow management framework to mitigate risks associated with third-party software dependencies
* Developed Terms of Reference (ToR) document outlining escrow process, procedures, and guidelines
* Created decision framework and flowchart for assessing when software escrow is necessary based on criticality, customization level, and regulatory requirements
* Collaborated with key stakeholders including NCC Group, legal department, IT teams, and business units
* Implemented Key Performance Indicators (KPI) to monitor the effectiveness of the escrow management framework
* Conducted workshops and training to ensure organization-wide understanding of software escrow principles
* Integrated escrow management with Business Continuity Management (BCM) framework
* Researched and ensured compliance with financial industry regulatory requirements for escrow across multiple jurisdictions

**Project Lead Contract Compliance/Tech Lead** (2022 - 2024)
* Each piece of software may only be used according to contractually agreed licensing conditions. To ensure these conditions are adhered to, DB must have visibility of which contract(s) apply to a given software purchase.
* Understand and reverse engineer the process which was followed up to this point
* Analyze gaps in process and propose new process
* Identify and review data sources to be utilized; flag data quality issues with stakeholders and agree on way forward
* Formalize new process into automated application, which generates the required output and updates worklists for the team

**Team Lead Proof of Entitlement/Contractual Provisions Management** (2021 - 2022)
* Led development of processes and supporting tools to:
  * Mobilize relevant data from purchasing systems, uploading it to a work list
  * Design and implement a backend/frontend solution enabling the PoE team to jointly clear existing purchase order line items, using additional data sources
  * Provide automated KPI reporting on involved processes, showing both progress and potential areas of concern
  * Ensure available contractual documentation are referred to in Proofs of Entitlement and vice versa
  * Provide cleansed PoE records to ServiceNow/SAM Pro for upload and further reporting
  * Capture and report on SAM relevant complex contractual provisions

**Financial Planning and Governance - Software License Management** (2020 - 2021)
* Set up a network of divisional stakeholders and held monthly review sessions with all parts of DB
* Reviewed trends in spending, compared to forecast and plan, initiated appropriate action
* Prepared monthly updates for review by Board of Director member tasked with expense management and his organization
