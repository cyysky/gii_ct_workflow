"""
WebSocket manager for real-time updates
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio


class SocketManager:
    """WebSocket connection manager."""

    def __init__(self):
        # Active connections by room
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # User subscriptions
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, room: str = "dashboard"):
        """Connect a WebSocket client."""
        await websocket.accept()

        if room not in self.active_connections:
            self.active_connections[room] = []

        self.active_connections[room].append(websocket)

    def disconnect(self, websocket: WebSocket, room: str = "dashboard"):
        """Disconnect a WebSocket client."""
        if room in self.active_connections:
            if websocket in self.active_connections[room]:
                self.active_connections[room].remove(websocket)

            if not self.active_connections[room]:
                del self.active_connections[room]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            pass

    async def broadcast(self, message: dict, room: str = "dashboard"):
        """Broadcast a message to all clients in a room."""
        if room in self.active_connections:
            disconnected = []

            for connection in self.active_connections[room]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    disconnected.append(connection)

            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect(connection, room)

    async def broadcast_scan_update(self, scan_data: dict):
        """Broadcast scan status update."""
        await self.broadcast({
            "type": "scan_update",
            "data": scan_data,
        }, room="scans")

        # Also broadcast to dashboard
        await self.broadcast({
            "type": "scan_update",
            "data": scan_data,
        }, room="dashboard")

    async def broadcast_patient_update(self, patient_data: dict):
        """Broadcast patient status update."""
        await self.broadcast({
            "type": "patient_update",
            "data": patient_data,
        }, room="patients")

        await self.broadcast({
            "type": "patient_update",
            "data": patient_data,
        }, room="dashboard")

    async def broadcast_notification(self, notification_data: dict, user_id: str = None):
        """Broadcast notification to specific user or all."""
        if user_id and user_id in self.user_connections:
            await self.send_personal_message({
                "type": "notification",
                "data": notification_data,
            }, self.user_connections[user_id])
        else:
            await self.broadcast({
                "type": "notification",
                "data": notification_data,
            }, room="dashboard")

    async def broadcast_scanner_update(self, scanner_data: dict):
        """Broadcast scanner status update."""
        await self.broadcast({
            "type": "scanner_update",
            "data": scanner_data,
        }, room="scanners")

        await self.broadcast({
            "type": "scanner_update",
            "data": scanner_data,
        }, room="dashboard")


# Global socket manager instance
socket_manager = SocketManager()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint handler."""
    room = websocket.query_params.get("room", "dashboard")

    await socket_manager.connect(websocket, room)

    try:
        while True:
            # Keep connection alive, handle incoming messages
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "ping":
                    await socket_manager.send_personal_message(
                        {"type": "pong"},
                        websocket
                    )
                elif message.get("type") == "subscribe":
                    # Handle room subscription
                    new_room = message.get("room", room)
                    socket_manager.disconnect(websocket, room)
                    await socket_manager.connect(websocket, new_room)
                    room = new_room

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        socket_manager.disconnect(websocket, room)


# Export for use in routes
__all__ = ["socket_manager"]