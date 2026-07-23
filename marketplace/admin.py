from django.contrib import admin

from .models import Category, Favourite, Listing, Message, Report


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "seller", "price", "status", "category", "created_at"]
    list_filter = ["status", "category"]
    search_fields = ["title", "seller__email"]


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "listing", "created_at"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "sender", "recipient", "listing", "created_at", "is_read"]
    list_filter = ["is_read"]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["id", "listing", "reporter", "reason", "created_at"]
    list_filter = ["reason"]
