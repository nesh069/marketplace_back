import base64
import datetime
import requests
from django.conf import settings

from .models import Transaction

STK_PUSH_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"


class MpesaService:
    def _get_access_token(self):
        credentials = base64.b64encode(
            f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
        ).decode()
        headers = {
            "Authorization": f"Basic {credentials}",
            "User-Agent": "CampusMarketplace/1.0",
        }

        # Try POST with JSON body (bypasses Imperva WAF on some IPs)
        post_headers = {**headers, "Content-Type": "application/json"}
        try:
            response = requests.post(
                "https://sandbox.safaricom.co.ke/oauth/v1/generate",
                params={"grant_type": "client_credentials"},
                json={"grant_type": "client_credentials"},
                headers=post_headers,
                timeout=15,
            )
            data = response.json()
            if "access_token" in data:
                return data["access_token"]
        except Exception:
            pass

        # Fallback: GET with query params (standard Daraja method)
        response = requests.get(
            "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def _generate_password(self, timestamp):
        raw = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
        return base64.b64encode(raw.encode()).decode()

    def initiate_stk_push(self, transaction: Transaction) -> str:
        access_token = self._get_access_token()
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        password = self._generate_password(timestamp)

        phone = transaction.phone_number.lstrip("+")
        if phone.startswith("0"):
            phone = "254" + phone[1:]

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(transaction.amount),
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": f"REF{transaction.listing.id}",
            "TransactionDesc": "Purchase",
        }

        response = requests.post(
            STK_PUSH_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "CampusMarketplace/1.0",
            },
            timeout=10,
        )
        data = response.json()

        checkout_request_id = data.get("CheckoutRequestID", "")
        transaction.checkout_request_id = checkout_request_id
        transaction.status = "pending"
        transaction.save()

        return checkout_request_id

    def confirm_payment(self, checkout_request_id, success: bool):
        try:
            transaction = Transaction.objects.get(checkout_request_id=checkout_request_id)
        except Transaction.DoesNotExist:
            return
        transaction.status = "success" if success else "failed"
        transaction.save()
        if success:
            transaction.listing.status = "sold"
            transaction.listing.save()