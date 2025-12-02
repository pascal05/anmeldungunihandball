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

# --- KONFIGURATION ---

URL = "https://www.sportangebot.uni-bonn.de/angebote/aktueller_zeitraum/_Fussball.html"
TARGET_KURS_NR = "121262"

USER_DATA = {
    "sex": "M",
    "vorname": "Max",
    "name": "Mustermann",
    "strasse": "",
    "ort": "",
    "status": "S-UNIB",
    "matnr": "",
    "email": "",
    "telefon": ""
}

def run_bot():
    # Chrome Options (HEADLESS)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222")

    # Chrome Binary Pfadsuche
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
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
        print(f"INFO: Chrome-Binary gefunden: {found_path}")
    else:
        print("WARNUNG: Kein Chrome-Binary gefunden – nutze System-PATH.")

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        print(f"Öffne {URL}...")
        driver.get(URL)

        print(f"Suche Kurs {TARGET_KURS_NR}...")
        xpath_button = f"//td[contains(text(), '{TARGET_KURS_NR}')]/..//input[@type='submit'][@value='buchen']"
        
        book_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_button))
        )

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", book_btn)
        time.sleep(0.4)
        driver.execute_script("arguments[0].click();", book_btn)

        print("Buchen angeklickt → Wechsle Tab...")
        original_window = driver.current_window_handle
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

        for window in driver.window_handles:
            if window != original_window:
                driver.switch_to.window(window)
                break

        print("Fülle Formular...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "vorname")))

        # Status
        status_select = Select(driver.find_element(By.NAME, "statusorig"))
        status_select.select_by_value(USER_DATA["status"])
        time.sleep(1)

        # Matrikelnummer (falls notwendig)
        if "UNIB" in USER_DATA["status"]:
            try:
                matnr = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.NAME, "matnr"))
                )
                matnr.clear()
                matnr.send_keys(USER_DATA["matnr"])
            except:
                print("Matrikelnummer-Feld nicht sichtbar oder nicht benötigt.")

        # Restliche Felder
        sex_radio = driver.find_element(By.CSS_SELECTOR, f"input[name='sex'][value='{USER_DATA['sex']}']")
        driver.execute_script("arguments[0].click();", sex_radio)

        driver.find_element(By.NAME, "vorname").send_keys(USER_DATA["vorname"])
        driver.find_element(By.NAME, "name").send_keys(USER_DATA["name"])
        driver.find_element(By.NAME, "strasse").send_keys(USER_DATA["strasse"])
        driver.find_element(By.NAME, "ort").send_keys(USER_DATA["ort"])
        driver.find_element(By.NAME, "email").send_keys(USER_DATA["email"])
        driver.find_element(By.NAME, "telefon").send_keys(USER_DATA["telefon"])

        # AGB Checkbox
        tnbed = driver.find_element(By.NAME, "tnbed")
        driver.execute_script("arguments[0].click();", tnbed)

        print("Warte 12 Sekunden (Spam-Schutz)...")
        time.sleep(12)

        submit_step1 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "bs_submit"))
        )

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_step1)
        time.sleep(0.4)
        driver.execute_script("arguments[0].click();", submit_step1)
        print("Daten abgeschickt → warte auf Finalseite...")

        try:
            final_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='verbindlich buchen']"))
            )
            driver.execute_script("arguments[0].click();", final_btn)
            print("✔ BUCHUNG ERFOLGREICH!")

        except TimeoutException:
            print("❌ Finaler Button nicht gefunden – Fehler-Screenshot gespeichert.")
            driver.save_screenshot("error_final_button.png")
            raise

        finally:
            # Screenshot der letzten Seite **immer** speichern
            try:
                time.sleep(1)
                driver.save_screenshot("screenshot_final_page.png")
                print("📸 Screenshot gespeichert: screenshot_final_page.png")
            except Exception as e:
                print(f"❌ Screenshot konnte nicht erstellt werden: {e}")

        time.sleep(4)

    except Exception as e:
        print(f"\n--- FEHLER ---\n{e}")
        if not found_path:
            print("Chrome-Pfad wurde nicht gefunden → installiere Chrome/Chromium.")
    finally:
        print("Beende Skript.")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    run_bot()
