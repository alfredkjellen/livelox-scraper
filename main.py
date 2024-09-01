import firebase_admin
from firebase_admin import credentials, storage, firestore
import os
import json
import reverse_geocoder as rg
import requests
from scrape_events import get_event_data
from scrape_coordinates import get_coordinates 

import requests
from firebase_admin import storage
from requests.exceptions import RequestException

json_link_Windows = 'C:/firebasekeys/o-guessr-315d061ed6c2.json'
json_link_mac = 'o-guessr-firebase-adminsdk-lx5bw-054e7ff677.json'
json_link = json_link_mac
cred = credentials.Certificate(json_link)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'o-guessr.appspot.com'
})
db = firestore.client()

def run(url, max_amount=5):
    ids, links = get_event_data(url)
    print(f"{len(ids)} events found")
    map_count = 0
    new_map_data = []
    
    if len(ids) > 0:
        for id, link in zip(ids, links):
            if map_count < max_amount:
                try:
                    if upload_map(id):
                        coordinates = get_coordinates(link)
                        if coordinates is not None:
                            country = get_country(coordinates)
                            map_object = {"id": id, "coordinates": coordinates, "country": country}
                            new_map_data.append(map_object)
                            map_count += 1
                        else:
                            print(f"Failed to get coordinates for map {id}")
                except Exception as e:
                    print(f"Error processing map {id}: {str(e)}")
            else:
                break
        
    path_to_svelte_project = '/Users/alfred.kjellen/Desktop/VisualStudioCodeProjekt/o-guessr-game/src/lib/ids.json'
    all_map_data = load_list(path_to_svelte_project)
    all_map_data.extend(new_map_data)
    save_list(path_to_svelte_project, all_map_data)
    print(f"{map_count} maps saved")


def upload_map(id):
    session = requests.Session()
    download_url = f"https://www.livelox.com/Classes/MapImage?classIds={id}&fileFormat=png&includeCoursePrint=false&download=true"
    try:
        download_response = session.get(download_url, timeout=30)
        download_response.raise_for_status()
        content_type = download_response.headers.get('Content-Type', '')
        if 'image' in content_type:
            save_to_firestore(id, download_response.content, content_type)
            return True
        else:
            print(f"Received non-image content type for map {id}")
            return False
    except RequestException as e:
        print(f"Failed to download map {id}: {str(e)}")
        return False

def save_to_firestore(id, content, content_type):
    bucket = storage.bucket()
    blob = bucket.blob(f"maps/{id}.png")
    try:
        blob.upload_from_string(content, content_type=content_type)
        print(f"Successfully uploaded map {id}")
    except Exception as e:
        print(f"Failed to upload map {id} to Firestore: {str(e)}")
        raise

def get_country(coordinates):
    result = rg.search((coordinates[0], coordinates[1]))
    return result[0]['cc']

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

        
if __name__ == "__main__":
    run("https://www.livelox.com/?tab=allEvents&timePeriod=pastWeek&country=SWE&sorting=time")
    