# Changelog

All notable changes to this project are documented in this file.

## v0.1.0 - 2026-04-10

### Added
- Live data adapters for token price and protocol TVL with robust mock fallback.
- RAG backend switching support (`simple` / `chroma`) with safe fallback when Chroma is unavailable.
- Function-calling style tool metadata in chat output.
- SSE chat streaming endpoint: `POST /chat/stream`.
- Next.js frontend app with streaming chat page and report page.
- GitHub Actions CI workflow for backend tests and frontend build.
- GitHub Actions release workflow for tag-based release creation.

### Changed
- Configuration loading now supports YAML file merge with defaults.
- Project docs updated for frontend usage, streaming API, and RAG settings.

### Validated
- Backend test suite passes in Python 3.11 environment.
