# Kopiere diese Datei zu config.py und trage dort deine echten Daten ein.
# config.py wird von git ignoriert — deine Daten landen nie im Repository.

URL = "https://www.sportangebot.uni-bonn.de/angebote/aktueller_zeitraum/_Basketball.html"  # Sportart-URL aus dem Portal
TARGET_KURS_NR = "000000"  # 6-stellige Kursnummer aus der Kurstabelle

USER_DATA = {
    "sex": "m",              # "m" = männlich, "w" = weiblich, "d" = divers, "x" = keine Angabe
    "vorname": "Vorname",
    "name": "Nachname",
    "strasse": "Musterstraße 1",
    "ort": "12345 Musterstadt",
    "status": "S-UNIB",      # Statusoptionen siehe README
    "matnr": "1234567",      # Matrikelnummer (nur für S-UNIB und ähnliche)
    "email": "deine@email.de",
    "telefon": "",           # optional — leer lassen zum Weglassen
}
