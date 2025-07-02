from django.contrib import admin
from .models import Product, Cart, Order, Category, OrderItem


# ✅ Product
admin.site.register(Product)

# ✅ Cart
admin.site.register(Cart)

# ✅ Category
admin.site.register(Category)


# ✅ Inline for Order Items (to show inside Order page)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# ✅ Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['user__username', 'id']
    inlines = [OrderItemInline]


# ✅ Register Order with customized admin
admin.site.register(Order, OrderAdmin)

# ✅ Order Item
admin.site.register(OrderItem)

