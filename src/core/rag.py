from __future__ import annotations

import hashlib
import warnings
from dataclasses import dataclass
from typing import Any

from src.core.settings import get_yaml_config


@dataclass
class RetrievedChunk:
    source: str
    content: str
    score: float


DEFAULT_DOCS: list[dict[str, Any]] = [
    {
        "source": "uniswap-v3-overview",
        "content": "Uniswap v3 uses concentrated liquidity, enabling LPs to provide capital within chosen price ranges.",
    },
    {
        "source": "aave-risk-note",
        "content": "Aave risk depends on collateral volatility, liquidation thresholds, and oracle reliability.",
    },
    {
        "source": "lido-tokenomics",
        "content": "Lido enables liquid staking and issues stETH. Key metrics include staking APR and validator concentration.",
    },
]


class SimpleRAG:
    """A tiny in-memory retriever used for MVP before vector DB integration."""

    def __init__(self, docs: list[dict[str, Any]] | None = None) -> None:
        self._docs: list[dict[str, Any]] = docs or DEFAULT_DOCS

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
        q_tokens = set(query.lower().split())
        scored: list[RetrievedChunk] = []

        for doc in self._docs:
            d_tokens = set(doc["content"].lower().split())
            overlap = len(q_tokens.intersection(d_tokens))
            score = overlap / max(len(q_tokens), 1)
            scored.append(
                RetrievedChunk(
                    source=doc["source"],
                    content=doc["content"],
                    score=score,
                )
            )

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]


class _HashEmbeddingFunction:
    """Deterministic local embedding to avoid external model downloads."""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim

    def __call__(self, input: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []

        for text in input:
            vec = [0.0] * self.dim
            tokens = text.lower().split()
            for token in tokens:
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                idx = int.from_bytes(digest[:4], "big") % self.dim
                vec[idx] += 1.0

            norm = sum(v * v for v in vec) ** 0.5
            if norm > 0:
                vec = [v / norm for v in vec]
            vectors.append(vec)

        return vectors


class ChromaRAG:
    """Vector retrieval backed by ChromaDB with local deterministic embeddings."""

    def __init__(
        self,
        docs: list[dict[str, Any]] | None = None,
        persist_directory: str = ".chroma",
        collection_name: str = "defi_research_docs",
    ) -> None:
        import chromadb

        self._docs = docs or DEFAULT_DOCS
        self._client = chromadb.PersistentClient(path=persist_directory)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=_HashEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"},
        )
        self._upsert_docs(self._docs)

    def _upsert_docs(self, docs: list[dict[str, Any]]) -> None:
        ids = [doc["source"] for doc in docs]
        documents = [doc["content"] for doc in docs]
        metadatas = [{"source": doc["source"]} for doc in docs]
        self._collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
        result = self._collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        docs = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        chunks: list[RetrievedChunk] = []
        for content, metadata, distance in zip(docs, metadatas, distances):
            source = str((metadata or {}).get("source", "unknown"))
            # Convert distance to a monotonic similarity score in (0, 1].
            score = 1.0 / (1.0 + float(distance))
            chunks.append(RetrievedChunk(source=source, content=content, score=score))

        return chunks


def create_rag(backend: str | None = None) -> SimpleRAG | ChromaRAG:
    cfg = get_yaml_config().get("rag", {})
    backend_used = (backend or str(cfg.get("backend", "simple"))).lower()

    if backend_used == "chroma":
        try:
            return ChromaRAG(
                persist_directory=str(cfg.get("persist_directory", ".chroma")),
                collection_name=str(cfg.get("collection_name", "defi_research_docs")),
            )
        except ModuleNotFoundError:
            warnings.warn(
                "Chroma backend requested but chromadb is not installed. Falling back to SimpleRAG.",
                RuntimeWarning,
                stacklevel=2,
            )

    return SimpleRAG()
