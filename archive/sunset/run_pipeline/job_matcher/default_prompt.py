    #!/usr/bin/env python3
"""
Fixed prompt for job matching - using the simple, working manual version.
"""

LLAMA3_PROMPT = '''Please read section 1 and follow the instructions.
# 1. Instructions
!!! Do not generate any output, until you reach section 1.2. !!!

##  1.1. Analysis and preparation
You are an expert job application assistant.
Review the CV in section 2.1 and the role description in section 2.2. They contain all the information you need.

### 1.1.1. Compare the role requirements carefully with the evidence in the CV. Based on your careful comparison, determine the CV-to-role match level:
- **Low match:** if the CV does not state direct experience in any key requirement of the role title and details (e.g., specific technology, industry, or critical skill explicitly required). THIS RULE IS ALWAYS VALID!
- **Moderate match:** if I have gaps in secondary requirements.
- **Good match:** if I have only minor gaps and decide to apply.

### 1.1.2. Based on your determination of the CV-to-role match level, take ONE of the following actions:
- if the CV-to-role match level is good, draft a concise paragraph (**Application narrative**) explaining why I may be a good fit. Do NOT draft a full cover letter - only one paragraph.
- in all other cases, i.e. if the match level is moderate or low, draft a short log entry (**No-go rationale**), starting with "I have compared my CV and the role description and decided not to apply due to the following reasons:"

## 1.2. Generate output
Output ONLY the elements below. Do NOT add anything, as this will generate an error.

**CV-to-role match:** [Low match/Moderate match/Good match]
**Application narrative:** [if the CV-to-role match level is good]
**No-go rationale:** [in all other cases, i.e. if the match level is moderate or low]

# 2. Input

## 2.1. CV:
{cv}

## 2.2. Role Description:
{job}
'''