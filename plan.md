# Iteration Plan

## Iteration Rule
- One iteration, one primary objective.
- No promotion to next objective before acceptance checks pass.

## Backlog (Priority)
1. DONE: Environment stabilization (Python 3.11 + dependency lock).
2. DONE: API smoke tests for /health /chat /analyze /report.
3. DONE: RAG upgrade to Chroma fallback path.
4. DONE: Function-calling style tool schema + `/chat/stream`.
5. DONE: Next.js frontend with streaming chat and report page.
6. P1: Redis caching and deployment pipeline.
7. P1: CI pipeline for backend/frontend tests.

## Acceptance Gates
- API Gate: All four endpoints pass happy path and error path.
- RAG Gate: Answers include retrievable sources.
- Agent Gate: Route correctness and tool-call success rate are measurable.
- Perf Gate: P95 latency and error rate meet target.
