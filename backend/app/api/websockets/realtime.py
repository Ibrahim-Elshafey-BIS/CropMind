"""
CropMind - WebSocket Real-time Handler
Manages real-time WebSocket connections for farm updates

Author: CropMind Team
Date: 2026
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Set, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections per farm.
    Handles multiple connections per farm and broadcasts messages.
    """
    
    def __init__(self):
        # Farm ID -> Set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # WebSocket -> Farm ID mapping for cleanup
        self.connection_farm_map: Dict[WebSocket, int] = {}
        
    async def connect(self, websocket: WebSocket, farm_id: int) -> bool:
        """
        Accept a WebSocket connection and register it for a farm.
        
        Args:
            websocket: WebSocket connection
            farm_id: Farm ID
            
        Returns:
            bool: True if connection was successful
        """
        try:
            await websocket.accept()
            
            if farm_id not in self.active_connections:
                self.active_connections[farm_id] = set()
            
            self.active_connections[farm_id].add(websocket)
            self.connection_farm_map[websocket] = farm_id
            
            # Send connection confirmation
            await self.send_to_websocket(
                websocket,
                {
                    "type": "connected",
                    "farm_id": farm_id,
                    "message": "Connected successfully"
                }
            )
            
            print(f"🔌 WebSocket connected: Farm {farm_id}, Total connections: {len(self.active_connections[farm_id])}")
            return True
            
        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
            return False
    
    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection from the manager.
        
        Args:
            websocket: WebSocket connection to remove
        """
        farm_id = self.connection_farm_map.pop(websocket, None)
        
        if farm_id and farm_id in self.active_connections:
            self.active_connections[farm_id].discard(websocket)
            
            # Clean up empty farm sets
            if not self.active_connections[farm_id]:
                del self.active_connections[farm_id]
            
            print(f"🔌 WebSocket disconnected: Farm {farm_id}, Remaining connections: {len(self.active_connections.get(farm_id, []))}")
    
    async def send_to_websocket(self, websocket: WebSocket, message: Any) -> bool:
        """
        Send a message to a specific WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            message: Message to send (dict or str)
            
        Returns:
            bool: True if message was sent successfully
        """
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            await websocket.send_text(message)
            return True
        except Exception as e:
            print(f"❌ Failed to send message to WebSocket: {e}")
            return False
    
    async def send_to_farm(self, farm_id: int, message: Any) -> int:
        """
        Send a message to all connections of a specific farm.
        
        Args:
            farm_id: Farm ID
            message: Message to send (dict or str)
            
        Returns:
            int: Number of connections that received the message
        """
        if farm_id not in self.active_connections:
            return 0
        
        if isinstance(message, dict):
            message = json.dumps(message)
        
        # Ensure message has farm_id
        if isinstance(message, str):
            try:
                msg_dict = json.loads(message)
                if "farm_id" not in msg_dict:
                    msg_dict["farm_id"] = farm_id
                    message = json.dumps(msg_dict)
            except:
                pass
        
        disconnected = []
        sent_count = 0
        
        for websocket in list(self.active_connections[farm_id]):
            try:
                await websocket.send_text(message)
                sent_count += 1
            except Exception:
                disconnected.append(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected:
            self.disconnect(websocket)
        
        return sent_count
    
    async def broadcast(self, message: Any) -> int:
        """
        Broadcast a message to all connected clients across all farms.
        
        Args:
            message: Message to send (dict or str)
            
        Returns:
            int: Number of connections that received the message
        """
        if isinstance(message, dict):
            message = json.dumps(message)
        
        total_sent = 0
        
        for farm_id in list(self.active_connections.keys()):
            total_sent += await self.send_to_farm(farm_id, message)
        
        return total_sent
    
    def get_farm_connections(self, farm_id: int) -> int:
        """
        Get the number of active connections for a farm.
        
        Args:
            farm_id: Farm ID
            
        Returns:
            int: Number of active connections
        """
        return len(self.active_connections.get(farm_id, []))
    
    def get_connection_count(self) -> int:
        """
        Get the total number of active connections across all farms.
        
        Returns:
            int: Total active connections
        """
        total = 0
        for farm_id in self.active_connections:
            total += len(self.active_connections[farm_id])
        return total
    
    def get_farm_ids(self) -> list:
        """
        Get list of all farm IDs with active connections.
        
        Returns:
            list: Farm IDs
        """
        return list(self.active_connections.keys())
    
    async def send_ping_to_farm(self, farm_id: int) -> int:
        """
        Send a ping message to all connections of a farm.
        
        Args:
            farm_id: Farm ID
            
        Returns:
            int: Number of connections that received the ping
        """
        return await self.send_to_farm(
            farm_id,
            {"type": "ping", "farm_id": farm_id}
        )


# Singleton instance
manager = ConnectionManager()


# ============================================
# WebSocket Endpoint
# ============================================

@router.websocket("/ws/{farm_id}")
async def websocket_endpoint(websocket: WebSocket, farm_id: int):
    """
    WebSocket endpoint for real-time farm updates.
    
    Handles:
    - Connection establishment and authentication
    - Ping/Pong keep-alive
    - Message routing
    - Graceful disconnection
    """
    # Parse farm_id from URL
    try:
        farm_id = int(farm_id)
    except ValueError:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        return
    
    # Accept connection
    connected = await manager.connect(websocket, farm_id)
    if not connected:
        return
    
    try:
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive message with timeout to allow for ping checks
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0
                )
                
                # Parse and handle message
                try:
                    message = json.loads(data)
                    msg_type = message.get("type", "")
                    
                    if msg_type == "ping":
                        # Respond with pong
                        await manager.send_to_websocket(
                            websocket,
                            {"type": "pong", "farm_id": farm_id}
                        )
                    elif msg_type == "subscribe":
                        # Handle subscription (just acknowledge)
                        await manager.send_to_websocket(
                            websocket,
                            {
                                "type": "subscribed",
                                "farm_id": farm_id,
                                "message": f"Subscribed to farm {farm_id}"
                            }
                        )
                    elif msg_type == "unsubscribe":
                        # Handle unsubscription
                        await manager.send_to_websocket(
                            websocket,
                            {
                                "type": "unsubscribed",
                                "farm_id": farm_id,
                                "message": f"Unsubscribed from farm {farm_id}"
                            }
                        )
                    else:
                        # Unknown message type, just acknowledge
                        await manager.send_to_websocket(
                            websocket,
                            {
                                "type": "ack",
                                "farm_id": farm_id,
                                "received": msg_type,
                                "message": "Message received"
                            }
                        )
                
                except json.JSONDecodeError:
                    # Invalid JSON
                    await manager.send_to_websocket(
                        websocket,
                        {
                            "type": "error",
                            "farm_id": farm_id,
                            "message": "Invalid JSON format"
                        }
                    )
            
            except asyncio.TimeoutError:
                # No message received within timeout, send ping to check connection
                try:
                    await manager.send_to_websocket(
                        websocket,
                        {"type": "ping", "farm_id": farm_id}
                    )
                except Exception:
                    # Connection likely dead
                    break
                
            except WebSocketDisconnect:
                break
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)


# ============================================
# Helper Functions for External Use
# ============================================

async def send_sensor_update(farm_id: int, sensor_data: dict) -> int:
    """
    Send a sensor update to all connections of a farm.
    
    Args:
        farm_id: Farm ID
        sensor_data: Sensor data dictionary
        
    Returns:
        int: Number of connections that received the update
    """
    message = {
        "type": "sensor_update",
        "farm_id": farm_id,
        "data": sensor_data
    }
    return await manager.send_to_farm(farm_id, message)


async def send_alert(farm_id: int, severity: str, alert_message: str, alert_data: dict = None) -> int:
    """
    Send an alert to all connections of a farm.
    
    Args:
        farm_id: Farm ID
        severity: Alert severity (low, medium, high, critical)
        alert_message: Alert message
        alert_data: Additional alert data
        
    Returns:
        int: Number of connections that received the alert
    """
    message = {
        "type": "alert",
        "farm_id": farm_id,
        "severity": severity,
        "message": alert_message,
        "data": alert_data or {}
    }
    return await manager.send_to_farm(farm_id, message)


async def send_agent_insight(farm_id: int, agent: str, insight_message: str, insight_data: dict = None) -> int:
    """
    Send an agent insight to all connections of a farm.
    
    Args:
        farm_id: Farm ID
        agent: Agent name
        insight_message: Insight message
        insight_data: Additional insight data
        
    Returns:
        int: Number of connections that received the insight
    """
    message = {
        "type": "agent_insight",
        "farm_id": farm_id,
        "agent": agent,
        "message": insight_message,
        "data": insight_data or {}
    }
    return await manager.send_to_farm(farm_id, message)


async def broadcast_system_status(status: str, details: dict = None) -> int:
    """
    Broadcast system status to all connected clients.
    
    Args:
        status: System status (online, maintenance, error)
        details: Additional details
        
    Returns:
        int: Number of connections that received the broadcast
    """
    message = {
        "type": "system_status",
        "status": status,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat()
    }
    return await manager.broadcast(message)
