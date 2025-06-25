# Skill Domain Relationship Framework

This document outlines a mathematical framework for analyzing relationships between professional skill domains, along with implementation guidance and LLM integration approaches.

## 1. Core Concepts and Definitions

For any skill domain `s` in the universal set of skills `S`:

- `knowledge_components[s]` = $K_s$ = Set of knowledge components required for the skill
- `context[s]` = $C_s$ = Set of contexts where the skill is applied
- `proficiency_level[s]` = $L_s$ = Numerical value representing required expertise (scale 0-10)
- `function[s]` = $F_s$ = Set of core functions/purposes of the skill

## 2. Relationship Types

### Hierarchical Relationships
- **Subset** (Specialization): When skill A is specialized within broader skill B
- **Superset** (Generalization): When skill A encompasses skill B

### Proximity Relationships
- **Adjacent**: Skills with significant knowledge/competency overlap but different focuses
- **Neighboring**: Skills that operate in the same environment but with different functions

### Level Relationships
- **Skill Level Disparity**: Skills within the same domain but with significant differences in proficiency level
- **Hierarchical Professional**: Skills within the same domain but at different levels of authority/certification

### Specialization Relationships
- **Parallel Specialization**: Skills that exist at the same level of specialization within a broader domain but are not interchangeable

### Conceptual Relationships
- **Analogous**: Skills that apply similar principles or methodologies in different domains
- **Transferable**: Skills that aren't directly related but have underlying competencies that transfer well
- **Superficial Overlap**: Skills that appear related due to terminology but have minimal practical overlap

### Additional Relationships
- **Complementary**: Skills designed to work together and enhance each other
- **Evolutionary**: Skills where one has evolved from or replaced the other
- **Asymmetric Knowledge Transfer**: Skills where expertise in one provides significant advantage in learning the other
- **Contextual Equivalence**: Skills that are different but serve equivalent functions in different contexts
- **Prerequisite**: Skills where one is a necessary foundation for developing the other
- **Composite**: When a role demands multiple distinct skill domains simultaneously
- **Outdated**: Skills once relevant to a domain but superseded by new approaches

## 3. Mathematical Operators

### Relationship Operators
- Subset: $A \subset B$
- Superset: $B \supset A$
- Adjacency: $A \sim B$ if $|K(A) \cap K(B)| / |K(A) \cup K(B)| > \theta_{adj}$
- Neighboring: $A \approx B$ if $|C(A) \cap C(B)| / |C(A) \cup C(B)| > \theta_{neigh}$
- Hierarchical Professional: $A \prec B$ if $F(A) \approx F(B)$ and $L(A) < L(B)$
- Parallel Specialization: $A \parallel B$ if $\exists C$ such that $A \subset C$ and $B \subset C$ and $|K(A) \cap K(B)| / |K(A) \cup K(B)| < \theta_{par}$
- Skill Level Disparity: $A \ll B$ if $F(A) \approx F(B)$ and $L(A) \ll L(B)$
- Analogous: $A \cong B$ if structure$(F(A)) \approx$ structure$(F(B))$ but $C(A) \neq C(B)$
- Transferable Skills: $A \rightsquigarrow B$ if $\exists K' \subset K(A)$ such that $K'$ can be applied in $C(B)$

### Distance Metric
$d(A, B) = 1 - \frac{|K(A) \cap K(B)|}{|K(A) \cup K(B)|} \cdot \frac{|C(A) \cap C(B)|}{|C(A) \cup C(B)|} \cdot \frac{\min(L(A), L(B))}{\max(L(A), L(B))} \cdot \frac{|F(A) \cap F(B)|}{|F(A) \cup F(B)|}$

This normalized distance (0-1) reflects how related the skills are, with 0 being identical and 1 being completely unrelated.

## 4. Implementation Pseudocode

### Core Helper Functions

```python
def jaccard_similarity(set_a, set_b):
    """Calculate Jaccard similarity between two sets"""
    if len(set_a.union(set_b)) == 0:
        return 0
    return len(set_a.intersection(set_b)) / len(set_a.union(set_b))

def calculate_skill_distance(skill_a, skill_b):
    """Calculate normalized distance between two skill domains"""
    # Knowledge component distance
    k_distance = 1 - jaccard_similarity(knowledge_components[skill_a], 
                                       knowledge_components[skill_b])
    
    # Context distance
    c_distance = 1 - jaccard_similarity(context[skill_a], context[skill_b])
    
    # Level distance (normalized)
    l_ratio = min(proficiency_level[skill_a], proficiency_level[skill_b]) / \
             max(proficiency_level[skill_a], proficiency_level[skill_b])
    l_distance = 1 - l_ratio
    
    # Function distance
    f_distance = 1 - jaccard_similarity(function[skill_a], function[skill_b])
    
    # Weighted combination
    distance = (0.4 * k_distance + 0.3 * c_distance + 
               0.1 * l_distance + 0.2 * f_distance)
    
    return distance
```

### Relationship Classification Functions

```python
def is_subset(skill_a, skill_b):
    """Check if skill_a is a subset of skill_b"""
    knowledge_subset = knowledge_components[skill_a].issubset(knowledge_components[skill_b])
    context_subset = context[skill_a].issubset(context[skill_b])
    level_check = proficiency_level[skill_a] >= proficiency_level[skill_b]
    
    return knowledge_subset and context_subset and level_check

def is_adjacent(skill_a, skill_b):
    """Check if skill_a and skill_b are adjacent"""
    knowledge_overlap = jaccard_similarity(knowledge_components[skill_a], 
                                          knowledge_components[skill_b])
    function_overlap = jaccard_similarity(function[skill_a], function[skill_b])
    
    return knowledge_overlap > adjacency_threshold and function_overlap > 0.4

def is_parallel_specialization(skill_a, skill_b):
    """Check if skills are parallel specializations"""
    # Find potential parent domains
    potential_parents = [s for s in all_skills 
                       if is_subset(skill_a, s) and is_subset(skill_b, s)]
    
    knowledge_overlap = jaccard_similarity(knowledge_components[skill_a], 
                                          knowledge_components[skill_b])
    
    level_similarity = abs(proficiency_level[skill_a] - proficiency_level[skill_b]) < 2
    
    return len(potential_parents) > 0 and knowledge_overlap < parallel_threshold and level_similarity

def has_skill_level_disparity(skill_a, skill_b):
    """Check if there's a significant skill level disparity"""
    domain_match = is_subset(skill_a, skill_b) or is_subset(skill_b, skill_a)
    function_overlap = jaccard_similarity(function[skill_a], function[skill_b])
    level_difference = abs(proficiency_level[skill_a] - proficiency_level[skill_b])
    
    return domain_match and function_overlap > 0.7 and level_difference > 3
```

### Main Classification Function

```python
def classify_relationship(skill_a, skill_b):
    """Determine the relationship type between two skill domains"""
    if skill_a == skill_b:
        return "Identical"
    
    if is_subset(skill_a, skill_b):
        return "Subset"
    
    if is_superset(skill_a, skill_b):
        return "Superset"
    
    if is_parallel_specialization(skill_a, skill_b):
        return "Parallel_Specialization"
    
    if has_skill_level_disparity(skill_a, skill_b):
        return "Skill_Level_Disparity"
    
    if is_hierarchical_professional(skill_a, skill_b):
        return "Hierarchical_Professional"
    
    if is_adjacent(skill_a, skill_b):
        return "Adjacent"
    
    if is_neighboring(skill_a, skill_b):
        return "Neighboring"
    
    if is_analogous(skill_a, skill_b):
        return "Analogous"
    
    if has_transferable_skills(skill_a, skill_b):
        return "Transferable"
    
    # Calculate overall distance
    distance = calculate_skill_distance(skill_a, skill_b)
    if distance > 0.8:
        return "Unrelated"
    else:
        return "Weakly_Related"
```

## 5. Transformation Analysis

```python
def calculate_training_probability(skill_a, skill_b):
    """Calculate probability of successful transition from skill_a to skill_b"""
    # Knowledge transfer
    k_transfer = len(knowledge_components[skill_a].intersection(knowledge_components[skill_b])) / \
                len(knowledge_components[skill_b])
    
    # Context familiarity
    c_transfer = len(context[skill_a].intersection(context[skill_b])) / \
                len(context[skill_b])
    
    # Level gap factor (harder to move up levels)
    level_gap = max(0, proficiency_level[skill_b] - proficiency_level[skill_a]) / 10
    level_factor = 1 - level_gap
    
    # Combined probability
    probability = 0.5 * k_transfer + 0.3 * c_transfer + 0.2 * level_factor
    
    return min(max(probability, 0), 1)  # Ensure between 0 and 1

def estimate_transition_time(skill_a, skill_b):
    """Estimate time needed to transition from skill_a to skill_b"""
    # Base time unit (e.g., months)
    base_time = 3
    
    # Knowledge gap to fill
    new_knowledge = knowledge_components[skill_b] - knowledge_components[skill_a]
    knowledge_factor = len(new_knowledge) / len(knowledge_components[skill_b])
    
    # Level gap
    level_gap = max(0, proficiency_level[skill_b] - proficiency_level[skill_a])
    
    # Complexity factor
    complexity = calculate_complexity(skill_b)  # Domain-specific function
    
    # Combined time estimate
    time_estimate = base_time * (1 + knowledge_factor) * (1 + level_gap/10) * complexity
    
    return time_estimate
```

## 6. LLM Integration

### Domain Knowledge Extraction Prompt

```python
def generate_domain_extraction_prompt(domain):
    """Generate prompt for extracting domain components using LLM"""
    prompt = f"""
    As a domain expert, please identify the core components of the skill domain "{domain}":
    
    1. Knowledge Components: List 10-15 specific knowledge areas required for this role (be precise and thorough)
    2. Context: List 5-8 environments/settings where this skill is typically applied
    3. Core Functions: List 5-8 primary functions or purposes of this role
    4. Proficiency Level: On a scale of 1-10, what level of expertise does this role typically require? Explain your rating.
    
    Format each section as a numbered list. Be comprehensive yet concise.
    """
    return prompt
```

### Relationship Analysis Prompt

```python
def generate_relationship_analysis_prompt(domain1_details, domain2_details):
    """Generate prompt for analyzing relationship between domains using LLM"""
    prompt = f"""
    You are analyzing the relationship between two professional domains based on their components.
    
    DOMAIN 1: {domain1_details['name']}
    Knowledge Components: {domain1_details['knowledge_components']}
    Context: {domain1_details['context']}
    Functions: {domain1_details['functions']}
    Proficiency Level: {domain1_details['proficiency_level']}
    
    DOMAIN 2: {domain2_details['name']}
    Knowledge Components: {domain2_details['knowledge_components']}
    Context: {domain2_details['context']}
    Functions: {domain2_details['functions']}
    Proficiency Level: {domain2_details['proficiency_level']}
    
    Please calculate:
    1. Knowledge overlap (Jaccard similarity of knowledge components)
    2. Context overlap (Jaccard similarity of contexts)
    3. Function overlap (Jaccard similarity of functions)
    4. Level ratio: min(L₁, L₂)/max(L₁, L₂)
    
    Then determine:
    1. The primary relationship type based on these metrics (Subset, Superset, Parallel Specialization, 
       Skill Level Disparity, Hierarchical Professional, Adjacent, Neighboring, Analogous, Transferable)
    2. A compatibility percentage (0-100%)
    3. Required training path to transition from Domain 1 to Domain 2
    
    Show all calculations and explain your reasoning.
    """
    return prompt
```

### LLM Pipeline Implementation

```python
def analyze_skill_domains(domain1, domain2):
    """Full pipeline for analyzing relationship between two skill domains using LLMs"""
    # Stage 1: Extract detailed domain knowledge for each skill
    domain1_details = llm_extract_domain_components(domain1)
    domain2_details = llm_extract_domain_components(domain2)
    
    # Stage 2: Analyze relationship between domains
    relationship_analysis = llm_analyze_relationship(domain1_details, domain2_details)
    
    # Stage 3: Format and present results
    formatted_results = format_analysis_results(
        domain1, domain2, domain1_details, domain2_details, relationship_analysis
    )
    
    return formatted_results

def llm_extract_domain_components(domain):
    """Extract components of a skill domain using LLM"""
    prompt = generate_domain_extraction_prompt(domain)
    response = call_llm_api(prompt)
    parsed_components = parse_llm_domain_response(response)
    return parsed_components

def llm_analyze_relationship(domain1_details, domain2_details):
    """Analyze relationship between domains using LLM"""
    prompt = generate_relationship_analysis_prompt(domain1_details, domain2_details)
    response = call_llm_api(prompt)
    parsed_analysis = parse_llm_analysis_response(response)
    return parsed_analysis
```

## 7. Example Data Structures

```python
# Example skill definition
chef = {
    "id": "chef",
    "knowledge_components": {
        "food_science", "culinary_techniques", "menu_planning", 
        "kitchen_management", "flavor_pairing", "cooking_methods"
    },
    "context": {"restaurant", "hotel", "catering", "food_service"},
    "proficiency_level": 8,
    "function": {"food_preparation", "menu_creation", "kitchen_oversight"}
}

# Example relationship analysis result
relationship_result = {
    "domains": {
        "domain1": "french_cook",
        "domain2": "japanese_cook"
    },
    "metrics": {
        "knowledge_overlap": 0.35,
        "context_overlap": 0.85,
        "function_overlap": 0.70,
        "level_ratio": 1.0
    },
    "classification": {
        "primary_relationship": "Parallel_Specialization",
        "compatibility_percentage": 68,
        "distance": 0.42
    },
    "transition": {
        "training_probability": 0.65,
        "estimated_time_months": 12,
        "key_areas_to_learn": ["japanese_ingredients", "raw_fish_handling", "knife_techniques"]
    }
}
```

## 8. Visualization Ideas

- **Relationship Network Graph**: Nodes represent skills, edges represent relationships
- **Skill Vector Space**: Project skills into 2D/3D space based on component similarities
- **Transition Path Diagram**: Visual representation of training path between domains
- **Compatibility Gauge**: Visual meter showing compatibility percentage
- **Component Overlap Venn Diagrams**: Visual representation of knowledge/context/function overlap

## 9. Implementation Considerations

1. **Threshold Parameters**:
   - `adjacency_threshold` (e.g., 0.5): Minimum knowledge overlap for adjacent skills
   - `neighboring_threshold` (e.g., 0.6): Minimum context overlap for neighboring skills
   - `parallel_threshold` (e.g., 0.3): Maximum knowledge overlap for parallel specializations
   - `superficial_threshold` (e.g., 0.2): Maximum overlap for superficial relationships

2. **Performance Optimization**:
   - Cache common skill domain definitions
   - Precompute relationships for frequently compared domains
   - Use sparse representations for large skill datasets

3. **Quality Assurance**:
   - Validate LLM outputs against expert-defined benchmarks
   - Implement feedback loop to improve domain component extraction
   - Use ensemble of LLMs for more robust analysis

## 10. Extension Ideas

1. **Skill Clustering**: Identify natural groupings of related skills
2. **Career Path Optimization**: Find optimal transitions between domains
3. **Team Composition Analysis**: Evaluate complementary skills within teams
4. **Job Recommendation**: Match candidates to positions based on compatibility
5. **Curriculum Design**: Create learning paths based on skill relationships

---

This framework provides a comprehensive approach for analyzing and quantifying relationships between professional skill domains, with both algorithmic implementations and LLM integration strategies.
