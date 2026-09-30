# Repositories Subtree DOX Contract — backend/app/repositories/AGENTS.md

> **Subtree Scope**: Data persistence layer (`backend/app/repositories/`)  
> **Parent Contract**: [`../AGENTS.md`](file:///../AGENTS.md)

---

## 1. Responsibilities

Encapsulate all data access and state storage behind clean repository interfaces:
- **`base.py`**: Defines abstract base classes:
  - `AbstractUserRepository`
  - `AbstractGoalRepository`
  - `AbstractJournalRepository`
  - `AbstractHabitRepository`
  - `AbstractProgressRepository`
  - `AbstractSummaryRepository`
  - `AbstractRoadmapRepository`
- **`in_memory.py`**: Thread-safe, dictionary-backed repository implementations protected with `threading.Lock` for ultra-fast local testing and RAM execution.
- **`postgres.py`**: SQLAlchemy-backed persistence implementation supporting both PostgreSQL (primary Docker container `ai_goal_journal_db` on port 5433 / production managed PostgreSQL) and transparent SQLite fallback (`sqlite:///./app.db`). Implements repositories for users, goals, journals, habits, progress tracking, weekly summaries, and goal roadmaps.
- **`calendar_repo.py`**: Repository for managing Google Calendar OAuth tokens and synchronized event IDs per user.

---

## 2. Invariants & Rules

1. **Strict User Isolation**:
   - Every read, update, or delete method MUST accept `user_id` and ensure that only records owned by that `user_id` are returned or modified.
2. **Order of Records**:
   - Journal list queries must return newest entries first (`created_at` descending).
   - Milestone list queries must return in canonical chronological order (`order_index` ascending).
3. **Dual PostgreSQL & SQLite Compatibility**:
   - Repositories accept domain inputs and return Pydantic schemas.
   - All models use SQLAlchemy standard types compatible with both PostgreSQL and SQLite.
   - When Docker PostgreSQL is active, all writes persist to the container volume. If Docker is offline, the backend seamlessly routes to local SQLite.
