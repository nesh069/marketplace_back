import uuid
import requests
from django.conf import settings
from .models import Transaction

# Sandbox URL
BASE_URL = "https://cybqa.pesapal.com/pesapalv3"


class PesapalService:
    def _get_access_token(self):
        """Get OAuth token from Pesapal."""
        payload = {
            "consumer_key": settings.PESAPAL_CONSUMER_KEY,
            "consumer_secret": settings.PESAPAL_CONSUMER_SECRET,
        }
        response = requests.post(
            f"{BASE_URL}/api/Auth/RequestToken",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["token"]

    def initiate_payment(self, transaction: Transaction) -> dict:
        """Create a payment order and return redirect URL."""
        token = self._get_access_token()
        
        payload = {
            "id": str(uuid.uuid4()),
            "currency": "KES",
            "amount": float(transaction.amount),
            "description": f"Purchase of {transaction.listing.title}",
            "callback_url": settings.PESAPAL_CALLBACK_URL,
            "redirect_mode": "TOP_WINDOW",
            "notification_id": settings.PESAPAL_IPN_ID,
            "billing_address": {
                "email_address": transaction.buyer.email,
                "phone_number": transaction.phone_number,
                "country_code": "KE",
                "first_name": transaction.buyer.username,
                "last_name": transaction.buyer.username,
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/Transactions/SubmitOrderRequest",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        data = response.json()

        if response.status_code != 200 or data.get("error"):
            raise RuntimeError(data.get("error", data.get("message", response.text)))
        
        transaction.checkout_request_id = data.get("order_tracking_id", "")
        transaction.status = "pending"
        transaction.save()
        
        return {
            "order_tracking_id": data.get("order_tracking_id"),
            "redirect_url": data.get("redirect_url"),
            "transaction_id": transaction.id,
        }

    def check_status(self, order_tracking_id: str) -> dict:
        """Check payment status."""
        token = self._get_access_token()
        response = requests.get(
            f"{BASE_URL}/api/Transactions/GetTransactionStatus",
            params={"orderTrackingId": order_tracking_id},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def confirm_payment(self, order_tracking_id: str, status: str):
        """Update transaction from callback/IPN."""
        try:
            transaction = Transaction.objects.get(checkout_request_id=order_tracking_id)
        except Transaction.DoesNotExist:
            return
        
        if status.lower() in ["completed", "success"]:
            transaction.status = "success"
            transaction.save()
            transaction.listing.status = "sold"
            transaction.listing.save()
        else:
            transaction.status = "failed"
            transaction.save()
