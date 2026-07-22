from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "buyer", "listing", "amount", "status", "created_at"]
    list_filter = ["status"]