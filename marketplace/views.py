from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Favourite, Listing, Message, Report
from .serializers import (
    CategorySerializer, FavouriteSerializer,
    ListingDetailSerializer, ListingSerializer,
    MessageSerializer, ReportSerializer,
)


class IsSellerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller == request.user


class ListingFilter(FilterSet):
    min_price = NumberFilter(field_name="price", lookup_expr="gte")
    max_price = NumberFilter(field_name="price", lookup_expr="lte")
    seller = NumberFilter(field_name="seller_id")

    class Meta:
        model = Listing
        fields = ["category", "status", "seller", "min_price", "max_price"]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.select_related("seller", "category").all().order_by("-created_at")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSellerOrReadOnly]
    filterset_class = ListingFilter
    search_fields = ["title", "description"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ListingDetailSerializer
        return ListingSerializer

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=True, methods=["patch"])
    def mark_sold(self, request, pk=None):
        listing = self.get_object()
        if listing.seller != request.user:
            return Response({"error": "Only the seller can mark as sold."}, status=status.HTTP_403_FORBIDDEN)
        listing.status = "sold"
        listing.save(update_fields=["status"])
        return Response({"status": "sold"})

    @action(detail=True, methods=["post"])
    def report(self, request, pk=None):
        listing = self.get_object()
        serializer = ReportSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(listing=listing, reporter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def favourites(self, request):
        favourited = Listing.objects.filter(favourited_by__user=request.user)
        page = self.paginate_queryset(favourited)
        serializer = ListingSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class FavouriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavouriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favourite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(recipient=user)).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Report.objects.all()
        return Report.objects.filter(reporter=user)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
