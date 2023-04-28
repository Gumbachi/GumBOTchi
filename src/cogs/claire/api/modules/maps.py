import requests
import urllib.parse

def get_lat_lon(zip_code: int):
    loc = urllib.parse.quote(str(zip_code))
    url = f'https://nominatim.openstreetmap.org/search/{loc}?format=json'

    response = requests.get(url).json()
    if response[0]:
        lat = response[0].get("lat")
        lon = response[0].get("lon")
    return lat, lon