import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

app = FastAPI(
    title="LangChain Postgres Chatbot",
    description="Multi-user chatbot with persistent conversation history in PostgreSQL.",
    version="1.0.0",
)

SYSTEM_PROMPT = "You are a helpful AI assistant. Be concise but thorough."


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "chatbot_db"),
        user=os.getenv("POSTGRES_USER", "langchain"),
        password=os.getenv("POSTGRES_PASSWORD", "langchain_password"),
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
    )


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class UserLogin(BaseModel):
    username: str

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: str

class ConversationCreate(BaseModel):
    title: str = "New Conversation"

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    user_message: str
    assistant_message: str
    conversation_id: int


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
def health():
    """Check API and database connectivity."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        db_status = "connected"
        db_host = os.getenv("POSTGRES_HOST", "localhost")
        db_name = os.getenv("POSTGRES_DB", "chatbot_db")
        db_user = os.getenv("POSTGRES_USER", "langchain")
    except Exception as e:
        db_status = f"error: {str(e)}"
        db_host = os.getenv("POSTGRES_HOST", "localhost")
        db_name = os.getenv("POSTGRES_DB", "chatbot_db")
        db_user = os.getenv("POSTGRES_USER", "langchain")

    return {
        "status": "ok",
        "database": {
            "status": db_status,
            "host": db_host,
            "dbname": db_name,
            "user": db_user,
        },
    }


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@app.post("/users/login", response_model=UserResponse, tags=["Users"])
def login(body: UserLogin):
    """Log in or auto-register by username. No password required."""
    if not body.username.strip():
        raise HTTPException(status_code=400, detail="Username cannot be empty.")
    username = body.username.strip()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            if not user:
                cur.execute(
                    "INSERT INTO users (username) VALUES (%s) RETURNING *",
                    (username,),
                )
                user = cur.fetchone()
                conn.commit()
    return {
        "id": user["id"],
        "username": user["username"],
        "created_at": str(user["created_at"]),
    }


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

@app.get("/users/{user_id}/conversations", response_model=list[ConversationResponse], tags=["Conversations"])
def list_conversations(user_id: int):
    """List all conversations for a user, most recently updated first."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="User not found.")
            cur.execute(
                """
                SELECT c.id, c.user_id, c.title, c.created_at, c.updated_at,
                       COUNT(m.id) AS message_count
                FROM conversations c
                LEFT JOIN messages m ON m.conversation_id = c.id
                WHERE c.user_id = %s
                GROUP BY c.id
                ORDER BY c.updated_at DESC
                """,
                (user_id,),
            )
            rows = cur.fetchall()
    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "title": r["title"],
            "created_at": str(r["created_at"]),
            "updated_at": str(r["updated_at"]),
            "message_count": r["message_count"],
        }
        for r in rows
    ]


@app.post("/users/{user_id}/conversations", response_model=ConversationResponse, tags=["Conversations"])
def create_conversation(user_id: int, body: ConversationCreate):
    """Create a new conversation for a user."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="User not found.")
            cur.execute(
                "INSERT INTO conversations (user_id, title) VALUES (%s, %s) RETURNING *",
                (user_id, body.title),
            )
            conv = cur.fetchone()
            conn.commit()
    return {
        "id": conv["id"],
        "user_id": conv["user_id"],
        "title": conv["title"],
        "created_at": str(conv["created_at"]),
        "updated_at": str(conv["updated_at"]),
        "message_count": 0,
    }


@app.delete("/conversations/{conversation_id}", tags=["Conversations"])
def delete_conversation(conversation_id: int):
    """Delete a conversation and all its messages."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM conversations WHERE id = %s", (conversation_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Conversation not found.")
            cur.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))
            conn.commit()
    return {"message": f"Conversation {conversation_id} deleted."}


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

@app.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse], tags=["Messages"])
def get_messages(conversation_id: int):
    """Get all messages in a conversation in chronological order."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM conversations WHERE id = %s", (conversation_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Conversation not found.")
            cur.execute(
                "SELECT * FROM messages WHERE conversation_id = %s ORDER BY created_at ASC",
                (conversation_id,),
            )
            rows = cur.fetchall()
    return [
        {
            "id": r["id"],
            "conversation_id": r["conversation_id"],
            "role": r["role"],
            "content": r["content"],
            "created_at": str(r["created_at"]),
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

@app.post("/conversations/{conversation_id}/chat", response_model=ChatResponse, tags=["Chat"])
def chat(conversation_id: int, body: ChatRequest):
    """
    Send a message and get an AI response.
    Full conversation history is loaded from the DB on every call.
    """
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title FROM conversations WHERE id = %s",
                (conversation_id,),
            )
            conv = cur.fetchone()
            if not conv:
                raise HTTPException(status_code=404, detail="Conversation not found.")

            # Load history
            cur.execute(
                "SELECT role, content FROM messages WHERE conversation_id = %s ORDER BY created_at ASC",
                (conversation_id,),
            )
            history = cur.fetchall()

    # Build LangChain messages
    lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in history:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        else:
            lc_messages.append(AIMessage(content=msg["content"]))
    lc_messages.append(HumanMessage(content=body.message))

    # Call LLM
    llm = get_llm()
    response = llm.invoke(lc_messages)
    assistant_text = response.content

    # Persist both messages
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)",
                (conversation_id, "user", body.message),
            )
            cur.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)",
                (conversation_id, "assistant", assistant_text),
            )
            cur.execute(
                "UPDATE conversations SET updated_at = NOW() WHERE id = %s",
                (conversation_id,),
            )
            # Auto-title from first user message
            if not history and conv["title"] == "New Conversation":
                auto_title = body.message[:60] + ("..." if len(body.message) > 60 else "")
                cur.execute(
                    "UPDATE conversations SET title = %s WHERE id = %s",
                    (auto_title, conversation_id),
                )
            conn.commit()

    return {
        "user_message": body.message,
        "assistant_message": assistant_text,
        "conversation_id": conversation_id,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
