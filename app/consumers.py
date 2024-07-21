from django.template.loader import render_to_string

from app import mediator
from app.models import Chat, ChatHistory, UserProfile

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

import json


class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_chat(self):
        uuid = str(self.room_name) 
        if Chat.objects.filter(uuid=uuid).exists():
            return Chat.objects.get(uuid=uuid)
        else:
            return None

    @database_sync_to_async
    def save_chat_message(self, message, is_llm=False):
        if is_llm == True:
            saved_message = ChatHistory.objects.create(chat=self.chat, message=message, is_llm=True)
        else:
            saved_message = ChatHistory.objects.create(chat=self.chat, sent_by=self.scope["user"], message=message)
        return saved_message
                
    @database_sync_to_async
    def get_user_profile(self):
        if UserProfile.objects.filter(user = self.scope["user"]).exists():
            return UserProfile.objects.get(user = self.scope["user"])
        else:
            return None
    
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.chat = await self.get_chat()
        self.room_group_name = f"chat_{self.room_name}"
        self.user_profile = await self.get_user_profile()

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["chat_message"]

        saved_message = await self.save_chat_message(message)
        html = render_to_string("chat-message.html", {"user":self.scope["user"], "user_profile":self.user_profile, "message":saved_message})

        # Send message with message-out class (for sender)
        await self.send(text_data=html)

        if self.chat.is_caucus == False:
            # Send message to room group
            # chat.message calls the chat_message method. The translation is done by replacing . with _
            # https://channels.readthedocs.io/en/latest/tutorial/part_2.html

            # Remove message-out class (for receivers)
            html = html.replace("message-out","")
            await self.channel_layer.group_send(
                self.room_group_name, {"type":"chat.message", "message":html, "sender_channel_name":self.channel_name}
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        # We only send each other's messages to the group
        if self.channel_name != event['sender_channel_name']:
            await self.send(text_data=message)

    # Receive message from Mediator
    async def chat_mediator(self, event):
        message = event["chat_message"]
        sender_user_id = event["sender_user_id"]

        if self.scope["user"].id == sender_user_id:
            saved_message = await self.save_chat_message(message, is_llm=True)
            html = render_to_string("mediator_message.html", {"message":saved_message})
            await self.channel_layer.group_send(self.room_group_name, {"type":"chat.message", "message":html, "sender_channel_name":self.channel_name + "-1234"})
