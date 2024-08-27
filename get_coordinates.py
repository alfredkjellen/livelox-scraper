from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from scrape_events import accept_cookies

def convert_coordinates(dms_str):
    def convert_to_decimal(degrees, minutes, seconds, direction):
        decimal = degrees + minutes/60 + seconds/3600
        if direction in ['S', 'W']:
            decimal *= -1
        return decimal

    # Dela upp strängen i latitud och longitud delar
    lat_str, lon_str = dms_str.split(" ")
    
    # Extrahera grader, minuter, sekunder och riktning för latitud
    lat_deg = int(lat_str[:-1].split("°")[0])
    lat_min = int(lat_str[:-1].split("°")[1].split("'")[0])
    lat_sec = float(lat_str[:-1].split("°")[1].split("'")[1][:-1])
    lat_dir = lat_str[-1]
    
    # Extrahera grader, minuter, sekunder och riktning för longitud
    lon_deg = int(lon_str[:-1].split("°")[0])
    lon_min = int(lon_str[:-1].split("°")[1].split("'")[0])
    lon_sec = float(lon_str[:-1].split("°")[1].split("'")[1][:-1])
    lon_dir = lon_str[-1]
    
    # Konvertera till decimal
    lat_decimal = convert_to_decimal(lat_deg, lat_min, lat_sec, lat_dir)
    lon_decimal = convert_to_decimal(lon_deg, lon_min, lon_sec, lon_dir)
    
    return lat_decimal, lon_decimal



def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_coordinates_from_event(url):
    driver = setup_driver()
    driver.get(url)

    accept_cookies(driver)
    
    try:
        # Vänta tills knappen för att öppna menyn är synlig och klicka på den
        menu_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "top-panel-menu-button"))
        )
        menu_button.click()
        
        # Vänta tills länken för att visa översiktskartan är synlig och klicka på den
        overview_map_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-bind='if: topPanel.showOverviewMapLink']/a"))
        )
        overview_map_link.click()
        
         # Vänta längre för att säkerställa att kartan och koordinaterna har laddats
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
         
        try:
            google_maps_iframe = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[src*="https://www.google.com/maps/embed/v1/place"]'))
            )
            
            driver.switch_to.frame(google_maps_iframe)
            
            # Försök att hämta koordinaterna från iframe
            coordinates_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "place-name"))
            )

            if coordinates_element:
                coordinates = coordinates_element.text
                coordinates = convert_coordinates()
                driver.switch_to.default_content()
                return coordinates
            else:
                driver.switch_to.default_content()
                return None
            
        except Exception as e:
            print(f"Error while getting coordinates: {e}")
            driver.switch_to.default_content()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
