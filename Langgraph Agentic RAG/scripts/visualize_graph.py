"""Script to generate graph visualization."""

import os
import sys

# Add project root to path for direct script execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.builder import save_graph_visualization


def main() -> None:
    """Generate and save graph visualization."""
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "rag_graph.png")
    save_graph_visualization(output_path)


if __name__ == "__main__":
    main()

