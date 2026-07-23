from rest_framework import serializers

from .models import Category, Favourite, Listing, Message, Report


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ListingSerializer(serializers.ModelSerializer):
    seller = serializers.ReadOnlyField(source="seller.email")
    seller_id = serializers.ReadOnlyField(source="seller.id")
    seller_joined = serializers.ReadOnlyField(source="seller.date_joined")
    category_name = serializers.ReadOnlyField(source="category.name")
    is_favourited = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "id", "seller", "seller_id", "seller_joined", "category",
            "category_name", "title", "description", "price", "image",
            "status", "created_at", "is_favourited",
        ]
        read_only_fields = ["seller", "created_at"]

    def get_is_favourited(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return Favourite.objects.filter(user=user, listing=obj).exists()
        return False

    def update(self, instance, validated_data):
        if "status" in validated_data:
            if instance.seller != self.context["request"].user:
                raise serializers.ValidationError({"status": "Only the seller can change the listing status."})
        return super().update(instance, validated_data)


class ListingDetailSerializer(ListingSerializer):
    class Meta(ListingSerializer.Meta):
        fields = ListingSerializer.Meta.fields + ["reports_count"]

    reports_count = serializers.SerializerMethodField()

    def get_reports_count(self, obj):
        return obj.reports.count()


class FavouriteSerializer(serializers.ModelSerializer):
    listing_title = serializers.ReadOnlyField(source="listing.title")

    class Meta:
        model = Favourite
        fields = ["id", "listing", "listing_title", "created_at"]
        read_only_fields = ["created_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source="sender.email")
    recipient_email = serializers.ReadOnlyField(source="recipient.email")

    class Meta:
        model = Message
        fields = ["id", "listing", "sender", "recipient", "recipient_email", "body", "created_at", "is_read"]
        read_only_fields = ["sender", "created_at", "is_read"]


class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.ReadOnlyField(source="reporter.email")

    class Meta:
        model = Report
        fields = ["id", "listing", "reporter", "reason", "description", "created_at"]
        read_only_fields = ["reporter", "created_at"]
