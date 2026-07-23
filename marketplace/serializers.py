from rest_framework import serializers

from .models import Category, Favourite, Listing, Message


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ListingSerializer(serializers.ModelSerializer):
    seller = serializers.ReadOnlyField(source="seller.email")
    seller_id = serializers.ReadOnlyField(source="seller.id")
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Listing
        fields = [
            "id", "seller", "seller_id", "category", "category_name",
            "title", "description", "price", "image", "status", "created_at",
        ]
        read_only_fields = ["seller", "status", "created_at"]


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = ["id", "listing", "created_at"]
        read_only_fields = ["created_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source="sender.email")

    class Meta:
        model = Message
        fields = ["id", "listing", "sender", "recipient", "body", "created_at", "is_read"]
        read_only_fields = ["sender", "created_at", "is_read"]