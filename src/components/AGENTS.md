# UI Components DOX Contract — src/components/AGENTS.md

> **Subtree Scope**: Reusable UI primitives and shared components (`src/components/`)  
> **Parent Contract**: [`../AGENTS.md`](file:///../AGENTS.md)

---

## 1. Responsibilities

Provide reusable, accessible, unstyled-by-default or token-styled UI components that encapsulate visual consistency and interaction states across the application.

---

## 2. Component Contracts

- **`TrendChart.jsx`**:
  - Reusable pure SVG vector trend chart for historical progress data and multi-goal trajectories.
  - Supports single-goal mode via `history` array or multi-goal mode via `multiSeries` array (each series containing `id`, `name`, `color`, and `points`).
  - Supports distinct Calm Moss line colors, milestone start/current badges (`Start 0%`, `Current X%`), coordinate scaling (`viewBox="0 0 100 100"` with `preserveAspectRatio="none"`), smooth gradient area fills, and interactive data point inspection.
  - Renders graceful empty state when fewer than 2 progress checkpoints are recorded.
- **`FormattedChatMessage.jsx`**:
  - High-readability chat renderer for AI coaching responses.
  - Formats markdown headers (`###`), bold keyphrases (`**`), bullet points, numbered action steps, and quote callouts into structured Calm Moss aesthetic cards.
- **`MoodBadge.jsx`**:
  - Semantic badge rendering for all 10 PyTorch emotion classes (`accomplishment`, `motivation`, `focus`, `gratitude`, `breakthrough`, `burnout`, `overwhelmed`, `frustration`, `guilt`, `neutral`).
- **`VoiceRecorder.jsx`**:
  - Encapsulates `navigator.mediaDevices.getUserMedia` and `MediaRecorder`.
  - Supports lifecycle: `idle` $\rightarrow$ `recording` $\rightarrow$ `recorded` $\rightarrow$ `transcribing` $\rightarrow$ `editable_transcript`.
  - Provides an editable `<textarea>` containing the raw transcript so the user can edit or discard before inserting into the journal.
  - Cleanly releases audio tracks (`stream.getTracks().forEach(t => t.stop())`) and revokes object URLs on unmount/reset.
- **`GoogleCalendarBanner.jsx` / `SyncGoogleCalendarModal.jsx` / `GoogleCalendarSetupModal.jsx`**:
  - Non-intrusive calendar banner providing instant setup modal and OAuth token verification for syncing goal deadlines and roadmap milestones.
- **`RoadmapCelebration.jsx` / `GoalCelebration.jsx` / `GoalCompletionCelebration.jsx`**:
  - Micro-celebration overlays with Canvas Confetti bursts triggered when completing a goal or reaching 100% on a learning roadmap.
- **`ErrorBoundary.jsx`**:
  - Graceful React component tree fallback preventing unhandled exceptions from crashing the application shell.
- **`Button.jsx` / `Card.jsx` / `Input.jsx`**:
  - Accessible form controls and containers adhering to the Calm Moss design tokens (`rounded-card`, focus rings, soft shadows).
- **`ToastNotification.jsx`**:
  - Notification pill rendering status toasts (`success`, `warning`, `error`).
- **`Navbar.jsx` / `Sidebar.jsx` / `AppShell.jsx`**:
  - Application layout frames providing consistent brand header and navigation links (`Dashboard`, `Calendar`, `Progress`, `AI Journal`, `Goals`, `Habits`, `AI Coach`, `AI Insights`, `Profile`, `Settings`).
  - `AppShell.jsx` ensures automatic scroll-to-top on route changes and persistent brand framing.
- **`PublicNavbar.jsx` / `PublicFooter.jsx`**:
  - Public landing page header with scroll detection, anchor links (`#how-it-works`, `#journey`, `#features`), and footer branding.

---

## 3. Prohibited Patterns

- Do NOT embed direct API calls inside primitive components (like `Button` or `Card`).
- Do NOT use hardcoded colors outside the Tailwind theme palette.
- Do NOT ignore reduced-motion user preferences during animation rendering.
