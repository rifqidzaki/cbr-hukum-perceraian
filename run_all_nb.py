import nbformat
from nbclient import NotebookClient
import sys
import os

notebooks = [
    "notebooks/02_Case_Representation.ipynb",
    "notebooks/03_retrieval.ipynb",
    "notebooks/04_predict.ipynb",
    "notebooks/05_evaluation.ipynb"
]

def run_notebook(notebook_path):
    print(f"Running {notebook_path}...")
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
        
    notebook_dir = os.path.dirname(os.path.abspath(notebook_path))
    
    # Run the notebook in the notebook's directory so relative paths work
    client = NotebookClient(nb, timeout=None, kernel_name='python3', resources={'metadata': {'path': notebook_dir}})
    try:
        client.execute()
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        print(f"Successfully executed {notebook_path}")
    except Exception as e:
        print(f"Error executing {notebook_path}: {e}")
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        sys.exit(1)

if __name__ == "__main__":
    for nb in notebooks:
        run_notebook(nb)
