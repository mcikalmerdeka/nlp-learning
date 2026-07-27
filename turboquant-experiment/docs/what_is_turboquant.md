# What Is TurboQuant?

This document explains what **TurboQuant** is, how it differs from **FAISS**,
and how it compares to dedicated vector databases like **Qdrant**, **Chroma**,
**pgvector**, and **Milvus**. The goal is to help you understand the design
choice behind this demo: using `turbovec`, a Rust implementation of TurboQuant,
as the vector index instead of a traditional FAISS-backed or database-backed
store.

---

## 1. TurboQuant in one sentence

**TurboQuant is a data-oblivious vector quantization algorithm that compresses
high-dimensional floating-point embeddings into a few bits per coordinate while
keeping nearest-neighbor search recall high — and it does so without any training
or preprocessing step.**

It comes from a Google Research paper published at ICLR 2026
([arXiv:2504.19874](https://arxiv.org/abs/2504.19874)). The core insight is that
after a random rotation, the coordinates of any high-dimensional unit vector tend
to follow a predictable statistical distribution. That lets the algorithm use
precomputed optimal scalar quantizers instead of learning a codebook from the
data.

---

## 2. Why vector quantization matters

Embeddings from modern models are large:

- OpenAI `text-embedding-3-small` produces 1,536-dimensional vectors.
- A 10-million-document corpus stored as `float32` takes roughly **31 GB** of RAM.
- Compressing each coordinate to 2 bits cuts the same corpus to roughly **4 GB**.

Vector quantization is the family of techniques that makes this compression
possible. The challenge is not just compression — it is doing it while
preserving the geometry that makes nearest-neighbor search useful.

---

## 3. How TurboQuant works (high level)

TurboQuant is a **two-stage pipeline**:

### Stage 1: Random rotation + coordinate-wise scalar quantization

1. The input vector is multiplied by a random rotation matrix.
2. After rotation, every coordinate behaves like a random draw from a known
   distribution (a Beta distribution that becomes nearly Gaussian in high
   dimensions).
3. Because the coordinates are now nearly independent, the problem decomposes
   into many simple one-dimensional quantization problems.
4. The algorithm applies precomputed **Lloyd-Max optimal scalar quantizers** to
   each coordinate.

This stage gives excellent **mean-squared error (MSE)** distortion.

### Stage 2: QJL residual correction for unbiased inner products

MSE-optimal quantizers are biased when you use them to estimate **inner products**
(the operation at the heart of cosine-similarity search). To fix this, the
algorithm spends one extra bit per coordinate on a **1-bit Quantized
Johnson-Lindenstrauss (QJL)** transform applied to the residual from stage 1.

The result is an **unbiased inner-product estimator** that is close to the
information-theoretic lower bound on distortion.

### Key properties

| Property | What it means in practice |
|---|---|
| **Data-oblivious** | No k-means, no training data, no retraining when the corpus changes. |
| **Online** | You can add vectors one at a time and start searching immediately. |
| **Near-optimal distortion** | The paper proves it is within a small constant factor (~2.7×) of the Shannon lower bound. |
| **Unbiased inner products** | The QJL stage removes the bias that pure MSE quantizers introduce. |
| **Fast SIMD search** | Scoring happens against compressed codes with NEON (ARM) or AVX-512 (x86) kernels. |

---

## 4. TurboQuant vs FAISS

**FAISS** (Facebook AI Similarity Search) is a library from Meta for efficient
similarity search and clustering of dense vectors. It is the most widely used open
source tool in this space, and it is the natural baseline for any new vector index.

### What FAISS does well

- Many index types: flat brute-force, IVF, HNSW graph, product quantization (PQ),
  scalar quantization, GPU indexes, and combinations of these.
- Extremely mature, heavily optimized C++ code.
- Strong GPU acceleration.
- Handles billion-scale datasets in a single node.
- Can be combined with other systems to build a full retrieval pipeline.

### What FAISS requires

- **Product quantization** needs a k-means training step on a representative data
  sample. If the data distribution drifts, the codebook may need retraining.
- **IVF** also needs training to build coarse clusters.
- No built-in persistence, metadata filtering, multi-tenancy, or API server.
- You write the surrounding infrastructure yourself.

### Head-to-head comparison

| Dimension | FAISS PQ | TurboQuant (turbovec) |
|---|---|---|
| Training / preprocessing | K-means training on a sample | **None** (data-oblivious) |
| Adding new vectors | Encode against existing codebook | **Add instantly, no retrain** |
| Compression | 8× typical (PQ) | **5–16×** (2–4 bits per coordinate) |
| Recall@10 | ~60% for PQ | **~95%** in many reported configs |
| Index build time | Minutes for large corpora | **Virtually instant** |
| GPU support | **Excellent** | None in current implementations |
| Index types | Many (IVF, HNSW, PQ, GPU, etc.) | Flat index + optional IVF partition |
| Maturity | Years of production use | Newer, smaller ecosystem |

### What the benchmarks say (and do not say)

Reported turbovec benchmarks (100K vectors, k=64, OpenAI-sized embeddings) show:

- **ARM**: turbovec beats FAISS IndexPQFastScan by roughly **12–20%**.
- **x86**: turbovec wins most 4-bit configs by **1–6%**, is within ~1% on 2-bit
  single-threaded, but lags FAISS by **2–4%** on some 2-bit multi-threaded configs
  where FAISS's AVX-512 VBMI path has an edge.
- **Recall**: turbovec and FAISS converge to near-perfect recall at k=4–8 for high
  dimensions. At low dimensions (e.g., GloVe d=200), TurboQuant's theoretical
  assumptions are looser, and FAISS can be ahead.

Important caveat: these are author-reported benchmarks at 100K scale. The
headline "10M embeddings in 4 GB" is a math-consistent projection, but
independent 10M-scale recall and speed measurements are not widely published yet.

### When to choose which

- **Choose TurboQuant / turbovec** when you want zero training overhead, fast
  online ingestion, strong memory compression, and a local-first deployment.
- **Choose FAISS** when you need GPU acceleration, many index-type options, very
  large scale, or a production stack that has already been validated around FAISS.

---

## 5. TurboQuant vs dedicated vector databases

A dedicated vector database (Qdrant, Chroma, Weaviate, Milvus, pgvector,
Pinecone, etc.) is a **complete system** that stores vectors, metadata, and
application data and exposes them through a query API. A quantization library like
turbovec is **not** a database — it is a compression and search engine that you
embed inside your application.

### What a vector database gives you

- **Persistence**: vectors and metadata survive restarts out of the box.
- **Metadata filtering**: combine vector search with `WHERE`-style filters.
- **CRUD operations**: update or delete individual documents without rebuilding.
- **Multi-tenancy, replication, sharding, access control**: production
  infrastructure concerns.
- **Client-server or managed API**: multiple applications can query the same
  index.

### What turbovec gives you instead

- **Zero setup**: no server, no Docker, no configuration file.
- **Tiny memory footprint**: compress the index by 5–16× compared to float32.
- **No training**: add vectors and search immediately.
- **No network hop**: everything runs in your Python process.
- **Simple save/load**: dump the index and document side-car to a folder.

### Quick comparison

| Concern | turbovec | Qdrant | Chroma | FAISS direct |
|---|---|---|---|---|
| Type | In-process library | Database server | Embedded DB / library | Library |
| Setup | `pip install` | Docker / binary | `pip install` | `pip install` |
| Training | None | None (HNSW) | None (HNSW) | Varies by index |
| Compression | **5–16×** | Scalar / binary / PQ | None / limited | PQ / SQ |
| Metadata filtering | Manual | **Rich, built-in** | Basic `where` | Manual |
| Persistence | Manual save/load | Built-in | Built-in | Manual save/load |
| CRUD | Reset or rebuild | Full | Full | Limited / complex |
| Multi-tenancy | Manual | Built-in | Collections | Manual |
| Scale | Single node | Distributed | Single node | Single node / custom |
| Best for | Local RAG, memory compression | Production RAG | Prototyping | Research, batch search |

### When to choose which

- **turbovec / TurboQuant**: local RAG experiments, air-gapped deployments,
  memory-constrained environments, or when you want to avoid the operational
  overhead of a separate database.
- **Qdrant / Weaviate / Milvus**: production RAG with filtering, multi-tenancy,
  scaling, or team-wide access.
- **Chroma**: fastest prototyping for small-to-medium datasets.
- **pgvector**: when you already run PostgreSQL and want vectors next to
  relational data.
- **FAISS**: research, offline batch processing, or custom high-performance
  pipelines where you build the surrounding infrastructure yourself.

---

## 6. How this demo uses TurboQuant

This project uses **`turbovec[langchain]`**, which wraps the TurboQuant index in a
LangChain `VectorStore` interface:

- Embeddings come from OpenAI (`text-embedding-3-small`).
- The index is an `IdMapIndex` from turbovec, quantized at **4 bits per coordinate**.
- Documents are loaded from `.txt` files and added to the index.
- Search and RAG use LangChain's standard `similarity_search` and
  `similarity_search_with_score` methods.
- The index can be saved to `./index_storage/` and reloaded later.

Because turbovec is a library and not a database, the app manages persistence,
metadata, and index lifecycle manually. That is the trade-off: less operational
complexity than a database, but fewer built-in production features.

---

## 7. Key takeaways

1. **TurboQuant is a compression algorithm**, not a database. It compresses
   embeddings and lets you search them fast.
2. **Its biggest differentiator is "no training"**. FAISS PQ and many other
   quantizers need k-means; TurboQuant does not.
3. **It is not universally faster or better than FAISS**. The speed and recall
   advantage depend on dimension, bit-width, hardware, and scale.
4. **It is not a replacement for a full vector database**. If you need
   metadata filtering, multi-tenancy, or distributed serving, use Qdrant,
   Weaviate, Milvus, or similar.
5. **It is an excellent fit for local RAG**. If you want a small, fast,
   in-process index that compresses embeddings and needs zero setup, turbovec is
   a compelling option.

---

## 8. References

- [TurboQuant paper (arXiv:2504.19874)](https://arxiv.org/abs/2504.19874)
- [Google Research blog post on TurboQuant](https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/)
- [turbovec on PyPI](https://pypi.org/project/turbovec/)
- [turbovec GitHub repository](https://github.com/RyanCodrai/turbovec)
- [FAISS repository](https://github.com/facebookresearch/faiss)
- [Qdrant documentation](https://qdrant.tech/documentation/)
- [Chroma documentation](https://docs.trychroma.com/)
- [pgvector documentation](https://github.com/pgvector/pgvector)
- [LangChain VectorStore documentation](https://python.langchain.com/docs/integrations/vectorstores/)
