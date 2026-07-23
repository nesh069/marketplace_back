from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from marketplace.models import Listing

from .models import Transaction
from .mpesa import MpesaService
from .serializers import TransactionSerializer


class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        listing_id = request.data.get("listing_id")
        phone_number = request.data.get("phone_number")

        listing = Listing.objects.get(id=listing_id)

        transaction = Transaction.objects.create(
            listing=listing,
            buyer=request.user,
            phone_number=phone_number,
            amount=listing.price,
        )

        MpesaService().initiate_stk_push(transaction)

        return Response(
            {"transaction_id": transaction.id, "status": transaction.status},
            status=status.HTTP_201_CREATED,
        )


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, transaction_id):
        transaction = Transaction.objects.get(id=transaction_id, buyer=request.user)
        return Response(TransactionSerializer(transaction).data)
    
    
class MpesaCallbackView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        callback = request.data.get("Body", {}).get("stkCallback", {})
        checkout_request_id = callback.get("checkoutRequestID")
        result_code = callback.get("ResultCode")
        
        MpesaService().confirm_payment(checkout_request_id, success=(result-code == 0))
        
        return Response({"ResultCode": 0, "ResultDesc": "Accepted"}, status=status.HTTP_200_OK)
    