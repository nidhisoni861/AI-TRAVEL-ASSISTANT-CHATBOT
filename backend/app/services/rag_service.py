"""ChromaDB-backed RAG service.

On first start, seeds the collection from `data/travel_knowledge.jsonl`.
Each line in that file should be {"text": "...", "source": "..."}.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from loguru import logger


@dataclass
class RetrievedDoc:
    page_content: str
    metadata: dict


class RAGService:
    COLLECTION = "travel_knowledge"

    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        self._client = None
        self._collection = None
        self._embedder = None
        self.ready = False

    def initialize(self) -> None:
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            logger.warning(f"chromadb / sentence-transformers not installed: {e}. RAG disabled.")
            return

        self._client = chromadb.PersistentClient(path=self.persist_dir)
        self._collection = self._client.get_or_create_collection(self.COLLECTION)
        self._embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        if self._collection.count() == 0:
            self._seed_from_file()
        self.ready = True
        logger.info(f"RAG ready, {self._collection.count()} docs in '{self.COLLECTION}'")

    def _seed_from_file(self) -> None:
        path = Path(__file__).parent.parent.parent / "data" / "travel_knowledge.jsonl"
        if not path.exists():
            logger.warning(f"No seed file at {path}; RAG starts empty.")
            return
        docs, ids, metas = [], [], []
        with path.open(encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                docs.append(obj["text"])
                ids.append(f"doc-{i}")
                metas.append({"source": obj.get("source", "kb")})
        if not docs:
            return
        embeddings = self._embedder.encode(docs).tolist()
        self._collection.add(documents=docs, ids=ids, metadatas=metas, embeddings=embeddings)
        logger.info(f"Seeded RAG with {len(docs)} docs from {path.name}")

    def query(self, text: str, k: int = 4) -> list[RetrievedDoc]:
        if not self.ready:
            return []
        try:
            qemb = self._embedder.encode([text]).tolist()
            res = self._collection.query(query_embeddings=qemb, n_results=k)
            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            return [RetrievedDoc(page_content=d, metadata=m or {}) for d, m in zip(docs, metas)]
        except Exception as e:
            logger.exception(f"RAG query failed: {e}")
            return []

    def add(self, text: str, source: Optional[str] = None) -> None:
        if not self.ready:
            return
        idx = self._collection.count()
        emb = self._embedder.encode([text]).tolist()
        self._collection.add(
            documents=[text],
            ids=[f"doc-{idx}"],
            metadatas=[{"source": source or "manual"}],
            embeddings=emb,
        )
