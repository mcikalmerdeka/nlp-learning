**PostgreSQL is actually a solid choice** and is what many production AI chat applications use (including likely some at major AI companies). It's not a bad default at all. But the "best" option depends on your access patterns and scale. Let me break it down:

---

**Why Postgres works well here:**

- Conversations are naturally relational: users → conversations → messages
- You get ACID transactions, which matter when appending messages reliably
- JSONB columns let you store flexible message metadata (tool calls, attachments, token counts, etc.) without a rigid schema
- Full-text search on message history is easy
- `pgvector` extension lets you add semantic search later without switching DBs
- Battle-tested at scale (Supabase, which powers many AI startups, is just Postgres under the hood)

A simple schema looks like:

```sql
users (id, ...)
conversations (id, user_id, title, created_at, updated_at)
messages (id, conversation_id, role, content, metadata JSONB, created_at)
```

---

**Where people sometimes reach for other tools:**

- **DynamoDB / Cassandra** — if you need massive write throughput or multi-region at scale. The access pattern (fetch all messages by `conversation_id`) maps well to a partition key. But you lose flexibility.
- **Redis** — great for storing _active/recent_ conversations in memory for fast retrieval, then flushing to a persistent store. Often used as a cache layer _on top of_ Postgres, not a replacement.
- **MongoDB** — messages are document-shaped, so it fits naturally, but Postgres JSONB largely eliminates the advantage here.
- **Vector DBs (Pinecone, Weaviate, etc.)** — only relevant if you're doing long-term memory retrieval via semantic search, not for storing raw conversation history.

---

**My recommendation:**

Start with **Postgres**. It handles the job well, you don't over-engineer early, and you can add Redis caching or pgvector later without a migration. The pattern most teams land on at scale is:

> **Postgres (source of truth) + Redis (hot cache for active sessions)**

The only reason to skip Postgres upfront is if you _know_ you're building for massive scale from day one — but even then, companies like Linear and Notion run on Postgres at impressive scale.
