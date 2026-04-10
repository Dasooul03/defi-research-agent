# DeFi Research Agent

AI-driven DeFi 投研分析系统

## 当前实现能力
- FastAPI 服务 + 多 Agent 编排（Data/Research/Report）
- 真实链上数据接入（CoinGecko/DefiLlama）与自动回退 mock
- RAG 后端切换：`simple` / `chroma`
- Function-calling 风格工具调用结果（`/chat` 响应包含 `tool_calling`）
- SSE 流式输出接口：`/chat/stream`
- Next.js 前端（流式聊天页 + 报告页）

## 快速启动

### 1) Conda 环境
```bash
conda env create -f environment.yml
conda activate defi-research-agent
```

### 2) 配置环境变量
```bash
copy .env.example .env
```

### 3) 启动服务
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 4) 访问文档
- Swagger: http://localhost:8000/docs

### 5) 运行 API 冒烟测试
```bash
pytest -q
```

### 6) 启动前端（Next.js）
```bash
cd frontend
npm install
npm run dev
```

默认前端访问：
- http://localhost:3000

如需修改后端地址，可设置环境变量：
- `NEXT_PUBLIC_API_BASE=http://localhost:8000`

## 项目结构

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
    core/
      settings.py
      rag.py
      tool_calling.py
    agents/
      data_agent.py
      research_agent.py
      report_agent.py
      orchestrator.py
    tools/
      defi_tools.py
    web/
      schemas.py
      routes/
        chat.py
        analyze.py
        report.py
        health.py
```

## API 一览
- `GET /health`
- `POST /chat`
- `POST /chat/stream`（SSE）
- `POST /analyze`
- `POST /report`

## 更真实的工程细节
- 请求可观测性：自动注入 `X-Request-Id`、`X-Process-Time-Ms`
- 统一错误响应：`VALIDATION_ERROR` / `INTERNAL_ERROR`
- 基础限流：按客户端 IP 的每分钟请求上限
- 健康检查增强：返回版本、环境、运行时长、依赖配置状态

可通过 `.env` 配置：
- `APP_VERSION`
- `LOG_LEVEL`
- `RATE_LIMIT_PER_MINUTE`

## RAG 后端切换
- 默认后端：`simple`（内存检索）
- 可选后端：`chroma`（向量检索）

当前代码已支持后端切换与自动回退：当配置为 `chroma` 且本地未安装 `chromadb` 时，会自动回退到 `simple`。

如需启用 Chroma：
```bash
pip install chromadb
```

可在 `config/default.yaml` 的 `rag.backend` 中设置 `simple` 或 `chroma`。

## 真实数据源开关
- `tools.use_mock_data: true`：始终使用 mock
- `tools.use_mock_data: false`：优先调用 CoinGecko/DefiLlama，失败自动回退 mock

## CI 与 Release
- CI 工作流：`.github/workflows/ci.yml`
  - 触发：push / pull_request 到 `main`
  - 内容：后端 `pytest -q` + 前端 `npm run build`

- Release 工作流：`.github/workflows/release.yml`
  - 触发：GitHub Actions 手动 `workflow_dispatch`
  - 输入：版本号（如 `v0.2.0`）
  - 内容：执行后端测试、前端构建、创建并推送 tag、生成 GitHub Release

- 版本说明：`CHANGELOG.md`

## License
This project is licensed under the MIT License. See `LICENSE` for details.
