"""WebSocket manager for real-time updates with anonymous and authenticated support."""

import asyncio
import json
import time
from typing import Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from app.core.config import settings
from app.core.auth import verify_token


class WebSocketManager:
    """WebSocket manager for real-time updates."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            'customer': [],  # Anonymous customer connections
            'admin': [],     # Authenticated admin connections
            'all': []        # All connections
        }
        self.connection_metadata: Dict[WebSocket, Dict] = {}
        self.running = False
        
    async def connect_anonymous(self, websocket: WebSocket, channel: str = 'customer') -> bool:
        """Connect anonymous customer clients."""
        try:
            await websocket.accept()
            
            # Add to appropriate channel
            if channel not in self.active_connections:
                self.active_connections[channel] = []
            
            self.active_connections[channel].append(websocket)
            self.active_connections['all'].append(websocket)
            
            # Store metadata
            self.connection_metadata[websocket] = {
                'type': 'anonymous',
                'channel': channel,
                'connected_at': time.time(),
                'user_id': None
            }
            
            # Send welcome message
            await self.send_personal_message({
                'type': 'connected',
                'message': 'Connected to real-time updates',
                'channel': channel
            }, websocket)
            
            return True
            
        except Exception as e:
            print(f"Anonymous connection error: {e}")
            return False
    
    async def connect_authenticated(self, websocket: WebSocket, token: str, channel: str = 'admin') -> bool:
        """Connect authenticated admin clients."""
        try:
            # Validate JWT token
            token_data = verify_token(token)
            if not token_data:
                await websocket.close(code=1008, reason="Invalid token")
                return False
            
            await websocket.accept()
            
            # Add to appropriate channel
            if channel not in self.active_connections:
                self.active_connections[channel] = []
            
            self.active_connections[channel].append(websocket)
            self.active_connections['all'].append(websocket)
            
            # Store metadata
            self.connection_metadata[websocket] = {
                'type': 'authenticated',
                'channel': channel,
                'connected_at': time.time(),
                'user_id': token_data.user_id,
                'username': token_data.username,
                'role': token_data.role
            }
            
            # Send welcome message
            await self.send_personal_message({
                'type': 'connected',
                'message': f'Connected as {token_data.username}',
                'channel': channel,
                'user_id': token_data.user_id
            }, websocket)
            
            return True
            
        except Exception as e:
            print(f"Authenticated connection error: {e}")
            try:
                await websocket.close(code=1008, reason="Authentication failed")
            except:
                pass
            return False
    
    async def disconnect(self, websocket: WebSocket) -> None:
        """Disconnect a WebSocket client."""
        try:
            # Remove from all channels
            for channel_connections in self.active_connections.values():
                if websocket in channel_connections:
                    channel_connections.remove(websocket)
            
            # Remove metadata
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
                
        except Exception as e:
            print(f"Disconnect error: {e}")
    
    async def send_personal_message(self, message: Dict, websocket: WebSocket) -> bool:
        """Send a message to a specific WebSocket client."""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(json.dumps(message))
                return True
        except Exception as e:
            print(f"Send personal message error: {e}")
        return False
    
    async def broadcast_to_channel(self, message: Dict, channel: str) -> int:
        """Broadcast a message to all clients in a specific channel."""
        sent_count = 0
        
        if channel not in self.active_connections:
            return sent_count
        
        # Create a copy of the list to avoid modification during iteration
        connections = self.active_connections[channel].copy()
        
        for websocket in connections:
            if await self.send_personal_message(message, websocket):
                sent_count += 1
            else:
                # Remove disconnected clients
                await self.disconnect(websocket)
        
        return sent_count
    
    async def broadcast_to_all(self, message: Dict) -> int:
        """Broadcast a message to all connected clients."""
        return await self.broadcast_to_channel(message, 'all')
    
    async def broadcast_part_update(self, part_id: int, changes: Dict) -> int:
        """Broadcast part update to all relevant clients."""
        message = {
            'type': 'part_updated',
            'part_id': part_id,
            'changes': changes,
            'timestamp': time.time()
        }
        
        # Broadcast to all channels
        total_sent = 0
        for channel in ['customer', 'admin', 'all']:
            sent = await self.broadcast_to_channel(message, channel)
            total_sent += sent
        
        return total_sent
    
    async def broadcast_stock_update(self, part_id: int, stock_changes: Dict) -> int:
        """Broadcast stock update to all relevant clients."""
        message = {
            'type': 'stock_updated',
            'part_id': part_id,
            'stock_changes': stock_changes,
            'timestamp': time.time()
        }
        
        # Broadcast to all channels
        total_sent = 0
        for channel in ['customer', 'admin', 'all']:
            sent = await self.broadcast_to_channel(message, channel)
            total_sent += sent
        
        return total_sent
    
    async def broadcast_system_message(self, message: str, channel: str = 'all') -> int:
        """Broadcast a system message to clients."""
        system_message = {
            'type': 'system_message',
            'message': message,
            'timestamp': time.time()
        }
        
        return await self.broadcast_to_channel(system_message, channel)
    
    async def start_heartbeat(self) -> None:
        """Start heartbeat to keep connections alive."""
        if self.running:
            return
        
        self.running = True
        
        async def heartbeat_loop():
            while self.running:
                try:
                    # Send heartbeat to all connections
                    heartbeat_message = {
                        'type': 'heartbeat',
                        'timestamp': time.time()
                    }
                    
                    await self.broadcast_to_all(heartbeat_message)
                    
                    # Wait for next heartbeat
                    await asyncio.sleep(settings.websocket_heartbeat_seconds)
                    
                except Exception as e:
                    print(f"Heartbeat error: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
        
        asyncio.create_task(heartbeat_loop())
    
    async def stop_heartbeat(self) -> None:
        """Stop heartbeat loop."""
        self.running = False
    
    def get_connection_stats(self) -> Dict[str, int]:
        """Get connection statistics."""
        stats = {}
        for channel, connections in self.active_connections.items():
            stats[channel] = len(connections)
        
        stats['total'] = len(self.active_connections['all'])
        return stats
    
    def get_connection_info(self) -> List[Dict]:
        """Get detailed connection information."""
        info = []
        for websocket, metadata in self.connection_metadata.items():
            info.append({
                'type': metadata['type'],
                'channel': metadata['channel'],
                'connected_at': metadata['connected_at'],
                'user_id': metadata.get('user_id'),
                'username': metadata.get('username'),
                'role': metadata.get('role')
            })
        return info
    
    async def cleanup_disconnected(self) -> None:
        """Clean up disconnected WebSocket clients."""
        disconnected = []
        
        for websocket in self.active_connections['all']:
            if websocket.client_state != WebSocketState.CONNECTED:
                disconnected.append(websocket)
        
        for websocket in disconnected:
            await self.disconnect(websocket)
        
        if disconnected:
            print(f"Cleaned up {len(disconnected)} disconnected clients")


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
