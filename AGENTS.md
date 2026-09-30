# AI Goal Journal & Accountability Coach — AGENTS.md

## Purpose

This repository contains the **AI Goal Journal & Accountability Coach** (Growth Workspace) platform.

This file provides the primary architectural and operational contract for developers and AI agents so that implementation, documentation, database schemas, and API contracts remain consistent across the entire repository.

---

## Project Overview

AI Goal Journal is an **AI-powered personal productivity platform** that transforms daily **voice or text journal entries** into structured goals, measurable progress insights, emotional pulse detection, habit accountability, and interactive AI coaching.

The platform eliminates the friction of traditional goal trackers by letting users reflect conversationally, while intelligent backend pipelines automatically extract activities, detect blockers, categorize emotional states, and compute productivity trajectories.

### Primary Capabilities

* **Voice & Text Journaling**: Conversational reflection input with local `faster-whisper` Tiny speech-to-text (INT8 CPU) and manual transcript refinement.
* **Custom Deep Learning Emotion AI**: On-device PyTorch 10-Class Attention BiLSTM model detecting emotional states (`accomplishment`, `motivation`, `focus`, `gratitude`, `breakthrough`, `burnout`, `overwhelmed`, `frustration`, `guilt`, `neutral`) with confidence and keywords in ~3–5 ms.
* **Structured Semantic Extraction**: Google Gemini (`gemini-3.1-flash-lite`) extracting completed activities, planned tasks, categorized blockers, and goal linkages.
* **Two-Way Conversational AI Coach**: Groq Cloud API (`openai/gpt-oss-120b`) coach grounded with user goals, habit streaks, recent journals, and detected emotional pulse.
* **AI Goal Roadmap Generator**: Automatically decomposes broad goals into 4–8 sequential milestones with durations and progress auto-synchronization.
* **Google Calendar Integration**: Two-way synchronization scheduling goal deadlines and roadmap milestone accountability events directly into Google Calendar.
* **Habits Accountability Matrix**: High-speed, single-query Monday–Sunday habit tracker with streaks, completion locks, and zero-latency caching.
* **Progress Trajectories & Trends**: Pure-SVG multi-goal trend visualization (`TrendChart.jsx`), period step deltas (`change_from_previous`), and 100% completion milestone celebrations.
* **Personal Productivity Score**: Deterministic 0–100 score evaluating completion, consistency, velocity, and blocker penalties.
* **Enterprise-Grade Field Encryption**: AES-256-GCM symmetric encryption (`crypto.py`, `key_rotation.py`) protecting user reflections with transparent backward-compatibility.
* **Dual Persistence Engine**: Dedicated PostgreSQL container on port 5433 with seamless, automatic fallback to local SQLite (`sqlite:///./app.db`).

---

## Problem Statement

Traditional productivity applications require users to manually create goals, check off checkboxes, update percentage bars, and review performance dashboards. Over time, this administrative overhead causes friction, fatigue, and eventual abandonment.

Conversely, standard journaling apps capture daily reflections but fail to convert them into **actionable goals, measurable progress, or structured insights**.

AI Goal Journal bridges this divide: **natural conversational journaling becomes the engine of automated goal tracking, habit momentum, emotional awareness, and AI coaching**.

---

## Primary Users

* **Students**: Coursework tracking, exam milestones, placement prep, and study consistency.
* **Working Professionals**: Project milestones, daily work-in-progress logs, burnout prevention, and performance reviews.
* **Freelancers & Consultants**: Client deliverables, deadline management, and habit routines.
* **Entrepreneurs & Creators**: High-velocity objectives, weekly accountability reflections, and focus management.

---

## Repository Structure

```text
AI-GOAL-JOURNAL/
├── AGENTS.md                       # Root DOX contract (this document)
├── README.md                       # User-facing repository overview & quickstart
├── package.json                    # Frontend dependencies and Vite build scripts
├── vite.config.js                  # Vite configuration
├── tailwind.config.js              # Tailwind tokens & Calm Moss theme definitions
├── render.yaml                     # Render backend deployment configuration
├── vercel.json                     # Vercel SPA routing & redirect rules
├── docker-compose.yml              # Local PostgreSQL container (port 5433:5432)
├── backend/                        # FastAPI application root
│   ├── AGENTS.md                   # Backend DOX contract
│   ├── requirements.txt            # Python dependencies
│   ├── alembic/                    # Database schema migrations
│   ├── app/
│   │   ├── AGENTS.md               # App subtree contract
│   │   ├── main.py                 # FastAPI application factory & CORS configuration
│   │   ├── api/                    # REST API route controllers
│   │   │   ├── AGENTS.md
│   │   │   └── v1/                 # Versioned endpoints (journals, goals, coach, habits, etc.)
│   │   ├── core/                   # Security, auth, settings, AES-256-GCM cryptography
│   │   │   ├── AGENTS.md
│   │   │   ├── auth.py             # Firebase ID token verification
│   │   │   ├── config.py           # Pydantic Settings
│   │   │   ├── crypto.py           # AES-256-GCM field encryption
│   │   │   └── key_rotation.py     # Zero-downtime key rotation
│   │   ├── database/               # Database connection probing, session creation, ORM models
│   │   ├── models/                 # Domain dataclasses & entities
│   │   ├── repositories/           # Abstract & concrete repositories (Dual Postgres/SQLite, In-Memory)
│   │   ├── schemas/                # Pydantic validation request/response schemas
│   │   └── services/               # Business logic, AI extraction, emotion model, Whisper STT
│   ├── scripts/                    # Maintenance & batch data encryption migration scripts
│   └── tests/                      # Pytest automated test suite
├── models/
│   └── mood_analyzer/              # PyTorch 10-Class Attention BiLSTM training, weights & inference
├── src/                            # React 18 frontend Single Page Application
│   ├── AGENTS.md                   # Frontend DOX contract
│   ├── components/                 # Reusable UI primitives, charts, modals, navigation frames
│   ├── context/                    # AuthContext, DataContext (caching/SWR), ModalContext
│   ├── pages/                      # Top-level views (Landing, Dashboard, Journal, Goals, etc.)
│   ├── services/                   # Frontend API clients (api.js, roadmapApi.js, authService.js)
│   ├── animations/                 # Motion helpers (Anime.js)
│   ├── assets/                     # Branding assets & logo
│   └── utils/                      # Client storage utilities
└── docs/                           # Architectural guides and deployment references
```

---

## Technology Stack

### Frontend
* **Core**: React 18, Vite 5
* **Routing**: React Router DOM v6
* **Styling**: Tailwind CSS 3 (Calm Moss aesthetic, Fraunces serif headings, Inter body)
* **Animations**: Anime.js, Canvas Confetti
* **Icons**: Lucide React

### Backend
* **Framework**: FastAPI (Python 3.10+)
* **Server**: Uvicorn (ASGI)
* **Validation**: Pydantic v2
* **ORM & Migrations**: SQLAlchemy 2.0, Alembic
* **Cryptography**: Cryptography library (`AES-256-GCM`)

### Database & Storage
* **Primary**: PostgreSQL (Docker container `ai_goal_journal_db` mapped to `5433:5432`)
* **Transparent Fallback**: SQLite (`sqlite:///./app.db`) for immediate offline operation

### Authentication
* **Provider**: Firebase Authentication
* **Verification**: Firebase Admin SDK & Google Public Keys (`get_current_user`)

### Machine Learning & AI
* **Speech-to-Text**: `faster-whisper` Tiny (INT8 CPU quantization)
* **Emotion Classification**: Custom PyTorch 4-Head Attention BiLSTM (10 classes, CPU inference ~3–5 ms)
* **Structured Extraction**: Google Gemini (`gemini-3.1-flash-lite` via `google-genai` SDK)
* **Conversational Coach**: Groq Cloud API (`openai/gpt-oss-120b`, fallback `qwen/qwen3.8-27b`)
* **Calendar Integration**: Google Calendar API v3 (OAuth 2.0)

---

## High-Level Architecture

```text
               User Interface (React 18 + Vite + Tailwind CSS)
                                    │
                                    ▼
                     Firebase Authentication (OAuth / JWT)
                                    │
                        [Bearer Token Authorization]
                                    │
                                    ▼
                         FastAPI Gateway (Uvicorn)
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
          Security & Crypto    Service Layer     Core Validation
          (AES-256-GCM)        (Business Logic)  (Pydantic v2)
                 │                  │                  │
                 └──────────────┬───┴──────────────────┘
                                │
       ┌────────────────────────┼────────────────────────┐
       ▼                        ▼                        ▼
  AI & Speech Layer      Repository Layer         External APIs
  • faster-whisper Tiny   • PostgresRepository     • Groq Cloud API (Coach)
  • PyTorch Emotion AI    • In-Memory / SQLite     • Google Calendar API
  • Gemini Flash-Lite           │
                                ▼
                       Persistence Engine
                   PostgreSQL (Primary :5433)
                   SQLite (Automatic Fallback)
```

---

## AI & Data Processing Pipeline

```text
1. User Ingestion: Text or Voice Audio via MediaRecorder
2. Speech Transcription: faster-whisper Tiny (INT8 CPU) -> Instant temporary audio deletion
3. Emotion Detection: PyTorch 10-Class Attention BiLSTM -> Primary mood, confidence, trigger keywords (~3-5ms)
4. Semantic Analysis: Gemini Flash-Lite -> Structured JSON (completed activities, blockers, goal links)
5. Cryptographic Guard: AES-256-GCM encryption for reflection content (enc:v1:<nonce+ciphertext+tag>)
6. Dual Persistence: PostgreSQL primary / SQLite fallback
7. Downstream Intelligence: 
   • Goal progress & velocity updates
   • Habit streak recalculation
   • Productivity score recalculation (0-100)
   • Conversational Groq Coach grounding
```

---

## Core Invariants & Rules

1. **4 GB RAM PC Safeguard**:
   - Only `faster-whisper` **Tiny** model with **INT8** quantization on **CPU** is permitted.
   - The PyTorch Mood Analyzer runs exclusively on **CPU** using lightweight embeddings (~30 MB RAM footprint).
   - All complex language reasoning (Gemini Flash-Lite, Groq Conversational Coach) executes **100% in the cloud** via remote APIs, preventing local RAM exhaustion.
   - Audio files must be deleted immediately after transcription.
2. **Dual Persistence Guarantee**:
   - The system must function seamlessly whether Docker PostgreSQL is running or offline.
   - If PostgreSQL connection fails on startup or query probing, the backend routes transparently to local SQLite (`app.db`).
3. **Field Encryption & Decryption**:
   - Encrypted database fields use the `enc:v1:<base64(12-byte-nonce + ciphertext + tag)>` format.
   - Any record lacking the `enc:v1:` prefix is treated as legacy plaintext and returned without error.
   - Gemini, Groq, and PyTorch AI models must always receive decrypted plaintext.
4. **Deterministic Authority**:
   - AI suggestions must be validated through deterministic business logic before mutating goal statuses or linking progress.
   - Original journal entries remain the immutable source of truth.
5. **Strict User Scoping**:
   - All protected routes enforce `current_user: AuthenticatedUser = Depends(get_current_user)`.
   - Never trust client-supplied user IDs; all repository operations must use `current_user.uid`.
6. **Calm Moss Aesthetic & Design Tokens**:
   - Backgrounds: `#FAF9F6` (paper) and `#F4F1E8` (workspace).
   - Accents: `#4B5D3C` (moss) and `#3A4A2E` (olive).
   - Text: `#26261F` (ink) and `#64748B` (slate).
   - Headings: `Fraunces` serif.

---

## Subtree DOX Contracts

Detailed operational specifications for specific subtrees are maintained in their respective `AGENTS.md` files:
- **Backend Root**: [`backend/AGENTS.md`](file:///backend/AGENTS.md)
- **Backend App**: [`backend/app/AGENTS.md`](file:///backend/app/AGENTS.md)
- **Backend API**: [`backend/app/api/AGENTS.md`](file:///backend/app/api/AGENTS.md)
- **Backend Core**: [`backend/app/core/AGENTS.md`](file:///backend/app/core/AGENTS.md)
- **Backend Models**: [`backend/app/models/AGENTS.md`](file:///backend/app/models/AGENTS.md)
- **Backend Repositories**: [`backend/app/repositories/AGENTS.md`](file:///backend/app/repositories/AGENTS.md)
- **Backend Schemas**: [`backend/app/schemas/AGENTS.md`](file:///backend/app/schemas/AGENTS.md)
- **Backend Services**: [`backend/app/services/AGENTS.md`](file:///backend/app/services/AGENTS.md)
- **Frontend Root**: [`src/AGENTS.md`](file:///src/AGENTS.md)
- **Frontend Components**: [`src/components/AGENTS.md`](file:///src/components/AGENTS.md)
- **Frontend Context**: [`src/context/AGENTS.md`](file:///src/context/AGENTS.md)
- **Frontend Pages**: [`src/pages/AGENTS.md`](file:///src/pages/AGENTS.md)
- **Frontend Services**: [`src/services/AGENTS.md`](file:///src/services/AGENTS.md)
