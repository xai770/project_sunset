# Inferred Skills Review Workflow

This document outlines the workflow for reviewing, validating, and managing skills that are automatically inferred from job postings and your CV content.

## Conceptual Framework

The inferred skills workflow follows this process:

```
+------------------+          +------------------+          +-----------------+
| Job Requirements |          | Your CV Content  |          | Projects History|
+------------------+          +------------------+          +-----------------+
         |                            |                            |
         v                            v                            v
+------------------+          +------------------+          +-----------------+
| Skill Gap        |--------->| Skill Inference  |<---------| Experience      |
| Identification   |          | Engine           |          | Analysis        |
+------------------+          +------------------+          +-----------------+
                                     |
                                     v
+------------------+          +------------------+
| Blacklisted      |<---------| Inferred Skill   |----------> +----------------+
| Skills           | Rejected | Review           | Accepted   | Your Skill Set |
+------------------+          +------------------+            +----------------+
```

## Key Components

### 1. Skill Gap Identification

When matching your skills against job requirements, the system identifies potential gaps where you lack specific skills requested in the job posting.

### 2. Experience Analysis

The system analyzes your CV content and project history to identify potential unlisted skills that you may possess based on your described experiences.

### 3. Skill Inference Engine

Using the identified gaps and your existing experience, the inference engine suggests skills that you likely possess but haven't explicitly listed.

### 4. Inferred Skill Review

Each inferred skill must go through a review process where you can:
- Accept the skill (adding it to your skill set)
- Reject the skill (adding it to a blacklist)
- Defer the decision for later review

### 5. Blacklisted Skills

Skills that have been reviewed and rejected are added to a blacklist to prevent the system from suggesting them again in the future.

## Skill Inference Data Model

```json
{
  "inferred_skill": {
    "name": "Regulatory Compliance",
    "confidence": 85.0,
    "source_job_id": 62675,
    "evidence": "Experience as a project manager in IT and sourcing, with cross-functional team management",
    "validated": true,
    "elementary_components": [
      "Compliance Monitoring",
      "Risk Assessment",
      "Policy Development",
      "Contract Analysis",
      "Software Licensing",
      "Legal Knowledge"
    ],
    "added_to_skillset": true,
    "notes": "Valid skill based on extensive software compliance management experience"
  }
}
```

## Review Process

### Adding a New Inferred Skill

1. When a job is analyzed, potential skill gaps are identified
2. The system checks your experience to see if you might possess a matching skill
3. If a potential match is found with sufficient confidence, it's added as an inferred skill

### Reviewing Inferred Skills

Currently, we use a collaborative discussion-based approach for reviewing pending inferred skills:

1. We review the list of pending inferred skills together
2. For each skill, we discuss the evidence, confidence, and relevance
3. Based on our discussion, we decide to accept or reject each skill
4. We then use the CLI commands to implement our decision:

```bash
# List all pending inferred skills
python -m scripts.utils.inferred_skill_manager list --pending

# Accept an inferred skill and add it to your skill set
python -m scripts.utils.inferred_skill_manager validate "Regulatory Compliance" --validate --add

# Reject an inferred skill (adds to blacklist)
python -m scripts.utils.inferred_skill_manager validate "Digital Marketing Knowledge" --reject
```

In the future, we may develop a more formal interactive CLI interface, but the current approach allows for thoughtful consideration of each skill.

### Validation Decision Factors

When reviewing an inferred skill, consider:

1. **Evidence Quality**: Is the evidence from your CV or project history compelling?
2. **Confidence Score**: How confident is the system in this inference?
3. **Relevance**: Is this skill relevant to your professional profile and goals?
4. **Accuracy**: Do you actually possess this skill, even if not explicitly listed?

### Managing the Blacklist

Rejected skills are added to a blacklist to prevent repeated suggestions:

```bash
# View the blacklisted skills
python -m scripts.utils.inferred_skill_manager list --blacklisted

# Remove a skill from the blacklist
python -m scripts.utils.inferred_skill_manager unblacklist "Digital Marketing Knowledge"
```

## Implementation Status

- [x] Basic skill inference from job gaps 
- [x] Evidence collection from CV and projects
- [x] Validation workflow for accepting skills
- [ ] Blacklist functionality for rejected skills
- [x] ~~Interactive CLI review interface~~ Collaborative review process
- [ ] Confidence scoring model refinement

## Next Steps

1. **Enhance the inferred_skill_manager.py** to implement blacklisting for rejected skills
2. ~~**Create an interactive review interface** for pending skills~~ **Continue with our collaborative review process** for pending skills
3. **Refine the confidence scoring model** to better predict valid inferences
4. **Integrate with job matching** to automatically suggest skills to develop
5. **Implement periodic review reminders** for deferred skill validations

This workflow enables us to continuously improve our skill profile based on job market demands while maintaining accuracy and relevance in our professional representation.
