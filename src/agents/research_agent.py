from __future__ import annotations

from typing import Any

from src.core.rag import ChromaRAG, SimpleRAG, create_rag
from src.tools.defi_tools import DeFiTools


class ResearchAgent:
    def __init__(self, rag: SimpleRAG | ChromaRAG | None = None, tools: DeFiTools | None = None) -> None:
        self.rag = rag or create_rag()
        self.tools = tools or DeFiTools()

    def run(self, query: str, protocol: str | None = None) -> dict[str, Any]:
        protocol_used = protocol or self._extract_protocol(query)
        chunks = self.rag.retrieve(query, top_k=3)
        risk = self.tools.risk_analysis(protocol_used)

        insights = [
            "协议基本面需要结合 TVL 趋势、收入质量和用户留存。",
            "风险识别优先关注清算机制与预言机依赖。",
            "结论应附带来源并标注不确定性。",
        ]

        return {
            "agent": "research",
            "protocol": protocol_used,
            "retrieved_context": [
                {"source": c.source, "content": c.content, "score": c.score} for c in chunks
            ],
            "risk": risk,
            "insights": insights,
        }

    @staticmethod
    def _extract_protocol(query: str) -> str:
        lower = query.lower()
        for p in ["uniswap", "aave", "lido"]:
            if p in lower:
                return p
        return "uniswap"
