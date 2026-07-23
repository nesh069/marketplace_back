from django.contrib import admin
from .models import Category, Listing, Favourite, Message

admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Favourite)
admin.site.register(Message)
