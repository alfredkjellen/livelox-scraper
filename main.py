from scrape_events import get_event_data
from map_image_handler import download_map_image, clear_temp_maps
from get_coordinates import get_coordinates_from_event 
from get_country import get_country
import firebase_admin
from firebase_admin import credentials, storage, firestore
import os
import json

json_link_Windows = 'C:/firebasekeys/o-guessr-315d061ed6c2.json'
json_link_mac = 'o-guessr-firebase-adminsdk-lx5bw-054e7ff677.json'
json_link = json_link_mac

# Initialisera Firebase app (gör detta endast en gång i din applikation)
cred = credentials.Certificate(json_link)

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


def save_map_to_firestore(map_id, coordinates):
    map_ref = db.collection('maps').document(map_id)
    map_ref.set({
        'coordinates': coordinates
    })

def get_map_from_firestore(map_id):
    map_ref = db.collection('maps').document(map_id)
    doc = map_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None



def store_map(image_path):
        firebase_image_path = f"maps/{os.path.basename(image_path)}"
        upload_image_to_firebase(image_path, firebase_image_path)


def run(url):
    ids, links = get_event_data(url)
    print(f"{len(ids)} events found")
    
    map_count = 0

    new_map_data = []
    
    if len(ids) > 0:
        for id, link in zip(ids, links):
            image_path = download_map_image(id)
            if image_path:
                coordinates = get_coordinates_from_event(link)
                if coordinates:
                    store_map(image_path)
                    country = get_country(coordinates)
                    map_object = [id, coordinates, country] # {"id": id, "coordinates":coordinates, "country":country}
                    new_map_data.append(map_object)
                    map_count += 1


    path_to_svelte_project = '/Users/alfred.kjellen/Desktop/VisualStudioCodeProjekt/o-guessr-game/src/lib/ids.json'
    all_map_data = load_list(path_to_svelte_project)
    all_map_data.extend(new_map_data)
    save_list(path_to_svelte_project, all_map_data)

    print(f"{map_count} maps uploaded")

    clear_temp_maps()


def load_list(filename):
    if os.path.getsize(filename) == 0:
        return []
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_list(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)


url = "https://www.livelox.com/?tab=allEvents&timePeriod=pastWeek&country=USA&sorting=time"
run(url)