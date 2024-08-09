from scrape_events import get_event_data
from map_image_handler import download_map_image, clear_temp_maps
from get_coordinates import get_coordinates_from_event 

import firebase_admin
from firebase_admin import credentials, storage, firestore
import os

# Initialisera Firebase app (gör detta endast en gång i din applikation)
cred = credentials.Certificate("C:/firebasekeys/o-guessr-315d061ed6c2.json")

firebase_admin.initialize_app(cred, {
    'storageBucket': 'o-guessr.appspot.com'
})


db = firestore.client()

def upload_image_to_firebase(local_image_path, firebase_image_path):
    bucket = storage.bucket()
    blob = bucket.blob(firebase_image_path)
    
    blob.upload_from_filename(local_image_path)
    
    # Gör URL:en offentligt tillgänglig
    blob.make_public()
    
    # Returnera den offentliga URL:en
    return blob.public_url

# Ersätt save_map_to_datastore funktionen med:
def save_map_to_firestore(map_id, image_url, coordinates):
    map_ref = db.collection('maps').document(map_id)
    map_ref.set({
        'image_url': image_url,
        'coordinates': coordinates
    })

# Ersätt get_map_from_datastore funktionen med:
def get_map_from_firestore(map_id):
    map_ref = db.collection('maps').document(map_id)
    doc = map_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None


# Exempel på användning i din Map-klass
class Map:
    id:str
    image_url: str
    coordinates: str

    def __init__(self, id, image_path, coordinates):
        self.id = id
        self.coordinates = coordinates

        firebase_image_path = f"maps/{os.path.basename(image_path)}"
        self.image_url = upload_image_to_firebase(image_path, firebase_image_path)
        save_map_to_firestore(self.id, self.image_url, self.coordinates)

def run(url):
    ids, links = get_event_data(url)
    print(f"{len(ids)} events found")
    
    map_count = 0
    
    if len(ids) > 0:
        for id, link in zip(ids, links):
            image_path = download_map_image(id)
            if image_path:
                coordinates = get_coordinates_from_event(link)
                if coordinates:
                    new_map = Map(id, image_path, coordinates)
                    map_count += 1
                    print(f"Karta uppladdad och sparad: {new_map.image_url}")
    
    print(f"{map_count} maps uploaded")

    clear_temp_maps()




url = "https://www.livelox.com/?tab=allEvents&timePeriod=pastWeek&country=AUS&sorting=time"
run(url)


