# App Core DOX Contract — backend/app/AGENTS.md

> **Subtree Scope**: FastAPI application root (`backend/app/`)  
> **Parent Contract**: [`../AGENTS.md`](file:///../AGENTS.md)

---

## 1. Responsibilities

`main.py` serves as the entry point for the FastAPI application. It configures:
- FastAPI instance with title, version, and OpenAPI metadata.
- CORS middleware allowing requests from local development hosts (`http://localhost:5173`, `http://127.0.0.1:5173`) and production frontends (Vercel deployments).
- Global exception handlers for standard HTTP errors, Pydantic validation issues, and internal failures.
- Routing mounts under `/api/v1`:
  - `/api/v1/users`
  - `/api/v1/journals`
  - `/api/v1/goals`
  - `/api/v1/coach`
  - `/api/v1/habits`
  - `/api/v1/progress`
  - `/api/v1/productivity`
  - `/api/v1/roadmap`
  - `/api/v1/summaries`
  - `/api/v1/calendar`
- Service health endpoint at `/api/v1/health` and root `/`.

---

## 2. Invariants

- Must maintain clean dependency injection across all routes.
- Must not contain inline database connection strings or ORM initialization directly inside route modules.
- Must ensure proper startup verification of database connections and graceful fallbacks.
