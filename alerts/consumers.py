# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'alerts'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"Client connected: {self.channel_name}")

    async def disconnect(self, close_code):
        # Leave the alerts group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"Client disconnected: {self.channel_name}")

    async def send_alert(self, event):
        title = event['title']
        message = event['message']
        period = event['period']
        # Send alert message to WebSocket
        await self.send(text_data=json.dumps({
            'title': title,
            'message': message,
            'period': period,
        }))
