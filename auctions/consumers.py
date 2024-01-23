import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone
from .models import Messages
from django.contrib.auth import get_user_model



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Create and connect users in private room
        self.user = self.scope['user']
        self.user_id = int(self.scope['user'].id)
        print("THIS IS THE  USER:", self.user_id)

        other_user_id = int(self.scope['url_route']['kwargs']['id'])
        print("THIS IS THE OTHER USER:", other_user_id)
        self.room_group_name = f'private_chat_{min(self.user_id, other_user_id)}_{max(self.user_id, other_user_id)}'
      
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data=None, bytes_data=None):
        sender_username = ''  
        try:
            text_data_json = json.loads(text_data)
            print("Data received:", text_data_json)
            sender_username = text_data_json.get('SenderUsername', " ")
            sender = await self.get_user(sender_username.replace('"', ''))
            message = text_data_json.get('message', '')
            now = timezone.now()
            timestamp = now
            await self.save_message(sender=sender, message=message, thread_name=self.room_group_name, timestamp=timestamp)

            messages = await self.get_messages()
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except KeyError as e:
            print(f"KeyError: {e}")

        await(self.channel_layer.group_send)(
        self.room_group_name,
          {
            'type': 'chat_message',
            'message': message,
            'SenderUsername':sender_username,
            'messages': messages,
            'datetime' : timestamp     
          }       
        )

    async def chat_message(self, event):
        # Sends message to websocket
        message  = event['message']
        username = event['SenderUsername']
        messages = event['messages']
       

        await self.send(text_data=json.dumps({
            'message': message,
            'senderUsername': username,
            'messages': messages,  
        }))

    @database_sync_to_async
    def get_user(self, username):
        return get_user_model().objects.filter(username=username).first()
    
    @database_sync_to_async
    def get_messages(self):
        messages = Messages.objects.filter(thread_name=self.room_group_name).select_related(
            'sendear'
        ).values(
            'sender__pk',
            'sender__username',
            'sender__last_name',
            'sender__first_name',
            'sender__email',
            'sender__last_login',
            'sender__is_staff',
            'sender__is_active',
            'sender__date_joined',
            'sender__is_superuser',
            'message',
            'thread_name',
            'timestamp',
        )
        return (messages)
    
    @database_sync_to_async
    def save_message(self, sender, message, thread_name, timestamp):
        print("Saving message:", sender, message, thread_name, timestamp)
        Messages.objects.create(sender=sender, message=message, thread_name=thread_name, timestamp=timestamp)
