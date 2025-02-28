import redis

# 测试 Redis 连接
r = redis.Redis(host='redis-14452.crce178.ap-east-1-1.ec2.redns.redis-cloud.com', port=14452, password='eAJSH4Xq9NM0CXCW8HobpSkrrVEIHMgZ', decode_responses=True)
r.set('test', 'hello')
value = r.get('test')
print(value, type(value))  # 应输出 'hello' <class 'str'>