# find_login_endpoint.py
import asyncio
import httpx

BASE_URL = "https://quran-app-kw38.onrender.com/api/"

# لیست endpoint‌های محتمل برای لاگین
POSSIBLE_ENDPOINTS = [
    "login/",
    "auth/login/",
    "users/login/", 
    "user/login/",
    "account/login/",
    "token/",
    "api-token-auth/",
    "jwt/create/",
    "auth/token/",
    "auth/jwt/create/"
]

async def test_endpoint(endpoint):
    try:
        async with httpx.AsyncClient() as client:
            # ابتدا با GET تست می‌کنیم ببینیم endpoint وجود دارد
            response = await client.get(f"{BASE_URL}{endpoint}", timeout=10.0)
            print(f"{endpoint}: GET -> {response.status_code}")
            
            # سپس با POST تست می‌کنیم
            test_data = {"username": "test", "password": "test"}
            response_post = await client.post(
                f"{BASE_URL}{endpoint}",
                json=test_data,
                timeout=10.0
            )
            print(f"{endpoint}: POST -> {response_post.status_code}")
            if response_post.status_code != 404:
                print(f"Response: {response_post.text[:100]}")
            
            return response_post.status_code != 404
            
    except Exception as e:
        print(f"{endpoint}: Error -> {e}")
        return False

async def main():
    print("正在测试所有可能的登录 endpoints...\n")
    
    for endpoint in POSSIBLE_ENDPOINTS:
        success = await test_endpoint(endpoint)
        if success:
            print(f"🎉 可能找到了正确的 endpoint: {endpoint}")
            break
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())