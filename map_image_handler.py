import requests
import os
import shutil

import cv2
import pytesseract
import numpy as np



def download_map_image(id):
    session = requests.Session()
    download_url = f"https://www.livelox.com/Classes/MapImage?classIds={id}&fileFormat=png&includeCoursePrint=false&download=true"
    download_response = session.get(download_url)
    
    if download_response.status_code == 200:
        content_type = download_response.headers.get('Content-Type', '')
        if 'image' in content_type:
            filename = f"{id}.png"
            filepath = os.path.join('temp_maps', filename)  # Spara i en temporär mapp
            os.makedirs('temp_maps', exist_ok=True)  # Skapa mappen om den inte finns
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
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            print(f"Temporär mapp '{temp_dir}' har rensats.")
        except Exception as e:
            print(f"Ett fel uppstod vid rensning av '{temp_dir}': {e}")
    else:
        print(f"Temporär mapp '{temp_dir}' existerar inte.")



# Ladda bilden
image = cv2.imread('maps_811966.png')

# Konvertera bilden till gråskala
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Använd pytesseract för att hitta textområden
detection = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

# Gå igenom alla upptäckta textområden
n_boxes = len(detection['level'])
for i in range(n_boxes):
    (x, y, w, h) = (detection['left'][i], detection['top'][i], detection['width'][i], detection['height'][i])
    
    # Fyll textområdena med vitt eller en annan bakgrundsfärg
    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)

# Spara bilden utan text
cv2.imwrite('bild_utan_text.png', image)
