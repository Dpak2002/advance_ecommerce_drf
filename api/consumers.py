import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Order

User = get_user_model()


class OrderConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time order notifications
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Get user from scope (set by authentication middleware)
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        # Create a unique group name for this user
        self.user_group_name = f'user_{self.user.id}'
        
        # Add user to their group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to order notifications',
            'user_id': self.user.id
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Remove user from their group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', '')
            
            if message_type == 'ping':
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'pong'
                }))
            elif message_type == 'subscribe_orders':
                # Subscribe to order updates
                await self.send(text_data=json.dumps({
                    'type': 'subscription_confirmed',
                    'message': 'Subscribed to order notifications'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def order_update(self, event):
        """Handle order update notifications"""
        # Send order update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'order_id': event['order_id'],
            'old_status': event['old_status'],
            'new_status': event['new_status'],
            'message': event['message'],
            'timestamp': event.get('timestamp', '')
        }))
    
    async def order_created(self, event):
        """Handle new order notifications"""
        await self.send(text_data=json.dumps({
            'type': 'order_created',
            'order_id': event['order_id'],
            'message': event['message'],
            'timestamp': event.get('timestamp', '')
        }))
    
    @classmethod
    async def send_order_update(cls, user_id, data):
        """Send order update to specific user"""
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        await channel_layer.group_send(
            f'user_{user_id}',
            {
                'type': 'order_update',
                'order_id': data['order_id'],
                'old_status': data['old_status'],
                'new_status': data['new_status'],
                'message': data['message'],
                'timestamp': data.get('timestamp', '')
            }
        )
    
    @classmethod
    async def send_order_created(cls, user_id, data):
        """Send new order notification to specific user"""
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        await channel_layer.group_send(
            f'user_{user_id}',
            {
                'type': 'order_created',
                'order_id': data['order_id'],
                'message': data['message'],
                'timestamp': data.get('timestamp', '')
            }
        )


class AdminOrderConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for admin order notifications
    """
    
    async def connect(self):
        """Handle WebSocket connection for admin"""
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated or not self.user.is_admin:
            await self.close()
            return
        
        # Create admin group
        self.admin_group_name = 'admin_orders'
        
        # Add admin to admin group
        await self.channel_layer.group_add(
            self.admin_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to admin order notifications',
            'user_id': self.user.id
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.admin_group_name,
            self.channel_name
        )
    
    async def new_order(self, event):
        """Handle new order notifications for admin"""
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'order_id': event['order_id'],
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'total_price': str(event['total_price']),
            'message': event['message'],
            'timestamp': event.get('timestamp', '')
        }))
    
    async def order_status_changed(self, event):
        """Handle order status change notifications for admin"""
        await self.send(text_data=json.dumps({
            'type': 'order_status_changed',
            'order_id': event['order_id'],
            'user_id': event['user_id'],
            'old_status': event['old_status'],
            'new_status': event['new_status'],
            'message': event['message'],
            'timestamp': event.get('timestamp', '')
        }))
    
    @classmethod
    async def notify_new_order(cls, order_data):
        """Notify admins about new order"""
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        await channel_layer.group_send(
            'admin_orders',
            {
                'type': 'new_order',
                'order_id': order_data['order_id'],
                'user_id': order_data['user_id'],
                'user_name': order_data['user_name'],
                'total_price': order_data['total_price'],
                'message': order_data['message'],
                'timestamp': order_data.get('timestamp', '')
            }
        )
    
    @classmethod
    async def notify_order_status_change(cls, order_data):
        """Notify admins about order status change"""
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        await channel_layer.group_send(
            'admin_orders',
            {
                'type': 'order_status_changed',
                'order_id': order_data['order_id'],
                'user_id': order_data['user_id'],
                'old_status': order_data['old_status'],
                'new_status': order_data['new_status'],
                'message': order_data['message'],
                'timestamp': order_data.get('timestamp', '')
            }
        ) 