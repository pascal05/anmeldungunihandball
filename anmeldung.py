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

# --- KONFIGURATION ---

URL = "https://www.sportangebot.uni-bonn.de/angebote/aktueller_zeitraum/_Handball.html"
TARGET_KURS_NR = "121401"

USER_DATA = {
    "sex": "m",         # "m" oder "w"
    "vorname": "",
    "name": "",
    "strasse": "",
    "ort": "",
    "status": "S-UNIB", # Student Uni Bonn
    "matnr": "",
    "email": "",
    "telefon": "",
}

# --- BOT ---

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
}


def hidden_fields(form):
    return {
        inp["name"]: inp.get("value", "")
        for inp in form.find_all("input", type="hidden")
        if inp.get("name")
    }


def submit_form(session, form, base_url, extra=None):
    action = urljoin(base_url, form.get("action", base_url))
    data = hidden_fields(form)
    if extra:
        data.update(extra)
    method = form.get("method", "get").lower()
    if method == "post":
        return session.post(action, data=data, timeout=30)
    return session.get(action, params=data, timeout=30)


def save_and_exit(html, filename, message):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    sys.exit(f"{message} — Antwort gespeichert in {filename}")


def run_bot():
    session = requests.Session()
    session.headers.update(HEADERS)

    # Schritt 1: Kursseite laden und Buchungsformular finden
    print(f"Lade Kursseite: {URL}")
    r1 = session.get(URL, timeout=30)
    r1.raise_for_status()
    soup1 = BeautifulSoup(r1.text, "html.parser")

    td = soup1.find("td", string=lambda t: t and TARGET_KURS_NR in t)
    if not td:
        save_and_exit(r1.text, "fehler.html", f"Kurs {TARGET_KURS_NR} nicht gefunden")

    row = td.find_parent("tr")
    form1 = row.find("form") if row else None
    if not form1:
        save_and_exit(r1.text, "fehler.html", "Kein Formular in der Kurszeile gefunden")

    # Submit-Button-Wert mitsenden (manche Portale prüfen ihn serverseitig)
    submit1 = form1.find("input", {"type": "submit", "value": "buchen"})
    extra1 = {}
    if submit1 and submit1.get("name"):
        extra1[submit1["name"]] = "buchen"

    # Schritt 2: Buchungsformular absenden → persönliches Datenformular
    print(f"Kurs {TARGET_KURS_NR} gefunden. Öffne Buchungsformular...")
    r2 = submit_form(session, form1, r1.url, extra1)
    r2.raise_for_status()
    soup2 = BeautifulSoup(r2.text, "html.parser")

    form2 = soup2.find("form")
    if not form2:
        save_and_exit(r2.text, "fehler.html", "Persönliches Datenformular nicht gefunden")

    # Persönliche Daten zusammenstellen
    personal = {
        "statusorig": USER_DATA["status"],
        "sex":        USER_DATA["sex"],
        "vorname":    USER_DATA["vorname"],
        "name":       USER_DATA["name"],
        "strasse":    USER_DATA["strasse"],
        "ort":        USER_DATA["ort"],
        "email":      USER_DATA["email"],
        "telefon":    USER_DATA["telefon"],
    }
    if "UNIB" in USER_DATA["status"]:
        personal["matnr"] = USER_DATA["matnr"]

    # AGB-Checkbox: HTML-Standardwert ist "on" falls kein value-Attribut gesetzt
    tnbed = form2.find("input", {"name": "tnbed"})
    personal["tnbed"] = tnbed.get("value", "on") if tnbed else "on"

    # Submit-Button einschließen
    bs_submit = soup2.find("input", {"id": "bs_submit"})
    if bs_submit and bs_submit.get("name"):
        personal[bs_submit["name"]] = bs_submit.get("value", "")

    print("Warte 12 Sekunden (Spam-Schutz des Portals)...")
    time.sleep(12)

    # Schritt 3: Persönliche Daten absenden → Bestätigungsseite
    print("Sende Formulardaten...")
    r3 = submit_form(session, form2, r2.url, personal)
    r3.raise_for_status()
    soup3 = BeautifulSoup(r3.text, "html.parser")

    form3 = soup3.find("form")
    final_btn = soup3.find("input", {"type": "submit", "value": "verbindlich buchen"})

    if not form3 or not final_btn:
        save_and_exit(r3.text, "fehler.html", "Bestätigungsseite nicht erreicht")

    # Schritt 4: Verbindliche Buchung absenden
    print("Bestätigungsseite erreicht. Sende verbindliche Buchung...")
    extra3 = {}
    if final_btn.get("name"):
        extra3[final_btn["name"]] = final_btn.get("value", "verbindlich buchen")

    r4 = submit_form(session, form3, r3.url, extra3)
    r4.raise_for_status()

    with open("bestaetigung.html", "w", encoding="utf-8") as f:
        f.write(r4.text)
    print("Buchung abgeschickt! Bestaetigung gespeichert in bestaetigung.html")


if __name__ == "__main__":
    run_bot()
