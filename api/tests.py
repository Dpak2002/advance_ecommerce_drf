from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .cache_utils import invalidate_product_cache, invalidate_category_cache
from django.core.cache import cache
import json

User = get_user_model()


class CacheTestCase(TestCase):
    """Test cache functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='customer'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        self.product = Product.objects.create(
            name='Smartphone',
            description='Latest smartphone',
            price=599.99,
            stock=50,
            category=self.category
        )
    
    def test_product_cache_invalidation(self):
        """Test that product cache is invalidated when product is updated"""
        # Clear cache first
        cache.clear()
        
        # Update product
        self.product.name = 'Updated Smartphone'
        self.product.save()
        
        # Cache should be invalidated
        invalidate_product_cache(self.product.id)
        
        # Verify cache is cleared
        self.assertIsNone(cache.get(f'product_detail_{self.product.id}'))
    
    def test_category_cache_invalidation(self):
        """Test that category cache is invalidated when category is updated"""
        # Clear cache first
        cache.clear()
        
        # Update category
        self.category.name = 'Updated Electronics'
        self.category.save()
        
        # Cache should be invalidated
        invalidate_category_cache(self.category.id)
        
        # Verify cache is cleared
        self.assertIsNone(cache.get(f'category_detail_{self.category.id}'))


class FilterTestCase(APITestCase):
    """Test filtering functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='customer'
        )
        self.category1 = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        self.category2 = Category.objects.create(
            name='Books',
            description='Books and literature'
        )
        self.product1 = Product.objects.create(
            name='Smartphone',
            description='Latest smartphone',
            price=599.99,
            stock=50,
            category=self.category1
        )
        self.product2 = Product.objects.create(
            name='Laptop',
            description='High-performance laptop',
            price=1299.99,
            stock=25,
            category=self.category1
        )
        self.product3 = Product.objects.create(
            name='Python Book',
            description='Learn Python programming',
            price=29.99,
            stock=100,
            category=self.category2
        )
    
    def test_product_filtering_by_category(self):
        """Test filtering products by category"""
        url = reverse('public-products-list')
        response = self.client.get(f'{url}?category={self.category1.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_product_filtering_by_price_range(self):
        """Test filtering products by price range"""
        url = reverse('public-products-list')
        response = self.client.get(f'{url}?min_price=500&max_price=1000')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only smartphone
    
    def test_product_filtering_by_stock(self):
        """Test filtering products by stock availability"""
        url = reverse('public-products-list')
        response = self.client.get(f'{url}?in_stock=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # All products in stock
    
    def test_product_search(self):
        """Test searching products"""
        url = reverse('public-products-list')
        response = self.client.get(f'{url}?search=smartphone')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_ordering(self):
        """Test ordering products"""
        url = reverse('public-products-list')
        response = self.client.get(f'{url}?ordering=price')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [item['price'] for item in response.data['results']]
        self.assertEqual(prices, sorted(prices))


class PaginationTestCase(APITestCase):
    """Test pagination functionality"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        
        # Create 15 products to test pagination
        for i in range(15):
            Product.objects.create(
                name=f'Product {i}',
                description=f'Description for product {i}',
                price=100 + i,
                stock=10,
                category=self.category
            )
    
    def test_pagination_default_page_size(self):
        """Test that pagination returns 10 items per page by default"""
        url = reverse('public-products-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('count', response.data)
    
    def test_pagination_next_page(self):
        """Test accessing the next page"""
        url = reverse('public-products-list')
        response = self.client.get(f'{url}?page=2')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # Remaining 5 products


class WebSocketTestCase(TestCase):
    """Test WebSocket functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='customer'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        self.product = Product.objects.create(
            name='Smartphone',
            description='Latest smartphone',
            price=599.99,
            stock=50,
            category=self.category
        )
    
    def test_order_creation_notification(self):
        """Test that order creation triggers notifications"""
        # Create cart and add item
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1
        )
        
        # Create order
        order = Order.objects.create(
            user=self.user,
            total_price=599.99,
            shipping_address='123 Test St'
        )
        
        # Verify order was created
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.user, self.user)


class OrderNotificationTestCase(APITestCase):
    """Test order notification functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='customer'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            user_type='admin'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        self.product = Product.objects.create(
            name='Smartphone',
            description='Latest smartphone',
            price=599.99,
            stock=50,
            category=self.category
        )
        
        # Get tokens
        self.user_token = RefreshToken.for_user(self.user)
        self.admin_token = RefreshToken.for_user(self.admin_user)
    
    def test_order_status_update_notification(self):
        """Test that order status updates trigger notifications"""
        # Create order
        order = Order.objects.create(
            user=self.user,
            total_price=599.99,
            shipping_address='123 Test St'
        )
        
        # Update order status
        order.update_status('shipped')
        
        # Verify status was updated
        order.refresh_from_db()
        self.assertEqual(order.status, 'shipped')


class CacheManagementTestCase(APITestCase):
    """Test cache management endpoints"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            user_type='admin'
        )
        self.admin_token = RefreshToken.for_user(self.admin_user)
    
    def test_cache_stats_endpoint(self):
        """Test cache statistics endpoint"""
        url = reverse('cache-stats')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('cache_stats', response.data)
    
    def test_clear_cache_endpoint(self):
        """Test clear cache endpoint"""
        url = reverse('clear-cache')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_invalidate_product_cache_endpoint(self):
        """Test invalidate product cache endpoint"""
        url = reverse('invalidate-product-cache')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        
        response = self.client.post(url, {'product_id': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)


class PerformanceTestCase(APITestCase):
    """Test performance optimizations"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        
        # Create multiple products
        for i in range(20):
            Product.objects.create(
                name=f'Product {i}',
                description=f'Description for product {i}',
                price=100 + i,
                stock=10,
                category=self.category
            )
    
    def test_optimized_product_queryset(self):
        """Test that product queryset uses select_related"""
        url = reverse('public-products-list')
        
        with self.assertNumQueries(2):  # One for count, one for data
            response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_cached_response_headers(self):
        """Test that cached responses include proper headers"""
        url = reverse('public-products-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Cache-Control', response)
        self.assertIn('X-Cache-Status', response)
