#!/usr/bin/env python3
"""
Skill Relationship Visualization Tool

This script generates visualizations for the skill relationships identified 
by the SDR framework. It helps analyze the connections between skills across
different domains.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Any, Optional
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from datetime import datetime
import math

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("skill_relationship_visualizer")

# Constants
SKILL_DIR = os.path.join(project_root, 'docs', 'skill_matching')
VISUALIZATION_DIR = os.path.join(project_root, 'docs', 'skill_matching', 'visualizations')
os.makedirs(VISUALIZATION_DIR, exist_ok=True)

# Define relationship colors
RELATIONSHIP_COLORS = {
    'Exact match': 'red',
    'Subset': 'blue',
    'Superset': 'green',
    'Neighboring': 'purple',
    'Hybrid': 'orange',
    'Unrelated': 'gray'
}

class SkillRelationshipVisualizer:
    """
    Visualizes the relationships between skills using network graphs
    and other visualization techniques.
    """
    
    def __init__(self):
        """Initialize the visualizer"""
        self.enriched_skills = []
        self.skill_relationships = {}
        self.domains = set()
        
    def load_data(self, skills_path: str, relationships_path: str) -> bool:
        """
        Load enriched skills and their relationships
        
        Args:
            skills_path: Path to the enriched skills JSON file
            relationships_path: Path to the skill relationships JSON file
            
        Returns:
            True if data loaded successfully, False otherwise
        """
        logger.info(f"Loading data from {skills_path} and {relationships_path}")
        
        try:
            # Load enriched skills
            with open(skills_path, 'r') as f:
                self.enriched_skills = json.load(f)
                
            # Extract all domains
            self.domains = set(skill.get('category', 'Unknown') for skill in self.enriched_skills)
            
            # Load relationships
            with open(relationships_path, 'r') as f:
                self.skill_relationships = json.load(f)
            
            logger.info(f"Loaded {len(self.enriched_skills)} skills across {len(self.domains)} domains")
            logger.info(f"Loaded relationships for {len(self.skill_relationships)} skills")
            
            return True
        
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def create_relationship_graph(self, 
                                 max_skills: int = 20,
                                 min_similarity: float = 0.3, 
                                 exclude_unrelated: bool = True) -> nx.Graph:
        """
        Create a graph representation of skill relationships
        
        Args:
            max_skills: Maximum number of skills to include in the graph
            min_similarity: Minimum similarity threshold for including relationships
            exclude_unrelated: Whether to exclude unrelated relationships
            
        Returns:
            A NetworkX graph of skill relationships
        """
        logger.info(f"Creating relationship graph with max {max_skills} skills, min similarity {min_similarity}")
        
        # Create a new graph
        G: nx.Graph = nx.Graph()
        
        # Limit to top N skills to avoid overcrowded visualization
        skill_names = [skill['name'] for skill in self.enriched_skills[:max_skills]]
        
        # Add nodes (skills)
        for skill in self.enriched_skills[:max_skills]:
            name = skill['name']
            domain = skill.get('category', 'Unknown')
            G.add_node(name, domain=domain)
        
        # Add edges (relationships)
        edge_count = 0
        for skill1 in skill_names:
            if skill1 in self.skill_relationships:
                for skill2, rel_data in self.skill_relationships[skill1].items():
                    if skill2 in skill_names:
                        relationship = rel_data.get('relationship', 'Unknown')
                        similarity = rel_data.get('similarity', 0)
                        
                        # Only add edges that meet criteria
                        if similarity >= min_similarity and (not exclude_unrelated or relationship != 'Unrelated'):
                            # Use a default color if not specified, or convert RGBA tuple to hex string
                            edge_color_val = RELATIONSHIP_COLORS.get(relationship, (0.5, 0.5, 0.5, 0.5))
                            if isinstance(edge_color_val, tuple) and len(edge_color_val) == 4:
                                edge_color_hex = '#{:02x}{:02x}{:02x}'.format(int(edge_color_val[0]*255), int(edge_color_val[1]*255), int(edge_color_val[2]*255))
                                alpha = edge_color_val[3]
                            else:
                                edge_color_hex = edge_color_val # assume it's already a string
                                alpha = 0.5


                            G.add_edge(skill1, skill2, 
                                      relationship=relationship, 
                                      similarity=similarity,
                                      weight=similarity,
                                      color=edge_color_hex,
                                      alpha=alpha)
                            edge_count += 1
        
        logger.info(f"Created graph with {len(G.nodes)} nodes and {edge_count} edges")
        return G
    
    def visualize_network_graph(self, output_path: str, max_skills: int = 50, min_similarity: float = 0.1):
        """
        Visualize the skill relationship network
        
        Args:
            output_path: Path to save the visualization
            
        Returns:
            Path to the saved visualization
        """
        logger.info("Generating network graph visualization")
        
        # Create the graph
        G = self.create_relationship_graph(max_skills, min_similarity)
        
        if len(G.nodes) == 0:
            logger.warning("No skills to visualize")
            return "No visualization generated - no skills to visualize"
        
        # Set up the figure
        plt.figure(figsize=(15, 12))
        
        # Get positions using a spring layout
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)  # Increased k for more spread
        
        # Draw nodes
        domain_colors = {}
        color_map = get_cmap('tab10')
        
        for i, domain in enumerate(self.domains):
            rgba = color_map(i / len(self.domains))
            # Convert RGBA to hex string for matplotlib
            domain_colors[domain] = '#{:02x}{:02x}{:02x}'.format(
                int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255)
            )
        
        for domain in self.domains:
            nodes = [node for node, data in G.nodes(data=True) if data.get('domain') == domain]
            nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=domain_colors[domain], 
                                  node_size=300, alpha=0.8, label=domain)
        
        # Draw edges with color based on relationship type
        for relationship_type, color in RELATIONSHIP_COLORS.items():
            edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('relationship') == relationship_type]
            nx.draw_networkx_edges(G, pos, edgelist=edges, width=1.5, alpha=0.7, edge_color=color, 
                                  label=relationship_type)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        # Add legends
        plt.legend(loc='upper right', title="Domains")
        
        edge_legend_elements = [plt.Line2D([0], [0], color=color, lw=2, label=rel_type) 
                               for rel_type, color in RELATIONSHIP_COLORS.items()]
        plt.legend(handles=edge_legend_elements, loc='upper left', title="Relationships")
        
        # Remove axis
        plt.axis('off')
        
        # Add title
        plt.title(f"Skill Relationship Network\n{len(G.nodes)} skills, {len(G.edges)} relationships", 
                 fontsize=16, pad=20)
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Network visualization saved to {output_path}")
        return output_path
    
    def visualize_domain_heatmap(self, output_path: str) -> str:
        """
        Create a heatmap of relationships between domains
        
        Args:
            output_path: Path to save the visualization
            
        Returns:
            Path to the saved visualization
        """
        logger.info("Generating domain relationship heatmap")
        
        # Create a domain relationship matrix
        domain_matrix = {}
        domain_list = sorted(list(self.domains))
        
        # Initialize the matrix
        for d1 in domain_list:
            domain_matrix[d1] = {d2: 0 for d2 in domain_list}
        
        # Count relationships between domains
        total_relationships = 0
        for skill1, relationships in self.skill_relationships.items():
            for skill2, rel_data in relationships.items():
                # Find the domains for each skill
                domain1 = next((s.get('category') for s in self.enriched_skills 
                               if s.get('name') == skill1), 'Unknown')
                domain2 = next((s.get('category') for s in self.enriched_skills 
                               if s.get('name') == skill2), 'Unknown')
                
                if domain1 in domain_matrix and domain2 in domain_matrix[domain1]:
                    # Only count non-unrelated relationships
                    if rel_data.get('relationship') != 'Unrelated':
                        domain_matrix[domain1][domain2] += 1
                        total_relationships += 1
        
        if total_relationships == 0:
            logger.warning("No relationships to visualize")
            return "No visualization generated - no relationships to visualize"
        
        # Create numpy array from the matrix for visualization
        import numpy as np
        matrix_data = []
        for d1 in domain_list:
            row = [domain_matrix[d1][d2] for d2 in domain_list]
            matrix_data.append(row)
        
        matrix_array = np.array(matrix_data)
        
        # Create the heatmap
        plt.figure(figsize=(12, 10))
        plt.imshow(matrix_array, cmap='YlOrRd')
        
        # Add labels
        plt.xticks(range(len(domain_list)), domain_list, rotation=45, ha='right')
        plt.yticks(range(len(domain_list)), domain_list)
        
        # Add colorbar
        cbar = plt.colorbar()
        cbar.set_label('Number of Relationships')
        
        # Add values to cells
        for i in range(len(domain_list)):
            for j in range(len(domain_list)):
                text_color = 'black' if matrix_array[i, j] < np.max(matrix_array)/2 else 'white'
                plt.text(j, i, str(int(matrix_array[i, j])), 
                        ha='center', va='center', color=text_color)
        
        # Add title
        plt.title(f"Domain Relationship Heatmap\n{total_relationships} relationships across {len(domain_list)} domains", 
                 fontsize=16, pad=20)
        
        # Make it tight
        plt.tight_layout()
        
        # Save the figure
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Domain heatmap saved to {output_path}")
        return output_path
    
    def visualize_relationship_chord_diagram(self, output_path: str) -> str:
        """
        Create a chord diagram of skill relationships between domains
        
        Args:
            output_path: Path to save the visualization
            
        Returns:
            Path to the saved visualization
        """
        try:
            import numpy as np
            import holoviews as hv  # type: ignore
            from holoviews import opts, dim
            hv.extension('matplotlib')
        except ImportError:
            logger.error("holoviews package is required for chord diagrams")
            return "Error: holoviews package is required for chord diagrams"
        
        logger.info("Generating relationship chord diagram")
        
        # Create a domain relationship matrix
        domain_list = sorted(list(self.domains))
        matrix_size = len(domain_list)
        matrix_data = np.zeros((matrix_size, matrix_size))
        
        # Count relationships between domains
        for skill1, relationships in self.skill_relationships.items():
            for skill2, rel_data in relationships.items():
                # Find the domains for each skill
                domain1 = next((s.get('category') for s in self.enriched_skills 
                               if s.get('name') == skill1), 'Unknown')
                domain2 = next((s.get('category') for s in self.enriched_skills 
                               if s.get('name') == skill2), 'Unknown')
                
                # Get indices
                if domain1 in domain_list and domain2 in domain_list:
                    d1_idx = domain_list.index(domain1)
                    d2_idx = domain_list.index(domain2)
                    
                    # Only count non-unrelated relationships
                    if rel_data.get('relationship') != 'Unrelated':
                        matrix_data[d1_idx, d2_idx] += 1
        
        # Create chord diagram
        chord = hv.Chord((range(matrix_size), range(matrix_size), matrix_data)).select(value=(1, None))
        chord = chord.opts(
            opts.Chord(cmap='Category20', edge_cmap='Category20', edge_color=dim('source').str(),
                      labels=domain_list, node_color=dim('index').str(),
                      title="Skill Relationship Chord Diagram")
        )
        
        # Save to file
        hv.save(chord, output_path, fmt='png', backend='matplotlib')
        
        logger.info(f"Chord diagram saved to {output_path}")
        return output_path
    
    def generate_all_visualizations(self) -> Dict[str, str]:
        """
        Generate all available visualizations
        
        Returns:
            Dictionary mapping visualization types to output paths
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        visualizations = {}
        
        # Network graph
        network_output = os.path.join(VISUALIZATION_DIR, f'skill_network_{timestamp}.png')
        visualizations['network'] = self.visualize_network_graph(network_output)
        
        # Domain heatmap
        heatmap_output = os.path.join(VISUALIZATION_DIR, f'domain_heatmap_{timestamp}.png')
        visualizations['heatmap'] = self.visualize_domain_heatmap(heatmap_output)
        
        # Try to generate chord diagram if dependencies are available
        try:
            chord_output = os.path.join(VISUALIZATION_DIR, f'relationship_chord_{timestamp}.png')
            visualizations['chord'] = self.visualize_relationship_chord_diagram(chord_output)
        except Exception as e:
            logger.warning(f"Could not generate chord diagram: {e}")
            visualizations['chord'] = f"Error: {str(e)}"
        
        return visualizations

def main():
    """Main function for the visualization tool"""
    parser = argparse.ArgumentParser(description='Generate visualizations for skill relationships')
    
    parser.add_argument('--skills', type=str, default=os.path.join(SKILL_DIR, 'enriched_skills.json'),
                       help='Path to the enriched skills JSON file')
    
    parser.add_argument('--relationships', type=str, default=os.path.join(SKILL_DIR, 'skill_relationships.json'),
                       help='Path to the skill relationships JSON file')
    
    parser.add_argument('--all', action='store_true',
                       help='Generate all available visualizations')
    
    parser.add_argument('--network', action='store_true',
                       help='Generate network graph visualization')
    
    parser.add_argument('--heatmap', action='store_true',
                       help='Generate domain relationship heatmap')
    
    parser.add_argument('--chord', action='store_true',
                       help='Generate chord diagram (requires holoviews)')
    
    args = parser.parse_args()
    
    # Create the visualizer
    visualizer = SkillRelationshipVisualizer()
    
    # Load data
    if not visualizer.load_data(args.skills, args.relationships):
        logger.error("Failed to load data. Exiting.")
        sys.exit(1)
    
    # Generate visualizations based on arguments
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {}
    
    if args.all or not (args.network or args.heatmap or args.chord):
        results = visualizer.generate_all_visualizations()
    else:
        if args.network:
            network_output = os.path.join(VISUALIZATION_DIR, f'skill_network_{timestamp}.png')
            results['network'] = visualizer.visualize_network_graph(network_output)
        
        if args.heatmap:
            heatmap_output = os.path.join(VISUALIZATION_DIR, f'domain_heatmap_{timestamp}.png')
            results['heatmap'] = visualizer.visualize_domain_heatmap(heatmap_output)
        
        if args.chord:
            try:
                chord_output = os.path.join(VISUALIZATION_DIR, f'relationship_chord_{timestamp}.png')
                results['chord'] = visualizer.visualize_relationship_chord_diagram(chord_output)
            except Exception as e:
                logger.warning(f"Could not generate chord diagram: {e}")
                results['chord'] = f"Error: {str(e)}"
    
    # Print results
    print("\n===== Skill Relationship Visualization Results =====")
    for viz_type, output_path in results.items():
        print(f"{viz_type.capitalize()}: {output_path}")
    print("====================================================\n")

if __name__ == "__main__":
    main()
