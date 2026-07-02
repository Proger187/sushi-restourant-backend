import math


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def estimate_minutes(distance_km: float) -> int:
    if distance_km <= 2:
        return 25
    elif distance_km <= 4:
        return 35
    elif distance_km <= 6:
        return 45
    elif distance_km <= 8:
        return 55
    return 65
