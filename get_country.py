import reverse_geocoder as rg

def get_country(lat, lon):
    result = rg.search((lat, lon))
    return result[0]['cc']


