import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import SessionNotCreatedException, TimeoutException
import os 

# --- KONFIGURATION (HIER ÄNDERN FÜR ANDERE KURSE) ---

# WICHTIG: Ändere die URL und die Kursnummer VOR dem Start.
URL = "https://www.sportangebot.uni-bonn.de/angebote/aktueller_zeitraum/_Fussball.html"
TARGET_KURS_NR = "121262"  

# Deine Daten
USER_DATA = {
    "sex": "M",
    "vorname": "Pascal",
    "name": "Haag",
    "strasse": "Magdalenenstraße 36",
    "ort": "53121 Bonn",
    "status": "S-UNIB", # Student Uni Bonn
    "matnr": "50282283",
    "email": "pascal.haag@outlook.de",
    "telefon": "01749134509"
}

def run_bot():
    # Setup Chrome Driver FÜR LOKALEN BETRIEB (SICHTBARER MODUS)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")         
    
    # NEU: Hinzugefügte Stabilitätsargumente für Ubuntu (auch im sichtbaren Modus notwendig)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # Ende der NEU hinzugefügten Stabilitätsargumente

    # --- FEHLERBEHEBUNG UBUNTU/DEBIAN: EXPLIZITE BINÄRE PFADSUECHE ---
    # Sucht nach gängigen Pfaden auf Debian/Ubuntu Systemen.
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/chromium-browser',
        '/usr/local/bin/google-chrome',
        '/opt/google/chrome/google-chrome'
    ]
    
    found_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            options.binary_location = path
            found_path = path
            break
            
    if found_path:
        print(f"INFO: Chrome/Chromium-Binary-Pfad explizit gesetzt auf: {found_path}")
    else:
        print("WARNUNG: Konnte Chrome-Binary nicht an Standardpfaden finden. Verlasse mich auf PATH-Variable.")
    # -------------------------------------------------------------------
    
    try:
        # Initialisiert ChromeDriver und startet die Session
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        print(f"Öffne {URL}...")
        driver.get(URL)
        
        # --- SEITE 1: KURS AUSWÄHLEN ---
        print(f"Suche Kurs {TARGET_KURS_NR}...")
        # Sucht den Buchen-Button in der Zeile mit der Kursnummer
        xpath_button = f"//td[contains(text(), '{TARGET_KURS_NR}')]/..//input[@type='submit'][@value='buchen']"
        
        book_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_button))
        )
        
        # Scrollen & JS Klick
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", book_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", book_btn)
        print("Buchen geklickt.")

        # Fenster-Wechsel (neuer Tab)
        original_window = driver.current_window_handle
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break

        # --- SEITE 2: FORMULAR AUSFÜLLEN ---
        print("Fülle Formular aus...")
        # Warten, bis das erste Feld geladen ist
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "vorname")))

        # 1. Status wählen (wichtig, da es weitere Felder einblenden kann)
        status_select = Select(driver.find_element(By.NAME, "statusorig"))
        status_select.select_by_value(USER_DATA['status'])
        time.sleep(1)

        # 2. Matrikelnummer (falls nötig)
        if "UNIB" in USER_DATA['status']:
            try:
                matnr_field = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.NAME, "matnr"))
                )
                matnr_field.clear()
                matnr_field.send_keys(USER_DATA['matnr'])
            except TimeoutException as e:
                print(f"Info: Matrikelnummer-Feld war nicht bereit oder nicht nötig (Timeout): {e}")
            except Exception as e:
                print(f"Info: Matrikelnummer-Feld-Fehler: {e}")

        # 3. Restliche Felder füllen
        sex_radio = driver.find_element(By.CSS_SELECTOR, f"input[name='sex'][value='{USER_DATA['sex']}']")
        driver.execute_script("arguments[0].click();", sex_radio)

        driver.find_element(By.NAME, "vorname").send_keys(USER_DATA['vorname'])
        driver.find_element(By.NAME, "name").send_keys(USER_DATA['name'])
        driver.find_element(By.NAME, "strasse").send_keys(USER_DATA['strasse'])
        driver.find_element(By.NAME, "ort").send_keys(USER_DATA['ort'])
        driver.find_element(By.NAME, "email").send_keys(USER_DATA['email'])
        driver.find_element(By.NAME, "telefon").send_keys(USER_DATA['telefon'])

        # AGB Checkbox klicken
        tnbed_checkbox = driver.find_element(By.NAME, "tnbed")
        driver.execute_script("arguments[0].click();", tnbed_checkbox)
        
        # --- TIMER ABWARTEN ---
        print("--- WARTE 12 SEKUNDEN AUF TIMER (SPAMSCHUTZ) ---")
        time.sleep(12) 
        
        # Sicherstellen, dass der Button über seine ID gefunden wird
        print("Suche Button 'bs_submit'...")
        submit_step1 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "bs_submit"))
        )
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_step1)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_step1)
        print("Erster Schritt abgeschickt.")

        # --- SEITE 3: BESTÄTIGUNG ---
        print("Warte auf Bestätigungsseite...")
        
        try:
            final_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='submit'][value='verbindlich buchen']"))
            )
            print("Erfolg: Finaler Button gefunden!")
            
            # --- BUCHUNG AUSLÖSEN ---
            # Um wirklich zu buchen, entferne das '#' in der nächsten Zeile:
            # driver.execute_script("arguments[0].click();", final_button)
            # print("BUCHUNG WURDE AUSGEFÜHRT!")

        except TimeoutException:
            print("FEHLER: Konnte Bestätigungsseite (verbindlich buchen) nicht erreichen. Mache Screenshot.")
            driver.save_screenshot("fehler_screenshot_final.png")
            raise 
        except Exception as e:
             print(f"Unbekannter Fehler beim finalen Schritt: {e}")
             driver.save_screenshot("fehler_screenshot_final.png")
             raise 

        time.sleep(5)

    except Exception as e:
        # Hier wird der SessionNotCreatedException abgefangen und ausgegeben
        print(f"\n--- FEHLERBERICHT ---\nEin Fehler ist aufgetreten: {e}")
        print("\n*** ZUSÄTZLICHE INFORMATION ***")
        if not found_path:
            print("Die WARNUNG oben besagt, dass der Chrome-Pfad nicht gefunden wurde.")
            print("Bitte prüfe, ob Google Chrome oder Chromium installiert ist. Wenn ja, suche den exakten Pfad zur Binärdatei (z.B. /usr/bin/google-chrome) und trage ihn manuell im Skript in der Liste 'chrome_paths' ein.")
            
    finally:
        print("Skript beendet.")
        if 'driver' in locals() and driver:
            driver.quit()

if __name__ == "__main__":
    run_bot()