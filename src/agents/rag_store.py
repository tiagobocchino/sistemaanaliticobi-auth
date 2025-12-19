"""
Lightweight RAG store using BM25 scoring over local docs.
Keeps a JSON index on disk to avoid external dependencies.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


_TOKEN_RE = re.compile(r"[a-z0-9_]+")


def _tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


def _chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    if chunk_size <= 0:
        return [text]
    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 4)
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(length, start + chunk_size)
        chunks.append(text[start:end])
        if end == length:
            break
        start = max(0, end - overlap)
    return chunks


@dataclass
class RagHit:
    source: str
    text: str
    score: float


class RagStore:
    """
    Simple BM25-based retriever backed by a JSON index.
    """

    def __init__(self, index_path: Optional[str] = None) -> None:
        self.index_path = index_path or os.getenv("RAG_INDEX_PATH", "data/rag_index.json")
        self._index: Dict[str, object] = {}

    def has_index(self) -> bool:
        return bool(self._index)

    def load(self) -> bool:
        path = Path(self.index_path)
        if not path.exists():
            return False
        self._index = json.loads(path.read_text(encoding="utf-8"))
        return True

    def save(self) -> None:
        path = Path(self.index_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._index, ensure_ascii=False), encoding="utf-8")

    def build_from_paths(
        self,
        paths: Iterable[str],
        chunk_size: int = 900,
        overlap: int = 200,
    ) -> None:
        docs = []
        for path_str in paths:
            path = Path(path_str)
            if path.is_dir():
                for child in path.rglob("*"):
                    if child.is_file() and child.suffix.lower() in {".md", ".txt"}:
                        docs.extend(self._read_and_chunk(child, chunk_size, overlap))
            elif path.is_file():
                docs.extend(self._read_and_chunk(path, chunk_size, overlap))

        tf_list: List[Dict[str, int]] = []
        df: Dict[str, int] = {}
        doc_lengths: List[int] = []

        for doc in docs:
            tokens = _tokenize(doc["text"])
            doc_lengths.append(len(tokens))
            tf: Dict[str, int] = {}
            for tok in tokens:
                tf[tok] = tf.get(tok, 0) + 1
            tf_list.append(tf)
            for tok in tf.keys():
                df[tok] = df.get(tok, 0) + 1

        avg_doc_len = (sum(doc_lengths) / len(doc_lengths)) if doc_lengths else 0.0

        self._index = {
            "docs": docs,
            "tf": tf_list,
            "df": df,
            "doc_lengths": doc_lengths,
            "avg_doc_len": avg_doc_len,
            "total_docs": len(docs),
        }

    def query(self, text: str, top_k: int = 4) -> List[RagHit]:
        if not self._index:
            if not self.load():
                return []

        docs = self._index.get("docs", [])
        tf_list = self._index.get("tf", [])
        df = self._index.get("df", {})
        doc_lengths = self._index.get("doc_lengths", [])
        avg_doc_len = self._index.get("avg_doc_len", 0.0)
        total_docs = self._index.get("total_docs", 0)

        if not docs or not total_docs:
            return []

        tokens = _tokenize(text)
        if not tokens:
            return []

        scores: List[float] = [0.0 for _ in range(total_docs)]
        k1 = 1.5
        b = 0.75

        for tok in tokens:
            doc_freq = df.get(tok, 0)
            if doc_freq == 0:
                continue
            idf = (1.0 + ((total_docs - doc_freq + 0.5) / (doc_freq + 0.5)))
            for idx, tf in enumerate(tf_list):
                freq = tf.get(tok, 0)
                if freq == 0:
                    continue
                denom = freq + k1 * (1.0 - b + b * (doc_lengths[idx] / (avg_doc_len or 1.0)))
                scores[idx] += idf * (freq * (k1 + 1.0) / denom)

        ranked = sorted(range(total_docs), key=lambda i: scores[i], reverse=True)[:top_k]
        hits: List[RagHit] = []
        for idx in ranked:
            if scores[idx] <= 0:
                continue
            doc = docs[idx]
            hits.append(RagHit(source=doc["source"], text=doc["text"], score=float(scores[idx])))
        return hits

    def _read_and_chunk(self, path: Path, chunk_size: int, overlap: int) -> List[Dict[str, str]]:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []
        chunks = _chunk_text(text, chunk_size, overlap)
        return [{"source": str(path), "text": chunk} for chunk in chunks if chunk.strip()]


def default_rag_paths() -> List[str]:
    paths = ["README.md", "EXECUTE_ISSO.md", "docs"]
    for match in Path(".").glob("GUIA COMPLETO - CONSTRU*"):
        paths.append(str(match))
    return paths
