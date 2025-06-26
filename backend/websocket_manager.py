"""
WebSocket Manager for Real-time Market Data
Provides real-time trading analytics and market updates
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set
import random
from fastapi import WebSocket, WebSocketDisconnect
import uuid

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time data streaming"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.connection_subscriptions: Dict[str, Set[str]] = {}  # connection_id -> subscribed topics
        
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
            
        self.connection_subscriptions[connection_id] = set()
        logger.info(f"WebSocket connection established: {connection_id} for user: {user_id}")
        
    async def disconnect(self, connection_id: str, user_id: str = None):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            
        if connection_id in self.connection_subscriptions:
            del self.connection_subscriptions[connection_id]
            
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
                
        logger.info(f"WebSocket connection closed: {connection_id}")
        
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send a message to a specific connection"""
        websocket = self.active_connections.get(connection_id)
        if websocket:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                await self.disconnect(connection_id)
                
    async def send_to_user(self, message: dict, user_id: str):
        """Send a message to all connections for a specific user"""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id].copy():
                await self.send_personal_message(message, connection_id)
                
    async def broadcast_to_topic(self, message: dict, topic: str):
        """Broadcast a message to all connections subscribed to a topic"""
        for connection_id, subscriptions in self.connection_subscriptions.items():
            if topic in subscriptions:
                await self.send_personal_message(message, connection_id)
                
    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all active connections"""
        for connection_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, connection_id)
            
    def subscribe_to_topic(self, connection_id: str, topic: str):
        """Subscribe a connection to a topic"""
        if connection_id in self.connection_subscriptions:
            self.connection_subscriptions[connection_id].add(topic)
            
    def unsubscribe_from_topic(self, connection_id: str, topic: str):
        """Unsubscribe a connection from a topic"""
        if connection_id in self.connection_subscriptions:
            self.connection_subscriptions[connection_id].discard(topic)
            
    def get_active_connections_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)

# Global connection manager instance
manager = ConnectionManager()

class MarketDataSimulator:
    """Simulates real-time market data for demo purposes"""
    
    def __init__(self):
        self.commodities = {
            'crude_oil': {'price': 75.50, 'volume': 12500, 'change': 0.0},
            'natural_gas': {'price': 2.85, 'volume': 8900, 'change': 0.0},
            'lng': {'price': 15.20, 'volume': 3400, 'change': 0.0},
            'gasoline': {'price': 2.25, 'volume': 15600, 'change': 0.0},
            'diesel': {'price': 2.45, 'volume': 11200, 'change': 0.0},
        }
        self.is_running = False
        
    async def start_simulation(self):
        """Start the market data simulation"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("Starting market data simulation")
        
        while self.is_running:
            try:
                # Update market data
                for commodity in self.commodities:
                    await self._update_commodity_data(commodity)
                    
                # Send trading activity simulation
                await self._simulate_trading_activity()
                
                # Wait before next update
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in market data simulation: {e}")
                await asyncio.sleep(1)
                
    def stop_simulation(self):
        """Stop the market data simulation"""
        self.is_running = False
        logger.info("Stopping market data simulation")
        
    async def _update_commodity_data(self, commodity: str):
        """Update data for a specific commodity"""
        current_data = self.commodities[commodity]
        
        # Simulate price changes
        price_change = random.uniform(-0.5, 0.5)  # Random change between -0.5% and +0.5%
        price_multiplier = 1 + (price_change / 100)
        new_price = current_data['price'] * price_multiplier
        
        # Simulate volume changes
        volume_change = random.uniform(-10, 10)  # Random change between -10% and +10%
        volume_multiplier = 1 + (volume_change / 100)
        new_volume = max(100, current_data['volume'] * volume_multiplier)
        
        # Update the data
        old_price = current_data['price']
        self.commodities[commodity] = {
            'price': round(new_price, 2),
            'volume': int(new_volume),
            'change': round(((new_price - old_price) / old_price) * 100, 2),
            'timestamp': datetime.utcnow().isoformat(),
            'high_24h': round(current_data.get('high_24h', new_price) * random.uniform(1.0, 1.02), 2),
            'low_24h': round(current_data.get('low_24h', new_price) * random.uniform(0.98, 1.0), 2),
        }
        
        # Broadcast update to subscribers
        message = {
            'type': 'MARKET_UPDATE',
            'commodity': commodity,
            'metrics': self.commodities[commodity]
        }
        
        await manager.broadcast_to_topic(message, f'market_data_{commodity}')
        await manager.broadcast_to_topic(message, 'market_data_all')
        
    async def _simulate_trading_activity(self):
        """Simulate trading activity data"""
        activities = []
        
        for _ in range(random.randint(1, 5)):  # 1-5 activities per update
            commodity = random.choice(list(self.commodities.keys()))
            activity_type = random.choice(['buy', 'sell'])
            quantity = random.randint(100, 5000)
            price = self.commodities[commodity]['price'] * random.uniform(0.98, 1.02)
            
            activities.append({
                'id': str(uuid.uuid4()),
                'commodity': commodity,
                'type': activity_type,
                'quantity': quantity,
                'price': round(price, 2),
                'timestamp': datetime.utcnow().isoformat(),
                'location': random.choice(['Houston', 'Singapore', 'Dubai', 'Rotterdam', 'Mumbai'])
            })
            
        message = {
            'type': 'TRADING_ACTIVITY',
            'activity': activities
        }
        
        await manager.broadcast_to_topic(message, 'trading_activity')

# Global market data simulator
market_simulator = MarketDataSimulator()

class AnalyticsStreamer:
    """Streams analytics data to connected clients"""
    
    def __init__(self):
        self.analytics_cache = {}
        
    async def send_analytics_update(self, user_id: str, analytics_data: dict):
        """Send analytics update to a specific user"""
        message = {
            'type': 'ANALYTICS_UPDATE',
            'data': analytics_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await manager.send_to_user(message, user_id)
        
    async def send_portfolio_update(self, user_id: str, portfolio_data: dict):
        """Send portfolio update to a specific user"""
        message = {
            'type': 'PORTFOLIO_UPDATE',
            'data': portfolio_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await manager.send_to_user(message, user_id)
        
    async def send_alert(self, user_id: str, alert_data: dict):
        """Send price alert to a specific user"""
        message = {
            'type': 'PRICE_ALERT',
            'alert': alert_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await manager.send_to_user(message, user_id)

# Global analytics streamer
analytics_streamer = AnalyticsStreamer()

async def handle_websocket_message(websocket: WebSocket, message: dict, connection_id: str):
    """Handle incoming WebSocket messages"""
    try:
        message_type = message.get('type')
        
        if message_type == 'SUBSCRIBE':
            # Subscribe to topics
            topics = message.get('topics', [])
            for topic in topics:
                manager.subscribe_to_topic(connection_id, topic)
                logger.info(f"Connection {connection_id} subscribed to {topic}")
                
            # Send confirmation
            await manager.send_personal_message({
                'type': 'SUBSCRIPTION_CONFIRMED',
                'topics': topics
            }, connection_id)
            
        elif message_type == 'UNSUBSCRIBE':
            # Unsubscribe from topics
            topics = message.get('topics', [])
            for topic in topics:
                manager.unsubscribe_from_topic(connection_id, topic)
                logger.info(f"Connection {connection_id} unsubscribed from {topic}")
                
        elif message_type == 'GET_CURRENT_DATA':
            # Send current market data
            commodity = message.get('commodity')
            if commodity and commodity in market_simulator.commodities:
                current_data = market_simulator.commodities[commodity]
                await manager.send_personal_message({
                    'type': 'CURRENT_DATA',
                    'commodity': commodity,
                    'data': current_data
                }, connection_id)
            else:
                # Send all commodities data
                await manager.send_personal_message({
                    'type': 'CURRENT_DATA',
                    'data': market_simulator.commodities
                }, connection_id)
                
        elif message_type == 'PING':
            # Respond to ping with pong
            await manager.send_personal_message({
                'type': 'PONG',
                'timestamp': datetime.utcnow().isoformat()
            }, connection_id)
            
        else:
            logger.warning(f"Unknown message type: {message_type}")
            
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")
        await manager.send_personal_message({
            'type': 'ERROR',
            'message': 'Failed to process message'
        }, connection_id)

async def websocket_endpoint(websocket: WebSocket, user_id: str = None):
    """WebSocket endpoint for real-time market data"""
    connection_id = str(uuid.uuid4())
    
    try:
        await manager.connect(websocket, connection_id, user_id)
        
        # Start market simulation if not already running
        if not market_simulator.is_running:
            asyncio.create_task(market_simulator.start_simulation())
            
        # Send welcome message
        await manager.send_personal_message({
            'type': 'CONNECTED',
            'connection_id': connection_id,
            'message': 'Welcome to Oil & Gas Finder real-time data stream'
        }, connection_id)
        
        # Listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                await handle_websocket_message(websocket, message, connection_id)
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    'type': 'ERROR',
                    'message': 'Invalid JSON format'
                }, connection_id)
                
    except WebSocketDisconnect:
        await manager.disconnect(connection_id, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(connection_id, user_id)

# Export the main components
__all__ = [
    'manager',
    'market_simulator', 
    'analytics_streamer',
    'websocket_endpoint',
    'handle_websocket_message'
]