# Prompt-Input-Output (PIO) Specification for Skill Matching System

This document details the exact prompts, expected inputs, and desired outputs for each component of our skill matching system using Ollama/OWUI.

## 1. CV Parsing Component

### Prompt for CV Parser (llama3.2)

```
You are a specialized skill extraction system designed to parse CVs or resumes according to a multi-dimensional skill framework.

FRAMEWORK EXPLANATION:
1. Ontological Categories:
   - Tool/Technological: Skills bound to specific tools or technologies
   - Methodological: Process-oriented approaches and techniques
   - Cognitive: Mental capacities or reasoning approaches
   - Social: Interpersonal capacities and abilities
   - Dispositional: Character traits enabling effectiveness
   - Meta-Skills: Skills about acquiring and managing other skills

2. Abstraction Levels:
   - Level 1: Concrete operations (direct manipulation)
   - Level 2: Procedural coordination (sequencing operations)
   - Level 3: Domain management (applying principles)
   - Level 4: Strategic planning (abstract goal-directed activity)
   - Level 5: Systemic understanding (whole systems comprehension)

3. Other Dimensions:
   - Knowledge Components: Specific elements of knowledge required for the skill
   - Contexts: Environments where the skill is applied
   - Functions: Purposes the skill serves
   - Proficiency Level: Estimated expertise level (1-10)

TASK:
Analyze the following CV/resume and extract all skills mentioned or implied. For each skill:
1. Identify the skill name
2. Categorize it according to the ontological framework
3. Assign an abstraction level (1-5)
4. List key knowledge components
5. Identify contexts where it would be applied
6. Define the functions it serves
7. Estimate the proficiency level (1-10) based on experience and achievements
8. Provide evidence from the text that indicates this skill

FORMAT OUTPUT as valid JSON following this schema:
{
  "personal": {
    "name": "",
    "contact": {}
  },
  "skills": [
    {
      "name": "",
      "ontological_category": "",
      "abstraction_level": 0,
      "knowledge_components": [],
      "contexts": [],
      "functions": [],
      "proficiency_level": 0,
      "evidence": []
    }
  ]
}

CV TEXT:
# Gershon Urs Pollatschek

Quellenstraße 1A, 64385 Reichelsheim, Germany  
+49 1512 5098515  
gershon.pollatschek@gmail.com

## Personal Information
* Birth date: 24.12.1964
* Married, 1 son
* German citizen
* First language: German
* Fluent in spoken and written English
* Fluent in spoken and written Hebrew

## Summary
I originally come from an IT background, starting out as an application developer, working many years as an IT management consultant, and finally finding my way into IT sourcing. I have always retained a vivid, personal, and professional interest in IT and find this essential to drive real value in IT Sourcing.

I am very much at home in the IT category. What I like most is being able to use my knowledge and skills to mobilize a diverse team, set real targets, devise a solid plan, and ultimately lead the team to deliver above stakeholder expectations.

## Core Competencies

**Sourcing and Vendor Management**
• Management and Governance of IT sourcing, including software, hardware, telecommunications, application development, IT consulting and contractors
• Enterprise Information Technology contract and asset management
• Strategic sourcing and contract negotiation
• Development and implementation of enterprise-wide end-to-end sourcing strategies and processes
• Design and implementation of vendor relationship management processes
• Software License and Vendor conflict management
• Transactional procurement management
• Software Escrow management and vendor risk mitigation

**Management**
• IT project and change management
• Spend, sourcing benefits and targets planning, tracking and reporting
• Cross functional team management in IT and sourcing
• Risk management and business continuity planning
• Regulatory compliance and governance implementation

**Information Technology**
• Ontology/Taxonomy development
• Data Warehouse design and implementation
• Rule based reporting and analysis database design and implementation
• Rollout and management of cross divisional IT systems
• Programming and application design experience
• Decision framework development for technology risk assessment

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

### Self-Employed (2016 - 2020)

**Development of Analysis Framework for Structured Text Documents**
* Created tool to track the status of each provision in all documents during negotiations with large vendors, streamlining the process
* Generated ontologies for structured content, such as scientific articles, legal texts, and technical documents
* Developed prediction of relevant key phrases, based on statistical models and user input, utilizing machine learning to formalize conclusions
* Implemented reporting of match/no match condition of paragraphs between document sets

### Novartis, Basel (2010 - 2016)

**Global Sourcing IT Change Management and Governance** (2012 - 2015)
* Responsible for the governance of the global IT category of the Novartis group
* Managed core aspects of the category team consisting of 15+ sub-category managers and business partners
* Set annual targets and provided regular reporting of spend and benefits
* Implemented standard operating procedures for sourcing and support processes (Supply Chain Finance, SAP CLM, SavePlan, eSourcing)
* Supported savings recognition and reporting, reporting to top management
* Designed, implemented and maintained reporting backend application, integrating feeds from various data sources and consolidating these into standardized KPI reporting

**Global Lead, Software License Management** (2010 - 2012)
* Served as Group-wide designated single point of contact for all software compliance challenges
* Managed major software compliance challenges from first contact to final settlement (Interwoven, SAS, SAP)
* Provided guidance to Novartis stakeholders on best practice of software compliance management
* Interfaced with the Novartis legal team and served as subject matter expert in contract negotiations and contract template updates
* Worked with internal development team to move Software Compliance Management into proactive mode by analyzing existing applications for possible licensing gaps

**Global Lead, Mobile Telecom Demand Management** (2010 - 2012)
* Led group-wide initiative to manage demand in mobile telecom services to contain spend, improve basket of goods and lower cost
* Ran project to evaluate benefits of using a Telecoms Expense Management Service (TEMS) in Basel
* Provided leading TEMS providers with detailed analysis of Connection Data Records (CDRs) to obtain and verify savings forecasts of up to 30% off cost
* Managed the TEMS portion of the Vodaphone MSA drafting and finalization as part of the Novartis negotiation team
* Worked with business partners to inform them of available savings levers, such as personal cost transparency, TEMs, VoIP, BYOD and policy adjustments
* Collaborated with sourcing leads to report spend and savings

**Software Category Manager** (2010 - 2012)
* Led SAP Enterprise License Management Program
* Redesigned the group-wide annual license measurement process
* Designed frontend and backend systems to collect, maintain, analyze and report all information relevant to SAP license management
* Prevented unintended spending for license true-ups using obtained information
* Collected and aggregated future license demands
* Negotiated agreement to purchase licenses in bulk from SAP from a strong position, resulting in significant benefits

### Deutsche Bank AG, Frankfurt (2005 - 2010)

**Software Licenses and Services Vendor Manager (Global Banking IT)** (2008 - 2010)
* Led Software Licenses and Services team for Deutsche Bank's Global Banking IT division globally
* Led Global Banking team in negotiations of strategic five-year outsourcing deal for software testing services to IBM (12m€+)
* Helped establish steering committee to monitor KPIs, manage change requests and disputes
* Supervised mandatory outsourcing review, ensuring compliance to national laws, regulations and internal policies
* Led centralized rate reduction initiative for contractors in Germany and US, resulting in calculated savings of 1.8m€
* Managed 70+ new contracts (46 Software, 18 time and material, 12 fixed price) amounting to 8m€ and saving 680k€+ in the software space
* Participated in team introducing and piloting end-to-end contract management processes and tools (HP mercury)
* Developed and enforced rules and guidelines for contract compliance
* Designed and built suite of automated reports (dashboard), publicizing vendor management activities by vendor, location, and program

**Software Category Manager (Global Procurement)** (2005 - 2008)
* Led software category management in EMEA and co-led the category globally
* Initiated and completed transactions with strategic software vendors that concluded in significant benefits (Microsoft, HP, WebMethods, Adobe)
* Collaborated with senior technology architects from CIO organizations to identify strategic vendors and implement terms and conditions supporting DB's business objectives
* Supported negotiation of new Enterprise Agreements with strategic vendors (Microsoft, Adobe, Hummingbird) and led contractual implementation including annual "True-Ups"
* Compiled existing DB contract templates into a dynamic contract master (189+ clauses) used to assess compliance risks of running contracts
* Initiated and managed vendor portal onboarding project for strategic vendors to upload contracts, catalogues, application signatures and license reports

**Global Software Compliance Manager (Global Procurement)** (2005 - 2007)
* Led Deutsche Bank's Software License Management organization
* Built and trained global team of 200+ License managers, Senior License Managers and Product Managers
* Wrote and maintained software policy and process documentation
* Resolved licensing issues with vendors such as Microsoft, Adobe, Borland, Bea, The Mathworks and Quest
* Generated demand-based software catalogues and used online/offline auctions to establish best prices
* Trained and utilized SLM team to handle centralized software distribution and procurement (12,000 requests per month), generating approximately 2M€ systematic savings annually

### Independent Producer for Public Television, Mainz (2002 - 2005)
* Produced video material for Germany's largest television station, the ZDF (Zweites Deutsches Fernsehen)
* Active in scripting, filming, producing, editing and CGI
* Productions included:
  * "Der brennende Dornbusch – Glanz und Elend der Juden in Europa" (3x45min, historical documentation)
  * "Das Wunder in der Wüste – Moses und der Aufbruch in die Freiheit" (45min, reenactment and documentary)
  * "37 Grad - Wie schön, dass Du geboren bist" (30min, documentary)
  * "37 Grad – Einmal drüber und schon sauber" (30min, documentary)

### Freelance Contractor (1996 - 2001)

**Deutsche Bank, Vendor Manager, Frankfurt** (2001 - 2002)
* Part of project eBranch, responsible for setting up vendor management team
* Modelled process framework for vendor management according to CMM (Capability Maturity Management)
* Researched and evaluated key technologies (functionality mapping)
* Set up and ran Requests for Proposal
* Compiled and evaluated project scenarios by risk, cost, usability and TCO
* Wrote contract specifications and reviewed them with internal and external partners
* Participated in contract negotiations, managed changes in vendor relationships, and was responsible for quality assurance of deliverables

**Commerzbank, Application Architect, Frankfurt** (1998 - 1999)
* Project manager of project ZUM (Zentrales User-Management) 
* Designed and implemented centralized user and IT resource requirements management for Deutsche Post
* Designed first prototypes as proof of concept
* Evaluated feasible software solutions
* Managed selection process and onboarding of chosen supplier
* Populated application with first set of data by integrating available data sources from LDAP and legacy systems
* Coordinated application development, rollout and coaching of the new team

**F. Hoffmann – La Roche, Rollout Manager, Basel** (1998)
* Member of development team for "Common Office Environment" (COE/2.1) – the standardized, Global Desktop environment of Client/Server-based systems
* Evaluated and fed back user test results into procedures for global rollout and localization of installed systems
* Documented core systems management processes, such as software distribution, license management and daily administrative tasks

**Dresdner Bank, Information Architect, Frankfurt** (1997 - 1998)
* Part of global effort to design and implement a new information desktop for Dresdner Private Banking
* Collected information requirements through series of business managers worldwide
* Distilled information requirements into an information desktop, presented to the global business manager community
* Planned, staffed, and budgeted implementation of information desktop

**Deutsche Bahn, Helpdesk and Rollout Manager, Frankfurt** (1996 - 1997)
* Worked as part of project team "Bürokommunikation unternehmensweit (BKU)" to establish helpdesk support for first Client/Server environment
* Defined procedures for identification and quick classification of recurring errors and their resolution
* Helped to outsource helpdesk to external vendor
* Planned rollout of active components of Deutsche Bahn's network

### Agricultural Research Organization, Application Developer, Israel (1991 - 1996)
* Worked in the Israeli offices of the International Union for the Protection of new Plant Varieties (UPOV) in Beit-Dagan
* Automatized daily workflows via macro programming
* Developed database application for budgeting process and to support administrative tasks

## Military Service

**Active Service in the Israeli Military** (1987 - 1989)
* Served as non-fighting professional in the medical corps
* Training as NCO for disaster control and civil protection (reserve)

**Reserve Duty** (1990 - 1996)
* Active duty during Gulf war as civil defense emergency unit
* Active duty as local defense unit

## Education

* **Self-study of Computer Programming** (1991 - 1996)
  * Database programming, Application design, Pascal, Prolog
* **Studies of Philosophy** (1988 - 1991)
  * Bar-Ilan University
  * Focus on theory of language, formal logic, Jewish mysticism, information theory
* **High School Diploma** (1983)
  * "De Shalit" Highschool in Rechovot, Israel
```

### Expected Input

The CV text in plain format, such as the Markdown CV of Gershon Urs Pollatschek.

### Expected Output

```json
{
  "personal": {
    "name": "Gershon Urs Pollatschek",
    "contact": {
      "email": "gershon.pollatschek@gmail.com",
      "phone": "+49 1512 5098515",
      "address": "Quellenstraße 1A, 64385 Reichelsheim, Germany"
    }
  },
  "skills": [
    {
      "name": "Software License Management",
      "ontological_category": "Methodological",
      "abstraction_level": 4,
      "knowledge_components": [
        "software compliance management",
        "license agreements",
        "vendor relationship management",
        "contract negotiations",
        "license optimization"
      ],
      "contexts": [
        "enterprise IT",
        "global banking",
        "pharmaceutical industry",
        "procurement"
      ],
      "functions": [
        "regulatory compliance",
        "cost optimization",
        "risk management",
        "asset management"
      ],
      "proficiency_level": 9,
      "evidence": [
        "Led Deutsche Bank's Software License Management organization",
        "Global Lead, Software License Management at Novartis",
        "Led SAP Enterprise License Management Program",
        "Managed major software compliance challenges at Novartis"
      ]
    },
    {
      "name": "IT Sourcing Strategy",
      "ontological_category": "Methodological",
      "abstraction_level": 5,
      "knowledge_components": [
        "strategic vendor selection",
        "cost-benefit analysis",
        "contract negotiation",
        "demand management",
        "outsourcing models"
      ],
      "contexts": [
        "enterprise IT",
        "procurement",
        "global banking",
        "pharmaceutical industry"
      ],
      "functions": [
        "cost optimization",
        "value creation",
        "risk mitigation",
        "vendor governance"
      ],
      "proficiency_level": 8,
      "evidence": [
        "Led Global Banking team in negotiations of strategic five-year outsourcing deal",
        "Led software category management in EMEA and co-led the category globally",
        "Initiated and completed transactions with strategic software vendors"
      ]
    }
    // Additional skills would continue here
  ]
}
```

## 2. Job Description Parsing Component

### Prompt for Job Description Parser (llama3.2)

```
You are a specialized skill extraction system designed to parse job descriptions according to a multi-dimensional skill framework.

FRAMEWORK EXPLANATION:
1. Ontological Categories:
   - Tool/Technological: Skills bound to specific tools or technologies
   - Methodological: Process-oriented approaches and techniques
   - Cognitive: Mental capacities or reasoning approaches
   - Social: Interpersonal capacities and abilities
   - Dispositional: Character traits enabling effectiveness
   - Meta-Skills: Skills about acquiring and managing other skills

2. Abstraction Levels:
   - Level 1: Concrete operations (direct manipulation)
   - Level 2: Procedural coordination (sequencing operations)
   - Level 3: Domain management (applying principles)
   - Level 4: Strategic planning (abstract goal-directed activity)
   - Level 5: Systemic understanding (whole systems comprehension)

3. Other Dimensions:
   - Knowledge Components: Specific elements of knowledge required for the skill
   - Contexts: Environments where the skill is applied
   - Functions: Purposes the skill serves
   - Proficiency Level: Required expertise level (1-10)
   - Requirement Level: Essential or Desirable

TASK:
Analyze the following job description and extract all skills required or preferred. For each skill:
1. Identify the skill name
2. Categorize it according to the ontological framework
3. Assign an abstraction level (1-5)
4. List key knowledge components
5. Identify contexts where it would be applied
6. Define the functions it serves
7. Estimate the required proficiency level (1-10)
8. Determine if the skill is essential or desirable
9. Provide evidence from the text that indicates this skill requirement

FORMAT OUTPUT as valid JSON following this schema:
{
  "position": "",
  "company": "",
  "skills": [
    {
      "name": "",
      "ontological_category": "",
      "abstraction_level": 0,
      "knowledge_components": [],
      "contexts": [],
      "functions": [],
      "proficiency_level": 0,
      "requirement_level": "",
      "evidence": []
    }
  ]
}

JOB DESCRIPTION:
{job_description}
```

### Expected Input

A job description text in plain format.

### Expected Output

```json
{
  "position": "IT Vendor Management Director",
  "company": "Global Financial Services Corporation",
  "skills": [
    {
      "name": "IT Vendor Relationship Management",
      "ontological_category": "Methodological",
      "abstraction_level": 4,
      "knowledge_components": [
        "vendor governance frameworks",
        "performance evaluation",
        "service level agreements",
        "escalation management",
        "strategic partnering"
      ],
      "contexts": [
        "enterprise IT",
        "financial services",
        "multinational environment",
        "regulated industry"
      ],
      "functions": [
        "relationship optimization",
        "performance monitoring",
        "strategic alignment",
        "risk management"
      ],
      "proficiency_level": 8,
      "requirement_level": "Essential",
      "evidence": [
        "Lead and develop our IT vendor management organization",
        "Develop and implement vendor governance frameworks",
        "10+ years of experience in IT vendor management"
      ]
    },
    {
      "name": "Contract Negotiation",
      "ontological_category": "Methodological",
      "abstraction_level": 3,
      "knowledge_components": [
        "terms and conditions",
        "pricing models",
        "service level definition",
        "compliance requirements",
        "legal terminology"
      ],
      "contexts": [
        "enterprise IT procurement",
        "software licensing",
        "outsourcing services",
        "cloud services"
      ],
      "functions": [
        "cost optimization",
        "risk mitigation",
        "value maximization",
        "compliance assurance"
      ],
      "proficiency_level": 7,
      "requirement_level": "Essential",
      "evidence": [
        "Lead complex contract negotiations with strategic vendors",
        "Experience negotiating enterprise agreements",
        "Track record of achieving cost savings in vendor contracts"
      ]
    }
    // Additional skills would continue here
  ]
}
```

## 3. Skill Matching Component

### Prompt for Skill Matcher (gemma3.1b)

```
You are a specialized skill matching system that evaluates the relationship between a candidate's skills and job requirements using a mathematical framework.

MATHEMATICAL FRAMEWORK:
1. For each skill pair evaluation, calculate:
   - Comparability: Skills must be in same ontological category and similar abstraction level
   - Knowledge Overlap: Jaccard similarity of knowledge components
   - Context Overlap: Jaccard similarity of contexts
   - Function Overlap: Jaccard similarity of functions
   - Level Ratio: min(candidate_level, job_level)/max(candidate_level, job_level)
   - Overall Compatibility: Weighted average of above metrics

2. Relationship Types:
   - Subset: Candidate skill is specialized version of job skill
   - Superset: Candidate skill encompasses job skill
   - Adjacent: Significant knowledge overlap
   - Neighboring: Shared context but different functions
   - Skill Level Disparity: Similar domain but different levels
   - Analogous: Similar functions in different contexts
   - Transferable: Some knowledge applies but not direct match
   - Weakly Related: Minimal meaningful overlap
   - Not Comparable: Different ontological categories or abstraction levels too different

TASK:
1. For each job skill, find the best matching candidate skill
2. Calculate compatibility percentage for each match using weighted formula:
   - 40% Knowledge Overlap
   - 30% Context Overlap
   - 20% Function Overlap
   - 10% Level Ratio
3. Determine relationship type for each match
4. Calculate overall match percentage as average of all job skill matches
5. Identify skill gaps (job skills with no good match)
6. Provide final recommendation:
   - Strong Match: >75% overall match AND no essential skill gaps
   - Moderate Match: 50-75% overall match OR has some essential skill gaps
   - Weak Match: <50% overall match OR missing multiple essential skills

CANDIDATE SKILLS:
{candidate_skills_json}

JOB SKILLS:
{job_skills_json}

FORMAT OUTPUT as valid JSON following this schema:
{
  "overall_match_percentage": 0,
  "matches": [
    {
      "job_skill": "",
      "candidate_skill": "",
      "compatibility_percentage": 0,
      "relationship_type": "",
      "knowledge_overlap": 0,
      "context_overlap": 0,
      "function_overlap": 0,
      "level_ratio": 0
    }
  ],
  "gaps": [
    {
      "job_skill": "",
      "requirement_level": "",
      "potential_partial_matches": []
    }
  ],
  "recommendation": "",
  "explanation": ""
}
```

### Expected Input

Two JSON objects representing:
1. The structured candidate skills from the CV parser
2. The structured job skills from the job description parser

### Expected Output

```json
{
  "overall_match_percentage": 78,
  "matches": [
    {
      "job_skill": "IT Vendor Relationship Management",
      "candidate_skill": "Vendor Management",
      "compatibility_percentage": 85,
      "relationship_type": "Adjacent",
      "knowledge_overlap": 0.82,
      "context_overlap": 0.90,
      "function_overlap": 0.75,
      "level_ratio": 1.0
    },
    {
      "job_skill": "Contract Negotiation",
      "candidate_skill": "Strategic Sourcing and Contract Negotiation",
      "compatibility_percentage": 92,
      "relationship_type": "Superset",
      "knowledge_overlap": 0.95,
      "context_overlap": 0.85,
      "function_overlap": 0.95,
      "level_ratio": 0.89
    },
    {
      "job_skill": "Software License Management",
      "candidate_skill": "Software License Management",
      "compatibility_percentage": 98,
      "relationship_type": "Identical",
      "knowledge_overlap": 0.96,
      "context_overlap": 1.0,
      "function_overlap": 1.0,
      "level_ratio": 0.95
    }
    // Additional matches would continue here
  ],
  "gaps": [
    {
      "job_skill": "Cloud Service Provider Management",
      "requirement_level": "Desirable",
      "potential_partial_matches": ["Vendor Management", "IT Sourcing Strategy"]
    }
  ],
  "recommendation": "Strong Match",
  "explanation": "The candidate shows exceptional compatibility with 85% of the essential job skills, especially in software license management, contract negotiation, and vendor relationship management. While there is a gap in cloud service provider management, this is listed as desirable rather than essential, and the candidate's strong vendor management skills could transfer to this domain with minimal training."
}
```

## 4. Implementation Testing Process

1. **Initial Setup Testing**:
   - Test CV Parser with Gershon's CV
   - Verify skill extraction accuracy and categorization
   - Manually review and adjust the output as needed

2. **Job Description Testing**:
   - Test with 2-3 sample job descriptions in IT procurement/vendor management
   - Verify skill requirement extraction
   - Adjust prompt based on results

3. **Matching Algorithm Testing**:
   - Create test cases with known expected outcomes (high match, moderate match, low match)
   - Test the matcher with various skill combinations
   - Fine-tune weights and thresholds based on results

4. **End-to-End Pipeline Testing**:
   - Process a real CV and job description through the complete pipeline
   - Compare results with human expert assessment
   - Document discrepancies and refine the system

## 5. Evaluation Criteria

1. **Precision**: Are the extracted skills actually mentioned/implied in the text?
2. **Recall**: Are all relevant skills being extracted?
3. **Categorization Accuracy**: Are skills correctly categorized?
4. **Match Accuracy**: Do the match recommendations align with expert human judgment?
5. **Explainability**: Are the reasons for match/non-match clear and logical?
