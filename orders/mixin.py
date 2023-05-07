from rest_framework.decorators import action
from rest_framework.response import Response

from orders.utils import get_route_polyline


class RouteMixin:
    @action(detail=True)
    def route(self, request, *args, **kwargs):
        trip = self.get_object()
        serializer = self.get_serializer(instance=trip, context={'request': self.request})
        data = serializer.data
        source = data["current_location"]
        destination = data["destination"]
        geojson = get_route_polyline(
            source, destination
            # {'latitude': 8.681495, 'longitude': 49.41461},
            # {'latitude': 8.687872, 'longitude': 49.420318}
        )
        return Response(data=geojson)
