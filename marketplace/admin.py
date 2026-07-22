from django.contrib import admin

from .models import Category, Favorite, Listing, Message

admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Favorite)
admin.site.register(Message)