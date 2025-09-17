# test_login.py
import asyncio
import httpx

BASE_URL = "https://quran-app-kw38.onrender.com/api/"
LOGIN_ENDPOINT = "auth/login/"

async def test_login(username, password):
    test_data = {
        "username": username,
        "password": password
    }
    
    try:
        print(f"正在测试登录: {username}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}{LOGIN_ENDPOINT}",
                json=test_data,
                timeout=30.0
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 登录成功!")
                return True
            else:
                print("❌ 登录失败!")
                return False
                
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    # 用你的实际用户名和密码测试
    asyncio.run(test_login("test", "test"))