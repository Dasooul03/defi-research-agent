from __future__ import annotations

from typing import Any

from src.core.settings import get_settings


class ToolCallingEngine:
    """Function-calling style execution with optional LangChain support."""

    def __init__(self) -> None:
        self._settings = get_settings()

    def run_data_tools(self, query: str, tools: Any, symbol: str, protocol: str) -> dict[str, Any]:
        tool_calls: list[dict[str, Any]] = []

        price = tools.get_token_price(symbol)
        tool_calls.append({"tool": "get_token_price", "args": {"symbol": symbol}, "output": price})

        tvl = tools.get_protocol_tvl(protocol)
        tool_calls.append(
            {"tool": "get_protocol_tvl", "args": {"protocol": protocol}, "output": tvl}
        )

        price_usd = price.get("price_usd")
        tvl_usd = tvl.get("tvl_usd")
        summary = (
            f"{symbol.upper()} 现价约 ${price_usd}。"
            f"{protocol.title()} TVL 约 ${tvl_usd}。"
        )

        return {
            "mode": "fallback-function-calling",
            "tool_calls": tool_calls,
            "summary": summary,
        }

    def try_langchain_plan(self, query: str) -> dict[str, Any] | None:
        """Returns planning metadata when LangChain is available and configured."""
        if not self._settings.openai_api_key:
            return None

        try:
            from langchain_core.messages import HumanMessage
            from langchain_openai import ChatOpenAI
        except ModuleNotFoundError:
            return None

        llm = ChatOpenAI(
            model=self._settings.model_name,
            timeout=self._settings.api_timeout_seconds,
            api_key=self._settings.openai_api_key,
        )
        msg = llm.invoke([HumanMessage(content=f"Extract intent from: {query}")])
        return {
            "mode": "langchain",
            "plan": getattr(msg, "content", ""),
        }
