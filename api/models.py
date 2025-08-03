from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )
    
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    
    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def is_customer(self):
        return self.user_type == 'customer'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def decrease_stock(self, quantity):
        """Decrease stock when product is ordered"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False
    
    @property
    def in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0


class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    @property
    def total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Calculate total price of all items in cart"""
        return sum(item.total_price for item in self.items.all())
    
    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.cart.user.username}'s cart"
    
    @property
    def total_price(self):
        """Calculate total price for this item"""
        return self.product.price * self.quantity
    
    def save(self, *args, **kwargs):
        # Ensure quantity doesn't exceed available stock
        if self.quantity > self.product.stock:
            self.quantity = self.product.stock
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username} - {self.status}"
    
    @property
    def total_items(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items.all())
    
    def update_status(self, new_status):
        """Update order status and send notification"""
        old_status = self.status
        self.status = new_status
        self.save()
        
        # Send WebSocket notification (import here to avoid circular import)
        import asyncio
        try:
            from .consumers import OrderConsumer
            asyncio.create_task(OrderConsumer.send_order_update(self.user.id, {
                'order_id': self.id,
                'old_status': old_status,
                'new_status': new_status,
                'message': f'Your order #{self.id} status has been updated to {new_status}'
            }))
        except Exception:
            # If WebSocket notification fails, continue without it
            pass


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order #{self.order.id}"
    
    @property
    def total_price(self):
        """Calculate total price for this item"""
        return self.price * self.quantity

