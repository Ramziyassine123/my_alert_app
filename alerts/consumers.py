"""
WebSocket consumers for real-time alert delivery - ROBUST with proper error handling
"""
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
import logging
import time
from autobahn.exception import Disconnected

logger = logging.getLogger(__name__)


class AlertConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sending_alerts = False  # Flag to prevent duplicate sending
        self.alert_task = None  # Store the task reference
        self.is_connected = False  # Track connection state

    async def connect(self):
        """Handle WebSocket connection"""
        self.group_name = 'alerts'
        self.is_connected = True

        # Join the alerts group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket client connected: {self.channel_name}")

        # Send a welcome message with timestamp
        await self.safe_send({
            'type': 'status',
            'message': 'Connected to Alert Server',
            'timestamp': time.time() * 1000  # milliseconds
        })

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        self.is_connected = False

        # Cancel any running alert task FIRST
        if self.alert_task and not self.alert_task.done():
            logger.info(f"Cancelling alert task for {self.channel_name}")
            self.alert_task.cancel()
            try:
                await self.alert_task
            except asyncio.CancelledError:
                logger.info(f"Alert task cancelled successfully for {self.channel_name}")
            except Exception as e:
                logger.warning(f"Error during task cancellation for {self.channel_name}: {e}")

        # Reset flags
        self.sending_alerts = False

        # Leave the alerts group
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except Exception as e:
            logger.warning(f"Error leaving group for {self.channel_name}: {e}")

        logger.info(f"WebSocket client disconnected: {self.channel_name} (code: {close_code})")

    async def receive(self, text_data):
        """Handle messages from WebSocket client"""
        if not self.is_connected:
            logger.warning(f"Received message on disconnected client: {self.channel_name}")
            return

        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'start_alerts':
                # Client requested to start receiving alerts
                if not self.sending_alerts:
                    logger.info(f"Starting alert sequence for {self.channel_name}")
                    self.sending_alerts = True
                    self.alert_task = asyncio.create_task(
                        self.send_alerts_sequence(),
                        name=f"alerts_{self.channel_name}"
                    )
                else:
                    logger.info(f"Alert sequence already running for {self.channel_name}")
                    await self.safe_send({
                        'type': 'status',
                        'message': 'Alert sequence already running',
                        'timestamp': time.time() * 1000
                    })

            elif message_type == 'stop_alerts':
                # Stop sending alerts
                await self.stop_alerts()

            elif message_type == 'ping':
                # Handle ping for latency measurement - FIXED to echo back ping_id
                ping_id = data.get('ping_id', 'unknown')
                ping_timestamp = data.get('timestamp')

                await self.safe_send({
                    'type': 'pong',
                    'ping_id': ping_id,  # Echo back the ping_id
                    'ping_timestamp': ping_timestamp,
                    'server_timestamp': time.time() * 1000
                })

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from WebSocket client {self.channel_name}")
        except Exception as e:
            logger.error(f"Error handling WebSocket message from {self.channel_name}: {e}")

    async def stop_alerts(self):
        """Stop sending alerts safely"""
        if self.alert_task and not self.alert_task.done():
            logger.info(f"Stopping alert sequence for {self.channel_name}")
            self.alert_task.cancel()
            try:
                await self.alert_task
            except asyncio.CancelledError:
                logger.info(f"Alert task stopped for {self.channel_name}")
            except Exception as e:
                logger.warning(f"Error stopping alert task for {self.channel_name}: {e}")

        self.sending_alerts = False
        await self.safe_send({
            'type': 'status',
            'message': 'Alert sequence stopped',
            'timestamp': time.time() * 1000
        })

    async def safe_send(self, data):
        """Safely send data with connection state checking"""
        if not self.is_connected:
            logger.debug(f"Attempted to send to disconnected client: {self.channel_name}")
            return False

        try:
            await self.send(text_data=json.dumps(data))
            return True
        except Disconnected:
            logger.warning(f"Client {self.channel_name} disconnected during send")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"Error sending to {self.channel_name}: {e}")
            self.is_connected = False
            return False

    async def send_alerts_sequence(self):
        """Send all alerts from JSON file sequentially with proper error handling"""
        try:
            alerts = await self.load_alerts()

            if not alerts:
                await self.safe_send({
                    'type': 'error',
                    'message': 'No alerts available',
                    'timestamp': time.time() * 1000
                })
                return

            logger.info(f"Sending {len(alerts)} alerts to {self.channel_name}")

            for i, alert in enumerate(alerts):
                # Check if we should stop (client disconnected or stop requested)
                if not self.sending_alerts or not self.is_connected:
                    logger.info(f"Alert sequence stopped for {self.channel_name} at alert {i+1}")
                    break

                try:
                    # Send alert with timestamp for latency calculation
                    alert_data = {
                        'type': 'alert',
                        'title': alert.get('title', f'Alert {i + 1}'),
                        'message': alert.get('message', 'Alert message'),
                        'sequence': i + 1,
                        'total': len(alerts),
                        'alert_id': f"ws_{self.channel_name}_{i}_{int(time.time())}",
                        'timestamp': time.time() * 1000,  # Add timestamp for latency measurement
                        'server_send_time': time.time() * 1000
                    }

                    success = await self.safe_send(alert_data)
                    if not success:
                        logger.warning(f"Failed to send alert {i + 1} to {self.channel_name}")
                        break

                    logger.info(f"Sent alert {i + 1}/{len(alerts)} to {self.channel_name}")

                    # Wait 3 seconds before sending next alert, but check for cancellation
                    try:
                        await asyncio.sleep(3)
                    except asyncio.CancelledError:
                        logger.info(f"Alert sequence cancelled during sleep for {self.channel_name}")
                        break

                except asyncio.CancelledError:
                    logger.info(f"Alert sequence cancelled for {self.channel_name} at alert {i + 1}")
                    break
                except Exception as e:
                    logger.error(f"Error sending alert {i + 1} to {self.channel_name}: {e}")
                    # Continue with next alert instead of breaking

            # Mark as completed only if we finished normally
            if self.sending_alerts and self.is_connected:
                self.sending_alerts = False
                await self.safe_send({
                    'type': 'status',
                    'message': f'All {len(alerts)} alerts sent successfully',
                    'timestamp': time.time() * 1000
                })
                logger.info(f"Alert sequence completed for {self.channel_name}")

        except asyncio.CancelledError:
            logger.info(f"Alert sequence task cancelled for {self.channel_name}")
            self.sending_alerts = False
        except Exception as e:
            logger.error(f"Error in alerts sequence for {self.channel_name}: {e}")
            self.sending_alerts = False
            await self.safe_send({
                'type': 'error',
                'message': f'Error in alert sequence: {str(e)}',
                'timestamp': time.time() * 1000
            })

    @database_sync_to_async
    def load_alerts(self):
        """Load alerts from JSON file"""
        try:
            with open(settings.ALERTS_JSON_FILE, 'r') as file:
                data = json.load(file)
                return data.get('alerts', [])
        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
            return []

    async def send_alert(self, event):
        """Handle alert messages sent to the group (from external sources)"""
        await self.safe_send({
            'type': 'alert',
            'title': event['title'],
            'message': event['message'],
            'data': event.get('data', {}),
            'source': 'group_message',
            'timestamp': time.time() * 1000
        })
