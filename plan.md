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
6. DONE: Streaming stability and output correctness fixes.
	- Fixed browser-side fetch failures with backend CORS support for localhost frontend origins.
	- Added robust frontend error handling for chat/report requests to avoid unhandled runtime crashes.
	- Fixed duplicated streamed output caused by mutable React state updates in development mode.
	- Fixed tool-call summary field binding readability by separating price and TVL into explicit sentences.
	- Adjusted stream chunk strategy to avoid token split ambiguity around numeric fields.
7. P1: Redis caching and deployment pipeline.
8. P1: CI pipeline for backend/frontend tests.

## Latest Acceptance Snapshot (2026-04-15)
- API/Streaming: `/chat/stream` verified with browser-origin CORS preflight and SSE content.
- Quality: backend tests passed (`17 passed`) after stability fixes.
- UX Safety: frontend now surfaces request errors in-page instead of crashing.

## Next Update Targets (Priority)
1. Add regression tests for SSE output correctness.
	- Validate no duplicated chunk assembly in frontend state update path.
	- Validate data-route answer format binds each metric to the correct field.
2. Harden frontend runtime and config.
	- Add explicit API base env validation and startup warning when backend is unreachable.
	- Add shared request utility with timeout/retry policy for non-stream endpoints.
3. Complete CI pipeline.
	- Enforce backend tests + frontend build in PR gates.
	- Add smoke E2E check for `/chat/stream` and `/report` flows.
4. Implement Redis caching and deployment baseline.
	- Cache hot protocol metrics and risk snapshots with TTL.
	- Prepare deployment docs and environment matrix for dev/staging.

## Acceptance Gates
- API Gate: All four endpoints pass happy path and error path.
- RAG Gate: Answers include retrievable sources.
- Agent Gate: Route correctness and tool-call success rate are measurable.
- Perf Gate: P95 latency and error rate meet target.
