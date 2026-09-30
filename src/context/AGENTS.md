# Context DOX Contract — src/context/AGENTS.md

> **Subtree Scope**: React Context Providers (`src/context/`)  
> **Parent Contract**: [`../AGENTS.md`](file:///../AGENTS.md)

---

## 1. Responsibilities

- **`AuthContext.jsx`**: Manages the global authentication session using Firebase Authentication's `onAuthStateChanged` listener. Handles Email/Password authentication, OAuth 2.0 social sign-in (`GoogleAuthProvider`, `OAuthProvider('microsoft.com')`), and token refreshing.
- **`DataContext.jsx`**: Manages in-memory cached application state (User Profile, Goals, Journal History, Habit Trackers, Progress Trends, Weekly AI Summaries) with SWR-style background revalidation and optimistic updates to ensure instant, flicker-free SPA route navigation.
- **`ModalContext.jsx`**: Manages global modal dialog state (e.g. Productivity Score calculator, goal creation modals).

---

## 2. Invariants & Rules

1. **Reactive Auth State**:
   - `user`: Holds the active Firebase User object or `null`.
   - `checkingAuth`: `true` while the initial Firebase SDK handshake completes, preventing premature redirects to `/login`.
2. **Global Data Caching & Optimistic Updates**:
   - Cache user profile, goals, journals, habits, and weekly AI summaries in memory.
   - Support zero-latency optimistic updates on goal completion and habit toggles before network confirmation.
   - Provide quiet background revalidation while rendering cached state instantly on route navigation.
3. **Exposed Helper Methods**:
   - Auth: `login(email, password)`, `register(email, password)`, `loginWithGoogle()`, `loginWithMicrosoft()`, `logout()`.
   - Data: `useData()` hook exposing cached state and sync helpers (`addGoal`, `updateGoalInCache`, `deleteGoalFromCache`, `addJournal`, `updateProfileInCache`, `habits`, `refreshHabits`, `refreshGoals`, etc.).
4. **No Mock Bypass**:
   - Never inject hardcoded users or fake metrics into context state.
   - Any code consuming auth or workspace data must use `useAuth()` or `useData()`.
