import re

from django.core.validators import MinValueValidator
from rest_framework import serializers

from .models import Transaction


def validate_phone_number(value):
    if not re.match(r'^(07\d{8}|01\d{8}|254[17]\d{8}|\+254[17]\d{8})$', value):
        raise serializers.ValidationError(
            "Enter a valid Kenyan phone number: 07XXXXXXXX, 01XXXXXXXX, 2547XXXXXXXX, or +2547XXXXXXXX."
        )
    return value


def normalize_phone(value):
    """Convert any Kenyan phone format to 254XXXXXXXXX."""
    cleaned = value.strip()
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    if cleaned.startswith('0'):
        cleaned = '254' + cleaned[1:]
    return cleaned


class TransactionSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        model = Transaction
        fields = [
            "id", "listing", "buyer", "phone_number", "amount",
            "status", "checkout_request_id", "created_at", "updated_at",
        ]
        read_only_fields = ["status", "checkout_request_id", "created_at", "updated_at", "buyer"]