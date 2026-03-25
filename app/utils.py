from geopy.distance import geodesic


def calculate_distance(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
    unit: str = "km",
) -> float:
    """Calculate the geodesic distance between two coordinate pairs."""
    distance = geodesic((latitude_1, longitude_1), (latitude_2, longitude_2))
    return distance.kilometers if unit == "km" else distance.miles
