from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product, Cart, CartItem, Order, OrderItem


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'products_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Products Count'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'in_stock', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'category__name')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('price', 'stock', 'is_active')
    
    def in_stock(self, obj):
        return obj.in_stock
    in_stock.boolean = True
    in_stock.short_description = 'In Stock'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('total_price',)


class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_price', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'total_items', 'total_price')
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'total_items', 'created_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'id')
    readonly_fields = ('created_at', 'updated_at', 'total_items')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    
    actions = ['mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as delivered"


# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
