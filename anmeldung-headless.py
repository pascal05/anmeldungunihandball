import time
import datetime
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

# --- KONFIGURATION ---
URL = "https://www.sportangebot.uni-bonn.de/angebote/aktueller_zeitraum/_Handball.html"
TARGET_KURS_NR = "121401"

# WANN GEHT DIE BUCHUNG LOS? (Format: JJJJ, MM, TT, HH, MM, SS)
# Beispiel: 2. Dez 2025 um 08:00:00 Uhr
START_TIME = datetime.datetime(2025, 12, 2, 8, 0, 0)

USER_DATA = {
    "sex": "W",
    "vorname": "Max",
    "name": "Mustermann",
    "strasse": "Musterstr. 1",
    "ort": "53111 Bonn",
    "status": "S-UNIB", 
    "matnr": "123456",
    "email": "deine.email@uni-bonn.de",
    "telefon": "0123456789"
}

def get_headless_driver():
    options = webdriver.ChromeOptions()
    # WICHTIG für VM/Headless:
    options.add_argument("--headless=new") 
    options.add_argument("--window-size=1920,1080") # Zwingend nötig, sonst fehlen Elemente
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage") # Verhindert RAM-Crash in VMs
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    
    # User-Agent Spoofing (damit wir wie ein echter Windows PC aussehen)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Pfad Suche (nur zur Sicherheit)
    if os.path.exists('/usr/bin/google-chrome'):
        options.binary_location = '/usr/bin/google-chrome'

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def wait_for_start_time(driver):
    """Wartet bis kurz vor Startzeit und lädt Seite vor."""
    now = datetime.datetime.now()
    
    # Wenn wir zu früh sind (mehr als 10 Sek), warten wir einfach
    wait_seconds = (START_TIME - now).total_seconds()
    
    if wait_seconds > 10:
        print(f"Noch {wait_seconds:.0f} Sekunden bis Start. Warte...")
        time.sleep(wait_seconds - 5) # Bis 5 Sek vor Start schlafen
    
    print("Lade Seite vor...")
    try:
        driver.get(URL)
    except Exception as e:
        print(f"Fehler beim ersten Laden (Server down?): {e}")

    # Exaktes Warten auf die Sekunde 0
    while datetime.datetime.now() < START_TIME:
        time.sleep(0.1)
    
    print(f"!!! STARTZEIT ERREICHT ({datetime.datetime.now()}) !!! RELOAD !!!")
    driver.refresh()

def run_bot():
    driver = None
    try:
        print("Initialisiere Headless Driver...")
        driver = get_headless_driver()
        
        # 1. Warten auf den Startschuss
        wait_for_start_time(driver)
        
        # 2. Kurs Button suchen (Mit Retry-Logik für Überlastung)
        print(f"Suche Kurs {TARGET_KURS_NR}...")
        xpath_button = f"//td[contains(text(), '{TARGET_KURS_NR}')]/ancestor::tr//input[@value='buchen']"
        
        attempts = 0
        book_btn = None
        
        # Wir versuchen es 30 Sekunden lang aggressiv
        while attempts < 30:
            try:
                book_btn = driver.find_element(By.XPATH, xpath_button)
                book_btn.click()
                print(">>> BUTTON GEKLICKT! <<<")
                break
            except NoSuchElementException:
                attempts += 1
                print(f"Button noch nicht da. Retry {attempts}/30 in 1s...")
                time.sleep(1)
                driver.refresh() # WICHTIG: Seite neu laden, falls Button erst später freigeschaltet wird
            except Exception as e:
                print(f"Klick-Fehler: {e}")
                time.sleep(0.5)

        if not book_btn:
            raise Exception("Konnte Buchen-Button nach 30 Versuchen nicht finden.")

        # Fenster-Handling
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[-1])

        # --- SEITE 2: FORMULAR ---
        print("Fülle Formular aus...")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "vorname")))

        Select(driver.find_element(By.NAME, "statusorig")).select_by_value(USER_DATA['status'])
        
        # Matrikelnummer
        if "UNIB" in USER_DATA['status']:
            try:
                # Schnelleres Polling
                matnr = WebDriverWait(driver, 5, poll_frequency=0.2).until(
                    EC.visibility_of_element_located((By.NAME, "matnr"))
                )
                matnr.clear()
                matnr.send_keys(USER_DATA['matnr'])
            except: pass

        # Geschlecht
        try:
            driver.find_element(By.XPATH, f"//input[@name='sex'][@value='{USER_DATA['sex']}']").click()
        except: pass

        # Felder
        for field in ["vorname", "name", "strasse", "ort", "email", "telefon"]:
            driver.find_element(By.NAME, field).clear()
            driver.find_element(By.NAME, field).send_keys(USER_DATA[field])

        # AGB
        driver.find_element(By.NAME, "tnbed").click()
        
        # --- WARTEZEIT (SPAMSCHUTZ) ---
        print("Warte 13s auf Spamschutz-Timer...")
        time.sleep(13) 
        
        # Abschicken Schritt 1
        submit_btn = driver.find_element(By.CSS_SELECTOR, "#bs_submit, input[value='weiter zur Buchung']")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
        submit_btn.click()
        print("Formular abgeschickt.")

        # --- FINALISIERUNG ---
        print("Warte auf finale Bestätigung...")
        final_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='verbindlich buchen']"))
        )
        
        # HIER FINALER KLICK
        # final_btn.click() 
        print("SUCCESS: Wäre jetzt verbindlich gebucht!")
        
        # Screenshot als Beweis speichern
        driver.save_screenshot("buchung_erfolg.png")

    except Exception as e:
        print(f"FATAL ERROR: {e}")
        if driver:
            driver.save_screenshot("error_headless.png")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    run_bot()
