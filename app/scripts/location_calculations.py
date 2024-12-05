from rijksdriehoek import rijksdriehoek
from geopy.distance import geodesic

def get_GPS_from_RD(x, y):
    rd = rijksdriehoek.Rijksdriehoek()
    rd.rd_x = float(x)
    rd.rd_y = float(y)
    lat,lon = rd.to_wgs()
    return lat, lon

def get_closest_point(target, points):
    closest_point = None
    min_distance = 9999999
    for point in points:
        coord = (point['latitude'], point['longtitude'])
        if geodesic(target, coord).km < min_distance:
            closest_point = point
            min_distance = geodesic(target, coord).km
    return closest_point, min_distance