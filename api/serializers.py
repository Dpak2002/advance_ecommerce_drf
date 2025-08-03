from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Category, Product, Cart, CartItem, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address', 'user_type')
        read_only_fields = ('id',)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile operations
    """
    email = serializers.EmailField(required=False)
    username = serializers.CharField(read_only=True)  # Username cannot be changed
    user_type = serializers.CharField(read_only=True)  # User type cannot be changed
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone', 'address', 'user_type', 'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'username', 'user_type', 'date_joined', 'last_login')


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone', 'address', 'user_type')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone', 'address')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        validated_data['user_type'] = 'customer'
        user = CustomUser.objects.create_user(**validated_data)
        return user


class AdminRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone', 'address')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        validated_data['user_type'] = 'admin'
        user = CustomUser.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password')


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model
    """
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'created_at', 'updated_at', 'products_count')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_products_count(self, obj):
        return obj.products.count()


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'price', 'stock', 'category', 
            'category_name', 'is_active', 'created_at', 'updated_at', 'in_stock'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'category_name', 'in_stock')


class ProductListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for product listing
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock', 'category_name', 'in_stock', 'is_active')


class StockUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating product stock
    """
    stock = serializers.IntegerField(min_value=0)
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value


# Cart and Order Serializers
class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    product_in_stock = serializers.BooleanField(source='product.in_stock', read_only=True)
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'product_price', 'quantity', 'total_price', 'product_in_stock', 'created_at')
        read_only_fields = ('id', 'product_name', 'product_price', 'total_price', 'product_in_stock', 'created_at')


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for Cart model
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_items', 'total_price', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'total_items', 'total_price', 'created_at', 'updated_at')


class AddToCartSerializer(serializers.Serializer):
    """
    Serializer for adding items to cart
    """
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    
    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, is_active=True)
            if not product.in_stock:
                raise serializers.ValidationError("Product is out of stock")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        return value
    
    def validate_quantity(self, value):
        product_id = self.initial_data.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                if value > product.stock:
                    raise serializers.ValidationError(f"Only {product.stock} items available in stock")
            except Product.DoesNotExist:
                pass
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    """
    Serializer for updating cart item quantity
    """
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_quantity(self, value):
        cart_item = self.context.get('cart_item')
        if cart_item and value > cart_item.product.stock:
            raise serializers.ValidationError(f"Only {cart_item.product.stock} items available in stock")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price', 'total_price', 'created_at')
        read_only_fields = ('id', 'product_name', 'total_price', 'created_at')


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model
    """
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'user', 'user_name', 'status', 'total_price', 'shipping_address', 'items', 'total_items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'user_name', 'total_price', 'items', 'total_items', 'created_at', 'updated_at')


class CreateOrderSerializer(serializers.Serializer):
    """
    Serializer for creating orders from cart
    """
    shipping_address = serializers.CharField(max_length=500)
    
    def validate_shipping_address(self, value):
        if not value.strip():
            raise serializers.ValidationError("Shipping address cannot be empty")
        return value


class UpdateOrderStatusSerializer(serializers.Serializer):
    """
    Serializer for updating order status (admin only)
    """
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    
    def validate_status(self, value):
        order = self.context.get('order')
        if order:
            # Prevent moving from delivered/cancelled back to other statuses
            if order.status in ['delivered', 'cancelled'] and value not in ['delivered', 'cancelled']:
                raise serializers.ValidationError(f"Cannot change status from {order.status} to {value}")
        return value 