import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- KONFIGURATION (HIER ÄNDERN FÜR ANDERE KURSE) ---

URL = "https://www.sportangebot.uni-bonn.de/angebote/aktueller_zeitraum/_Fussball.html"

TARGET_KURS_NR = "121262"  

# 3. PRÜFEN: Deine Daten (bleiben gleich, wenn es für dich ist)
USER_DATA = {
    "sex": "M",
    "vorname": "Pascal",
    "name": "Haag",
    "strasse": "Magdalenenstraße 36",
    "ort": "53121 Bonn",
    "status": "S-UNIB",
    "matnr": "50282283",
    "email": "pascal.haag@outlook.de",
    "telefon": "01749134509"
}

def run_bot():
    # Setup
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized") 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print(f"Öffne {URL}...")
        driver.get(URL)
        
        # --- SEITE 1: KURS AUSWÄHLEN ---
        print(f"Suche Kurs {TARGET_KURS_NR}...")
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
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "vorname")))

        # 1. Status wählen
        status_select = Select(driver.find_element(By.NAME, "statusorig"))
        status_select.select_by_value(USER_DATA['status'])
        time.sleep(1)

        # 2. Matrikelnummer
        if "UNIB" in USER_DATA['status']:
            try:
                matnr_field = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.NAME, "matnr"))
                )
                matnr_field.clear()
                matnr_field.send_keys(USER_DATA['matnr'])
            except Exception as e:
                print(f"Info: Matrikelnummer-Feld nicht bereit oder nötig: {e}")

        # 3. Restliche Felder
        sex_radio = driver.find_element(By.CSS_SELECTOR, f"input[name='sex'][value='{USER_DATA['sex']}']")
        driver.execute_script("arguments[0].click();", sex_radio)

        driver.find_element(By.NAME, "vorname").send_keys(USER_DATA['vorname'])
        driver.find_element(By.NAME, "name").send_keys(USER_DATA['name'])
        driver.find_element(By.NAME, "strasse").send_keys(USER_DATA['strasse'])
        driver.find_element(By.NAME, "ort").send_keys(USER_DATA['ort'])
        driver.find_element(By.NAME, "email").send_keys(USER_DATA['email'])
        driver.find_element(By.NAME, "telefon").send_keys(USER_DATA['telefon'])

        tnbed_checkbox = driver.find_element(By.NAME, "tnbed")
        driver.execute_script("arguments[0].click();", tnbed_checkbox)
        
        # --- TIMER ABWARTEN ---
        print("--- WARTE 12 SEKUNDEN AUF TIMER (SPAMSCHUTZ) ---")
        time.sleep(12) 
        
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
            driver.execute_script("arguments[0].click();", final_button)
            print("BUCHUNG WURDE AUSGEFÜHRT!")

        except Exception:
            print("FEHLER: Konnte Bestätigungsseite nicht erreichen.")
            driver.save_screenshot("fehler_screenshot_final.png")
            raise 

        time.sleep(5)

    except Exception as e:
        print(f"\n--- FEHLERBERICHT ---\n{e}")
    finally:
        print("Skript beendet.")
        driver.quit()

if __name__ == "__main__":
    run_bot()