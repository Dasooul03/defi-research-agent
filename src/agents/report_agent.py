from __future__ import annotations

from typing import Any


class ReportAgent:
    def run(self, query: str, data_result: dict[str, Any], research_result: dict[str, Any]) -> dict[str, Any]:
        protocol = research_result.get("protocol", "unknown")
        price = data_result.get("price", {})
        tvl = data_result.get("tvl", {})
        risk = research_result.get("risk", {})

        report = {
            "title": f"{protocol.title()} Protocol Research Snapshot",
            "summary": "本报告为自动生成的 DeFi 快照分析，建议结合最新链上数据复核。",
            "key_metrics": {
                "token_price_usd": price.get("price_usd"),
                "tvl_usd": tvl.get("tvl_usd"),
                "risk_level": risk.get("risk_level"),
            },
            "highlights": research_result.get("insights", []),
            "sources": [
                item.get("source")
                for item in research_result.get("retrieved_context", [])
                if item.get("source")
            ],
            "disclaimer": "This output is for research reference only and not investment advice.",
        }

        return {
            "agent": "report",
            "query": query,
            "report": report,
        }
