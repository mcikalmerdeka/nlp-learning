""""
Check the redis history of a session inside the terminal
"""
# import redis
# import json

# redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# # Get all keys matching your session
# keys = redis_client.keys("chat:session_1:*")

# # Sort by ULID (they're chronologically sortable)
# keys.sort()

# # Get each message
# for key in keys:
#     # For RedisJSON, use json().get()
#     msg = redis_client.json().get(key)
#     print(f"\n{msg['type'].upper()}: {msg['data']['content']}")

import redis
import json

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
keys = sorted(redis_client.keys("chat:session_1:*"))

for key in keys:
    msg = redis_client.json().get(key)
    print(json.dumps(msg, indent=2))
    print("-" * 50)