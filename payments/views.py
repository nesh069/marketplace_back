import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from marketplace.models import Listing

from .models import Transaction
from .pesapal import PesapalService
from .serializers import TransactionSerializer


class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        listing_id = request.data.get("listing_id")
        phone_number = request.data.get("phone_number")

        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            return Response({"error": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)

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
        """Handle Pesapal IPN/callback."""
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



