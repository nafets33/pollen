from fastapi import WebSocket
from typing import Dict
import json
import asyncio
import logging


class ConnectionManager:
    def __init__(self):
        # Store connections: {websocket: {username, metadata}}
        self.active_connections: Dict[WebSocket, Dict] = {}
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, initial_data: dict):
        """
        Register new WebSocket connection.
        NOTE: websocket.accept() should be called BEFORE this!
        """
        async with self.lock:
            self.active_connections[websocket] = initial_data
        
        client_user = initial_data.get("username", "unknown")
        client_prod = initial_data.get("prod", "unknown")
        logging.info(f"✅ WebSocket connected: {client_user} env: {client_prod} | Total: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        async with self.lock:
            if websocket in self.active_connections:
                client_user = self.active_connections[websocket].get("username", "unknown")
                del self.active_connections[websocket]
                logging.info(f"❌ WebSocket disconnected: {client_user} | Remaining: {len(self.active_connections)}")
    
    async def send_to_user(self, client_user: str, message, prod: bool):
        """Send message to specific user by username."""
        to_remove = set()
        sent = False
        
        for connection, initial_data in self.active_connections.items():
            if (initial_data.get("username") == client_user and initial_data.get("prod") == prod):
                try:
                    # ✅ Ensure message is a string
                    # ✅ Message should already be a JSON string from websocket_updates.py
                    if not isinstance(message, str):
                        logging.error(f"❌ Expected string, got {type(message)}. Converting...")
                        message_str = json.dumps(message)
                    else:
                        message_str = message
                    
                    # ✅ Debug: Log message length and first 200 chars
                    logging.info(f"📤 Sending to {client_user}: {len(message_str)} chars")
                    logging.debug(f"📦 Message preview: {message_str[:200]}...")
                    
                    await connection.send_text(message_str)
                    
                    logging.info(f"✅ Sent update to {client_user}")
                    sent = True
                except Exception as e:
                    logging.error(f"❌ Error sending to {client_user}: {e}")
                    import traceback
                    traceback.print_exc()
                    to_remove.add(connection)
        
        # Clean up disconnected
        for connection in to_remove:
            await self.disconnect(connection)
        
        if not sent:
            logging.warning(f"⚠️  No active connection found for {client_user}")
        
        return sent
        
    def is_connected(self, client_user: str, prod: bool = None) -> bool:
        """Check if user is connected, optionally filter by environment."""
        for initial_data in self.active_connections.values():
            if initial_data.get("username") == client_user:
                # print("init data router", initial_data)
                if prod is not None:
                    if initial_data.get("prod") == prod:
                        return True
                else:
                    # If prod not specified, just check username
                    return None
        return False
    
    def get_active_users(self):
        """Get list of connected users with their environments."""
        return [
            {
                'username': data.get("username"),
                'prod': data.get("prod"),
                'toggle_view': data.get("toggle_view_selection")
            } 
            for data in self.active_connections.values()
        ]

# Global manager instance
manager = ConnectionManager()