import redis

def test_redis_connection():
    try:
        # 替换为你的 Redis 配置
        client = redis.Redis(
            host="redis-14452.crce178.ap-east-1-1.ec2.redns.redis-cloud.com",
            port=14452,
            username="default",
            password="eAJSH4Xq9NM0CXCW8HobpSkrrVEIHMgZ",
            decode_responses=True
        )
        
        # 测试 PING 命令
        response = client.ping()
        print("Redis 连接成功！PING 返回:", response)
        
        # 测试读写
        client.set("test_key", "Hello, Redis!")
        value = client.get("test_key")
        print("读取 test_key 的值:", value)
        
    except Exception as e:
        print("连接失败，错误信息:", e)

if __name__ == "__main__":
    test_redis_connection()