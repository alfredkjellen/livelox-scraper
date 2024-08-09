from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
from webdriver_manager.chrome import ChromeDriverManager


def accept_cookies(driver):
    try:
        consent_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fc-button.fc-cta-consent.fc-primary-button"))
        )
        consent_button.click() 
        print("Accepted cookies")
    except Exception as e:
        print(f"Error occured while accepting cookies: {e}")


def setup_driver():
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def get_event_data(url):
    driver = setup_driver()
    driver.get(url)
    
    # Vänta på att sidan laddas och acceptera cookies
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "row.event"))
    )
    accept_cookies(driver)
    
    ids = []
    links = []   
    
    while True:
        try:
            events = driver.find_elements(By.CLASS_NAME, "row.event")
            for event in events:
                try:
                    # Scrolla till elementet
                    driver.execute_script("arguments[0].scrollIntoView(true);", event)
                    time.sleep(0.1)  # Kort paus för att låta sidan stabiliseras efter scrollning
                    
                    # Se till att elementet är synligt och klickbart
                    WebDriverWait(driver, 0.1).until(EC.element_to_be_clickable((By.CLASS_NAME, "row.event")))
                    
                    # Använd ActionChains för att klicka på elementet
                    ActionChains(driver).move_to_element(event).click(event).perform()
                    time.sleep(0.1)  # Vänta på att innehållet laddas
                    
                    # Försök hitta den första länken i det expanderade innehållet
                    link_element = WebDriverWait(driver, 0.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/Viewer/']"))
                    )
                    if link_element:

                        link = link_element.get_attribute('href')
                        id = link.split('classId=')[1]
                        
                        ids.append(id)
                        links.append(link)
                        
                        
                    # Klicka på ett neutralt område inom eventet för att kollapsa det
                    neutral_area = event.find_element(By.CSS_SELECTOR, "div.col-sm-3.time-interval-container")
                    ActionChains(driver).move_to_element(neutral_area).click().perform()
                except Exception as e:
                    print(f"Kunde inte hantera event: {e}")
            break
        except Exception as e:
            print(f"Stale element reference, försök igen: {e}")
            time.sleep(1)  # Vänta lite innan nästa försök
    
    driver.quit()
    return ids, links


def main():
    url = "https://www.livelox.com/?tab=allEvents&timePeriod=pastWeek&country=SWE&sorting=time"
    event_links = get_event_data(url)
    
    print(f"Antal hittade events: {len(event_links)}")
    print("Event namn och länkar:")
    for name, link in event_links:
        print(f"Namn: {name}")
        print(f"Länk: {link}")
        print("---")









