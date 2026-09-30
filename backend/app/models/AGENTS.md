# Models Subtree DOX Contract — backend/app/models/AGENTS.md

> **Subtree Scope**: Domain entity models (`backend/app/models/`)  
> **Parent Contract**: [`../AGENTS.md`](file:///../AGENTS.md)

---

## 1. Responsibilities

Defines internal domain dataclasses / models representing persistent state in memory:
- **`User`**: `firebase_uid`, `email`, `display_name`, `profession`, `created_at`, `updated_at`.
- **`Goal`**: `id`, `user_id`, `title`, `description`, `category`, `status`, `target_date`, `progress`, `priority`, `estimated_days`, `created_at`, `updated_at`.
- **`JournalEntry`**: `id`, `user_id`, `content`, `source`, `created_at`, `updated_at`, `ai_analysis`, `primary_emotion`, `emotion_confidence`, `emotion_keywords`.
- **`Habit`**: `id`, `user_id`, `name`, `frequency`, `created_at`, `updated_at`.
- **`HabitLog`**: `id`, `habit_id`, `user_id`, `log_date`, `status`, `created_at`.
- **`Roadmap`**: `id`, `user_id`, `goal_id`, `goal_title`, `overview`, `total_estimated_weeks`, `milestones`, `created_at`.
- **`RoadmapMilestone`**: `id`, `roadmap_id`, `order_index`, `title`, `description`, `duration_days`, `is_completed`, `completed_at`.
- **`ProgressRecord`**: `id`, `goal_id`, `user_id`, `progress_value`, `notes`, `created_at`.
- **`WeeklySummary`**: `id`, `user_id`, `headline`, `wins`, `recurring_blockers`, `goal_status_changes`, `mood_trend`, `coaching_suggestion`, `created_at`.

---

## 2. Invariants

- Domain models are decoupled from any ORM base (no direct SQLAlchemy DeclarativeBase dependency inside pure domain modules).
- Timestamps must default to UTC datetimes.
- Attribute mutations must preserve typing integrity.
