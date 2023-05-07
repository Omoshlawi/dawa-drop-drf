import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

"""
Channel is like a pipe with two ends server and client that handle duplex communication 
between server and client.

Group is like a collection of channels that are to be brodcasted to

Layers are used for scalability to enable multiple connection with same state(in sync)

"""


class TripConsumer(WebsocketConsumer):
    def connect(self):
        self.id = self.scope['url_route']['kwargs']['trip_id']
        self.trip_group_name = 'Trip_%s' % self.id

        # join trip group
        async_to_sync(self.channel_layer.group_add)(
            self.trip_group_name,
            self.channel_name
        )

        # accept
        self.accept()
        # reject
        # self.close()

    def disconnect(self, close_code):
        # leave trip group
        async_to_sync(self.channel_layer.group_discard)(
            self.trip_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # send message to trip group
        """
        type: The event type. This is a special key that corresponds to the name of 
            the method that should be invoked on consumers that receive the event. You 
            can implement a method in the consumer named the same as the message 
            type so that it gets executed every time a message with that specific type is 
            received.
        message: The actual message you are sending.
        """
        async_to_sync(self.channel_layer.group_send)(
            self.trip_group_name,
            {
                'type': 'trip_tracking_info',
                'message': text_data,
            }
        )

        # message = text_data_json["message"]
        # print(text_data)
        # self.send(text_data=json.dumps(text_data_json))

        # receive message from room group

    def trip_tracking_info(self, event):
        """
        You name this method trip_tracking_info() to match the type key that is sent to the
        channel group when a message is received from the WebSocket. When a message
        with type trip_tracking_info is sent to the group, all consumers subscribed to the group
        will receive the message and will execute the trip_tracking_info() method. In the chat_
        message() method, you send the event message received to the WebSocket
        """
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))

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
