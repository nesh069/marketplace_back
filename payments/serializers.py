from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id", "listing", "buyer", "phone_number", "amount",
            "status", "checkout_request_id", "created_at", "updated_at",
        ]
        read_only_fields = ["status", "checkout_request_id", "created_at", "updated_at", "buyer"]