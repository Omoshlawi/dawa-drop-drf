import json

from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

"""
Channel is like a pipe with two ends server and client that handle duplex communication 
between server and client.

Group is like a collection of channels that are to be brodcasted to

Layers are used for scalability to enable multiple connection with same state(in sync)

"""


class TripConsumer(WebsocketConsumer):
    """
    Synchronous consumers are convenient because they can call regular synchronous
    I/O functions such as those that access Django models without writing special code.
    """

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


class AsyncTripConsumer(AsyncWebsocketConsumer):
    """
    Very similar to above except for it is asynchronous
     if AsyncTripConsumer did access Django models or other synchronous code it
     would still be possible to rewrite it as asynchronous.
     Utilities like asgiref.sync.sync_to_async and channels.db.database_sync_to_async
     can be used to call synchronous code from an asynchronous consumer.
     The performance gains however would be less than if it only used async-native libraries.

     https://channels.readthedocs.io/en/stable/topics/databases.html
     NB: ADD IT AS A METHOD DECORATED IN THIS CLASS OR JUST PASS ITS REFERENCE TO DB ASYNC,
     IMPORTANT THING IS TO INCLUDE IT AS A METHOD T
    """

    async def connect(self):
        self.id = self.scope['url_route']['kwargs']['trip_id']
        self.trip_group_name = 'Trip_%s' % self.id
        self.user = self.scope['user']
        print(self.user)

        # Join room group
        await self.channel_layer.group_add(self.trip_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.trip_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        # text_data_json = json.loads(text_data)
        # message = text_data_json["message"]

        """
        NB: The dictionary can contain any keys and values that the developer wants to
        pass to the group.
        However, the type key is commonly used in Channels to specify the type of
        message being sent. This key is not predefined, but it is a common convention
        to use it to indicate the type of the message being sent, so that the
        appropriate handler function can be called on the receiving end. In this
        case, the type key is set to 'trip_tracking_info' to indicate that the message
        is related to trip tracking information.

        eg:
            {
                'my_type': 'trip_tracking_info',
                'message': text_data,
             }
             Then, you would need to use the same key name 'my_type' when you
             handle the message in the consumers or in the routing code.
        """
        # Send message to room group
        await self.channel_layer.group_send(
            self.trip_group_name,
            {
                'type': 'trip_tracking_info',
                'info': text_data,
            }
        )

    # Receive message from room group
    async def trip_tracking_info(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))
