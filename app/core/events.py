"""Event bus system for cache invalidation and real-time updates."""

import asyncio
import json
import time
from typing import Any, Callable, Dict, List, Optional

from app.core.cache import cache_service
from app.core.config import settings


class EventBus:
    """Event bus for handling cache invalidation and real-time updates."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.redis_client = cache_service.redis_client
        self.pubsub = self.redis_client.pubsub()
        self.running = False
        
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
            except ValueError:
                pass
    
    async def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to all subscribers."""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': time.time()
        }
        
        # Notify local subscribers
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    print(f"Event callback error: {e}")
        
        # Publish to Redis for distributed notifications
        try:
            self.redis_client.publish("events", json.dumps(event))
        except Exception as e:
            print(f"Redis publish error: {e}")
    
    def start_listening(self) -> None:
        """Start listening for distributed events."""
        if self.running:
            return
            
        self.running = True
        self.pubsub.subscribe("events")
        
        def listen():
            while self.running:
                try:
                    message = self.pubsub.get_message(ignore_subscribe_messages=True)
                    if message and message['type'] == 'message':
                        event = json.loads(message['data'])
                        # Handle event synchronously
                        self._handle_distributed_event_sync(event)
                except Exception as e:
                    print(f"Event listening error: {e}")
                    time.sleep(1)
        
        # Run in background thread
        import threading
        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
    
    def stop_listening(self) -> None:
        """Stop listening for distributed events."""
        self.running = False
        self.pubsub.unsubscribe("events")
    
    def _handle_distributed_event_sync(self, event: Dict[str, Any]) -> None:
        """Handle events from other instances (sync version)."""
        event_type = event.get('type')
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        # Run async callback in new event loop
                        asyncio.run(callback(event))
                    else:
                        callback(event)
                except Exception as e:
                    print(f"Distributed event callback error: {e}")
    
    async def _handle_distributed_event(self, event: Dict[str, Any]) -> None:
        """Handle events from other instances."""
        event_type = event.get('type')
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    print(f"Distributed event callback error: {e}")


class EventHandlers:
    """Predefined event handlers for common operations."""
    
    @staticmethod
    async def handle_part_updated(event: Dict[str, Any]) -> None:
        """Handle part update events."""
        data = event.get('data', {})
        part_id = data.get('part_id')
        
        if part_id:
            # Invalidate cache
            cache_service.invalidate_part(part_id)
            
            # Notify WebSocket clients
            await WebSocketManager.broadcast_part_update(part_id, data)
    
    @staticmethod
    async def handle_stock_updated(event: Dict[str, Any]) -> None:
        """Handle stock update events."""
        data = event.get('data', {})
        part_id = data.get('part_id')
        
        if part_id:
            # Invalidate cache
            cache_service.invalidate_stock(part_id)
            
            # Notify WebSocket clients
            await WebSocketManager.broadcast_stock_update(part_id, data)
    
    @staticmethod
    async def handle_cache_invalidation(event: Dict[str, Any]) -> None:
        """Handle cache invalidation events."""
        data = event.get('data', {})
        event_type = data.get('type')
        part_id = data.get('part_id')
        
        if event_type == 'part_updated' and part_id:
            cache_service.invalidate_part(part_id)
        elif event_type == 'stock_updated' and part_id:
            cache_service.invalidate_stock(part_id)


# Global event bus instance
event_bus = EventBus()

# Register default handlers
event_bus.subscribe('part_updated', EventHandlers.handle_part_updated)
event_bus.subscribe('stock_updated', EventHandlers.handle_stock_updated)
event_bus.subscribe('cache_invalidation', EventHandlers.handle_cache_invalidation)


# Import WebSocket manager
from app.core.websocket import websocket_manager as WebSocketManager
