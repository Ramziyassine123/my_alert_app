"""
Enhanced WebSocket consumers for real-time alert delivery with delivery confirmation
"""
import json
import asyncio
import time
import uuid
import psutil
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
import logging
from autobahn.exception import Disconnected

logger = logging.getLogger(__name__)


class RealTimeWebSocketMetrics:
    """Real-time WebSocket performance metrics collection"""

    def __init__(self):
        self.connection_times = []
        self.message_latencies = []
        self.ping_latencies = []
        self.memory_usage = []
        self.cpu_usage = []
        self.bytes_sent = 0
        self.bytes_received = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.connections_count = 0
        self.errors_count = 0
        self.reconnections_count = 0
        self.start_time = time.time()

    def record_connection(self, connection_time_ms):
        """Record connection establishment time"""
        self.connection_times.append(connection_time_ms)
        self.connections_count += 1

    def record_ping_latency(self, latency_ms):
        """Record ping-pong latency"""
        self.ping_latencies.append(latency_ms)

    def record_message_latency(self, latency_ms):
        """Record message processing latency"""
        self.message_latencies.append(latency_ms)

    def record_data_transfer(self, bytes_sent=0, bytes_received=0):
        """Record data transfer"""
        self.bytes_sent += bytes_sent
        self.bytes_received += bytes_received

    def record_message_activity(self, sent=False, received=False):
        """Record message activity"""
        if sent:
            self.messages_sent += 1
        if received:
            self.messages_received += 1

    def record_system_metrics(self):
        """Record current system metrics"""
        try:
            process = psutil.Process(os.getpid())
            self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
            self.cpu_usage.append(process.cpu_percent())
        except:
            pass  # In case psutil fails

    def get_real_metrics(self):
        """Get comprehensive real-time metrics"""
        duration = time.time() - self.start_time

        import statistics

        return {
            'connection_time_ms': statistics.mean(self.connection_times) if self.connection_times else 0,
            'message_latency_ms': statistics.mean(self.message_latencies) if self.message_latencies else 0,
            'ping_latency_ms': statistics.mean(self.ping_latencies) if self.ping_latencies else 0,
            'latency_min_ms': min(self.message_latencies) if self.message_latencies else 0,
            'latency_max_ms': max(self.message_latencies) if self.message_latencies else 0,
            'latency_p95_ms': self._percentile(self.message_latencies, 95) if self.message_latencies else 0,
            'throughput_msg_per_sec': self.messages_sent / duration if duration > 0 else 0,
            'success_rate_percent': ((self.messages_sent - self.errors_count) / max(self.messages_sent, 1)) * 100,
            'memory_usage_mb': statistics.mean(self.memory_usage) if self.memory_usage else 0,
            'cpu_usage_percent': statistics.mean(self.cpu_usage) if self.cpu_usage else 0,
            'network_bytes_sent': self.bytes_sent,
            'network_bytes_received': self.bytes_received,
            'error_rate_percent': (self.errors_count / max(self.messages_sent, 1)) * 100,
            'reconnection_count': self.reconnections_count,
            'active_connections': self.connections_count,
            'total_messages_sent': self.messages_sent,
            'total_messages_received': self.messages_received
        }

    def _percentile(self, data, percentile):
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))


# Global metrics instance
websocket_metrics = RealTimeWebSocketMetrics()


class AlertConsumer(AsyncWebsocketConsumer):
    """Enhanced WebSocket consumer with delivery confirmation and performance tracking"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sending_alerts = False
        self.alert_task = None
        self.is_connected = False
        self.connection_start_time = None
        self.pending_confirmations = {}  # Track message confirmations
        self.client_metrics = {}

    async def connect(self):
        """Handle WebSocket connection with enhanced performance measurement"""
        self.connection_start_time = time.time()
        self.group_name = 'alerts'
        self.is_connected = True

        # Join the alerts group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # Calculate real connection time
        connection_time = (time.time() - self.connection_start_time) * 1000
        websocket_metrics.record_connection(connection_time)
        websocket_metrics.record_system_metrics()

        logger.info(f"Enhanced WebSocket client connected: {self.channel_name} in {connection_time:.2f}ms")

        # Send enhanced welcome message
        await self.safe_send({
            'type': 'status',
            'message': 'Connected to Enhanced Alert Server',
            'connection_time_ms': connection_time,
            'server_timestamp': time.time() * 1000,
            'enhanced_features': [
                'delivery_confirmation',
                'performance_tracking',
                'unlimited_scaling'
            ]
        })

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection with cleanup"""
        self.is_connected = False
        websocket_metrics.connections_count -= 1

        # Cancel any running alert task
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
        self.pending_confirmations.clear()

        # Leave the alerts group
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except Exception as e:
            logger.warning(f"Error leaving group for {self.channel_name}: {e}")

        logger.info(f"Enhanced WebSocket client disconnected: {self.channel_name} (code: {close_code})")

    async def receive(self, text_data):
        """Handle messages with enhanced features and delivery confirmation"""
        receive_time = time.time() * 1000

        if not self.is_connected:
            logger.warning(f"Received message on disconnected client: {self.channel_name}")
            return

        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            # Record data received
            websocket_metrics.record_data_transfer(bytes_received=len(text_data.encode()))
            websocket_metrics.record_message_activity(received=True)

            if message_type == 'start_alerts':
                # Enhanced alert start with delivery confirmation support
                client_timestamp = data.get('timestamp')
                requires_confirmation = data.get('requires_confirmation', False)
                message_id = data.get('message_id')

                if client_timestamp:
                    processing_latency = receive_time - client_timestamp
                    websocket_metrics.record_message_latency(processing_latency)
                    logger.debug(f"Message processing latency: {processing_latency:.2f}ms")

                # Send confirmation that we received the request
                if requires_confirmation and message_id:
                    await self.safe_send({
                        'type': 'delivery_confirmation',
                        'message_id': message_id,
                        'confirmed_at': time.time() * 1000,
                        'confirmation_type': 'request_received'
                    })

                if not self.sending_alerts:
                    logger.info(f"Starting enhanced alert sequence for {self.channel_name}")
                    self.sending_alerts = True
                    self.alert_task = asyncio.create_task(
                        self.send_enhanced_alerts_sequence(requires_confirmation),
                        name=f"enhanced_alerts_{self.channel_name}"
                    )
                else:
                    await self.safe_send({
                        'type': 'status',
                        'message': 'Enhanced alert sequence already running',
                        'server_timestamp': receive_time
                    })

            elif message_type == 'delivery_confirmation':
                # Handle delivery confirmation from client
                await self.handle_delivery_confirmation(data)

            elif message_type == 'stop_alerts':
                await self.stop_alerts()

            elif message_type == 'ping':
                # Enhanced ping handling with detailed timing
                ping_id = data.get('ping_id', 'unknown')
                client_timestamp = data.get('timestamp')

                response_data = {
                    'type': 'pong',
                    'ping_id': ping_id,
                    'client_timestamp': client_timestamp,
                    'server_receive_timestamp': receive_time,
                    'server_send_timestamp': time.time() * 1000,
                    'server_processing_time_ms': time.time() * 1000 - receive_time
                }

                await self.safe_send(response_data)

                # Record ping metrics
                if client_timestamp:
                    ping_latency = receive_time - client_timestamp
                    websocket_metrics.record_ping_latency(ping_latency)
                    logger.debug(f"Enhanced ping latency: {ping_latency:.2f}ms")

            elif message_type == 'performance_request':
                # Send current performance metrics
                await self.send_performance_metrics()

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from WebSocket client {self.channel_name}")
            websocket_metrics.errors_count += 1
        except Exception as e:
            logger.error(f"Error handling enhanced WebSocket message from {self.channel_name}: {e}")
            websocket_metrics.errors_count += 1

    async def handle_delivery_confirmation(self, data):
        """Handle delivery confirmation from client"""
        message_id = data.get('message_id')
        if message_id in self.pending_confirmations:
            confirmation_time = time.time() * 1000
            send_time = self.pending_confirmations[message_id]
            delivery_latency = confirmation_time - send_time

            logger.info(f"Enhanced delivery confirmed: {message_id} in {delivery_latency:.2f}ms")

            # Record successful delivery
            websocket_metrics.record_message_latency(delivery_latency)

            # Remove from pending
            del self.pending_confirmations[message_id]

    async def stop_alerts(self):
        """Stop sending alerts safely"""
        if self.alert_task and not self.alert_task.done():
            logger.info(f"Stopping enhanced alert sequence for {self.channel_name}")
            self.alert_task.cancel()
            try:
                await self.alert_task
            except asyncio.CancelledError:
                logger.info(f"Enhanced alert task stopped for {self.channel_name}")
            except Exception as e:
                logger.warning(f"Error stopping enhanced alert task for {self.channel_name}: {e}")

        self.sending_alerts = False
        self.pending_confirmations.clear()

        await self.safe_send({
            'type': 'status',
            'message': 'Enhanced alert sequence stopped',
            'server_timestamp': time.time() * 1000
        })

    async def safe_send(self, data):
        """Safely send data with enhanced connection state checking and metrics"""
        if not self.is_connected:
            logger.debug(f"Attempted to send to disconnected client: {self.channel_name}")
            return False

        try:
            message_json = json.dumps(data)
            await self.send(text_data=message_json)

            # Record enhanced metrics
            websocket_metrics.record_data_transfer(bytes_sent=len(message_json.encode()))
            websocket_metrics.record_message_activity(sent=True)
            websocket_metrics.record_system_metrics()

            return True
        except Disconnected:
            logger.warning(f"Client {self.channel_name} disconnected during send")
            self.is_connected = False
            websocket_metrics.reconnections_count += 1
            return False
        except Exception as e:
            logger.error(f"Error sending to {self.channel_name}: {e}")
            self.is_connected = False
            websocket_metrics.errors_count += 1
            return False

    async def send_enhanced_alerts_sequence(self, requires_confirmation=False):
        """Send alerts with enhanced delivery confirmation and performance tracking"""
        try:
            alerts = await self.load_alerts()

            if not alerts:
                await self.safe_send({
                    'type': 'error',
                    'message': 'No alerts available',
                    'server_timestamp': time.time() * 1000
                })
                return

            logger.info(f"Sending {len(alerts)} enhanced alerts to {self.channel_name}")

            for i, alert in enumerate(alerts):
                if not self.sending_alerts or not self.is_connected:
                    logger.info(f"Enhanced alert sequence stopped for {self.channel_name} at alert {i+1}")
                    break

                try:
                    # Generate unique message ID for tracking
                    message_id = str(uuid.uuid4())
                    send_timestamp = time.time() * 1000

                    alert_data = {
                        'type': 'alert',
                        'title': alert.get('title', f'Alert {i + 1}'),
                        'message': alert.get('message', 'Enhanced alert message'),
                        'sequence': i + 1,
                        'total': len(alerts),
                        'alert_id': f"enhanced_ws_{self.channel_name}_{i}_{int(time.time())}",
                        'message_id': message_id,
                        'server_send_timestamp': send_timestamp,
                        'alert_index': i,
                        'requires_confirmation': requires_confirmation,
                        'enhanced_features': True
                    }

                    # Track for confirmation if required
                    if requires_confirmation:
                        self.pending_confirmations[message_id] = send_timestamp

                    success = await self.safe_send(alert_data)
                    if not success:
                        logger.warning(f"Failed to send enhanced alert {i + 1} to {self.channel_name}")
                        break

                    logger.info(f"Sent enhanced alert {i + 1}/{len(alerts)} to {self.channel_name}")

                    # Wait with cancellation check
                    try:
                        await asyncio.sleep(3)
                    except asyncio.CancelledError:
                        logger.info(f"Enhanced alert sequence cancelled during sleep for {self.channel_name}")
                        break

                except asyncio.CancelledError:
                    logger.info(f"Enhanced alert sequence cancelled for {self.channel_name} at alert {i + 1}")
                    break
                except Exception as e:
                    logger.error(f"Error sending enhanced alert {i + 1} to {self.channel_name}: {e}")
                    websocket_metrics.errors_count += 1

            # Mark as completed
            if self.sending_alerts and self.is_connected:
                self.sending_alerts = False
                await self.safe_send({
                    'type': 'status',
                    'message': f'All {len(alerts)} enhanced alerts sent successfully',
                    'server_timestamp': time.time() * 1000,
                    'total_alerts_sent': len(alerts),
                    'pending_confirmations': len(self.pending_confirmations)
                })
                logger.info(f"Enhanced alert sequence completed for {self.channel_name}")

        except asyncio.CancelledError:
            logger.info(f"Enhanced alert sequence task cancelled for {self.channel_name}")
            self.sending_alerts = False
        except Exception as e:
            logger.error(f"Error in enhanced alerts sequence for {self.channel_name}: {e}")
            self.sending_alerts = False
            websocket_metrics.errors_count += 1
            await self.safe_send({
                'type': 'error',
                'message': f'Error in enhanced alert sequence: {str(e)}',
                'server_timestamp': time.time() * 1000
            })

    async def send_performance_metrics(self):
        """Send current enhanced WebSocket performance metrics"""
        try:
            metrics = websocket_metrics.get_real_metrics()

            await self.safe_send({
                'type': 'performance_metrics',
                'technology': 'enhanced_websocket',
                'metrics': metrics,
                'server_timestamp': time.time() * 1000,
                'client_channel': self.channel_name,
                'enhanced_features': True
            })
        except Exception as e:
            logger.error(f"Error sending enhanced performance metrics: {e}")

    @database_sync_to_async
    def load_alerts(self):
        """Load alerts from JSON file"""
        try:
            alerts_file = getattr(settings, 'ALERTS_JSON_FILE', 'alerts.json')
            with open(alerts_file, 'r') as file:
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
            'server_timestamp': time.time() * 1000,
            'enhanced_features': True
        })
