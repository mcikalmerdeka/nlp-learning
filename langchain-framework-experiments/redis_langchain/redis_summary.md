# Redis for LangChain Chat Memory - Local Setup Guide

## Overview

This guide covers setting up Redis locally with Docker to use as persistent chat memory storage for LangChain applications.

## Prerequisites

- Docker installed on your system
- Python with `redis` and `langchain-redis` packages

## 1. Pull and Run Redis Container

### Pull Redis Image

```bash
docker pull redis:latest
```

### Run Redis Container

```bash
docker run --name langchain-redis -d -p 6379:6379 redis redis-server --save 60 1 --loglevel warning
```

**Flags explained:**

- `--name langchain-redis`: Container name
- `-d`: Run in detached mode (background)
- `-p 6379:6379`: Map port 6379 (host:container)
- `redis-server --save 60 1`: Save snapshot every 60 seconds if at least 1 key changed
- `--loglevel warning`: Reduce log verbosity

### Optional: Run with Volume Mount (Persist Data on Host)

```bash
docker run --name langchain-redis -d -p 6379:6379 -v redis-data:/data redis redis-server --save 60 1 --loglevel warning
```

## 2. Connect from Python

### Basic Connection (No Password)

```python
import redis
from langchain_redis import RedisChatMessageHistory

# Connect to local Redis
redis_client = redis.Redis(host="localhost", port=6379)

# Create chat history
history = RedisChatMessageHistory(
    session_id="your_session_id",
    redis_client=redis_client
)
```

**Important:** Local Redis by default has no password. Don't include `password` parameter.

## 3. Data Storage Structure

### How Data is Stored

- **Format**: RedisJSON documents (not lists or simple strings)
- **Key pattern**: `chat:{session_id}:{ulid}`
- **ULID**: Timestamp-based unique identifier (chronologically sortable)

### Example Keys

```
chat:dfsdfsfs:01KE4DZ5RAAMHZ407C1HZ03KXR  (human message)
chat:dfsdfsfs:01KE4DZ5RJJ0TMG9QA65YM0FGP  (ai message)
```

### Message Structure

```json
{
  "type": "human",
  "message_id": "01KE4DZ5RAAMHZ407C1HZ03KXR",
  "data": {
    "content": "Hi my name is Cikal",
    "additional_kwargs": {},
    "type": "human"
  },
  "session_id": "dfsdfsfs",
  "timestamp": 1767527913.22634
}
```

## 4. Inspecting Data

### Using Redis CLI (Inside Container)

```bash
# Enter Redis CLI
docker exec -it langchain-redis redis-cli

# List all keys
KEYS *

# Check key type
TYPE chat:dfsdfsfs:01KE4DZ5RAAMHZ407C1HZ03KXR

# Get RedisJSON data
JSON.GET chat:dfsdfsfs:01KE4DZ5RAAMHZ407C1HZ03KXR
```

### Using Python Script

```python
import redis
import json

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Get all keys for a session
keys = sorted(redis_client.keys("chat:your_session_id:*"))

# Print all messages
for key in keys:
    msg = redis_client.json().get(key)
    print(f"\n{msg['type'].upper()}: {msg['data']['content']}")
```

### Using VS Code/Cursor Extension

**Option 1: Redis for VS Code** by Redis (Recommended for Redis-specific work)

1. Search for "Redis for VS Code" by "Redis" in extensions
2. Automatically detects local Docker containers
3. Browse keys, view RedisJSON content
4. Built-in support for all Redis data types

**Option 2: Database Client** by Weijan Chen (Multi-database support)

1. Search for "Database Client" in extensions
2. Add connection: `localhost:6379` (no password)
3. Browse keys visually
4. Supports Redis, MySQL, PostgreSQL, MongoDB, etc.

## 5. Container Management

### Check Container Status

```bash
docker ps -a
```

### Stop Container (Data Persists)

```bash
docker stop langchain-redis
```

### Start Container Again

```bash
docker start langchain-redis
```

### Remove Container (Data Lost)

```bash
docker stop langchain-redis
docker rm langchain-redis
```

### Clear All Data (Keep Container)

**Option 1: Using Redis CLI**

```bash
docker exec -it langchain-redis redis-cli FLUSHALL
```

**Option 2: Using VS Code/Cursor Extension**

- Open Redis connection in the extension
- Right-click on keys or database
- Select "Delete" or "Flush Database"
- Confirm deletion

**Option 3: Delete Specific Keys**

```bash
# Delete all keys matching a pattern
docker exec -it langchain-redis redis-cli --eval "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" , "chat:*"
```

Or use the extension to select and delete specific keys individually.

### Check Persisted Data File

```bash
docker exec -it langchain-redis ls -la /data
```

You'll see `dump.rdb` - the binary snapshot file containing your data.

## 6. Common Issues

### Authentication Error

**Error:** `AUTH <password> called without any password configured`

**Solution:** Remove `password` parameter from Redis connection:

```python
# Wrong
redis_client = redis.Redis(host="localhost", port=6379, password="docker")

# Correct
redis_client = redis.Redis(host="localhost", port=6379)
```

### WRONGTYPE Error

**Error:** `WRONGTYPE Operation against a key holding the wrong kind of value`

**Cause:** Using wrong Redis command for the data type.

**Solution:** Use `JSON.GET` for RedisJSON data, not `GET` or `LRANGE`.

### Empty Results

If `LRANGE message_store:session_id` returns empty, your data is stored as individual RedisJSON keys, not in a list. Use `KEYS chat:*` to find them.

## 7. Data Persistence

- **In-memory**: Redis stores data in RAM for fast access
- **Disk snapshots**: `--save 60 1` creates `dump.rdb` every 60 seconds
- **Container restart**: Data survives container stop/start
- **Container removal**: Data is lost unless using volume mount
- **Volume mount**: Use `-v redis-data:/data` to persist data on host filesystem

## Summary

1. Run Redis: `docker run --name langchain-redis -d -p 6379:6379 redis redis-server --save 60 1 --loglevel warning`
2. Connect without password: `redis.Redis(host="localhost", port=6379)`
3. Data stored as RedisJSON with keys: `chat:{session_id}:{ulid}`
4. View data: `docker exec -it langchain-redis redis-cli` then `JSON.GET {key}`
5. Manage: `docker stop/start/rm langchain-redis`
