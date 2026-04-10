from __future__ import annotations

from typing import Any

from src.tools.defi_tools import DeFiTools


class DataAgent:
    def __init__(self, tools: DeFiTools | None = None) -> None:
        self.tools = tools or DeFiTools()

    def run(self, query: str, symbol: str | None = None, protocol: str | None = None) -> dict[str, Any]:
        symbol_used = symbol or self._extract_symbol(query)
        protocol_used = protocol or self._extract_protocol(query)

        price = self.tools.get_token_price(symbol_used)
        tvl = self.tools.get_protocol_tvl(protocol_used)

        return {
            "agent": "data",
            "inputs": {"query": query, "symbol": symbol_used, "protocol": protocol_used},
            "price": price,
            "tvl": tvl,
        }

    @staticmethod
    def _extract_symbol(query: str) -> str:
        upper = query.upper()
        for s in ["ETH", "BTC", "UNI", "AAVE", "LDO"]:
            if s in upper:
                return s
        return "ETH"

    @staticmethod
    def _extract_protocol(query: str) -> str:
        lower = query.lower()
        for p in ["uniswap", "aave", "lido"]:
            if p in lower:
                return p
        return "uniswap"
