from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from src.agents.data_agent import DataAgent
from src.agents.research_agent import ResearchAgent
from src.agents.report_agent import ReportAgent
from src.core.tool_calling import ToolCallingEngine


class AgentOrchestrator:
    def __init__(self) -> None:
        self.data_agent = DataAgent()
        self.research_agent = ResearchAgent()
        self.report_agent = ReportAgent()
        self.tool_calling = ToolCallingEngine()

    def route_task(self, query: str) -> str:
        q = query.lower()
        if any(k in q for k in ["price", "价格", "tvl", "市值"]):
            return "data"
        if any(k in q for k in ["report", "报告", "总结"]):
            return "report"
        return "research"

    def run_chat(self, query: str) -> dict[str, Any]:
        route = self.route_task(query)

        if route == "data":
            data_result = self.data_agent.run(query)
            tool_info = self.tool_calling.run_data_tools(
                query=query,
                tools=self.data_agent.tools,
                symbol=data_result["inputs"]["symbol"],
                protocol=data_result["inputs"]["protocol"],
            )
            return {
                "route": route,
                "result": data_result,
                "tool_calling": tool_info,
                "answer": tool_info["summary"],
            }

        if route == "research":
            research_result = self.research_agent.run(query)
            return {
                "route": route,
                "result": research_result,
                "answer": "已完成研究分析，重点见 insights 与 risk 字段。",
            }

        data_result = self.data_agent.run(query)
        research_result = self.research_agent.run(query)
        report_result = self.report_agent.run(query, data_result, research_result)

        return {
            "route": route,
            "result": report_result,
            "answer": "已生成结构化报告，请查看 report 字段中的摘要与关键指标。",
        }

    def stream_chat(self, query: str) -> Iterator[str]:
        result = self.run_chat(query)
        text = str(result.get("answer") or "分析完成。")
        for token in text.split():
            yield token + " "

    def run_analysis(self, query: str, protocol: str | None = None) -> dict[str, Any]:
        data_result = self.data_agent.run(query, protocol=protocol)
        research_result = self.research_agent.run(query, protocol=protocol)
        return {
            "data": data_result,
            "research": research_result,
        }

    def run_report(self, query: str, protocol: str | None = None) -> dict[str, Any]:
        data_result = self.data_agent.run(query, protocol=protocol)
        research_result = self.research_agent.run(query, protocol=protocol)
        return self.report_agent.run(query, data_result, research_result)
