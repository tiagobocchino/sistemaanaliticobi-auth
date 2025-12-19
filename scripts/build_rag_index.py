"""
Build the local RAG index from project docs.
"""
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.agents.rag_store import RagStore, default_rag_paths


def main() -> None:
    store = RagStore()
    paths = default_rag_paths()
    existing = [p for p in paths if Path(p).exists()]
    if not existing:
        print("No doc paths found to index.")
        return
    store.build_from_paths(existing)
    store.save()
    print(f"RAG index saved to {store.index_path} with {store._index.get('total_docs', 0)} chunks.")


if __name__ == "__main__":
    main()
