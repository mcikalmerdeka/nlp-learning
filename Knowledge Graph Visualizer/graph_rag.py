import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from typing import List, Dict, Tuple, Optional
import re

class MedicalKnowledgeGraph:
    """
    A graph-based RAG system for medical knowledge with improved structure
    and query capabilities.
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_knowledge_graph()
        
    def _build_knowledge_graph(self):
        """Build comprehensive medical knowledge graph"""
        
        # Define nodes with enhanced metadata
        nodes = {
            # Diseases
            'diabetes_t2': {
                'type': 'disease',
                'name': 'Type 2 Diabetes',
                'description': 'Chronic condition affecting blood sugar regulation',
                'prevalence': 'high',
                'severity': 'moderate'
            },
            
            # Medications
            'metformin': {
                'type': 'medication',
                'name': 'Metformin',
                'description': 'First-line medication for type 2 diabetes',
                'class': 'biguanide',
                'dosage': '500-2000mg daily'
            },
            'insulin': {
                'type': 'medication',
                'name': 'Insulin',
                'description': 'Hormone medication for blood sugar control',
                'class': 'hormone',
                'dosage': 'varies by patient'
            },
            'lisinopril': {
                'type': 'medication',
                'name': 'Lisinopril',
                'description': 'ACE inhibitor for blood pressure',
                'class': 'ace_inhibitor',
                'dosage': '10-40mg daily'
            },
            'glipizide': {
                'type': 'medication',
                'name': 'Glipizide',
                'description': 'Sulfonylurea that stimulates insulin release',
                'class': 'sulfonylurea',
                'dosage': '5-20mg daily'
            },
            
            # Conditions
            'kidney_disease': {
                'type': 'condition',
                'name': 'Chronic Kidney Disease',
                'description': 'Progressive loss of kidney function',
                'severity': 'high'
            },
            'hypertension': {
                'type': 'condition',
                'name': 'Hypertension',
                'description': 'Elevated blood pressure',
                'severity': 'moderate'
            },
            'heart_disease': {
                'type': 'condition',
                'name': 'Cardiovascular Disease',
                'description': 'Heart and blood vessel disorders',
                'severity': 'high'
            },
            
            # Side Effects
            'lactic_acidosis': {
                'type': 'side_effect',
                'name': 'Lactic Acidosis',
                'description': 'Dangerous buildup of lactic acid',
                'frequency': 'rare',
                'severity': 'severe'
            },
            'weight_gain': {
                'type': 'side_effect',
                'name': 'Weight Gain',
                'description': 'Increase in body weight',
                'frequency': 'common',
                'severity': 'mild'
            },
            'hypoglycemia': {
                'type': 'side_effect',
                'name': 'Hypoglycemia',
                'description': 'Low blood sugar episodes',
                'frequency': 'common',
                'severity': 'moderate'
            },
            'gi_distress': {
                'type': 'side_effect',
                'name': 'GI Distress',
                'description': 'Nausea, diarrhea, stomach upset',
                'frequency': 'common',
                'severity': 'mild'
            },
            
            # Symptoms
            'high_blood_sugar': {
                'type': 'symptom',
                'name': 'Hyperglycemia',
                'description': 'Elevated blood glucose levels',
                'severity': 'varies'
            },
            'fatigue': {
                'type': 'symptom',
                'name': 'Fatigue',
                'description': 'Persistent tiredness',
                'severity': 'mild'
            },
            'thirst': {
                'type': 'symptom',
                'name': 'Excessive Thirst',
                'description': 'Polydipsia - increased thirst',
                'severity': 'mild'
            },
            
            # Lifestyle Interventions
            'exercise': {
                'type': 'lifestyle',
                'name': 'Regular Exercise',
                'description': 'Physical activity 150+ min/week',
                'effectiveness': 'high'
            },
            'diet': {
                'type': 'lifestyle',
                'name': 'Dietary Changes',
                'description': 'Low carb, balanced nutrition',
                'effectiveness': 'high'
            },
            'weight_loss': {
                'type': 'lifestyle',
                'name': 'Weight Loss',
                'description': '5-10% body weight reduction',
                'effectiveness': 'high'
            }
        }
        
        # Add nodes to graph
        for node_id, attrs in nodes.items():
            self.graph.add_node(node_id, **attrs)
        
        # Define edges with relationship metadata
        edges = [
            # Disease to Symptoms
            ('diabetes_t2', 'high_blood_sugar', {'relation': 'has_symptom', 'strength': 'primary'}),
            ('diabetes_t2', 'fatigue', {'relation': 'has_symptom', 'strength': 'secondary'}),
            ('diabetes_t2', 'thirst', {'relation': 'has_symptom', 'strength': 'secondary'}),
            
            # Disease to Treatments
            ('diabetes_t2', 'metformin', {'relation': 'treated_by', 'line': 'first', 'efficacy': 0.85}),
            ('diabetes_t2', 'insulin', {'relation': 'treated_by', 'line': 'second', 'efficacy': 0.95}),
            ('diabetes_t2', 'glipizide', {'relation': 'treated_by', 'line': 'second', 'efficacy': 0.75}),
            
            # Disease to Lifestyle
            ('diabetes_t2', 'exercise', {'relation': 'managed_by', 'impact': 'high'}),
            ('diabetes_t2', 'diet', {'relation': 'managed_by', 'impact': 'high'}),
            ('diabetes_t2', 'weight_loss', {'relation': 'managed_by', 'impact': 'very_high'}),
            
            # Disease Complications
            ('diabetes_t2', 'kidney_disease', {'relation': 'can_lead_to', 'probability': 0.3}),
            ('diabetes_t2', 'hypertension', {'relation': 'often_occurs_with', 'probability': 0.6}),
            ('diabetes_t2', 'heart_disease', {'relation': 'can_lead_to', 'probability': 0.4}),
            
            # Medication Side Effects
            ('metformin', 'lactic_acidosis', {'relation': 'rare_side_effect', 'frequency': 0.001}),
            ('metformin', 'gi_distress', {'relation': 'side_effect', 'frequency': 0.25}),
            ('insulin', 'weight_gain', {'relation': 'side_effect', 'frequency': 0.4}),
            ('insulin', 'hypoglycemia', {'relation': 'side_effect', 'frequency': 0.5}),
            ('glipizide', 'hypoglycemia', {'relation': 'side_effect', 'frequency': 0.6}),
            ('glipizide', 'weight_gain', {'relation': 'side_effect', 'frequency': 0.3}),
            
            # Contraindications
            ('metformin', 'kidney_disease', {'relation': 'contraindicated_in', 'severity': 'absolute'}),
            ('glipizide', 'kidney_disease', {'relation': 'requires_adjustment', 'severity': 'moderate'}),
            
            # Condition Treatments
            ('hypertension', 'lisinopril', {'relation': 'treated_by', 'line': 'first', 'efficacy': 0.8}),
            
            # Protective Effects
            ('lisinopril', 'kidney_disease', {'relation': 'protects_against', 'strength': 'moderate'}),
            ('lisinopril', 'heart_disease', {'relation': 'protects_against', 'strength': 'moderate'}),
            
            # Lifestyle Effects
            ('exercise', 'high_blood_sugar', {'relation': 'reduces', 'impact': 'high'}),
            ('exercise', 'weight_gain', {'relation': 'prevents', 'impact': 'high'}),
            ('diet', 'high_blood_sugar', {'relation': 'reduces', 'impact': 'very_high'}),
            ('weight_loss', 'high_blood_sugar', {'relation': 'reduces', 'impact': 'very_high'}),
        ]
        
        # Add edges to graph
        self.graph.add_edges_from([(e[0], e[1], e[2]) for e in edges])
    
    def find_paths(self, start: str, end: str, max_depth: int = 4) -> List[List[str]]:
        """Find all paths between two nodes"""
        try:
            paths = list(nx.all_simple_paths(self.graph, start, end, cutoff=max_depth))
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def get_neighbors(self, node: str, relation: Optional[str] = None) -> List[Dict]:
        """Get neighboring nodes with optional relation filter"""
        neighbors = []
        for successor in self.graph.successors(node):
            edge_data = self.graph.get_edge_data(node, successor)
            if relation is None or edge_data.get('relation') == relation:
                neighbors.append({
                    'node_id': successor,
                    'node_data': self.graph.nodes[successor],
                    'edge_data': edge_data
                })
        return neighbors
    
    def find_node_by_keyword(self, keyword: str) -> Optional[Tuple[str, Dict]]:
        """Find node by keyword match"""
        keyword_lower = keyword.lower()
        for node_id, attrs in self.graph.nodes(data=True):
            if (keyword_lower in attrs.get('name', '').lower() or 
                keyword_lower in attrs.get('description', '').lower()):
                return (node_id, attrs)
        return None
    
    def query(self, question: str) -> Dict:
        """
        Process natural language queries using graph traversal
        """
        question_lower = question.lower()
        response = {
            'answer': '',
            'reasoning': [],
            'paths': [],
            'confidence': 0.0
        }
        
        # Query Pattern: Side effects
        if 'side effect' in question_lower:
            med_match = None
            for med in ['metformin', 'insulin', 'glipizide', 'lisinopril']:
                if med in question_lower:
                    med_match = med
                    break
            
            if med_match:
                node_result = self.find_node_by_keyword(med_match)
                if node_result:
                    node_id, node_data = node_result
                    side_effects = self.get_neighbors(node_id, 'side_effect')
                    rare_effects = self.get_neighbors(node_id, 'rare_side_effect')
                    all_effects = side_effects + rare_effects
                    
                    response['reasoning'].append(f"Found {node_data['name']}")
                    response['reasoning'].append(f"Retrieved {len(all_effects)} side effects")
                    
                    effects_list = []
                    for effect in all_effects:
                        freq = effect['edge_data'].get('frequency', 'unknown')
                        effects_list.append(
                            f"{effect['node_data']['name']} ({effect['node_data']['description']}) - "
                            f"Frequency: {freq}"
                        )
                    
                    response['answer'] = (
                        f"Side effects of {node_data['name']}:\n" +
                        "\n".join(f"• {e}" for e in effects_list)
                    )
                    response['confidence'] = 0.95
        
        # Query Pattern: Contraindications
        elif 'contraindication' in question_lower or 'contraindicated' in question_lower:
            med_match = None
            for med in ['metformin', 'insulin', 'glipizide']:
                if med in question_lower:
                    med_match = med
                    break
            
            if med_match:
                node_result = self.find_node_by_keyword(med_match)
                if node_result:
                    node_id, node_data = node_result
                    contras = self.get_neighbors(node_id, 'contraindicated_in')
                    adjustments = self.get_neighbors(node_id, 'requires_adjustment')
                    
                    response['reasoning'].append(f"Found {node_data['name']}")
                    response['reasoning'].append(f"Found {len(contras)} absolute contraindications")
                    
                    if contras:
                        contra_list = [
                            f"{c['node_data']['name']}: {c['node_data']['description']}"
                            for c in contras
                        ]
                        response['answer'] = (
                            f"{node_data['name']} is contraindicated in:\n" +
                            "\n".join(f"• {c}" for c in contra_list)
                        )
                        if adjustments:
                            adj_list = [a['node_data']['name'] for a in adjustments]
                            response['answer'] += f"\n\nRequires dose adjustment in: {', '.join(adj_list)}"
                        response['confidence'] = 0.95
        
        # Query Pattern: Treatment
        elif 'treat' in question_lower or 'medication' in question_lower:
            disease_match = None
            if 'diabetes' in question_lower:
                disease_match = 'diabetes_t2'
            elif 'hypertension' in question_lower or 'blood pressure' in question_lower:
                disease_match = 'hypertension'
            
            if disease_match:
                treatments = self.get_neighbors(disease_match, 'treated_by')
                lifestyle = self.get_neighbors(disease_match, 'managed_by')
                
                disease_name = self.graph.nodes[disease_match]['name']
                response['reasoning'].append(f"Found {disease_name}")
                response['reasoning'].append(f"Found {len(treatments)} medications, {len(lifestyle)} lifestyle interventions")
                
                med_list = []
                for t in treatments:
                    line = t['edge_data'].get('line', 'unknown')
                    efficacy = t['edge_data'].get('efficacy', 0) * 100
                    med_list.append(
                        f"{t['node_data']['name']} ({line}-line, ~{efficacy:.0f}% efficacy) - "
                        f"{t['node_data']['description']}"
                    )
                
                lifestyle_list = [
                    f"{l['node_data']['name']}: {l['node_data']['description']}"
                    for l in lifestyle
                ]
                
                response['answer'] = f"Treatment options for {disease_name}:\n\n"
                response['answer'] += "Medications:\n" + "\n".join(f"• {m}" for m in med_list)
                response['answer'] += "\n\nLifestyle Interventions:\n" + "\n".join(f"• {l}" for l in lifestyle_list)
                response['confidence'] = 0.9
        
        # Query Pattern: Relationship/Connection
        elif 'relate' in question_lower or 'connection' in question_lower or 'link' in question_lower:
            # Find entities mentioned
            entities = []
            for node_id, attrs in self.graph.nodes(data=True):
                if attrs['name'].lower() in question_lower:
                    entities.append(node_id)
            
            if len(entities) >= 2:
                paths = self.find_paths(entities[0], entities[1])
                
                if paths:
                    response['reasoning'].append(f"Found {len(paths)} connection path(s)")
                    
                    # Describe the shortest path
                    shortest = paths[0]
                    path_desc = []
                    for i in range(len(shortest) - 1):
                        from_node = self.graph.nodes[shortest[i]]
                        to_node = self.graph.nodes[shortest[i + 1]]
                        edge_data = self.graph.get_edge_data(shortest[i], shortest[i + 1])
                        relation = edge_data.get('relation', 'related to')
                        
                        path_desc.append(
                            f"{from_node['name']} [{relation}] {to_node['name']}"
                        )
                    
                    response['answer'] = (
                        f"Connection between {self.graph.nodes[entities[0]]['name']} and "
                        f"{self.graph.nodes[entities[1]]['name']}:\n\n" +
                        "\n → ".join(path_desc)
                    )
                    response['paths'] = paths
                    response['confidence'] = 0.85
        
        if not response['answer']:
            response['answer'] = (
                "I can answer questions about:\n"
                "• Medication side effects (e.g., 'What are the side effects of metformin?')\n"
                "• Contraindications (e.g., 'What are contraindications for metformin?')\n"
                "• Treatment options (e.g., 'How is diabetes treated?')\n"
                "• Relationships (e.g., 'How does diabetes relate to kidney disease?')"
            )
            response['confidence'] = 0.5
        
        return response
    
    def visualize_graph_3d(self, figsize=(12, 10)):
        """Create 3D visualization of the knowledge graph"""
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # Use spring layout in 3D
        pos = nx.spring_layout(self.graph, dim=3, k=2, iterations=50)
        
        # Color mapping by node type
        color_map = {
            'disease': '#ff6b6b',
            'medication': '#4ecdc4',
            'condition': '#ffe66d',
            'side_effect': '#ff8c42',
            'symptom': '#a8e6cf',
            'lifestyle': '#95e1d3'
        }
        
        # Extract node positions and colors
        node_xyz = np.array([pos[node] for node in self.graph.nodes()])
        node_colors = [color_map.get(self.graph.nodes[node]['type'], '#888888') 
                       for node in self.graph.nodes()]
        
        # Plot nodes
        ax.scatter(node_xyz[:, 0], node_xyz[:, 1], node_xyz[:, 2],
                   c=node_colors, s=500, alpha=0.8, edgecolors='black', linewidths=1.5)
        
        # Plot edges
        for edge in self.graph.edges():
            x = [pos[edge[0]][0], pos[edge[1]][0]]
            y = [pos[edge[0]][1], pos[edge[1]][1]]
            z = [pos[edge[0]][2], pos[edge[1]][2]]
            ax.plot(x, y, z, 'gray', alpha=0.3, linewidth=1)
        
        # Add labels
        for node, (x, y, z) in pos.items():
            ax.text(x, y, z, self.graph.nodes[node]['name'], 
                   fontsize=8, ha='center', va='bottom')
        
        # Styling
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Medical Knowledge Graph - 3D Visualization', fontsize=14, fontweight='bold')
        
        # Remove grid
        ax.grid(False)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        
        # Create legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, label=type_name.replace('_', ' ').title())
                          for type_name, color in color_map.items()]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=9)
        
        plt.tight_layout()
        return fig


def main():
    """Demo of the Graph RAG system"""
    
    # Initialize knowledge graph
    print("Initializing Medical Knowledge Graph RAG System...\n")
    kg = MedicalKnowledgeGraph()
    
    print(f"Graph Statistics:")
    print(f"  • Nodes: {kg.graph.number_of_nodes()}")
    print(f"  • Edges: {kg.graph.number_of_edges()}")
    print(f"  • Avg Degree: {sum(dict(kg.graph.degree()).values()) / kg.graph.number_of_nodes():.2f}")
    print()
    
    # Example queries
    queries = [
        "What are the side effects of metformin?",
        "What are the contraindications for metformin?",
        "How is type 2 diabetes treated?",
        "How does diabetes relate to kidney disease?",
        "What are the side effects of insulin?",
    ]
    
    print("=" * 80)
    print("EXAMPLE QUERIES")
    print("=" * 80)
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        
        result = kg.query(query)
        
        print(f"Answer:\n{result['answer']}\n")
        
        if result['reasoning']:
            print("Reasoning Steps:")
            for i, step in enumerate(result['reasoning'], 1):
                print(f"  {i}. {step}")
        
        print(f"\nConfidence: {result['confidence']:.0%}")
        print("=" * 80)
    
    # Visualize
    print("\nGenerating 3D visualization...")
    fig = kg.visualize_graph_3d()
    plt.show()
    
    # Interactive mode
    print("\n" + "=" * 80)
    print("INTERACTIVE MODE (type 'quit' to exit)")
    print("=" * 80)
    
    while True:
        user_query = input("\nYour question: ").strip()
        if user_query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_query:
            continue
        
        result = kg.query(user_query)
        print(f"\n{result['answer']}")
        
        if result['reasoning']:
            print(f"\nConfidence: {result['confidence']:.0%}")


if __name__ == "__main__":
    main()