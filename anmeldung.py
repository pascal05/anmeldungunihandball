#!/usr/bin/env python3
"""
Uni Bonn Sportbuchungs-Bot
Abhängigkeiten: pip install requests beautifulsoup4
Kein Browser oder Selenium notwendig.
"""

import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

try:
    from config import URL, TARGET_KURS_NR, USER_DATA
except ImportError:
    sys.exit(
        "config.py nicht gefunden. Kopiere config.example.py zu config.py "
        "und trage dort deine Daten ein."
    )

# --- BOT ---

# Falls die Buchung exakt zum Öffnungszeitpunkt per Cron gestartet wird, kann
# die Seite im selben Moment noch die alte Ansicht (Autostart-Hinweis statt
# "buchen"-Button) ausliefern. Es wird daher mehrfach mit kurzer Pause erneut
# versucht, bevor endgültig aufgegeben wird.
BUCHEN_RETRY_ATTEMPTS = 20
BUCHEN_RETRY_DELAY = 3  # Sekunden zwischen den Versuchen

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Origin": "https://www.sportangebot.uni-bonn.de",
}


def hidden_fields(form):
    return {
        inp["name"]: inp.get("value", "")
        for inp in form.find_all("input", type="hidden")
        if inp.get("name")
    }


def submit_form(session, form, base_url, extra=None, referer=None):
    action = urljoin(base_url, form.get("action", base_url))
    data = hidden_fields(form)
    if extra:
        data.update(extra)
    headers = {"Referer": referer} if referer else {}
    method = form.get("method", "get").lower()
    if method == "post":
        return session.post(action, data=data, timeout=30, headers=headers)
    return session.get(action, params=data, timeout=30, headers=headers)


def save_and_exit(html, filename, message):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    sys.exit(f"{message} — Antwort gespeichert in {filename}")


def is_personal_data_form(form):
    """Gibt True zurück, wenn das Formular das Persönliche-Daten-Eingabeformular ist (sichtbares Vorname-Feld)."""
    return bool(form.find("input", {"name": "vorname", "type": "text"}))


def course_name(soup):
    el = soup.find(id="bs_ag_name")
    return el.get_text(strip=True) if el else f"Kurs {TARGET_KURS_NR}"


def skip_intermediate_pages(session, soup, url):
    """
    Manche Kurse zeigen nach dem Buchen-Klick eine Zwischenseite (z. B. Terminauswahl
    bei Einzelstunden wie Basketball). Diese wird automatisch übersprungen, indem der
    erste verfügbare Termin gewählt wird.
    Gibt (form, url, soup) des Persönliche-Daten-Formulars zurück.
    """
    for _ in range(3):
        form = soup.find("form")
        if not form:
            return None, url, soup
        if is_personal_data_form(form):
            return form, url, soup

        print("Zwischenseite erkannt. Wähle ersten verfügbaren Termin...")
        extra = {}

        # Terminauswahl per eigenem Submit-Button (name="BS_Termin_JJJJ-MM-TT")
        termin_btns = [
            b for b in form.find_all("input", {"type": "submit"})
            if b.get("name", "").startswith("BS_Termin_")
        ]
        if termin_btns:
            btn = termin_btns[0]
            extra[btn["name"]] = btn.get("value", "buchen")
            date_part = btn["name"].replace("BS_Termin_", "")
            print(f"  Termin: {date_part}")
        else:
            # Radiobuttons (z. B. Terminauswahl als Radio)
            for radio in form.find_all("input", {"type": "radio"}):
                name = radio.get("name")
                if name and name not in extra:
                    extra[name] = radio.get("value", "")
                    print(f"  {name} = {extra[name]}")
            # Dropdown-Felder
            for sel in form.find_all("select"):
                name = sel.get("name")
                if name:
                    opts = [o for o in sel.find_all("option") if o.get("value")]
                    if opts:
                        extra[name] = opts[0]["value"]
                        print(f"  {name} = {extra[name]}")
            # Fallback: Submit-Button mit Name übernehmen
            submit_btn = form.find("input", {"type": "submit"})
            if submit_btn and submit_btn.get("name"):
                extra[submit_btn["name"]] = submit_btn.get("value", "weiter")

        r = submit_form(session, form, url, extra, referer=url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        url = r.url

    return None, url, soup


def find_buchen_button(session):
    """
    Lädt die Kursseite und sucht den Buchen-Button in der Kurszeile. Zeigt die
    Zeile stattdessen einen Autostart-Hinweis (z. B. "ab 13.07., 07:00"), ist
    die Buchung noch nicht offen — dann wird mehrfach mit kurzer Pause erneut
    versucht (wichtig bei Cron-Start exakt zur Öffnungszeit).
    Gibt (r1, submit1) zurück.
    """
    for attempt in range(1, BUCHEN_RETRY_ATTEMPTS + 1):
        print(f"Lade Kursseite: {URL}")
        r1 = session.get(URL, timeout=30)
        r1.raise_for_status()
        soup1 = BeautifulSoup(r1.text, "html.parser")

        row = soup1.find("tr", id=f"K{TARGET_KURS_NR}")
        if not row:
            save_and_exit(r1.text, "fehler.html",
                          f"Kurs {TARGET_KURS_NR} nicht in der Kursliste gefunden "
                          f"(falsche Kurs-Nr. oder Seite hat sich geändert)")

        submit1 = row.find("input", {"type": "submit", "value": "buchen"})
        if submit1:
            return r1, submit1

        autostart = row.find(class_="bs_btn_autostart")
        if autostart and attempt < BUCHEN_RETRY_ATTEMPTS:
            print(f"  Buchung noch nicht offen ({autostart.get_text(strip=True)}). "
                  f"Versuch {attempt}/{BUCHEN_RETRY_ATTEMPTS}, warte {BUCHEN_RETRY_DELAY}s...")
            time.sleep(BUCHEN_RETRY_DELAY)
            continue

        hint = f" — öffnet {autostart.get_text(strip=True)}" if autostart else ""
        save_and_exit(r1.text, "fehler.html",
                      f"Kurs {TARGET_KURS_NR}: kein Buchen-Button sichtbar"
                      f"{hint} (Buchung noch nicht geöffnet oder Kurs bereits ausgebucht)")


def run_bot():
    session = requests.Session()
    session.headers.update(HEADERS)

    # Schritt 1: Kursseite laden und Buchungsformular finden
    r1, submit1 = find_buchen_button(session)
    form1 = submit1.find_parent("form")
    if not form1:
        save_and_exit(r1.text, "fehler.html",
                      "Buchungsformular auf der Kursseite nicht gefunden")

    extra1 = {}
    if submit1.get("name"):
        extra1[submit1["name"]] = "buchen"

    # Schritt 2: Buchungsformular absenden
    print(f"Kurs {TARGET_KURS_NR} gefunden. Starte Buchungsvorgang...")
    r2 = submit_form(session, form1, r1.url, extra1, referer=r1.url)
    r2.raise_for_status()
    soup2 = BeautifulSoup(r2.text, "html.parser")

    # Optionale Zwischenseite(n) überspringen (z. B. Terminauswahl bei Basketball)
    form2, url2, soup2 = skip_intermediate_pages(session, soup2, r2.url)
    if not form2:
        save_and_exit(soup2.prettify() if soup2 else r2.text, "fehler.html",
                      "Persönliches Datenformular nicht gefunden "
                      "(Zwischenseite nicht erkannt — Seitenstruktur hat sich ggf. geändert)")

    kurs = course_name(soup2)
    print(f"Kurs: {kurs}")

    # Persönliche Daten zusammenstellen
    personal = {
        "statusorig": USER_DATA["status"],
        "sex":        USER_DATA["sex"].upper(),
        "vorname":    USER_DATA["vorname"],
        "name":       USER_DATA["name"],
        "strasse":    USER_DATA["strasse"],
        "ort":        USER_DATA["ort"],
        "email":      USER_DATA["email"],
        "telefon":    USER_DATA.get("telefon", ""),
        "newsletter": "",
    }
    if "UNIB" in USER_DATA["status"]:
        personal["matnr"] = USER_DATA["matnr"]

    tnbed = form2.find("input", {"name": "tnbed"})
    personal["tnbed"] = tnbed.get("value", "1") if tnbed else "1"

    print("Warte 12 Sekunden (Spam-Schutz des Portals)...")
    time.sleep(12)

    # Schritt 3: Persönliche Daten absenden → Bestätigungsseite
    print("Sende persönliche Daten...")
    r3 = submit_form(session, form2, url2, personal, referer=url2)
    r3.raise_for_status()
    soup3 = BeautifulSoup(r3.text, "html.parser")

    form3 = soup3.find("form")

    # Catch: server schickt Eingabeformular erneut (Daten abgelehnt)
    if form3 and is_personal_data_form(form3):
        save_and_exit(r3.text, "fehler.html",
                      "Server hat Daten zurückgewiesen und das Eingabeformular erneut gesendet "
                      "(Felder prüfen, z. B. Matrikelnummer oder E-Mail)")

    # Bestätigungs-Button suchen
    final_btn = None
    if form3:
        for val in ("verbindlich buchen", "buchen"):
            final_btn = form3.find("input", {"type": "submit", "value": val})
            if final_btn:
                break
        if not final_btn:
            final_btn = form3.find("input", {"type": "submit"})

    if not form3 or not final_btn:
        save_and_exit(r3.text, "fehler.html",
                      "Bestätigungsseite nicht erreicht "
                      "(Session abgelaufen oder Portal hat den Vorgang abgebrochen)")

    # Schritt 4: Verbindliche Buchung absenden
    print("Bestätigungsseite erreicht. Sende verbindliche Buchung...")
    extra3 = {}
    if final_btn.get("name"):
        extra3[final_btn["name"]] = final_btn.get("value", "buchen")

    r4 = submit_form(session, form3, r3.url, extra3, referer=r3.url)
    r4.raise_for_status()

    soup4 = BeautifulSoup(r4.text, "html.parser")
    page_text = soup4.get_text()

    # Portal-seitige Fehlermeldung erkennen
    error_phrases = [
        "konnte nicht ausgeführt werden",
        "booking could not be completed",
        "Fehler aufgetreten",
    ]
    if any(p in page_text for p in error_phrases):
        with open("fehler.html", "w", encoding="utf-8") as f:
            f.write(r4.text)
        sys.exit(f"Portal meldet Buchungsfehler für '{kurs}' — Details in fehler.html")

    with open("bestaetigung.html", "w", encoding="utf-8") as f:
        f.write(r4.text)

    if soup4.find("form") and is_personal_data_form(soup4.find("form")):
        print("WARNUNG: Buchung scheinbar fehlgeschlagen — Antwort enthält erneut das Eingabeformular.")
        print("Details in bestaetigung.html prüfen.")
    else:
        print(f"Buchung für '{kurs}' erfolgreich abgeschlossen!")
        print("Bestätigung gespeichert in bestaetigung.html")


if __name__ == "__main__":
    run_bot()
