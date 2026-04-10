"use client";

import { FormEvent, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function ReportPage() {
  const [protocol, setProtocol] = useState("aave");
  const [report, setReport] = useState<any>(null);

  async function generateReport(e: FormEvent) {
    e.preventDefault();
    const resp = await fetch(`${API_BASE}/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: `generate report for ${protocol}`, protocol }),
    });
    const data = await resp.json();
    setReport(data.data?.report || null);
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
          <button type="submit">生成报告</button>
        </form>

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
