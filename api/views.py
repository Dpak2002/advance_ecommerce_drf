from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from django.db.models import Prefetch
from .models import CustomUser, Category, Product, Cart, CartItem, Order, OrderItem
from .serializers import (
    UserSerializer, UserRegistrationSerializer, CustomerRegistrationSerializer, 
    AdminRegistrationSerializer, LoginSerializer, UserProfileSerializer, ChangePasswordSerializer,
    CategorySerializer, ProductSerializer, ProductListSerializer, StockUpdateSerializer,
    CartSerializer, CartItemSerializer, AddToCartSerializer, UpdateCartItemSerializer,
    OrderSerializer, OrderItemSerializer, CreateOrderSerializer, UpdateOrderStatusSerializer
)
from .permissions import IsAdminUser, IsCustomerUser
from .filters import ProductFilter, CategoryFilter, OrderFilter
from .consumers import OrderConsumer, AdminOrderConsumer
from .cache_utils import (
    invalidate_product_cache, invalidate_category_cache, 
    invalidate_order_cache, get_cache_stats, clear_all_cache
)
import asyncio
from datetime import datetime
from django.conf import settings


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class CustomerRegisterView(generics.CreateAPIView):
    """
    Register a new customer user
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Universal profile view for all users
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        """
        Get user profile with universal information
        """
        user = self.get_object()
        serializer = self.get_serializer(user)
        
        # Add universal profile information for all users
        profile_data = serializer.data
        profile_data.update({
            'is_admin': user.is_admin,
            'is_customer': user.is_customer,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
        })
        
        return Response(profile_data)

    def put(self, request, *args, **kwargs):
        """
        Update user profile
        """
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Partially update user profile
        """
        return super().patch(request, *args, **kwargs)


class ChangePasswordView(generics.GenericAPIView):
    """
    Change user password
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileStatsView(generics.GenericAPIView):
    """
    Get universal user profile statistics for all users
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        from datetime import datetime
        days_since_joined = (datetime.now().replace(tzinfo=None) - user.date_joined.replace(tzinfo=None)).days
        
        stats = {
            'user_id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'days_since_joined': days_since_joined,
            'is_active': user.is_active,
            'last_login': user.last_login,
            'date_joined': user.date_joined,
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'profile_complete': bool(user.first_name and user.last_name and user.email and user.phone),
        }
        
        return Response(stats)


class LogoutView(generics.GenericAPIView):
    """
    Logout user
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class AdminUserListView(generics.ListAPIView):
    """
    Admin-only view to list all users
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin-only view to manage individual users
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class AdminDashboardView(generics.GenericAPIView):
    """
    Admin dashboard with user statistics
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_users = CustomUser.objects.count()
        admin_users = CustomUser.objects.filter(user_type='admin').count()
        customer_users = CustomUser.objects.filter(user_type='customer').count()
        
        return Response({
            'dashboard_type': 'admin',
            'total_users': total_users,
            'admin_users': admin_users,
            'customer_users': customer_users,
            'recent_users': UserSerializer(CustomUser.objects.order_by('-date_joined')[:5], many=True).data,
            'user_info': UserSerializer(request.user).data
        })


class CustomerDashboardView(generics.GenericAPIView):
    """
    Customer dashboard
    """
    permission_classes = [IsCustomerUser]

    def get(self, request):
        return Response({
            'dashboard_type': 'customer',
            'message': 'Welcome to your customer dashboard',
            'user_info': UserSerializer(request.user).data
        })


class CategoryListView(generics.ListCreateAPIView):
    """
    List and create categories (Admin only)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete categories (Admin only)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


class ProductListView(generics.ListCreateAPIView):
    """
    List and create products (Admin only)
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete products with cache invalidation (Admin only)
    """
    queryset = Product.objects.all().select_related('category')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]

    def perform_update(self, serializer):
        """Invalidate cache when product is updated"""
        instance = serializer.save()
        # Invalidate product cache
        invalidate_product_cache(instance.id)
        return instance

    def perform_destroy(self, instance):
        """Invalidate cache when product is deleted"""
        # Invalidate product cache
        invalidate_product_cache(instance.id)
        return super().perform_destroy(instance)


class ProductStockUpdateView(generics.GenericAPIView):
    """
    Update product stock with cache invalidation (Admin only)
    """
    serializer_class = StockUpdateSerializer
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                product.stock = serializer.validated_data['stock']
                product.save()
                
                # Invalidate cache when stock is updated
                invalidate_product_cache(product.id)
                
                return Response({
                    'message': 'Stock updated successfully',
                    'product': ProductSerializer(product).data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class PublicProductListView(generics.ListAPIView):
    """
    List all active products with caching, pagination, and filtering (Public)
    """
    queryset = Product.objects.filter(is_active=True).select_related('category')
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'stock', 'created_at']
    ordering = ['-created_at']

    @method_decorator(cache_page(3600))  # Cache for 1 hour
    @method_decorator(vary_on_cookie)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Optimized queryset with select_related for better performance"""
        return Product.objects.filter(is_active=True).select_related('category')

    def list(self, request, *args, **kwargs):
        """Override list to add cache invalidation logic"""
        response = super().list(request, *args, **kwargs)
        
        # Add cache headers
        response['Cache-Control'] = 'public, max-age=3600'
        response['X-Cache-Status'] = 'HIT'
        
        return response


class PublicProductDetailView(generics.RetrieveAPIView):
    """
    Retrieve product details (Public)
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class PublicCategoryListView(generics.ListAPIView):
    """
    List all categories with caching and filtering (Public)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @method_decorator(cache_page(3600))  # Cache for 1 hour
    @method_decorator(vary_on_cookie)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Optimized queryset with prefetch_related for products count"""
        return Category.objects.prefetch_related('products')

    def list(self, request, *args, **kwargs):
        """Override list to add cache headers"""
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=3600'
        response['X-Cache-Status'] = 'HIT'
        return response


# Cart Management Views (Customer Only)
class CartView(generics.RetrieveAPIView):
    """
    Get user's cart (Customer only)
    """
    serializer_class = CartSerializer
    permission_classes = [IsCustomerUser]

    def get_object(self):
        # Get or create cart for user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartView(generics.GenericAPIView):
    """
    Add product to cart (Customer only)
    """
    serializer_class = AddToCartSerializer
    permission_classes = [IsCustomerUser]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            
            # Get or create cart
            cart, created = Cart.objects.get_or_create(user=user)
            
            # Get product
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check stock
            if product.stock < quantity:
                return Response({'error': f'Only {product.stock} items available'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Add or update cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Update existing item
                cart_item.quantity += quantity
                if cart_item.quantity > product.stock:
                    cart_item.quantity = product.stock
                cart_item.save()
            
            return Response({
                'message': 'Product added to cart successfully',
                'cart': CartSerializer(cart).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateCartItemView(generics.GenericAPIView):
    """
    Update cart item quantity (Customer only)
    """
    serializer_class = UpdateCartItemSerializer
    permission_classes = [IsCustomerUser]

    def patch(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(data=request.data, context={'cart_item': cart_item})
        if serializer.is_valid():
            cart_item.quantity = serializer.validated_data['quantity']
            cart_item.save()
            
            return Response({
                'message': 'Cart item updated successfully',
                'cart': CartSerializer(cart_item.cart).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveFromCartView(generics.GenericAPIView):
    """
    Remove item from cart (Customer only)
    """
    permission_classes = [IsCustomerUser]

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart = cart_item.cart
            cart_item.delete()
            
            return Response({
                'message': 'Item removed from cart successfully',
                'cart': CartSerializer(cart).data
            }, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)


class ClearCartView(generics.GenericAPIView):
    """
    Clear all items from cart (Customer only)
    """
    permission_classes = [IsCustomerUser]

    def delete(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.clear()
        
        return Response({
            'message': 'Cart cleared successfully',
            'cart': CartSerializer(cart).data
        }, status=status.HTTP_200_OK)


# Order Management Views
class CreateOrderView(generics.GenericAPIView):
    """
    Create order from cart (Customer only)
    """
    serializer_class = CreateOrderSerializer
    permission_classes = [IsCustomerUser]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Get user's cart
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not cart.items.exists():
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate stock availability
            for item in cart.items.all():
                if item.quantity > item.product.stock:
                    return Response({
                        'error': f'Insufficient stock for {item.product.name}. Available: {item.product.stock}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create order
            order = Order.objects.create(
                user=user,
                total_price=cart.total_price,
                shipping_address=serializer.validated_data['shipping_address']
            )
            
            # Create order items and decrease stock
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                # Decrease stock
                item.product.decrease_stock(item.quantity)
            
            # Clear cart
            cart.clear()
            
            # Send real-time notifications
            try:
                # Notify customer about order creation
                asyncio.create_task(OrderConsumer.send_order_created(user.id, {
                    'order_id': order.id,
                    'message': f'Your order #{order.id} has been created successfully!',
                    'timestamp': datetime.now().isoformat()
                }))
                
                # Notify admins about new order
                asyncio.create_task(AdminOrderConsumer.notify_new_order({
                    'order_id': order.id,
                    'user_id': user.id,
                    'user_name': user.username,
                    'total_price': order.total_price,
                    'message': f'New order #{order.id} created by {user.username}',
                    'timestamp': datetime.now().isoformat()
                }))
            except Exception as e:
                # Log the error but don't fail the order creation
                print(f"WebSocket notification failed: {e}")
            
            return Response({
                'message': 'Order created successfully',
                'order': OrderSerializer(order).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerOrderListView(generics.ListAPIView):
    """
    List customer's orders (Customer only)
    """
    serializer_class = OrderSerializer
    permission_classes = [IsCustomerUser]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class CustomerOrderDetailView(generics.RetrieveAPIView):
    """
    Get customer's order details (Customer only)
    """
    serializer_class = OrderSerializer
    permission_classes = [IsCustomerUser]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class AdminOrderListView(generics.ListAPIView):
    """
    List all orders with filtering and pagination (Admin only)
    """
    queryset = Order.objects.all().select_related('user').prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['user__username', 'user__email', 'shipping_address']
    ordering_fields = ['created_at', 'total_price', 'status']
    ordering = ['-created_at']


class AdminOrderDetailView(generics.RetrieveAPIView):
    """
    Get order details (Admin only)
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]


class AdminOrderStatusUpdateView(generics.GenericAPIView):
    """
    Update order status (Admin only)
    """
    serializer_class = UpdateOrderStatusSerializer
    permission_classes = [IsAdminUser]

    def patch(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(data=request.data, context={'order': order})
        if serializer.is_valid():
            old_status = order.status
            new_status = serializer.validated_data['status']
            order.update_status(new_status)
            
            # Send real-time notifications
            try:
                # Notify customer about status change
                asyncio.create_task(OrderConsumer.send_order_update(order.user.id, {
                    'order_id': order.id,
                    'old_status': old_status,
                    'new_status': new_status,
                    'message': f'Your order #{order.id} status has been updated to {new_status}',
                    'timestamp': datetime.now().isoformat()
                }))
                
                # Notify admins about status change
                asyncio.create_task(AdminOrderConsumer.notify_order_status_change({
                    'order_id': order.id,
                    'user_id': order.user.id,
                    'old_status': old_status,
                    'new_status': new_status,
                    'message': f'Order #{order.id} status changed from {old_status} to {new_status}',
                    'timestamp': datetime.now().isoformat()
                }))
            except Exception as e:
                # Log the error but don't fail the status update
                print(f"WebSocket notification failed: {e}")
            
            return Response({
                'message': f'Order status updated to {new_status}',
                'order': OrderSerializer(order).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Cache Management Views (Admin Only)
class CacheStatsView(generics.GenericAPIView):
    """
    Get cache statistics (Admin only)
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        """Get cache statistics"""
        stats = get_cache_stats()
        return Response({
            'cache_stats': stats,
            'cache_backend': settings.CACHES['default']['BACKEND'],
            'cache_timeout': settings.CACHES['default']['TIMEOUT'],
        })


class ClearCacheView(generics.GenericAPIView):
    """
    Clear all cache (Admin only)
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        """Clear all cache"""
        try:
            clear_all_cache()
            return Response({
                'message': 'All cache cleared successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'Failed to clear cache: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvalidateProductCacheView(generics.GenericAPIView):
    """
    Invalidate product cache (Admin only)
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        """Invalidate product cache"""
        try:
            product_id = request.data.get('product_id')
            invalidate_product_cache(product_id)
            return Response({
                'message': f'Product cache invalidated successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'Failed to invalidate product cache: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvalidateCategoryCacheView(generics.GenericAPIView):
    """
    Invalidate category cache (Admin only)
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        """Invalidate category cache"""
        try:
            category_id = request.data.get('category_id')
            invalidate_category_cache(category_id)
            return Response({
                'message': f'Category cache invalidated successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'Failed to invalidate category cache: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
