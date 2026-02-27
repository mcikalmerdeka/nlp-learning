# LangChain Postgres Chatbot

Multi-user chatbot with persistent conversation history stored in PostgreSQL.

## Schema

```
users          → id, username, created_at
conversations  → id, user_id, title, created_at, updated_at
messages       → id, conversation_id, role, content, metadata (JSONB), created_at
```

---

## Setup

### 1. Start Postgres with Docker

Make sure Docker Desktop is running, then from this folder:

```powershell
docker compose up -d
```

This pulls `postgres:16`, creates the database, and runs `init.sql` to set up the schema automatically.

> **Note:** Postgres is mapped to port `5433` on the host to avoid conflicts with any local Postgres installation.

**Verify it's healthy:**

```powershell
docker compose ps
```

You should see `langchain_postgres` with status `healthy`.

**To stop the container (data is preserved in the volume):**

```powershell
docker compose down
```

**To stop AND delete all data:**

```powershell
docker compose down -v
```

---

### 2. Install Python dependencies

```powershell
pip install -r requirements.txt
```

---

### 3. Configure environment

Copy `.env.example` to `.env` and fill in your OpenAI API key:

```powershell
copy .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini   # or gpt-4o, etc.
```

The Postgres values already match the Docker Compose defaults.

---

### 4. Run the API

```powershell
uv run .\app.py
```

Swagger UI → **http://127.0.0.1:8000/docs**

---

## API Endpoints

### Full workflow to verify persistent conversation history

#### Step 1 — Confirm DB connection

```
GET /health
```

Expected: `"status": "connected"`. If not, check Docker is running.

---

#### Step 2 — Create a user (or log back in)

```
POST /users/login
{ "username": "alice" }
```

Returns a `user_id`. Creating the same username again returns the existing user — this is your "login".

---

#### Step 3 — Create a conversation session

```
POST /users/{user_id}/conversations
{ "title": "My first chat" }
```

Returns a `conversation_id`. Each user can have as many sessions as they want, just like ChatGPT's sidebar.

---

#### Step 4 — Send messages and get AI responses

```
POST /conversations/{conversation_id}/chat
{ "message": "What is the capital of France?" }
```

Returns the assistant's reply. Call this multiple times — each message is saved to Postgres and the full history is passed to the LLM on every turn, so the AI remembers context within the session.

---

#### Step 5 — Verify history is stored

```
GET /conversations/{conversation_id}/messages
```

Lists every message in chronological order (role: `user` or `assistant`). This is the raw data being persisted in the `messages` table.

---

#### Step 6 — Verify persistence across restarts

1. Stop the API (`Ctrl+C`)
2. Restart it (`uv run .\app.py`)
3. Call `POST /conversations/{conversation_id}/chat` with a follow-up message like `"What did I just ask you?"`

The AI will correctly reference the earlier message — proving history is loaded from Postgres on every request, not from memory.

---

#### Step 7 — Multi-user isolation

```
POST /users/login         → { "username": "bob" }
POST /users/{bob_id}/conversations
POST /conversations/{bob_conv_id}/chat  → { "message": "Hello" }
GET  /users/{alice_id}/conversations   → alice's sessions only
GET  /users/{bob_id}/conversations     → bob's sessions only
```

Each user sees only their own conversations.

---

#### Other endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/{user_id}/conversations` | List all conversations for a user |
| `DELETE` | `/conversations/{conv_id}` | Delete a conversation and all its messages |
