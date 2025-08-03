from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, CustomerRegisterView, LoginView, UserProfileView, LogoutView,
    AdminUserListView, AdminUserDetailView, AdminDashboardView, CustomerDashboardView,
    ChangePasswordView, ProfileStatsView,
    CategoryListView, CategoryDetailView, ProductListView, ProductDetailView, ProductStockUpdateView,
    PublicProductListView, PublicProductDetailView, PublicCategoryListView,
    CartView, AddToCartView, UpdateCartItemView, RemoveFromCartView, ClearCartView,
    CreateOrderView, CustomerOrderListView, CustomerOrderDetailView,
    AdminOrderListView, AdminOrderDetailView, AdminOrderStatusUpdateView,
    CacheStatsView, ClearCacheView, InvalidateProductCacheView, InvalidateCategoryCacheView
)

urlpatterns = [
    # Authentication endpoints
    # path('auth/register/', RegisterView.as_view(), name='register'),  # General registration (deprecated)
    path('auth/register/', CustomerRegisterView.as_view(), name='register-customer'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('auth/profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/profile/stats/', ProfileStatsView.as_view(), name='profile-stats'),
    
    # Admin endpoints
    path('admin/users/', AdminUserListView.as_view(), name='admin-users-list'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # Admin Product Management endpoints
    path('admin/categories/', CategoryListView.as_view(), name='admin-categories-list'),
    path('admin/categories/<int:pk>/', CategoryDetailView.as_view(), name='admin-category-detail'),
    path('admin/products/', ProductListView.as_view(), name='admin-products-list'),
    path('admin/products/<int:pk>/', ProductDetailView.as_view(), name='admin-product-detail'),
    path('admin/products/<int:pk>/stock/', ProductStockUpdateView.as_view(), name='admin-product-stock'),
    
    # Admin Order Management endpoints
    path('admin/orders/', AdminOrderListView.as_view(), name='admin-orders-list'),
    path('admin/orders/<int:pk>/', AdminOrderDetailView.as_view(), name='admin-order-detail'),
    path('admin/orders/<int:pk>/status/', AdminOrderStatusUpdateView.as_view(), name='admin-order-status'),
    
    # Admin Cache Management endpoints
    path('admin/cache/stats/', CacheStatsView.as_view(), name='cache-stats'),
    path('admin/cache/clear/', ClearCacheView.as_view(), name='clear-cache'),
    path('admin/cache/invalidate-products/', InvalidateProductCacheView.as_view(), name='invalidate-product-cache'),
    path('admin/cache/invalidate-categories/', InvalidateCategoryCacheView.as_view(), name='invalidate-category-cache'),
    
    # Customer endpoints
    path('customer/dashboard/', CustomerDashboardView.as_view(), name='customer-dashboard'),
    
    # Cart endpoints (Customer only)
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/items/<int:item_id>/', UpdateCartItemView.as_view(), name='update-cart-item'),
    path('cart/items/<int:item_id>/remove/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/clear/', ClearCartView.as_view(), name='clear-cart'),
    
    # Order endpoints
    path('orders/create/', CreateOrderView.as_view(), name='create-order'),
    path('orders/', CustomerOrderListView.as_view(), name='customer-orders-list'),
    path('orders/<int:pk>/', CustomerOrderDetailView.as_view(), name='customer-order-detail'),
    
    # Public Product endpoints
    path('products/', PublicProductListView.as_view(), name='public-products-list'),
    path('products/<int:pk>/', PublicProductDetailView.as_view(), name='public-product-detail'),
    path('categories/', PublicCategoryListView.as_view(), name='public-categories-list'),
]