# test_connection.py
import asyncio
import httpx

BASE_URL = "https://quran-app-kw38.onrender.com/"

async def test_connection():
    try:
        print("正在测试服务器连接...")
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL, timeout=30.0)
            print(f"✅ 连接成功!")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text[:200]}...")
            return True
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())