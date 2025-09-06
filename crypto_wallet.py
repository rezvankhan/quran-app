import requests
from decimal import Decimal

class CryptoWallet:
    def __init__(self):
        self.api_key = os.getenv("CRYPTO_API_KEY")
        self.base_url = "https://api.crypto.com/v1"
    
    def create_invoice(self, amount: Decimal, currency: str = "USDT"):
        response = requests.post(
            f"{self.base_url}/invoices",
            json={"amount": float(amount), "currency": currency},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()
    
    def check_payment(self, invoice_id: str):
        response = requests.get(
            f"{self.base_url}/invoices/{invoice_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()