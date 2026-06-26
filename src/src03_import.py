import importlib.util
from pathlib import Path

module_path = Path(__file__).resolve().parent / '03_retrieval.py'
spec = importlib.util.spec_from_file_location('retrieval_module', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def retrieve_safe(query: str, k: int = 5):
    return module.retrieve(query, k)
