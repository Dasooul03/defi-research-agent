"use client";

import { FormEvent, useState } from "react";

type ChatMessage = { role: "user" | "assistant"; text: string };

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function HomePage() {
  const [query, setQuery] = useState("请给我 ETH 和 Uniswap 的快照分析");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!query.trim() || streaming) return;

    setMessages((prev) => [...prev, { role: "user", text: query }, { role: "assistant", text: "" }]);
    setStreaming(true);

    const resp = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });

    if (!resp.body) {
      setStreaming(false);
      return;
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const dataLine = line.split("\n").find((l) => l.startsWith("data: "));
        if (!dataLine) continue;
        const payload = JSON.parse(dataLine.slice(6));

        if (payload.type === "chunk") {
          setMessages((prev) => {
            const copy = [...prev];
            const last = copy[copy.length - 1];
            if (last && last.role === "assistant") {
              last.text += payload.content;
            }
            return copy;
          });
        }
      }
    }

    setStreaming(false);
  }

  return (
    <main className="shell">
      <section className="hero">
        <h1>DeFi Research Console</h1>
        <p>流式函数调用投研台，实时查看 Agent 输出。</p>
        <a href="/report">打开报告面板</a>
      </section>

      <section className="panel">
        <form onSubmit={handleSubmit}>
          <textarea value={query} onChange={(e) => setQuery(e.target.value)} rows={3} />
          <button type="submit" disabled={streaming}>{streaming ? "分析中..." : "开始流式分析"}</button>
        </form>

        <div className="messages">
          {messages.map((m, idx) => (
            <article key={idx} className={m.role === "user" ? "msg user" : "msg assistant"}>
              <header>{m.role === "user" ? "你" : "Agent"}</header>
              <pre>{m.text || "..."}</pre>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
