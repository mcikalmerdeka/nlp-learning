import subprocess
import json

def get_ollama_models():
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        lines = result.stdout.strip().split('\n')
        
        if len(lines) < 2:
            print("No models found.")
            return
        
        print("Available Ollama Models:\n")
        print(lines[0])  # Header
        print("-" * 80)
        
        for line in lines[1:]:
            print(line)
        
        print(f"\nTotal models: {len(lines) - 1}")
        
    except FileNotFoundError:
        print("Error: Ollama is not installed or not in PATH")
    except subprocess.CalledProcessError as e:
        print(f"Error running ollama: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    get_ollama_models()
