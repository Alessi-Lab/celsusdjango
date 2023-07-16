import json

from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer


class CurtainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.personal_id = self.scope['url_route']['kwargs']['personal_id']
        await self.channel_layer.group_add(self.session_id, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.session_id, self.channel_name)
        pass

    async def receive(self, text_data, **kwargs):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.session_id,
            {
                'type': 'chat_message',
                'message': {
                    'message': data['message'],
                    'requestType': data['requestType'],
                    'senderName': data['senderName']
                }
            }
        )

    async def chat_message(self, event):
        data = event['message']
        await self.send(text_data=json.dumps({
            'message': data['message'],
            'senderID': self.personal_id,
            'senderName': data['senderName'],
            'requestType': data['requestType']
        }))



