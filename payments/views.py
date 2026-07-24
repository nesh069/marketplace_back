import logging
import re

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from marketplace.models import Listing

from .models import Transaction
from .pesapal import PesapalService
from .serializers import TransactionSerializer, normalize_phone, validate_phone_number


class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        listing_id = request.data.get("listing_id")
        phone_number = request.data.get("phone_number")

        if not phone_number:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_phone_number(str(phone_number))
        except Exception:
            return Response(
                {"error": "Enter a valid Kenyan phone number: 07XXXXXXXX, 01XXXXXXXX, 2547XXXXXXXX, or +2547XXXXXXXX."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone_number = normalize_phone(str(phone_number))

        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            return Response({"error": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)

        if listing.seller == request.user:
            return Response({"error": "You cannot buy your own listing."}, status=status.HTTP_400_BAD_REQUEST)

        if listing.status == "sold":
            return Response({"error": "This listing has already been sold."}, status=status.HTTP_400_BAD_REQUEST)

        transaction = Transaction.objects.create(
            listing=listing,
            buyer=request.user,
            phone_number=phone_number,
            amount=listing.price,
        )

        try:
            result = PesapalService().initiate_payment(transaction)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            transaction.status = "failed"
            transaction.save()
            return Response({"error": f"Payment initiation failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, transaction_id):
        try:
            transaction = Transaction.objects.get(id=transaction_id, buyer=request.user)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check live status from Pesapal
        if transaction.checkout_request_id:
            try:
                pesapal_status = PesapalService().check_status(transaction.checkout_request_id)
                # Update local status if changed
                if pesapal_status.get("status") == "COMPLETED" and transaction.status != "success":
                    transaction.status = "success"
                    transaction.save()
                    transaction.listing.status = "sold"
                    transaction.listing.save()
            except Exception:
                pass  # Return cached status if API fails
        
        return Response(TransactionSerializer(transaction).data)


class PesapalCallbackView(APIView):
    permission_classes = [AllowAny]
    
    STATUS_MAP = {
        "COMPLETED": "success",
        "PENDING": "pending",
        "FAILED": "failed",
        "CANCELLED": "failed",
        "INVALID": "failed",
    }
    
    def post(self, request):
        """Handle Pesapal IPN (server-to-server)."""
        logger = logging.getLogger(__name__)
        
        try:
            data = request.data
            
            # Handle both key formats
            order_tracking_id = data.get("OrderTrackingId") or data.get("order_tracking_id")
            raw_status = data.get("Status") or data.get("status", "")
            
            if not order_tracking_id:
                logger.warning("Callback missing order_tracking_id: %s", data)
                return Response({"status": "received"}, status=status.HTTP_200_OK)
            
            # Map Pesapal status to internal status
            mapped_status = self.STATUS_MAP.get(raw_status.upper(), "pending")
            
            PesapalService().confirm_payment(order_tracking_id, mapped_status, raw_status)
        except Exception as e:
            logger.exception("Callback error: %s", e)
        
        return Response({"status": "received"}, status=status.HTTP_200_OK)

    def get(self, request):
        """Handle browser redirect from Pesapal (GET)."""
        order_tracking_id = request.query_params.get("OrderTrackingId") or request.query_params.get("order_tracking_id")
        raw_status = request.query_params.get("Status") or request.query_params.get("status", "")
        mapped_status = self.STATUS_MAP.get(raw_status.upper(), "pending")

        if order_tracking_id:
            try:
                PesapalService().confirm_payment(order_tracking_id, mapped_status, raw_status)
            except Exception:
                pass

        from django.http import HttpResponseRedirect
        frontend_url = f"{settings.FRONTEND_URL}/payment/callback?status={mapped_status}&order={order_tracking_id}"
        return HttpResponseRedirect(frontend_url)


class PesapalRedirectView(APIView):
    permission_classes = [AllowAny]

    STATUS_MAP = PesapalCallbackView.STATUS_MAP

    def get(self, request):
        """Handle redirect after payment."""
        order_tracking_id = request.query_params.get("OrderTrackingId") or request.query_params.get("order_tracking_id")
        raw_status = request.query_params.get("Status") or request.query_params.get("status", "")
        mapped_status = self.STATUS_MAP.get(raw_status.upper(), "pending")

        if order_tracking_id:
            try:
                PesapalService().confirm_payment(order_tracking_id, mapped_status, raw_status)
            except Exception:
                pass

        from django.http import HttpResponseRedirect
        frontend_url = f"{settings.FRONTEND_URL}/payment/callback?status={mapped_status}&order={order_tracking_id}"
        return HttpResponseRedirect(frontend_url)



