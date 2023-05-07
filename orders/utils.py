import requests

ORS_API_KEY = "5b3ce3597851110001cf62489174bcdc8f554d299974dd0047a0e714"


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


if __name__ == '__main__':
    get_route_polyline(
        {'latitude': 8.681495, 'longitude': 49.41461},
        {'latitude': 8.687872, 'longitude': 49.420318}
    )
