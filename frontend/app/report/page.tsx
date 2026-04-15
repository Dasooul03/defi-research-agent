"use client";

import { FormEvent, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function ReportPage() {
  const [protocol, setProtocol] = useState("aave");
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function generateReport(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: `generate report for ${protocol}`, protocol }),
      });
      if (!resp.ok) throw new Error(`请求失败: ${resp.status}`);
      const data = await resp.json();
      setReport(data.data?.report || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "网络异常，请检查后端服务");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell report-shell">
      <section className="hero">
        <h1>Protocol Report Deck</h1>
        <p>一键生成结构化报告，适配日常投研复盘。</p>
        <a href="/">返回聊天台</a>
      </section>

      <section className="panel">
        <form onSubmit={generateReport} className="row">
          <input value={protocol} onChange={(e) => setProtocol(e.target.value)} placeholder="协议，如 aave" />
          <button type="submit" disabled={loading}>{loading ? "生成中..." : "生成报告"}</button>
        </form>

        {error && <p style={{ color: "red" }}>错误：{error}</p>}

        {report && (
          <div className="report-card">
            <h2>{report.title}</h2>
            <p>{report.summary}</p>
            <ul>
              <li>Token Price: {report.key_metrics?.token_price_usd}</li>
              <li>TVL: {report.key_metrics?.tvl_usd}</li>
              <li>Risk: {report.key_metrics?.risk_level}</li>
            </ul>
          </div>
        )}
      </section>
    </main>
  );
}
