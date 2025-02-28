"""Basic connection example.
"""

import redis

r = redis.Redis(
    host='redis-14452.crce178.ap-east-1-1.ec2.redns.redis-cloud.com',
    port=14452,
    decode_responses=True,
    username="default",
    password="eAJSH4Xq9NM0CXCW8HobpSkrrVEIHMgZ",
)

success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)
# >>> bar

