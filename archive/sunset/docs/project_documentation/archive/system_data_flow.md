# Project Sunset - System Data Flow

This document visualizes the data flow through the job application automation system.

## Overall System Data Flow (Improved)

```mermaid
flowchart TD
    %% Main Modules
    scraper[Job Scraper Module]
    decomposer[Skill Decomposer Module]
    matcher[Skill Matching]
    selfassess[Self-Assessment Generator]
    docgen[Document Generator]
    emailer[Email Sender]
    
    %% Data Stores
    jobPostings[(Job Postings)]
    jobDecompositions[(Job Decompositions)]
    matchResults[(Match Results)]
    skillDB[(Skill Database)]
    cvFiles[(CV Files)]
    assessments[(Self-Assessments)]
    coverLetters[(Cover Letters)]
    sentLog[(Sent Documents Log)]
    consolidated[(Consolidated Jobs)]
    
    %% User Interaction Points
    userJobConfig[User Job Config]
    userSkillConfig[User Skill Config]
    userCoverReview[User Cover Letter Review]
    
    %% Decision Points
    matchDecision{Match Score > Threshold?}
    
    %% Main Flow
    userJobConfig -->|configuration| scraper
    scraper -->|saves raw job data| jobPostings
    jobPostings -->|job requirements| decomposer
    decomposer -->|structured job requirements| jobDecompositions
    jobDecompositions -->|consolidated data| consolidated
    
    userSkillConfig -->|skill definitions| skillDB
    cvFiles -->|personal skills info| decomposer
    skillDB -->|elementary skills| decomposer
    
    jobDecompositions -->|job requirements| matcher
    skillDB -->|complex skills| matcher
    matcher -->|skill match results| matchResults
    matchResults --> matchDecision
    matchDecision -->|Yes| selfassess
    matchDecision -->|No, but promising| selfassess
    matchDecision -->|No, low match| jobArchive[Job Archive]
    
    matchResults -->|match data| selfassess
    consolidated -->|job data| selfassess
    selfassess -->|assessment document| assessments
    assessments -->|stores in| consolidated
    
    matchResults -->|match strengths| docgen
    assessments -->|qualification paragraphs| docgen
    consolidated -->|job details| docgen
    userCoverReview -->|customizations| docgen
    docgen -->|cover letter files| coverLetters
    
    coverLetters -->|document files| emailer
    sentLog -->|previously sent docs| emailer
    emailer -->|updates sent status| sentLog
    emailer -->|emails with attachments| externEmail[External Email]
    
    %% Feedback Loops
    emailer -.->|application status| consolidated
    userSkillConfig -.->|skill updates based on results| skillDB
    
    %% Error Handling
    scraper -.->|connection errors| errorLog[Error Log]
    decomposer -.->|LLM errors| errorLog
    matcher -.->|matching errors| errorLog
    
    %% Styling
    classDef module fill:#f9f,stroke:#333,stroke-width:2px;
    classDef datastore fill:#bbf,stroke:#333,stroke-width:1px;
    classDef external fill:#bfb,stroke:#333,stroke-width:1px;
    classDef user fill:#ffd,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5;
    classDef decision fill:#fdf,stroke:#333,stroke-width:2px,shape:diamond;
    classDef errornode fill:#fbb,stroke:#333,stroke-width:1px;
    
    class scraper,decomposer,matcher,selfassess,docgen,emailer module;
    class jobPostings,jobDecompositions,matchResults,skillDB,cvFiles,assessments,coverLetters,sentLog,consolidated,jobArchive datastore;
    class externEmail external;
    class userJobConfig,userSkillConfig,userCoverReview user;
    class matchDecision decision;
    class errorLog errornode;
```

## Detailed Module Data Flows

### Job Scraper Module

```mermaid
flowchart LR
    %% Components
    fetch[Job Fetcher]
    extract[Job Detail Extractor]
    process[Job Processor]
    reporter[Report Generator]
    
    %% Data Stores
    apiResponse[(API Response)]
    jobFiles[(Job JSON Files)]
    reportFiles[(Report Files)]
    
    %% Flow
    fetch -->|raw job listings| apiResponse
    apiResponse -->|job IDs & URLs| extract
    extract -->|detailed job info| process
    process -->|structured job data| jobFiles
    jobFiles --> reporter
    reporter -->|summary reports| reportFiles

    %% Styling
    classDef component fill:#fcf,stroke:#333,stroke-width:1px;
    classDef store fill:#ddf,stroke:#333,stroke-width:1px;
    
    class fetch,extract,process,reporter component;
    class apiResponse,jobFiles,reportFiles store;
```

### Skill Decomposer Module

```mermaid
flowchart TD
    %% Components
    decomp[Decomposition Engine]
    api[Ollama API Client]
    semant[Semantic Matcher]
    cv[CV Inferencer]
    blacklist[Skill Blacklister]
    
    %% Data Stores
    elemSkills[(Elementary Skills)]
    compSkills[(Complex Skills)]
    inferSkills[(Inferred Skills)]
    blacklisted[(Blacklisted Skills)]
    semCache[(Semantic Cache)]
    
    %% Flow
    decomp -->|complex skill queries| api
    api -->|LLM responses| decomp
    decomp -->|decomposes| compSkills
    decomp -->|identifies| elemSkills
    
    cv -->|CV text analysis| api
    api -->|skill inferences| cv
    cv -->|stores inferences| inferSkills
    
    blacklisted -->|filter skills| blacklist
    blacklist -->|restricts| cv
    blacklist -->|restricts| decomp
    
    semant -->|similarity queries| api
    api -->|semantic evaluations| semant
    semant -->|caches results| semCache
    
    elemSkills -->|provides| decomp
    inferSkills -->|supplements| compSkills

    %% Styling
    classDef component fill:#fcf,stroke:#333,stroke-width:1px;
    classDef store fill:#ddf,stroke:#333,stroke-width:1px;
    classDef external fill:#cfc,stroke:#333,stroke-width:1px;
    
    class decomp,api,semant,cv,blacklist component;
    class elemSkills,compSkills,inferSkills,blacklisted,semCache store;
```

### Document Generation & Email Module

```mermaid
flowchart LR
    %% Components
    assess[Self-Assessment Generator]
    integrate[Cover Letter Integrator]
    generate[Cover Letter Generator]
    email[Email Sender]
    
    %% Data Stores
    templates[(Letter Templates)]
    coverLetters[(Cover Letters)]
    sentLog[(Sent Log)]
    
    %% Flow
    assess -->|qualifications text| integrate
    integrate -->|skill paragraphs| generate
    templates -->|letter structure| generate
    generate -->|formatted documents| coverLetters
    coverLetters -->|document files| email
    sentLog -->|sent history| email
    email -->|updates| sentLog
    email -->|sends| externEmail[Work Email]

    %% Styling
    classDef component fill:#fcf,stroke:#333,stroke-width:1px;
    classDef store fill:#ddf,stroke:#333,stroke-width:1px;
    classDef external fill:#cfc,stroke:#333,stroke-width:1px;
    
    class assess,integrate,generate,email component;
    class templates,coverLetters,sentLog store;
    class externEmail external;
```

## Key File Relationships

```mermaid
flowchart TD
    %% Key Files
    jobPostings["/data/postings/*.json"]
    jobDecomps["/data/job_decompositions/*.json"]
    matches["/data/job_decompositions/*_matches.json"]
    consolidated["/data/consolidated_jobs/*.json"]
    elemSkills["/profile/skills/elementary_skills.json"]
    compSkills["/profile/skills/skill_decompositions.json"]
    inferSkills["/profile/skills/inferred_skills.json"]
    blacklist["/profile/skills/skill_blacklist.json"]
    semCache["/data/semantic_similarity_cache.json"]
    cvFiles["/profile/cv/*"]
    templates["/templates/cover_letter_template.md"]
    coverLetters["/docs/cover_letters/*"]
    sentLog["/data/logs/sent_documents_log.json"]
    
    %% Relationships
    scraper[scraper.py] -->|outputs| jobPostings
    
    processor[process_job.py] -->|reads| jobPostings
    processor -->|writes| jobDecomps
    processor -->|writes| matches
    processor -->|writes| consolidated
    
    decomposer[decomposition.py] -->|reads & writes| elemSkills
    decomposer -->|reads & writes| compSkills
    
    cvInfer[cv_inference.py] -->|reads| cvFiles
    cvInfer -->|writes| inferSkills
    
    matchingEngine[matching.py] -->|reads| matches
    matchingEngine -->|reads| compSkills
    matchingEngine -->|reads| elemSkills
    matchingEngine -->|reads| inferSkills
    matchingEngine -->|reads| blacklist
    
    semantics[semantics.py] -->|reads & writes| semCache
    
    assessment[generator.py] -->|reads| matches
    assessment -->|reads| consolidated
    assessment -->|writes| consolidated
    
    coverGen[generate_cover_letter.py] -->|reads| templates
    coverGen -->|reads| consolidated 
    coverGen -->|reads| matches
    coverGen -->|writes| coverLetters
    
    emailSender[email_sender.py] -->|reads| coverLetters
    emailSender -->|reads & writes| sentLog

    %% Styling
    classDef script fill:#f9d,stroke:#333,stroke-width:1px;
    classDef datafile fill:#9df,stroke:#333,stroke-width:1px;
    
    class scraper,processor,decomposer,cvInfer,matchingEngine,semantics,assessment,coverGen,emailSender script;
    class jobPostings,jobDecomps,matches,consolidated,elemSkills,compSkills,inferSkills,blacklist,semCache,cvFiles,templates,coverLetters,sentLog datafile;
```