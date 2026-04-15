# DeFi Research Agent

AI-driven DeFi research system with multi-agent orchestration, streaming responses, and report generation.

## Table of Contents
- [Overview](#overview)
- [Core Capabilities](#core-capabilities)
- [Agent Architecture](#agent-architecture)
- [Data Flow](#data-flow)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Engineering Notes](#engineering-notes)
- [Roadmap](#roadmap)
- [License](#license)

## Overview
DeFi Research Agent is an end-to-end MVP for DeFi analysis workflows. It combines:
- a FastAPI backend,
- a multi-agent pipeline (Data, Research, Report),
- tool-calling style responses,
- SSE streaming for chat,
- and a Next.js frontend for interactive analysis.

The project is designed for rapid iteration: real data first, mock fallback always available, and clear API contracts for integration.

## Core Capabilities
- Multi-agent orchestration for routing between data query, analysis, and report generation.
- Live DeFi data integration with automatic fallback:
  - token prices via CoinGecko,
  - protocol TVL via DefiLlama,
  - fallback to deterministic mock values on upstream failure.
- RAG backend switch (`simple` / `chroma`) with graceful fallback to `simple` when `chromadb` is unavailable.
- Function-calling style tool trace in `/chat` responses.
- Streaming output via `/chat/stream` (SSE).
- Frontend pages:
  - streaming chat console,
  - report generation dashboard.

## Agent Architecture

```text
User Query
   |
   v
AgentOrchestrator (routing)
   |-------------------------------|
   |                               |
   v                               v
DataAgent                      ResearchAgent
   |                               |
   v                               v
DeFiTools (price/TVL/risk)     RAG (simple/chroma)
   |                               |
   |----------- merge -------------|
               |
               v
           ReportAgent
               |
               v
     API Response / SSE Stream
```

### Agent Roles
- `AgentOrchestrator`: task routing and execution path selection (`data`, `research`, `report`).
- `DataAgent`: structured metric retrieval (symbol extraction, protocol extraction, price/TVL calls).
- `ResearchAgent`: context retrieval + risk analysis + structured insights.
- `ReportAgent`: consolidates data/research outputs into report schema.
- `ToolCallingEngine`: function-calling style tool trace and deterministic summary composition.

### Reliability Improvements (Latest)
- Added backend CORS policy for local frontend origins.
- Added frontend request error boundaries to prevent unhandled runtime crashes.
- Fixed SSE chunk duplication caused by mutable state update path.
- Improved data-route answer formatting to prevent field binding ambiguity.

## Data Flow

```text
Frontend (Next.js)
   |
   | POST /chat or /chat/stream
   v
FastAPI Route Layer
   |
   v
AgentOrchestrator
   |
   +--> DataAgent --> DeFiTools --> tool_calling summary
   |
   +--> ResearchAgent --> RAG + risk
   |
   +--> ReportAgent (when report path)
   |
   v
JSON response or SSE chunks
```

## Project Structure

```text
defi-research-agent/
  config/
    default.yaml
  frontend/
    app/
      page.tsx
      report/page.tsx
  src/
    main.py
    agents/
      data_agent.py
      research_agent.py
      report_agent.py
      orchestrator.py
    core/
      settings.py
      rag.py
      tool_calling.py
    tools/
      defi_tools.py
    web/
      app.py
      middleware.py
      schemas.py
      routes/
        health.py
        chat.py
        analyze.py
        report.py
  tests/
    test_api_smoke.py
    test_defi_tools.py
    test_rag_backends.py
```

## Quick Start

### 1) Environment (Conda)
```bash
conda env create -f environment.yml
conda activate defi-research-agent
```

### 2) Configure env vars
```bash
copy .env.example .env
```

### 3) Run backend
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend docs:
- Swagger: http://localhost:8000/docs

### 4) Run tests
```bash
pytest -q
```

### 5) Run frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend:
- http://localhost:3000

If backend endpoint differs, set:
```bash
set NEXT_PUBLIC_API_BASE=http://localhost:8000
```

## API Reference

### Health
- `GET /health`

### Chat
- `POST /chat`
  - request:
    ```json
    { "query": "ETH price and Uniswap TVL" }
    ```
  - response includes:
    - `route`
    - `result`
    - optional `tool_calling`
    - `answer`

### Streaming Chat (SSE)
- `POST /chat/stream`
  - request:
    ```json
    { "query": "summarize ETH DeFi trends" }
    ```
  - stream events:
    - `{"type":"chunk","content":"..."}`
    - `{"type":"done"}`

### Analyze
- `POST /analyze`
  - request:
    ```json
    { "query": "30d snapshot", "protocol": "Aave" }
    ```

### Report
- `POST /report`
  - request:
    ```json
    { "query": "generate investment brief", "protocol": "Aave" }
    ```

## Configuration

### App-level env
- `APP_VERSION`
- `LOG_LEVEL`
- `RATE_LIMIT_PER_MINUTE`

### Frontend env
- `NEXT_PUBLIC_API_BASE`

### RAG backend
- `config/default.yaml` -> `rag.backend`
  - `simple` (default)
  - `chroma`

Install chroma backend dependency when needed:
```bash
pip install chromadb
```

### Data source policy
- `tools.use_mock_data: true`: force mock mode.
- `tools.use_mock_data: false`: use live APIs first; fallback to mock on failure.

## Engineering Notes
- Request observability headers:
  - `X-Request-Id`
  - `X-Process-Time-Ms`
- Unified error format:
  - `VALIDATION_ERROR`
  - `INTERNAL_ERROR`
- Basic in-memory rate limiting per client IP.
- CORS enabled for local frontend development origins.

## Roadmap
- Redis caching layer and deployment baseline.
- CI gate hardening for backend tests + frontend build + stream smoke checks.
- SSE/output regression tests for duplication and field binding correctness.

## License
This project is licensed under the MIT License. See `LICENSE` for details.
