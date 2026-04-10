from __future__ import annotations

import builtins

from src.core.rag import ChromaRAG, RetrievedChunk, SimpleRAG, create_rag


def test_simple_rag_retrieve_returns_top_k() -> None:
    rag = SimpleRAG()

    chunks = rag.retrieve("uniswap liquidity range", top_k=2)

    assert len(chunks) == 2
    assert all(isinstance(c, RetrievedChunk) for c in chunks)
    assert chunks[0].score >= chunks[1].score


def test_create_rag_default_backend_is_simple() -> None:
    rag = create_rag(backend="simple")
    assert isinstance(rag, SimpleRAG)


def test_create_rag_falls_back_when_chroma_missing(monkeypatch) -> None:
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "chromadb":
            raise ModuleNotFoundError("No module named 'chromadb'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    rag = create_rag(backend="chroma")

    assert isinstance(rag, SimpleRAG)


def test_create_rag_chroma_when_available() -> None:
    try:
        import chromadb  # noqa: F401
    except ModuleNotFoundError:
        return

    rag = create_rag(backend="chroma")

    assert isinstance(rag, ChromaRAG)
