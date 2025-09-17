# explore_all_endpoints.py
import requests
from urllib.parse import urljoin

BASE_URL = "https://quran-app-kw38.onrender.com/api/"

def explore_all_endpoints():
    # لیست endpointهای معمول REST API
    endpoints_to_test = [
        "",  # root
        "auth/",
        "users/",
        "user/",
        "accounts/", 
        "account/",
        "login/",
        "signin/",
        "auth/",
        "token/",
        "register/",
        "signup/",
        "students/",
        "teachers/",
        "profile/",
        "posts/",
        "articles/",
        "quran/",
        "verses/",
        "surahs/"
    ]
    
    print("探索所有可能的 endpoints...\n")
    
    for endpoint in endpoints_to_test:
        url = urljoin(BASE_URL, endpoint)
        try:
            response = requests.get(url, timeout=10)
            print(f"{endpoint.ljust(15)}: {response.status_code} ", end="")
            
            if response.status_code == 200:
                print("✅")
                try:
                    data = response.json()
                    print(f"   Response: {str(data)[:100]}...")
                except:
                    print("   (Non-JSON response)")
            elif response.status_code == 405:
                print("⚠️  (Method Not Allowed -可能需要 POST)")
            else:
                print()
                
        except Exception as e:
            print(f"{endpoint.ljust(15)}: Error - {e}")

if __name__ == "__main__":
    explore_all_endpoints()