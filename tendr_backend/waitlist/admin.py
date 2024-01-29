from django.contrib import admin

from .models import Waiter


@admin.register(Waiter)
class WaiterAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "company", "phone", "other")
    search_fields = ("full_name", "email")
