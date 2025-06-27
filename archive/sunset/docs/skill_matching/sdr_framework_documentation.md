# Enhanced Skill Domain Relationship (SDR) Framework Documentation

## Overview

The Enhanced Skill Domain Relationship (SDR) Framework is a comprehensive system for standardizing skill definitions, classifying relationships between skills across domains, and enabling more accurate skill matching. This documentation provides details about the implementation, usage, and extension of the framework.

## Table of Contents

1. [Framework Components](#framework-components)
2. [Installation and Requirements](#installation-and-requirements)
3. [Usage Guide](#usage-guide)
4. [OLMo2 Enhancements](#olmo2-enhancements)
5. [Visualization Tools](#visualization-tools)
6. [Continuous Learning System](#continuous-learning-system)
7. [Testing and Validation](#testing-and-validation)
8. [Development Roadmap](#development-roadmap)

## Framework Components

The SDR framework consists of the following core components:

### 1. Skill Analyzer

Located in `run_pipeline/skill_matching/skill_analyzer.py`, this component is responsible for:
- Loading job and CV skills from various sources
- Calculating skill ambiguity factors
- Determining skill impact scores
- Selecting top skills for enrichment
- Creating enriched skill definitions with domain information

### 2. Domain Relationship Classifier

Located in `run_pipeline/skill_matching/domain_relationship_classifier.py`, this component:
- Classifies relationships between skills based on domain components
- Uses Jaccard similarity and thresholds for classification
- Identifies relationships such as "Exact match", "Subset", "Superset", etc.
- Creates a comprehensive relationship matrix for all skills

### 3. Domain-Aware Matching Algorithm

Located in `run_pipeline/skill_matching/domain_aware_matcher.py`, this component:
- Enables matching job requirements with candidate skills
- Uses domain relationships to filter out false positives
- Considers knowledge components, contexts, and functions in matching
- Provides explanations for each match or non-match

### 4. Skill Validation System

Located in `run_pipeline/skill_matching/skill_validation.py`, this component:
- Validates the quality and completeness of enriched skill definitions
- Checks for missing fields and inconsistencies
- Provides quality scores for each skill definition
- Generates recommendations for improvement

### 5. Continuous Learning System

Located in `run_pipeline/skill_matching/continuous_learning.py`, this component:
- Incorporates expert feedback to improve skill definitions
- Calculates quality scores for skill definitions
- Checks for consistency issues across domains
- Generates quality reports and recommendations

### 6. Visualization Tools

Located in `run_pipeline/skill_matching/visualize_relationships.py`, this component:
- Creates network graphs of skill relationships
- Generates heatmaps of domain relationships
- Provides chord diagrams for cross-domain relationships
- Helps analyze the structure of the skill relationship network

### 7. Enhanced SDR Pipeline

Located in `run_pipeline/skill_matching/run_enhanced_sdr.py`, this component:
- Integrates all components into a unified pipeline
- Provides command-line interface for running the pipeline
- Offers options for customizing the pipeline execution
- Handles loading and saving of intermediate results

## Installation and Requirements

### Prerequisites

- Python 3.9 or higher
- Required packages: numpy, scikit-learn, matplotlib, networkx, holoviews
- Access to an LLM API (optional, for enhanced skill enrichment)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sunset
   ```

2. Install required packages:
   ```bash
   pip install -r requirements-pipeline.txt
   ```

3. Set up any necessary API credentials for LLM access in `config/credentials.json`

## Usage Guide

### Running the Full Pipeline

The Enhanced SDR pipeline can be run using the `run_enhanced_sdr.py` script:

```bash
cd /home/xai/Documents/sunset
python run_pipeline/skill_matching/run_enhanced_sdr.py --use-llm --max-skills 100 --test-matching
```

#### Command Line Arguments

- `--use-llm`: Enable LLM for skill enrichment (higher quality but slower)
- `--max-skills <n>`: Maximum number of skills to analyze (default: 50)
- `--skip-validation`: Skip validation of enriched skills
- `--test-matching`: Test domain-aware matching with sample data
- `--load-existing`: Load existing enriched skills instead of generating new ones

### Running Individual Components

#### Skill Analysis

```bash
python run_pipeline/skill_matching/skill_analyzer.py --max-skills 100 --use-llm
```

#### Domain Relationship Classification

```bash
python run_pipeline/skill_matching/domain_relationship_classifier.py --skills docs/skill_matching/enriched_skills.json
```

#### Visualization Generation

```bash
python run_pipeline/skill_matching/visualize_relationships.py --all
```

#### Continuous Learning

```bash
python run_pipeline/skill_matching/continuous_learning.py --apply-feedback --generate-report
```

## OLMo2 Enhancements

Based on recommendations from OLMo2, the SDR framework has been enhanced with:

### 1. Improved Skill Definition Structure

- Added standardized categories for all skills
- Enhanced knowledge components with domain-specific terminology
- Added context information to situate skills appropriately
- Included function information to clarify how skills are used

### 2. Continuous Learning Through Expert Feedback

- Implemented a system for incorporating expert feedback
- Added quality scoring for skill definitions
- Created consistency checking across domains
- Enabled automated improvement of skill definitions

### 3. Enhanced Visualization and Analysis

- Added multiple visualization types for relationship analysis
- Implemented statistics on relationship distribution
- Created tools for identifying clusters and outliers
- Enhanced the ability to analyze cross-domain relationships

### 4. Quality Monitoring and Assessment

- Implemented automated validation of skill definitions
- Added quality scoring based on completeness and depth
- Created consistency checking across domains
- Generated recommendations for improvement

## Visualization Tools

The SDR framework includes several visualization tools:

### Network Graph

The network graph visualization shows skills as nodes and relationships as edges:
- Node colors represent different domains
- Edge colors represent different relationship types
- Node size can be adjusted based on importance measures
- The layout shows clusters of related skills

### Domain Heatmap

The domain heatmap visualization shows relationships between domains:
- Cells show the number of relationships between domains
- Darker colors indicate more relationships
- The diagonal shows relationships within domains
- Provides a high-level view of domain interactions

### Chord Diagram

The chord diagram shows the flow of relationships between domains:
- Arcs represent domains
- Ribbons represent relationships between domains
- Color coding shows the directionality of relationships
- Width represents the number of relationships

## Continuous Learning System

The continuous learning system enhances the SDR framework over time:

### Expert Feedback Collection

- Domain experts can provide feedback on skill definitions
- Feedback is collected in structured JSON format
- Experts can provide ratings, corrections, and notes
- Feedback is versioned for tracking improvements

### Quality Scoring

- Each skill definition receives a quality score (0-100)
- Scores are based on completeness, depth, and expert ratings
- Low scores trigger recommendations for improvement
- Quality scores are tracked over time to measure progress

### Consistency Checking

- The system checks for consistency issues across skills
- Unique components within domains are flagged
- Inconsistent terminology is identified
- Sparse definitions compared to domain averages are flagged

### Automated Improvement

- Expert feedback is automatically applied to skill definitions
- Corrections are merged with existing definitions
- Quality scores are recalculated after improvements
- Improvements are tracked and reported

## Testing and Validation

The SDR framework includes comprehensive testing and validation:

### Unit Tests

- Each component has unit tests for basic functionality
- Tests cover edge cases and error handling
- Tests ensure compatibility between components
- Regression tests prevent breaking changes

### Integration Tests

- The full pipeline is tested end-to-end
- Test data is provided for reproducible testing
- Performance metrics are calculated and compared
- Integration tests verify expected outputs

### Quality Validation

- Skill definitions are validated for completeness
- Quality scores are calculated for each definition
- Consistency issues are identified and reported
- Recommendations are generated for improvement

### Performance Metrics

- False positive reduction is measured
- Match quality is assessed against expert judgments
- Processing speed and scalability are measured
- Overall quality improvements are tracked over time

## Development Roadmap

### Short-Term Goals

- Implement remaining OLMo2 recommendations
- Expand test coverage to 90%
- Enhance visualization tools with more dynamic options
- Improve documentation with more examples

### Medium-Term Goals

- Integrate with larger skill ecosystem
- Develop API for external access
- Create web-based visualization dashboard
- Extend continuous learning with more feedback sources

### Long-Term Goals

- Implement automated skill definition generation
- Create dynamic relationship classification system
- Develop predictive model for skill trends
- Enable real-time skill matching at scale

---

## Appendix: Key File Paths

- Enriched Skills: `/docs/skill_matching/enriched_skills.json`
- Skill Relationships: `/docs/skill_matching/skill_relationships.json`
- Quality Reports: `/docs/skill_matching/quality_report_*.json`
- Visualizations: `/docs/skill_matching/visualizations/`
- Test Results: `/tests/output/`
- Expert Feedback: `/data/skill_enrichment_feedback/`

For more information, contact the development team or visit the project repository.
