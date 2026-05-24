# Multi-Department Internal Knowledge Base: Architecture Guide

When building a RAG-based internal knowledge base that serves multiple departments, your primary challenge is balancing **security partitioning** against **operational cost and complexity**. You need to prevent HR from accidentally seeing Engineering's technical blueprints, and prevent Sales from accessing Finance's payroll data — while keeping the system maintainable and affordable.

---

## The Three Architectural Options

### Option 1: Single Collection with Metadata Filtering ✅ Recommended

Every department's documents go into **one collection**, but each vector chunk is tagged with metadata that controls access. Your application enforces a hard filter at query time before the search even runs.

**Pros:**
- One database cluster — lowest cost, flat infrastructure
- Supports cross-department search (e.g., an executive searching across Sales and Marketing simultaneously)
- Simple to scale: adding a new department is just a new metadata tag, not a new collection

**Cons:**
- Security is enforced at the **application layer**. If your filter logic has a bug, a user could search another department's data
- Requires careful backend implementation to ensure filters are always injected

**Best for:** Most companies. Works great with Pinecone Serverless, Qdrant, or Milvus.

---

### Option 2: Separate Collections / Namespaces per Department

Each department gets its own collection (e.g., `company-hr`, `company-legal`, `company-sales`). A query sent to `company-sales` physically cannot return results from `company-hr`.

**Pros:**
- Hard logical isolation at the database level — no risk of application-layer filter bugs leaking data
- Keeps individual index sizes smaller, which helps search performance at scale (>50M vectors per department)

**Cons:**
- More expensive: many vector databases charge extra for multiple indices or suffer performance overhead
- Operationally heavier: adding a department means provisioning and managing a new collection
- Cross-department search becomes complex (requires querying multiple collections and merging results)

**Best for:** Environments with strict regulatory or compliance requirements (HIPAA, SOC 2) where data mixing creates legal risk.

---

### Option 3: Separate Database Instances

Each department gets its own completely isolated database server or cloud project.

**Pros:**
- Maximum security: complete network and physical isolation

**Cons:**
- Costs multiply linearly with the number of departments
- Massive operational overhead

**Best for:** Multi-national conglomerates with entirely independent subsidiaries, or environments with extreme compliance mandates.

---

## Decision Matrix

| Requirement | Best Approach | Reason |
|---|---|---|
| Lowest cost | Metadata Filtering | Shared compute across the whole company |
| Cross-department search | Metadata Filtering | Single query can span multiple access groups |
| Strict compliance (HIPAA, SOC 2) | Separate Collections | Zero risk of cross-index data leakage |
| Massive scale (>50M vectors/dept) | Separate Collections | Smaller indexes = faster search per department |
| Extreme isolation (legal subsidiaries) | Separate Instances | Full network and physical separation |

---

## Implementing Metadata Filtering (The Recommended Path)

### 1. Chunk Payload Schema

Use an `allowed_groups` array (not a single string). This lets you model complex permissions — for example, a manager who belongs to both `sales` and `operations`.

```json
{
  "id": "chunk_9823",
  "vector": [0.023, -0.432, "..."],
  "metadata": {
    "text": "The Q3 budget allocation for software licenses is...",
    "source_file": "q3_budget.pdf",
    "department": "finance",
    "allowed_groups": ["finance", "executive_leadership"],
    "confidentiality": "internal",
    "created_at": "2026-05-22"
  }
}
```

### 2. Ingestion Pipeline (Python + Qdrant Example)

```python
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

client = QdrantClient(url="http://localhost:6333")

# Create a single shared collection
client.create_collection(
    collection_name="company_knowledge",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

def ingest_document(chunks: list[dict], department: str, allowed_groups: list[str]):
    points = []
    for chunk in chunks:
        embedding = embed(chunk["text"])  # your embedding function
        points.append(PointStruct(
            id=chunk["id"],
            vector=embedding,
            payload={
                "text": chunk["text"],
                "source_file": chunk["source_file"],
                "department": department,
                "allowed_groups": allowed_groups,
            }
        ))
    client.upsert(collection_name="company_knowledge", points=points)
```

### 3. Query-Time Access Enforcement

The most critical part: your backend **must always** inject the user's groups as a pre-filter. Never let the raw user query hit the vector DB without it.

```python
from qdrant_client.models import Filter, FieldCondition, MatchAny

def search_knowledge_base(query: str, user_groups: list[str], top_k: int = 5):
    """
    user_groups comes from your identity provider (Okta, Azure AD, etc.)
    and is resolved at login time — never trust the client to send this.
    """
    query_vector = embed(query)

    # This filter is injected server-side, not passed from the frontend
    access_filter = Filter(
        must=[
            FieldCondition(
                key="allowed_groups",
                match=MatchAny(any=user_groups)
            )
        ]
    )

    results = client.search(
        collection_name="company_knowledge",
        query_vector=query_vector,
        query_filter=access_filter,
        limit=top_k,
    )
    return results
```

### 4. FastAPI Endpoint Example

```python
from fastapi import FastAPI, Depends
from your_auth import get_current_user  # resolves JWT → user groups

app = FastAPI()

@app.post("/search")
async def search(query: str, current_user=Depends(get_current_user)):
    # user_groups resolved from identity provider, never from request body
    user_groups = current_user.groups  # e.g., ["finance", "executive_leadership"]

    results = search_knowledge_base(query, user_groups)
    return {"results": [r.payload["text"] for r in results]}
```

> **Security note:** Never accept `allowed_groups` from the frontend. Always resolve group membership server-side from your identity provider (Okta, Azure AD, Google Workspace, etc.) using the user's session token.

---

## Cross-Department Search (Executives / Admins)

One of the biggest advantages of the metadata approach is that cross-department search is trivially easy — just expand the user's `allowed_groups`:

```python
# Executive with access to everything
user_groups = ["finance", "hr", "engineering", "sales", "executive_leadership"]

# This single query will search across all of them simultaneously
results = search_knowledge_base("Q3 revenue vs engineering headcount", user_groups)
```

With the separate collections approach, this would require N parallel queries + result merging + re-ranking, which is significantly more complex.

---

## When to Upgrade to Separate Collections

Start with metadata filtering, but consider migrating specific departments to separate collections if:

- A department has **strict regulatory requirements** (e.g., HR under GDPR, Medical under HIPAA)
- A department's data volume exceeds **50M vectors** and you see latency degradation
- Your legal team mandates **demonstrable isolation** for an audit

You can run a **hybrid architecture** — metadata filtering for most departments, a separate collection for just HR and Legal.

---

## Checklist Before Going to Production

- [ ] Group membership is resolved from your identity provider, not from client input
- [ ] Every ingestion pipeline sets `allowed_groups` on every chunk — no orphaned chunks with missing metadata
- [ ] Integration tests that verify a Finance user cannot retrieve HR chunks
- [ ] Access control middleware is enforced at the API gateway layer, not just in the route handler
- [ ] Audit logging on all search queries (who searched what, when)
