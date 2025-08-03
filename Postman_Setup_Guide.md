# Postman Collection Setup Guide

## Overview
This guide will help you set up and use the comprehensive Postman collection for the Django E-commerce API. The collection includes all endpoints for authentication, user management, product management, cart operations, and order processing.

## 📁 Collection Structure

The collection is organized into the following folders:

### 1. **Authentication**
- Customer Registration
- Admin Registration  
- Login
- Logout
- Refresh Token

### 2. **Profile Management**
- Get Profile
- Update Profile (PUT)
- Update Profile (PATCH)
- Change Password
- Get Profile Statistics

### 3. **Admin Management**
- Admin Dashboard
- List All Users
- Get User Details
- Update User
- Delete User

### 4. **Customer Dashboard**
- Customer Dashboard

### 5. **Product Management (Admin)**
- List Categories
- Create Category
- Get Category Details
- Update Category
- Delete Category
- List Products
- Create Product
- Get Product Details
- Update Product
- Delete Product
- Update Product Stock

### 6. **Public Products**
- List All Products
- List Products by Category
- Get Product Details
- List Categories

### 7. **Cart Management**
- View Cart
- Add Product to Cart
- Update Cart Item Quantity
- Remove Item from Cart
- Clear Cart

### 8. **Order Management**
- Create Order from Cart
- List Customer Orders
- Get Customer Order Details

### 9. **Admin Order Management**
- List All Orders
- Get Order Details
- Update Order Status

## 🚀 Setup Instructions

### Step 1: Import the Collection

1. Open Postman
2. Click **Import** button
3. Select the `E-commerce_API_Postman_Collection.json` file
4. The collection will be imported with all endpoints

### Step 2: Configure Environment Variables

The collection uses environment variables for dynamic values. You need to set up these variables:

#### **Collection Variables** (Set these in the collection):
- `base_url`: `http://localhost:8000` (or your server URL)
- `access_token`: Leave empty initially
- `refresh_token`: Leave empty initially
- `admin_token`: Leave empty initially
- `customer_token`: Leave empty initially

#### **How to Set Variables:**
1. Click on the collection name
2. Go to **Variables** tab
3. Set the `base_url` to your server URL
4. Leave other token variables empty for now

### Step 3: Get Authentication Tokens

#### **For Customer Testing:**
1. Run **Customer Registration** to create a customer account
2. Run **Login** with the customer credentials
3. Copy the `access` token from the response
4. Set it as the `customer_token` variable
5. Copy the `refresh` token and set it as `refresh_token`

#### **For Admin Testing:**
1. Run **Admin Registration** (requires existing admin token)
2. Or use the Django admin to create an admin user
3. Run **Login** with admin credentials
4. Copy the `access` token and set it as `admin_token`

### Step 4: Test the API Flow

#### **Complete Customer Flow:**
1. **Register Customer** → Get customer account
2. **Login** → Get tokens
3. **Browse Products** → View available products
4. **Add to Cart** → Add products to cart
5. **View Cart** → Check cart contents
6. **Create Order** → Place order from cart
7. **View Orders** → Check order status

#### **Complete Admin Flow:**
1. **Login as Admin** → Get admin tokens
2. **Create Category** → Add product categories
3. **Create Product** → Add products to categories
4. **View Orders** → Check customer orders
5. **Update Order Status** → Change order status

## 🔧 Testing Workflow

### **Initial Setup (One-time):**
```bash
# 1. Start your Django server
python manage.py runserver

# 2. Start Redis (for WebSocket support)
redis-server

# 3. Import collection and set base_url
```

### **Daily Testing Workflow:**
1. **Login** to get fresh tokens
2. **Update tokens** in collection variables
3. **Test specific features** you're working on
4. **Use WebSocket** for real-time order notifications

## 📝 Example Testing Scenarios

### **Scenario 1: Complete E-commerce Flow**
1. Register a customer
2. Login and get tokens
3. Browse products (public endpoint)
4. Add products to cart
5. Create an order
6. Login as admin
7. Update order status
8. Check WebSocket notifications

### **Scenario 2: Product Management**
1. Login as admin
2. Create categories
3. Create products
4. Update product stock
5. View products (public endpoint)

### **Scenario 3: User Management**
1. Login as admin
2. List all users
3. Update user details
4. View user statistics

## 🔐 Authentication Flow

### **JWT Token Management:**
- **Access tokens** expire after 60 minutes
- **Refresh tokens** expire after 24 hours
- Use **Refresh Token** endpoint to get new access tokens
- Store tokens in collection variables for reuse

### **Token Usage:**
- `customer_token`: For customer-specific operations
- `admin_token`: For admin operations
- `access_token`: General purpose (can be either)
- `refresh_token`: For token renewal

## 🌐 WebSocket Testing

### **For Real-time Notifications:**
1. Use a WebSocket client (like wscat or browser console)
2. Connect to: `ws://localhost:8000/ws/orders/`
3. Send authentication token in connection
4. Listen for order status updates

### **JavaScript Example:**
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/orders/');

socket.onopen = function(e) {
    console.log('Connected to order notifications');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'order_update') {
        console.log('Order status updated:', data.message);
    }
};
```

## 🛠️ Troubleshooting

### **Common Issues:**

#### **401 Unauthorized:**
- Check if token is valid
- Refresh token if expired
- Verify correct token type (admin vs customer)

#### **404 Not Found:**
- Verify `base_url` is correct
- Check if Django server is running
- Ensure endpoint URL is correct

#### **500 Server Error:**
- Check Django server logs
- Verify database is running
- Check if migrations are applied

#### **WebSocket Connection Failed:**
- Ensure Redis is running
- Check if ASGI server is used
- Verify WebSocket URL is correct

### **Debug Tips:**
1. **Check Response Headers** for error details
2. **View Django Logs** for server-side errors
3. **Use Django Admin** to verify data
4. **Test with curl** to isolate issues

## 📊 Response Examples

### **Successful Login Response:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "address": "123 Main St",
        "user_type": "customer"
    }
}
```

### **Cart Response:**
```json
{
    "id": 1,
    "user": 1,
    "items": [
        {
            "id": 1,
            "product": 1,
            "product_name": "Smartphone",
            "product_price": "599.99",
            "quantity": 2,
            "total_price": "1199.98",
            "product_in_stock": true,
            "created_at": "2024-01-01T12:00:00Z"
        }
    ],
    "total_items": 2,
    "total_price": "1199.98",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}
```

### **Order Response:**
```json
{
    "id": 1,
    "user": 1,
    "user_name": "testuser",
    "status": "pending",
    "total_price": "1199.98",
    "shipping_address": "123 Main St, City, State",
    "items": [
        {
            "id": 1,
            "product": 1,
            "product_name": "Smartphone",
            "quantity": 2,
            "price": "599.99",
            "total_price": "1199.98",
            "created_at": "2024-01-01T12:00:00Z"
        }
    ],
    "total_items": 2,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}
```

## 🎯 Best Practices

### **Testing Strategy:**
1. **Start with public endpoints** (no auth required)
2. **Test authentication** before protected endpoints
3. **Use separate tokens** for admin and customer testing
4. **Clean up test data** after testing
5. **Test error scenarios** (invalid tokens, missing data)

### **Collection Organization:**
1. **Group related endpoints** in folders
2. **Use descriptive names** for requests
3. **Include example data** in request bodies
4. **Document expected responses**
5. **Use variables** for dynamic values

### **Security Considerations:**
1. **Don't commit tokens** to version control
2. **Use environment variables** for sensitive data
3. **Rotate test tokens** regularly
4. **Test with different user roles**
5. **Verify permission restrictions**

## 📚 Additional Resources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Postman Learning Center](https://learning.postman.com/)
- [JWT Token Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Django Channels Documentation](https://channels.readthedocs.io/)

---

**Happy Testing! 🚀**

This collection provides a comprehensive testing environment for your Django E-commerce API. Use it to verify all functionality, test edge cases, and ensure your API works correctly across different user roles and scenarios. 