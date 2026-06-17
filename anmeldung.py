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


def run_bot():
    session = requests.Session()
    session.headers.update(HEADERS)

    # Schritt 1: Kursseite laden und Buchungsformular finden
    print(f"Lade Kursseite: {URL}")
    r1 = session.get(URL, timeout=30)
    r1.raise_for_status()
    soup1 = BeautifulSoup(r1.text, "html.parser")

    # Each course row has id="K<KURS_NR>"
    row = soup1.find("tr", id=f"K{TARGET_KURS_NR}")
    if not row:
        save_and_exit(r1.text, "fehler.html", f"Kurs {TARGET_KURS_NR} nicht gefunden")

    # The buchen button lives in the row; the <form> wraps the whole page above it
    submit1 = row.find("input", {"type": "submit", "value": "buchen"})
    if not submit1:
        save_and_exit(r1.text, "fehler.html", f"Kein Buchen-Button für Kurs {TARGET_KURS_NR} (Buchung noch nicht geöffnet?)")

    form1 = submit1.find_parent("form")
    if not form1:
        save_and_exit(r1.text, "fehler.html", "Kein Formular gefunden")

    extra1 = {}
    if submit1.get("name"):
        extra1[submit1["name"]] = "buchen"

    # Schritt 2: Buchungsformular absenden → persönliches Datenformular
    print(f"Kurs {TARGET_KURS_NR} gefunden. Öffne Buchungsformular...")
    r2 = submit_form(session, form1, r1.url, extra1, referer=r1.url)
    r2.raise_for_status()
    soup2 = BeautifulSoup(r2.text, "html.parser")

    form2 = soup2.find("form")
    if not form2:
        save_and_exit(r2.text, "fehler.html", "Persönliches Datenformular nicht gefunden")

    # Persönliche Daten zusammenstellen
    personal = {
        "statusorig": USER_DATA["status"],
        "sex":        USER_DATA["sex"].upper(),  # form expects M/W/D/X
        "vorname":    USER_DATA["vorname"],
        "name":       USER_DATA["name"],
        "strasse":    USER_DATA["strasse"],
        "ort":        USER_DATA["ort"],
        "email":      USER_DATA["email"],
        "telefon":    USER_DATA["telefon"],
        "newsletter": "",
    }
    if "UNIB" in USER_DATA["status"]:
        personal["matnr"] = USER_DATA["matnr"]

    # AGB-Checkbox: read value attribute from the form element
    tnbed = form2.find("input", {"name": "tnbed"})
    personal["tnbed"] = tnbed.get("value", "1") if tnbed else "1"

    print("Warte 12 Sekunden (Spam-Schutz des Portals)...")
    time.sleep(12)

    # Schritt 3: Persönliche Daten absenden → Bestätigungsseite
    print("Sende Formulardaten...")
    r3 = submit_form(session, form2, r2.url, personal, referer=r2.url)
    r3.raise_for_status()
    soup3 = BeautifulSoup(r3.text, "html.parser")

    form3 = soup3.find("form")
    # Final confirm button has a name (cancel/reset buttons do not); label varies by portal state
    final_btn = None
    if form3:
        for val in ("verbindlich buchen", "buchen"):
            final_btn = form3.find("input", {"type": "submit", "value": val, "name": True})
            if final_btn:
                break
        # Fallback: any named submit button
        if not final_btn:
            final_btn = form3.find(lambda tag: tag.name == "input" and tag.get("type") == "submit" and tag.get("name"))

    if not form3 or not final_btn:
        save_and_exit(r3.text, "fehler.html", "Bestätigungsseite nicht erreicht")

    # Schritt 4: Verbindliche Buchung absenden
    print("Bestätigungsseite erreicht. Sende verbindliche Buchung...")
    extra3 = {final_btn["name"]: final_btn.get("value", "buchen")}

    r4 = submit_form(session, form3, r3.url, extra3, referer=r3.url)
    r4.raise_for_status()

    with open("bestaetigung.html", "w", encoding="utf-8") as f:
        f.write(r4.text)
    print("Buchung abgeschickt! Bestaetigung gespeichert in bestaetigung.html")


if __name__ == "__main__":
    run_bot()
