import re

from rest_framework import serializers

from .models import Transaction


def validate_phone_number(value):
    if not re.match(r'^2547\d{8}$', value):
        raise serializers.ValidationError("Phone number must be in format 2547XXXXXXXX (e.g. 254712345678).")
    return value


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id", "listing", "buyer", "phone_number", "amount",
            "status", "checkout_request_id", "created_at", "updated_at",
        ]
        read_only_fields = ["status", "checkout_request_id", "created_at", "updated_at", "buyer"]