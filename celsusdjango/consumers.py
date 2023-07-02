import json

from channels.generic.websocket import AsyncWebsocketConsumer

class CurtainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.personal_id = self.scope['url_route']['kwargs']['personal_id']
        await self.channel_layer.group_add(self.session_id, self.personal_id)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.session_id, self.personal_id)
        pass

    async def receive(self, text_data, **kwargs):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.session_id,
            {
                'type': 'chat.message',
                'message': data['message']
            }
        )

    async def chat_message(self, event):
        message = event['message']
        print(message)
        await self.send(text_data=json.dumps({
            'message': message
        }))



