from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/delivery/(?P<trip_id>\d+)/$', consumers.AsyncTripConsumer.as_asgi()),
    # re_path(r'ws/trip/(?P<trip_id>\d+)/$', consumers.TripConsumer.as_asgi()),
]