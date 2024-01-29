from django.contrib import admin

from .models import WaitDocument, Waiter


@admin.register(Waiter)
class WaiterAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "company", "phone", "other")
    search_fields = ("full_name", "email")


@admin.register(WaitDocument)
class WaitDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "tendr_id",
    )
    search_fields = (
        "user_id",
        "tendr_id",
    )
