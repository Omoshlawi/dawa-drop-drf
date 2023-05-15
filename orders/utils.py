import requests
import math

ORS_API_KEY = "5b3ce3597851110001cf62489174bcdc8f554d299974dd0047a0e714"


# https://openrouteservice.org/dev/#/home

def get_route_polyline(source, destination):
    # Make a request to the Google Maps Directions API to get the route information
    """url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{source['latitude']},{source['longitude']}",
        "destination": f"{destination['latitude']},{destination['longitude']}",
        "mode": "driving",
        "key": "AIzaSyA0WoecFWukfc9lUgCVcA20W11Eoj49jpo"
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Parse the response to get the polyline information for the route
    polyline = data["routes"][0]["overview_polyline"]["points"]

    return polyline

    :return data = {'error_message': 'This API project is not authorized to use this API.', 'routes': [], 'status': 'REQUEST_DENIED'}
    """
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': '5b3ce3597851110001cf62489174bcdc8f554d299974dd0047a0e714',
        'Content-Type': 'application/json; charset=utf-8'
    }
    body = {"coordinates": [[8.681495, 49.41461], [8.686507, 49.41943], [8.687872, 49.420318]]}
    # url = f'https://api.openrouteservice.org/v2/directions/driving-car?' \
    #       f'api_key={ORS_API_KEY}&start={source["latitude"]},{source["longitude"]}' \
    #       f'&end={destination["latitude"]},{destination["longitude"]}&radiuses=500;500'
    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    data = {
        "coordinates": [
            [float(source["longitude"]), float(source["latitude"])],
            [float(destination["longitude"]), float(destination["latitude"])]
        ],
        "radiuses": [-1]
    }
    response = requests.post(url=url, json=data, headers=headers)
    return response.json()


# Bard
def get_distance_between_coordinates(lat1, lng1, lat2, lng2):
    R = 6371.0088
    dLat = lat2 - lat1
    dLng = lng2 - lng1
    a = math.sin(dLat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dLng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ChartGpt
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    dLat = deg2rad(lat2 - lat1)
    dLon = deg2rad(lon2 - lon1)
    a = (
            math.sin(dLat / 2) * math.sin(dLat / 2) +
            math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) *
            math.sin(dLon / 2) * math.sin(dLon / 2)
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c  # Distance in km
    return d


def deg2rad(deg):
    return deg * (math.pi / 180)


if __name__ == '__main__':
    # get_route_polyline(
    #     {'latitude': 8.681495, 'longitude': 49.41461},
    #     {'latitude': 8.687872, 'longitude': 49.420318}
    # )
    print(calculate_distance(8.681495, 49.41461, 8.687872, 49.420318))
    print(get_distance_between_coordinates(8.681495, 49.41461, 8.687872, 49.420318))
