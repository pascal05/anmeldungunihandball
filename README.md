# 🏋️‍♂️ Uni Bonn Sportbuchungs-Bot

Dieses Skript bucht automatisch einen Sportkurs beim Hochschulsport der
Uni Bonn.\
Es öffnet den gewünschten Kurs, klickt auf **buchen**, füllt das
Formular aus und führt die **verbindliche Buchung** automatisch aus.

------------------------------------------------------------------------

## ⚡ Installation

### 1. Repository klonen

``` bash
git clone https://github.com/pascal05/anmeldungunihandball
```

### 2. Abhängigkeiten installieren

``` bash
pip install selenium webdriver-manager
```

### 3. Google Chrome / Chromium installieren

Unter Linux z. B.:

``` bash
sudo apt install chromium-browser
```

Das Skript erkennt Chrome/Chromium automatisch.

------------------------------------------------------------------------

## 🔧 Konfiguration

Öffne das Skript und passe oben diese zwei Dinge an:

### 1. Kurs-URL + Kursnummer

``` python
URL = "https://www.sportangebot.uni-bonn.de/angebote/aktueller_zeitraum/_Handball.html"
TARGET_KURS_NR = "121401"
```

### 2. Persönliche Daten

``` python
USER_DATA = {
    "sex": "m",
    "vorname": "Max",
    "name": "Mustermann",
    "strasse": "Musterweg 6",
    "ort": "53111 Bonn",
    "status": "S-UNIB",
    "matnr": "123456",
    "email": "max@uni-bonn.de",
    "telefon": "015112345678"
}
```

------------------------------------------------------------------------

## ▶️ Starten

``` bash
python3 anmeldung.py
```

Chrome öffnet sich automatisch, der Bot übernimmt den Rest.

------------------------------------------------------------------------

## ⚠️ Hinweis

Die Buchung wird **wirklich automatisch abgesendet**.\
Achte darauf, dass deine Daten und der Kurs korrekt sind.
Es wird eine grafische Oberfläche für den Bot benötigt, da er wirklich chrome öffnet.
