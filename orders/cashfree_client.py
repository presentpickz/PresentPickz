import requests
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CashfreeClient:
    def __init__(self):
        self.app_id = settings.CASHFREE_APP_ID
        self.secret_key = settings.CASHFREE_SECRET_KEY
        self.base_url = settings.CASHFREE_API_URL
        self.headers = {
            "x-client-id": self.app_id,
            "x-client-secret": self.secret_key,
            "x-api-version": "2022-09-01",
            "Content-Type": "application/json"
        }
        
        # Check if we are in mock mode (using default placeholders)
        self.is_mock = (
            self.app_id == "YOUR_CASHFREE_APP_ID" or 
            self.secret_key == "YOUR_CASHFREE_SECRET_KEY" or
            getattr(settings, 'CASHFREE_MOCK', False)
        )

    def create_order(self, order_id, amount, customer_id, customer_phone, return_url):
        if self.is_mock:
            # Return mock response
            return {
                "payment_session_id": "mock_session_" + order_id,
                "payment_link": f"/orders/mock-payment/{order_id}/",
                "order_status": "ACTIVE"
            }

        payload = {
            "order_id": order_id,
            "order_amount": float(amount),
            "order_currency": "INR",
            "customer_details": {
                "customer_id": customer_id,
                "customer_phone": customer_phone
            },
            "order_meta": {
                "return_url": return_url
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Cashfree Create Order Error: {e.response.text}")
            return {"error": e.response.text}
        except Exception as e:
            logger.error(f"Cashfree General Error: {str(e)}")
            return {"error": str(e)}

    def verify_order(self, order_id):
        if self.is_mock:
             return {
                 "order_status": "PAID",
                 "order_id": order_id,
                 "payment_status": "SUCCESS"
             }

        url = f"{self.base_url}/{order_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
             logger.error(f"Cashfree Verify Order Error: {str(e)}")
             return None
