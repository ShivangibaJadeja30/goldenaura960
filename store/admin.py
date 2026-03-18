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

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "payment_method", "status", "created_at")
    list_filter = ("status", "payment_method")
    actions = ["mark_as_paid"]

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status="Paid")
        self.message_user(request, f"{updated} order(s) marked as Paid.")
    mark_as_paid.short_description = "Mark selected orders as Paid"
