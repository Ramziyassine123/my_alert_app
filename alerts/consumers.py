# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("alerts", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the alerts group
        await self.channel_layer.group_discard("alerts", self.channel_name)

    async def send_alert(self, event):
        # Send alert message to WebSocket
        await self.send(text_data=json.dumps({
            'title': event['title'],
            'message': event['message'],
            'period': event['period'],
        }))
