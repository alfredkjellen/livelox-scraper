import requests
import os
import shutil


def download_map_image(id):
    session = requests.Session()
    download_url = f"https://www.livelox.com/Classes/MapImage?classIds={id}&fileFormat=png&includeCoursePrint=false&download=true"
    download_response = session.get(download_url)
    
    if download_response.status_code == 200:
        content_type = download_response.headers.get('Content-Type', '')
        if 'image' in content_type:
            filename = f"{id}.png"
            filepath = os.path.join('temp_maps', filename)  # Spara i en temporär mapp
            os.makedirs('temp_maps', exist_ok=True)  
            with open(filepath, 'wb') as f:
                f.write(download_response.content)
            print(f"Karta nedladdad och sparad som: {filepath}")
            return filepath
        else:
            print(f"Ogiltig innehållstyp för nedladdad fil: {content_type}")
    else:
        print(f"Kunde inte ladda ner kartan för class ID: {id}")
    
    return None

def clear_temp_maps():
    temp_dir = 'temp_maps'

    try:
        shutil.rmtree(temp_dir)
        print(f"Deleted temporary folder'{temp_dir}'")
    except Exception as e:
        print(f"An error occurred while deleting'{temp_dir}': {e}")
