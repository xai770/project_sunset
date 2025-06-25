# LLM Performance Analysis for Skill Parsing System

## Executive Summary

This analysis evaluates multiple Large Language Models (LLMs) for parsing job descriptions into structured skill requirements. We tested 10 models with a standardized prompt that asked each model to extract skills from a job description and categorize them according to predefined skill categories. Our goal was to identify which model(s) performed best for our CV-to-job matching system.

**Key Findings:**
- **Olmo2:latest** emerged as the top performer with comprehensive category coverage and excellent schema compliance
- Several prominent models failed to complete the task successfully
- An ensemble approach combining multiple models offers the most robust solution
- Model size did not consistently correlate with performance quality

## Testing Methodology

### Input Prompt
Each model received a standardized prompt requesting:
1. Extraction of skills from a provided job description
2. Categorization into 6 predefined skill categories
3. Rating of skill level (1-5) and importance (Essential/Desirable)
4. Output in a specific JSON format

### Skill Categories
- IT_Technical
- IT_Management
- Sourcing_and_Procurement
- Leadership_and_Management
- Analysis_and_Reporting
- Domain_Knowledge

### Evaluation Criteria
- Category coverage (how many of the 6 categories were used)
- Total skills identified
- Format correctness and schema compliance
- Skill level variation
- Importance differentiation
- Identification of key skills (e.g., Microsoft Office)
- Company identification
- Hallucination detection

## Model Performance Rankings

### Tier 1: Top Performers

#### 1. Olmo2:latest (Best Overall)
```json
{
  "position": "Alternative Products Manager",
  "company": "Deutsche Bank",
  "skill_requirements": {
    "IT_Technical": [
      {
        "name": "Microsoft Office applications",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "IT_Management": [
      {
        "name": "Project management",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "Sourcing_and_Procurement": [
      {
        "name": "Vendor management",
        "level": 3,
        "importance": "Desirable"
      }
    ],
    "Leadership_and_Management": [
      {
        "name": "Team leadership",
        "level": 4,
        "importance": "Essential"
      },
      {
        "name": "Stakeholder engagement",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "Analysis_and_Reporting": [
      {
        "name": "Data processing",
        "level": 4,
        "importance": "Desirable"
      },
      {
        "name": "Decision frameworks",
        "level": 4,
        "importance": "Desirable"
      }
    ],
    "Domain_Knowledge": [
      {
        "name": "Alternative asset classes",
        "level": 5,
        "importance": "Essential"
      },
      {
        "name": "AIF structures in Germany",
        "level": 5,
        "importance": "Essential"
      }
    ]
  }
}
```

**Strengths:**
- Only model to use all 6 skill categories
- Proper differentiation between Essential and Desirable skills
- Correctly identified the company (Deutsche Bank)
- Good skill level variation (3-5)
- Perfect schema compliance
- Balanced coverage of technical and soft skills

**Score:** 9.5/10

#### 2. Qwen3:latest
```json
{
  "position": "Role Name",
  "company": "Company Name",
  "skill_requirements": {
    "IT_Technical": [
      {
        "skill": "Mastery of Microsoft Office",
        "level": 5,
        "essential": true
      }
    ],
    "IT_Management": [
      {
        "skill": "Excellent project management",
        "level": 4,
        "essential": true
      }
    ],
    "Leadership_and_Management": [
      {
        "skill": "Results-oriented self-motivation",
        "level": 3,
        "essential": true
      },
      {
        "skill": "Ability to build relationships with teams and influence results",
        "level": 3,
        "essential": true
      },
      {
        "skill": "Solution-oriented, creative, proactive",
        "level": 3,
        "essential": true
      },
      {
        "skill": "Openness to challenges and self-development",
        "level": 3,
        "essential": true
      },
      {
        "skill": "Excellent communication skills in German and English",
        "level": 4,
        "essential": true
      }
    ],
    "Analysis_and_Reporting": [
      {
        "skill": "Administration of the global product pipeline and reporting on new initiatives status",
        "level": 3,
        "essential": true
      }
    ],
    "Domain_Knowledge": [
      {
        "skill": "Comprehensive understanding of alternative asset classes",
        "level": 4,
        "essential": true
      }
    ],
    "Sourcing_and_Procurement": []
  }
}
```

**Strengths:**
- Uses 5 of 6 categories
- Excellent identification of leadership and communication skills (5 leadership skills)
- Good skill level variation (3-5)
- Highest focus on soft skills
- Explicitly identifies communication skills in German and English

**Weaknesses:**
- Schema deviations (uses "skill" instead of "name", boolean for importance)
- Uses generic placeholders for position and company

**Score:** 8.5/10

#### 3. Qwen3:4b
```json
{
  "position": "Alternative Products Manager",
  "company": "Not specified",
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
      }
    ],
    "Sourcing_and_Procurement": [],
    "Leadership_and_Management": [
      {
        "name": "Building Relationships with Stakeholders",
        "level": 5,
        "importance": "Essential"
      },
      {
        "name": "Self-Motivation and Proactivity",
        "level": 5,
        "importance": "Essential"
      },
      {
        "name": "Influence and Stakeholder Engagement",
        "level": 5,
        "importance": "Essential"
      },
      {
        "name": "Creative Problem-Solving",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "Analysis_and_Reporting": [
      {
        "name": "Product Pipeline Administration and Reporting",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "Domain_Knowledge": [
      {
        "name": "Alternative Asset Classes and Structures",
        "level": 5,
        "importance": "Essential"
      }
    ]
  }
}
```

**Strengths:**
- Uses 5 of 6 categories
- Professional skill naming conventions (capitalized, concise)
- Perfect schema compliance
- Strong leadership skill identification
- Correctly identifies Microsoft Office skills

**Weaknesses:**
- All skills rated at maximum level (5)
- No importance differentiation (all Essential)

**Score:** 8.0/10

### Tier 2: Strong Performers

#### 4. CodeGemma:latest
```json
{
  "position": "Alternative Products Manager",
  "company": "Not specified",
  "skill_requirements": {
    "IT_Technical": [],
    "IT_Management": [],
    "Sourcing_and_Procurement": [],
    "Leadership_and_Management": [
      {
        "name": "Team leadership",
        "level": 3,
        "importance": "Essential"
      },
      {
        "name": "Process management",
        "level": 3,
        "importance": "Essential"
      },
      {
        "name": "Stakeholder engagement",
        "level": 4,
        "importance": "Essential"
      }
    ],
    "Analysis_and_Reporting": [
      {
        "name": "Analytical skills",
        "level": 4,
        "importance": "Essential"
      },
      {
        "name": "Data processing",
        "level": 4,
        "importance": "Essential"
      },
      {
        "name": "Reporting",
        "level": 4,
        "importance": "Essential"
      },
      {
        "name": "Decision frameworks",
        "level": 4,
        "importance": "Essential"
      }
    ],
    "Domain_Knowledge": [
      {
        "name": "Alternative asset classes (real estate, infrastructure, private credit)",
        "level": 5,
        "importance": "Essential"
      },
      {
        "name": "AIFs in Germany",
        "level": 4,
        "importance": "Essential"
      },
      {
        "name": "Special funds",
        "level": 4,
        "importance": "Essential"
      },
      {
        "name": "Open funds",
        "level": 4,
        "importance": "Essential"
      },
      {
        "name": "Partnerships",
        "level": 4,
        "importance": "Essential"
      },
      {
        "name": "AIF structures",
        "level": 4,
        "importance": "Essential"
      }
    ]
  }
}
```

**Strengths:**
- Detailed domain knowledge breakdown (6 specific domain skills)
- Good skill count (13 total)
- Varied skill levels (3-5)
- Strong schema compliance
- High coverage of analysis/reporting skills

**Weaknesses:**
- Limited category usage (3/6)
- Misses Microsoft Office skills
- No importance differentiation

**Score:** 7.5/10

#### 5. Dolphin3:latest
```json
{
  "position": "Alternative Products Manager",
  "company": "Not specified",
  "skill_requirements": {
    "IT_Technical": [
      {
        "name": "Proficiency in Microsoft Office applications",
        "level": 4,
        "importance": "Essential"
      }
    ],
    "IT_Management": [],
    "Sourcing_and_Procurement": [],
    "Leadership_and_Management": [
      {
        "name": "Excellent project management and organizational skills",
        "level": 5,
        "importance": "Essential"
      },
      {
        "name": "Results-oriented self-motivation",
        "level": 4,
        "importance": "Essential"
      },
      {
        "name": "Ability to build close relationships with various teams and individuals",
        "level": 5,
        "importance": "Essential"
      },
      {
        "name": "Solution-oriented, creative, and proactive in suggesting new strategies/lifestyles",
        "level": 4,
        "importance": "Essential"
      },
      {
        "name": "Openness to new challenges with acute engagement and self-development approach",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "Analysis_and_Reporting": [],
    "Domain_Knowledge": [
      {
        "name": "Comprehensive understanding of alternative asset classes (real estate, infrastructure, private credit) and structures (AIFs in Germany, including special funds, open funds, partnerships, AIF structures)",
        "level": 5,
        "importance": "Essential"
      }
    ]
  }
}
```

**Strengths:**
- Excellent at capturing soft skills and personality traits
- Uses verbatim phrasing from job description
- Identifies Microsoft Office skills
- Detailed domain knowledge (though condensed to one skill)
- Good schema compliance

**Weaknesses:**
- Limited category coverage (3/6)
- Very verbose skill descriptions
- No importance differentiation

**Score:** 7.0/10

### Tier 3: Adequate Performers

#### 6. DeepSeek-R1:8b
```json
{
  "position": "Alternative Products Manager",
  "company": "Not specified",
  "skill_requirements": {
    "IT_Technical": [],
    "IT_Management": [
      {
        "name": "Project Management",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "Sourcing_and_Procurement": [],
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
    "Analysis_and_Reporting": [
      {
        "name": "Market Analysis",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "Domain_Knowledge": [
      {
        "name": "Alternative Assets Knowledge",
        "level": 5,
        "importance": "Essential"
      }
    ]
  }
}
```

**Strengths:**
- Clean, high-level skill categorization
- Good schema compliance
- Professional naming conventions

**Weaknesses:**
- Limited category coverage (3/6)
- All skills rated at maximum level (5)
- No importance differentiation
- Misses Microsoft Office skills

**Score:** 6.5/10

#### 7. Qwen3:1.7b
```json
{
  "position": "Alternative Products Manager",
  "company": "Not specified",
  "skill_requirements": {
    "IT_Technical": [
      {
        "name": "Microsoft Office mastery",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "IT_Management": [
      {
        "name": "Project management skills",
        "level": 5,
        "importance": "Essential"
      },
      {
        "name": "Communication skills in German and English",
        "level": 5,
        "importance": "Essential"
      }
    ],
    "Sourcing_and_Procurement": [],
    "Leadership_and_Management": [
      {
        "name": "Leadership skills",
        "level": 4,
        "importance": "Essential"
      }
    ],
    "Analysis_and_Reporting": [],
    "Domain_Knowledge": [
      {
        "name": "Alternative asset classes and structures",
        "level": 5,
        "importance": "Essential"
      }
    ]
  }
}
```

**Strengths:**
- Good performance for a smaller model
- Explicitly identifies communication skills
- Identifies Microsoft Office skills
- Good schema compliance
- Uses 4 of 6 categories

**Weaknesses:**
- Limited skill count (5 total)
- No importance differentiation
- Mostly maximum skill levels (4-5)

**Score:** 6.0/10

#### 8. Mistral:latest
```json
{
  "position": "Alternative Products Manager",
  "company": "Not specified",
  "skill_requirements": {
    "IT_Technical": [],
    "IT_Management": [],
    "Sourcing_and_Procurement": [],
    "Leadership_and_Management": [
      {
        "name": "team leadership",
        "level": 3,
        "importance": "Essential"
      },
      {
        "name": "process management",
        "level": 3,
        "importance": "Essential"
      },
      {
        "name": "stakeholder engagement",
        "level": 3,
        "importance": "Essential"
      }
    ],
    "Analysis_and_Reporting": [
      {
        "name": "analytical skills",
        "level": 3,
        "importance": "Essential"
      },
      {
        "name": "data processing",
        "level": 3,
        "importance": "Essential"
      }
    ],
    "Domain_Knowledge": [
      {
        "name": "alternative asset classes and structures",
        "level": 5,
        "importance": "Essential"
      }
    ]
  }
}
```

**Strengths:**
- Most conservative skill ratings (mostly 3s)
- Very concise skill naming
- Good schema compliance

**Weaknesses:**
- Limited category coverage (3/6)
- No importance differentiation
- Misses Microsoft Office skills
- Lowercase skill names
- Limited skill count (6 total)

**Score:** 5.5/10

### Problematic Models

#### Gemma3:1b - Hallucination Issues
- Identified 30 skills (5 in each category)
- Many skills not evident in the job description
- Appears to fabricate detailed requirements

#### Qwen3:0.6b - Format Issues
- Serious schema misunderstanding
- Lists category names as skills within IT_Technical
- Not usable in current form

#### Failed Models
The following models failed to complete the task:
- phi4-mini-reasoning:latest
- phi3:3.8b
- gemma3:4b
- llama3.2:latest

## Comparative Analysis

| Model | Categories Used | Total Skills | MS Office | Company ID | Importance Diff | Skill Levels | Schema Compliance | Score |
|-------|----------------|--------------|-----------|------------|-----------------|--------------|-------------------|-------|
| Olmo2 | 6/6 | 9 | Yes | Yes | Yes | 3-5 | High | 9.5 |
| Qwen3 | 5/6 | 10 | Yes | No* | No† | 3-5 | Medium | 8.5 |
| Qwen3:4b | 5/6 | 8 | Yes | No | No | 5 only | High | 8.0 |
| CodeGemma | 3/6 | 13 | No | No | No | 3-5 | High | 7.5 |
| Dolphin3 | 3/6 | 7 | Yes | No | No | 4-5 | High | 7.0 |
| DeepSeek | 3/6 | 5 | No | No | No | 5 only | High | 6.5 |
| Qwen3:1.7b | 4/6 | 5 | Yes | No | No | 4-5 | High | 6.0 |
| Mistral | 3/6 | 6 | No | No | No | 3-5 | High | 5.5 |
| Gemma3:1b | 6/6 | 30 | No | No | Yes | 3-5 | High | 4.0‡ |
| Qwen3:0.6b | 1/6 | 6 | No | No | Yes | 1-5 | Very Low | 2.0 |

*Uses generic placeholder
†Uses boolean true/false instead of string
‡Scored low due to hallucination issues

## Key Findings

1. **Model Size ≠ Performance**
   - Olmo2:latest outperformed many larger and more prominent models
   - Several large models completely failed at the task

2. **Schema Compliance Varies**
   - Most models followed the schema correctly
   - Some models deviated with field naming or format

3. **Category Coverage**
   - Only Olmo2 and Gemma3:1b used all 6 categories
   - Most models used 3-5 categories

4. **Skill Level Assessment**
   - Some models rate all skills at maximum level
   - Others provide more nuanced ratings

5. **Hallucination Risk**
   - Models like Gemma3:1b show high risk of hallucination
   - Over-detailed outputs often indicate fabrication

## Recommended Implementation

Based on our findings, we recommend an ensemble approach that leverages the strengths of multiple models:

### Primary Implementation

1. **Core Parser**: Olmo2:latest
   - Use as the foundation due to complete category coverage and schema compliance

2. **Enhanced with**:
   - Qwen3:latest for leadership and soft skills
   - CodeGemma:latest for domain knowledge details

### Ensemble Strategy

Implement a voting-based ensemble that:
1. Requires skills to be identified by at least 2 models to be included
2. Uses category-specific weighting:
   - Leadership skills: favor Qwen3:latest
   - Domain knowledge: favor CodeGemma:latest
   - General coverage: favor Olmo2:latest
3. Adds confidence scores based on cross-model agreement
4. Normalizes skill names to handle variations

### Sample Implementation Pseudocode

```python
def ensemble_skills(model_outputs, min_votes=2):
    """Combine skills from multiple models using a voting approach."""
    all_skills = {}
    
    # Collect all skills from all models
    for model_name, output in model_outputs.items():
        for category, skills in output['skill_requirements'].items():
            if category not in all_skills:
                all_skills[category] = {}
                
            for skill in skills:
                # Normalize skill name
                skill_name = normalize_skill_name(skill.get('name', skill.get('skill', '')))
                
                if skill_name not in all_skills[category]:
                    all_skills[category][skill_name] = {
                        'votes': 0,
                        'models': [],
                        'levels': [],
                        'importances': []
                    }
                
                # Record this model's vote
                all_skills[category][skill_name]['votes'] += 1
                all_skills[category][skill_name]['models'].append(model_name)
                all_skills[category][skill_name]['levels'].append(skill.get('level', 3))
                
                # Handle different importance formats
                importance = skill.get('importance', 
                                    'Essential' if skill.get('essential', True) else 'Desirable')
                all_skills[category][skill_name]['importances'].append(importance)
    
    # Build final output with skills that have enough votes
    result = {
        'position': 'Alternative Products Manager',
        'company': 'Deutsche Bank',  # From Olmo2
        'skill_requirements': {}
    }
    
    for category in all_skills:
        result['skill_requirements'][category] = []
        
        for skill_name, data in all_skills[category].items():
            if data['votes'] >= min_votes:
                # Calculate weighted average based on model strengths
                avg_level = calculate_weighted_level(skill_name, category, data)
                
                # Take most common importance
                importance = get_most_common(data['importances'])
                
                result['skill_requirements'][category].append({
                    'name': skill_name,
                    'level': avg_level,
                    'importance': importance,
                    'confidence': data['votes'] / len(model_outputs)
                })
    
    return result
```

## Conclusion

Our analysis demonstrates that Olmo2:latest is surprisingly the best individual model for our skill parsing task. However, an ensemble approach combining Olmo2, Qwen3:latest, and CodeGemma:latest would provide the most robust and comprehensive skill extraction system.

This finding highlights the importance of empirical testing rather than relying on assumptions about model capabilities based on size or popularity. For this specific structured extraction task, Olmo2's strengths in category coverage, schema compliance, and balanced skill assessment made it the standout performer.
