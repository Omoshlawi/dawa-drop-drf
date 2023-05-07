import json

from channels.generic.websocket import WebsocketConsumer


class TripConsumer(WebsocketConsumer):
    def connect(self):
        # accept
        self.accept()
        # reject
        # self.close()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # message = text_data_json["message"]
        print(text_data)
        self.send(text_data=json.dumps(text_data_json))

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
#
# class TripConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.trip_id = self.scope['url_route']['kwargs']['trip_id']
#         self.room_group_name = f'trip_{self.trip_id}'
#
#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['name']
#
#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'echo_message',
#                 'message': message
#             }
#         )
#
#     async def echo_message(self, event):
#         message = event['message']
#
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))
