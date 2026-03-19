from django.contrib import admin

# Register your models here.
from .models import Category, Product, Cart, Order, Feedback

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "created_at")
    search_fields = ("user__username", "message")



from django.contrib import admin
from .models import Order

from django.contrib import admin
from django.utils.html import format_html
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "payment_method", "colored_status", "created_at")
    list_filter = ("status", "payment_method")
    actions = ["mark_as_paid", "mark_as_pending", "mark_as_cancelled"]

    # Colored status display
    def colored_status(self, obj):
        if obj.status == "Paid":
            color = "green"
        elif obj.status == "Pending":
            color = "orange"
        elif obj.status == "Cancelled":
            color = "red"
        else:
            color = "black"
        return format_html('<span style="color: {};">{}</span>', color, obj.status)
    colored_status.admin_order_field = "status"
    colored_status.short_description = "Status"

    # Action: mark orders as Paid
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status="Paid")
        self.message_user(request, f"{updated} order(s) marked as Paid.")
    mark_as_paid.short_description = "Mark selected orders as Paid"

    # Action: mark orders as Pending
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status="Pending")
        self.message_user(request, f"{updated} order(s) marked as Pending.")
    mark_as_pending.short_description = "Mark selected orders as Pending"

    # Action: mark orders as Cancelled
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status="Cancelled")
        self.message_user(request, f"{updated} order(s) marked as Cancelled.")
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"

from django.contrib import admin
from .models import Product, Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "comment", "created_at")
    search_fields = ("product__name", "user__username", "comment")
    list_filter = ("rating", "created_at")







