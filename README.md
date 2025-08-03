# Advanced E-commerce API with Caching and Notifications

A comprehensive Django REST API for a small e-commerce system with advanced features including caching, pagination, filtering, and real-time notifications.

## Features

### 🔐 Authentication & Authorization
- **JWT-based Authentication** using Django REST Framework SimpleJWT
- **User Registration** with email and password
- **User Types**: Admin and Customer roles
- **Profile Management** with name, address, phone, etc.
- **Password Change** functionality
- **Token Refresh** mechanism

### 🛍️ Product Management
- **Product CRUD** operations (Admin only)
- **Category Management** with hierarchical structure
- **Stock Management** with automatic stock reduction on orders
- **Product Status** (active/inactive)
- **Advanced Filtering** by category, price range, stock availability
- **Search Functionality** across product names and descriptions
- **Sorting** by name, price, stock, creation date

### 🛒 Shopping Cart
- **Cart Management** for customers
- **Add/Remove Items** with quantity control
- **Stock Validation** when adding items
- **Cart Total** calculation
- **Cart Clearing** functionality

### 📦 Order System
- **Order Creation** from cart
- **Order Status Flow**: Pending → Shipped → Delivered
- **Order History** for customers
- **Order Management** for admins
- **Real-time Status Updates** via WebSocket notifications

### ⚡ Performance Optimizations
- **Redis Caching** for products and categories
- **Cache Invalidation** when data changes
- **Database Query Optimization** with select_related and prefetch_related
- **Pagination** (10 items per page by default)
- **Cache Management** endpoints for admins

### 🔄 Real-time Notifications
- **WebSocket Support** using Django Channels
- **Order Status Updates** sent to customers in real-time
- **New Order Notifications** sent to admins
- **Connection Management** with authentication

### 🎯 Advanced Filtering & Search
- **Django Filter** integration for complex filtering
- **Price Range Filtering** (min_price, max_price)
- **Stock Availability Filtering** (in_stock, out_of_stock)
- **Category-based Filtering**
- **Date Range Filtering**
- **Search Across Multiple Fields**

## Technology Stack

- **Backend**: Django 5.2.4
- **API Framework**: Django REST Framework 3.14.0
- **Authentication**: JWT (SimpleJWT 5.3.0)
- **Database**: PostgreSQL
- **Caching**: Redis
- **Real-time**: Django Channels 4.0.0
- **Filtering**: Django Filter 23.0
- **Environment**: python-dotenv

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis Server

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ecommerce_api
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Redis Configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

### 4. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Start Redis Server
```bash
redis-server
```

### 7. Run the Development Server
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new customer
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/logout/` - Logout and blacklist token
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `POST /api/auth/profile/change-password/` - Change password

### Public Endpoints
- `GET /api/products/` - List products (with filtering, pagination, caching)
- `GET /api/products/{id}/` - Get product details
- `GET /api/categories/` - List categories (with filtering, caching)

### Customer Endpoints
- `GET /api/customer/dashboard/` - Customer dashboard
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/add/` - Add item to cart
- `PATCH /api/cart/items/{id}/` - Update cart item quantity
- `DELETE /api/cart/items/{id}/remove/` - Remove item from cart
- `DELETE /api/cart/clear/` - Clear cart
- `POST /api/orders/create/` - Create order from cart
- `GET /api/orders/` - List customer's orders
- `GET /api/orders/{id}/` - Get order details

### Admin Endpoints
- `GET /api/admin/dashboard/` - Admin dashboard
- `GET /api/admin/users/` - List all users
- `GET /api/admin/users/{id}/` - Get user details
- `GET /api/admin/categories/` - List categories (CRUD)
- `POST /api/admin/categories/` - Create category
- `PUT /api/admin/categories/{id}/` - Update category
- `DELETE /api/admin/categories/{id}/` - Delete category
- `GET /api/admin/products/` - List products (CRUD)
- `POST /api/admin/products/` - Create product
- `PUT /api/admin/products/{id}/` - Update product
- `DELETE /api/admin/products/{id}/` - Delete product
- `PATCH /api/admin/products/{id}/stock/` - Update product stock
- `GET /api/admin/orders/` - List all orders
- `GET /api/admin/orders/{id}/` - Get order details
- `PATCH /api/admin/orders/{id}/status/` - Update order status

### Cache Management (Admin Only)
- `GET /api/admin/cache/stats/` - Get cache statistics
- `POST /api/admin/cache/clear/` - Clear all cache
- `POST /api/admin/cache/invalidate-products/` - Invalidate product cache
- `POST /api/admin/cache/invalidate-categories/` - Invalidate category cache

## WebSocket Endpoints

### Real-time Notifications
- `ws://localhost:8000/ws/orders/` - Customer order notifications
- `ws://localhost:8000/ws/admin/orders/` - Admin order notifications

## Usage Examples

### Product Filtering
```bash
# Filter by price range
GET /api/products/?min_price=10&max_price=100

# Filter by category
GET /api/products/?category=1

# Filter by stock availability
GET /api/products/?in_stock=true

# Search products
GET /api/products/?search=laptop

# Sort by price (ascending)
GET /api/products/?ordering=price

# Sort by price (descending)
GET /api/products/?ordering=-price
```



## Caching Strategy

### Cache Configuration
- **Products**: Cached for 1 hour
- **Categories**: Cached for 1 hour
- **Orders**: Cached for 30 minutes
- **Cache Invalidation**: Automatic when data changes

### Cache Keys
- Product list: `products_list_<hash>`
- Product detail: `product_detail_<id>`
- Category list: `categories_list_<hash>`
- Category detail: `category_detail_<id>`







### Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- Database configuration variables
- Redis configuration variables




