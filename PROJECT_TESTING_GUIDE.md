# Advanced E-commerce API - Complete Testing Guide

This guide provides step-by-step instructions to test all features of the Advanced E-commerce API with caching, pagination, filtering, and real-time notifications.

## 📋 Prerequisites

Before starting the tests, ensure you have:

1. **Python 3.8+** installed
2. **PostgreSQL** database running
3. **Redis** server running
4. **Postman** installed (for API testing)
5. **Web browser** (for WebSocket testing)

## 🚀 Initial Setup

### Step 1: Environment Setup
```bash
# Clone or navigate to project directory
cd ecommerce_api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Database Configuration
```bash
# Create .env file with your database credentials
cp env.example .env

# Edit .env file with your PostgreSQL credentials:
# DB_NAME=ecommerce_db
# DB_USER=your_username
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432
```

### Step 3: Database Migration
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser
# Follow prompts to create admin user
```

### Step 4: Start Services
```bash
# Start Redis server (in a separate terminal)
redis-server

# Start Django development server
python manage.py runserver
```

## 🧪 Testing Checklist

### ✅ 1. Authentication & User Management

#### 1.1 User Registration
- [ ] **Test Customer Registration**
  ```bash
  POST http://localhost:8000/api/auth/register/
  Content-Type: application/json
  
  {
    "username": "testcustomer",
    "email": "customer@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "Customer",
    "phone": "+1234567890",
    "address": "123 Main St, City, State"
  }
  ```
  **Expected**: 201 Created with user data

#### 1.2 User Login
- [ ] **Test Login**
  ```bash
  POST http://localhost:8000/api/auth/login/
  Content-Type: application/json
  
  {
    "username": "testcustomer",
    "password": "testpass123"
  }
  ```
  **Expected**: 200 OK with access and refresh tokens

#### 1.3 Profile Management
- [ ] **Get User Profile**
  ```bash
  GET http://localhost:8000/api/auth/profile/
  Authorization: Bearer <access_token>
  ```
  **Expected**: 200 OK with user profile data

- [ ] **Update Profile**
  ```bash
  PUT http://localhost:8000/api/auth/profile/
  Authorization: Bearer <access_token>
  Content-Type: application/json
  
  {
    "first_name": "Updated",
    "last_name": "Name",
    "email": "updated@example.com"
  }
  ```
  **Expected**: 200 OK with updated profile

### ✅ 2. Admin Management

#### 2.1 Admin Dashboard
- [ ] **Access Admin Dashboard**
  ```bash
  GET http://localhost:8000/api/admin/dashboard/
  Authorization: Bearer <admin_token>
  ```
  **Expected**: 200 OK with dashboard statistics

#### 2.2 User Management
- [ ] **List All Users**
  ```bash
  GET http://localhost:8000/api/admin/users/
  Authorization: Bearer <admin_token>
  ```
  **Expected**: 200 OK with paginated user list

### ✅ 3. Product Management (Admin)

#### 3.1 Category Management
- [ ] **Create Category**
  ```bash
  POST http://localhost:8000/api/admin/categories/
  Authorization: Bearer <admin_token>
  Content-Type: application/json
  
  {
    "name": "Electronics",
    "description": "Electronic devices and gadgets"
  }
  ```
  **Expected**: 201 Created

- [ ] **List Categories**
  ```bash
  GET http://localhost:8000/api/admin/categories/
  Authorization: Bearer <admin_token>
  ```
  **Expected**: 200 OK with category list

#### 3.2 Product Management
- [ ] **Create Product**
  ```bash
  POST http://localhost:8000/api/admin/products/
  Authorization: Bearer <admin_token>
  Content-Type: application/json
  
  {
    "name": "Smartphone",
    "description": "Latest smartphone with advanced features",
    "price": "599.99",
    "stock": 50,
    "category": 1,
    "is_active": true
  }
  ```
  **Expected**: 201 Created

- [ ] **Update Product Stock**
  ```bash
  PATCH http://localhost:8000/api/admin/products/1/stock/
  Authorization: Bearer <admin_token>
  Content-Type: application/json
  
  {
    "stock": 45
  }
  ```
  **Expected**: 200 OK with updated product

### ✅ 4. Public Product Browsing (with Caching & Filtering)

#### 4.1 Basic Product Listing
- [ ] **List All Products (Paginated)**
  ```bash
  GET http://localhost:8000/api/products/
  ```
  **Expected**: 200 OK with paginated results (10 items per page)

#### 4.2 Advanced Filtering
- [ ] **Filter by Category**
  ```bash
  GET http://localhost:8000/api/products/?category=1
  ```
  **Expected**: 200 OK with products from category 1

- [ ] **Filter by Price Range**
  ```bash
  GET http://localhost:8000/api/products/?min_price=100&max_price=500
  ```
  **Expected**: 200 OK with products in price range

- [ ] **Filter by Stock Availability**
  ```bash
  GET http://localhost:8000/api/products/?in_stock=true
  ```
  **Expected**: 200 OK with products in stock

- [ ] **Search Products**
  ```bash
  GET http://localhost:8000/api/products/?search=smartphone
  ```
  **Expected**: 200 OK with matching products

- [ ] **Sort Products**
  ```bash
  GET http://localhost:8000/api/products/?ordering=price
  GET http://localhost:8000/api/products/?ordering=-price
  ```
  **Expected**: 200 OK with sorted results

#### 4.3 Caching Verification
- [ ] **Check Cache Headers**
  ```bash
  GET http://localhost:8000/api/products/
  ```
  **Expected**: Response includes `Cache-Control` and `X-Cache-Status` headers

### ✅ 5. Cart Management (Customer)

#### 5.1 Cart Operations
- [ ] **View Cart**
  ```bash
  GET http://localhost:8000/api/cart/
  Authorization: Bearer <customer_token>
  ```
  **Expected**: 200 OK with cart contents

- [ ] **Add Product to Cart**
  ```bash
  POST http://localhost:8000/api/cart/add/
  Authorization: Bearer <customer_token>
  Content-Type: application/json
  
  {
    "product_id": 1,
    "quantity": 2
  }
  ```
  **Expected**: 200 OK with updated cart

- [ ] **Update Cart Item**
  ```bash
  PATCH http://localhost:8000/api/cart/items/1/
  Authorization: Bearer <customer_token>
  Content-Type: application/json
  
  {
    "quantity": 3
  }
  ```
  **Expected**: 200 OK with updated cart

- [ ] **Remove Item from Cart**
  ```bash
  DELETE http://localhost:8000/api/cart/items/1/remove/
  Authorization: Bearer <customer_token>
  ```
  **Expected**: 200 OK with updated cart

### ✅ 6. Order Management

#### 6.1 Customer Orders
- [ ] **Create Order from Cart**
  ```bash
  POST http://localhost:8000/api/orders/create/
  Authorization: Bearer <customer_token>
  Content-Type: application/json
  
  {
    "shipping_address": "123 Main St, City, State, 12345"
  }
  ```
  **Expected**: 201 Created with order details

- [ ] **List Customer Orders**
  ```bash
  GET http://localhost:8000/api/orders/
  Authorization: Bearer <customer_token>
  ```
  **Expected**: 200 OK with customer's orders

#### 6.2 Admin Order Management
- [ ] **List All Orders (with Filtering)**
  ```bash
  GET http://localhost:8000/api/admin/orders/
  Authorization: Bearer <admin_token>
  ```
  **Expected**: 200 OK with paginated order list

- [ ] **Filter Orders by Status**
  ```bash
  GET http://localhost:8000/api/admin/orders/?status=pending
  Authorization: Bearer <admin_token>
  ```
  **Expected**: 200 OK with pending orders

- [ ] **Update Order Status**
  ```bash
  PATCH http://localhost:8000/api/admin/orders/1/status/
  Authorization: Bearer <admin_token>
  Content-Type: application/json
  
  {
    "status": "shipped"
  }
  ```
  **Expected**: 200 OK with updated order

### ✅ 7. Cache Management (Admin)

#### 7.1 Cache Operations
- [ ] **Get Cache Statistics**
  ```bash
  GET http://localhost:8000/api/admin/cache/stats/
  Authorization: Bearer <admin_token>
  ```
  **Expected**: 200 OK with cache statistics

- [ ] **Clear All Cache**
  ```bash
  POST http://localhost:8000/api/admin/cache/clear/
  Authorization: Bearer <admin_token>
  ```
  **Expected**: 200 OK with success message

- [ ] **Invalidate Product Cache**
  ```bash
  POST http://localhost:8000/api/admin/cache/invalidate-products/
  Authorization: Bearer <admin_token>
  Content-Type: application/json
  
  {
    "product_id": 1
  }
  ```
  **Expected**: 200 OK with success message

### ✅ 8. Real-time Notifications (WebSocket)

#### 8.1 WebSocket Connection Testing

**Prerequisites**: Open `websocket_client_example.html` in a web browser

- [ ] **Test Customer WebSocket Connection**
  1. Open the HTML file in browser
  2. Click "Connect as Customer"
  3. **Expected**: Status shows "Connected"

- [ ] **Test Admin WebSocket Connection**
  1. Click "Connect as Admin"
  2. **Expected**: Status shows "Connected"

#### 8.2 Real-time Notifications Testing

- [ ] **Test Order Creation Notification**
  1. Ensure WebSocket connections are active
  2. Create an order using the API
  3. **Expected**: Customer receives "Order Created" notification
  4. **Expected**: Admin receives "New Order" notification

- [ ] **Test Order Status Update Notification**
  1. Update order status using admin API
  2. **Expected**: Customer receives "Order Update" notification
  3. **Expected**: Admin receives "Order Status Changed" notification

### ✅ 9. Performance Testing

#### 9.1 Database Query Optimization
- [ ] **Test Optimized Queries**
  ```bash
  # Monitor database queries during product listing
  GET http://localhost:8000/api/products/
  ```
  **Expected**: Minimal database queries due to select_related

#### 9.2 Caching Performance
- [ ] **Test Cache Hit Performance**
  1. Make first request to products endpoint
  2. Make second request immediately
  3. **Expected**: Second request should be faster (cached)

### ✅ 10. Error Handling & Edge Cases

#### 10.1 Authentication Errors
- [ ] **Test Invalid Token**
  ```bash
  GET http://localhost:8000/api/auth/profile/
  Authorization: Bearer invalid_token
  ```
  **Expected**: 401 Unauthorized

- [ ] **Test Expired Token**
  ```bash
  # Use expired token
  GET http://localhost:8000/api/auth/profile/
  Authorization: Bearer <expired_token>
  ```
  **Expected**: 401 Unauthorized

#### 10.2 Permission Errors
- [ ] **Test Customer Accessing Admin Endpoints**
  ```bash
  GET http://localhost:8000/api/admin/dashboard/
  Authorization: Bearer <customer_token>
  ```
  **Expected**: 403 Forbidden

#### 10.3 Business Logic Errors
- [ ] **Test Adding Out-of-Stock Product**
  ```bash
  POST http://localhost:8000/api/cart/add/
  Authorization: Bearer <customer_token>
  Content-Type: application/json
  
  {
    "product_id": 1,
    "quantity": 1000
  }
  ```
  **Expected**: 400 Bad Request with stock error

## 🧪 Automated Testing

### Run Unit Tests
```bash
# Run all tests
python manage.py test

# Run specific test classes
python manage.py test api.tests.CacheTestCase
python manage.py test api.tests.FilterTestCase
python manage.py test api.tests.PaginationTestCase
python manage.py test api.tests.WebSocketTestCase
```

### Test Coverage
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

## 📊 Performance Monitoring

### 1. Database Performance
```bash
# Monitor database queries
python manage.py shell
>>> from django.db import connection
>>> from api.models import Product
>>> Product.objects.all()[:10]
>>> print(len(connection.queries))
```

### 2. Cache Performance
```bash
# Check cache statistics via API
GET http://localhost:8000/api/admin/cache/stats/
```

### 3. Response Time Monitoring
- Use Postman's response time metrics
- Monitor WebSocket connection latency
- Check pagination performance with large datasets

## 🔧 Troubleshooting

### Common Issues

#### 1. Redis Connection Error
```bash
# Check if Redis is running
redis-cli ping
# Expected: PONG

# If Redis is not running:
redis-server
```

#### 2. Database Connection Error
```bash
# Check PostgreSQL status
# On Windows: Check Services
# On Linux: sudo systemctl status postgresql

# Test database connection
python manage.py dbshell
```

#### 3. WebSocket Connection Issues
- Ensure Redis is running
- Check browser console for errors
- Verify ASGI configuration

#### 4. Cache Not Working
```bash
# Clear cache manually
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

## 📈 Success Criteria

### Functional Requirements
- [ ] All API endpoints return correct responses
- [ ] Authentication and authorization work properly
- [ ] Real-time notifications are delivered
- [ ] Caching improves response times
- [ ] Filtering and pagination work correctly

### Performance Requirements
- [ ] Product listing responds within 500ms
- [ ] Cached responses are 50% faster than uncached
- [ ] WebSocket connections establish within 2 seconds
- [ ] Database queries are optimized (minimal N+1 queries)

### Security Requirements
- [ ] JWT tokens are properly validated
- [ ] Role-based access control is enforced
- [ ] Input validation prevents malicious data
- [ ] Sensitive data is not exposed

## 🎯 Final Verification

### Complete Workflow Test
1. **Register a customer user**
2. **Login and get tokens**
3. **Browse products with filtering**
4. **Add products to cart**
5. **Create an order**
6. **Update order status as admin**
7. **Verify real-time notifications**
8. **Test cache management**

### Expected Results
- All steps complete successfully
- Real-time notifications appear in WebSocket client
- Cache improves performance on subsequent requests
- Filtering and pagination work as expected
- No security vulnerabilities are exposed

## 📝 Test Report Template

After completing all tests, document your findings:

```markdown
# Test Report - Advanced E-commerce API

## Test Date: [Date]
## Tester: [Name]

## Summary
- [ ] All functional tests passed
- [ ] Performance requirements met
- [ ] Security requirements satisfied
- [ ] Real-time notifications working
- [ ] Caching system operational

## Issues Found
- [List any issues encountered]

## Recommendations
- [List any improvements suggested]

## Sign-off
- [ ] Ready for production deployment
- [ ] Requires additional testing
- [ ] Needs fixes before deployment
```

---

**Congratulations!** 🎉 If you've completed all the tests successfully, your Advanced E-commerce API is ready for production deployment. 