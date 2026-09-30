# Schemas Subtree DOX Contract — backend/app/schemas/AGENTS.md

> **Subtree Scope**: Pydantic request/response schemas (`backend/app/schemas/`)  
> **Parent Contract**: [`../AGENTS.md`](file:///../AGENTS.md)

---

## 1. Responsibilities

Define Pydantic v2 schemas for data validation, serialization, and API contracts:
- **`user.py`**: `UserProfileUpdate`, `UserProfileResponse`, `UserStats`.
- **`goal.py`**: `GoalCreate`, `GoalUpdate`, `GoalResponse`, `GoalPriority`, `GoalStatus` (`Active`, `Completed`, `Stalled`).
- **`journal.py`**: `JournalCreate`, `JournalUpdate`, `JournalResponse`, `ActivityItem`, `BlockerItem`, `GoalSuggestionItem`, `AIAnalysisResult`.
- **`coach.py`**: `CoachChatRequest`, `CoachChatResponse`, `ChatMessage`.
- **`habit.py`**: `HabitCreate`, `HabitResponse`, `HabitToggleResponse`, `HabitWithStatusResponse`.
- **`progress.py`**: `ProgressRecordRequest`, `ProgressRecordResponse`, `GoalTrendResponse`, `ProgressCheckpoint`.
- **`productivity.py`**: `ProductivityScoreResponse`, `ProductivityBreakdown`.
- **`roadmap.py`**: `RoadmapGenerateRequest`, `RoadmapResponse`, `MilestoneToggleResponse`, `RoadmapMilestoneItem`.
- **`voice.py`**: `VoiceTranscribeResponse`.
- **`summary.py`**: `WeeklySummaryResponse`, `WeeklySummaryCreate`.

---

## 2. Invariants

- Use Pydantic V2 syntax (`model_config = ConfigDict(from_attributes=True)`).
- Ensure strict type annotations, Field descriptions, and default values.
- AI analysis schema must support validation of Gemini-generated structured JSON and PyTorch emotion classifications.
