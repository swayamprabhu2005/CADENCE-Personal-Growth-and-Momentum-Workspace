# Core Subtree DOX Contract — backend/app/core/AGENTS.md

> **Subtree Scope**: Core configuration, security dependencies, and encryption utilities (`backend/app/core/`)  
> **Parent Contract**: [`../AGENTS.md`](file:///../AGENTS.md)

---

## 1. Responsibilities

- **`config.py`**: Centralized Pydantic Settings loading environment variables from `.env` (`GROQ_API_KEY`, `GROQ_MODEL`, `GEMINI_API_KEY`, `ENCRYPTION_KEY`, `DATABASE_URL`, `FIREBASE_CREDENTIALS_PATH`, etc.).
- **`auth.py`**: Firebase Admin SDK initialization and FastAPI authentication dependency (`get_current_user`).
- **`crypto.py`**: AES-256-GCM symmetric field-level encryption for sensitive user content (journal reflections, titles). Encapsulates 12-byte cryptographically secure nonce generation, ciphertext authentication tags, and backward-compatible plaintext handling (`enc:v1:` prefix format).
- **`key_rotation.py`**: Key rotation utility supporting dual-key transitions, re-encrypting existing ciphertext with updated keys without downtime.

---

## 2. Invariants & Rules

1. **Firebase Admin Verification**:
   - `fb_auth.verify_id_token(token)` validates the cryptographic signature against Google public keys.
   - Extracts `uid`, `email`, and `name` into an immutable `AuthenticatedUser` model.
   - Raises `HTTPException(401, "Invalid or expired Firebase token")` on any verification failure.
2. **No Fallback Mock Auth in Production Routes**:
   - Live endpoints must strictly enforce real token validation.
   - Controlled test doubles are reserved exclusively for isolated unit tests.
3. **AES-256-GCM Cryptographic Safety**:
   - Any sensitive user reflection stored in persistent storage must be encrypted via `crypto.encrypt_field(plaintext)`.
   - The cipher format must follow `enc:v1:<base64(12-byte-nonce + ciphertext + 16-byte-tag)>`.
   - Plaintext strings lacking `enc:v1:` must be transparently handled for legacy data compatibility.
   - Plaintext must NEVER be logged or leaked to error handlers.
