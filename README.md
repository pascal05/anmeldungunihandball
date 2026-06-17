# Uni Bonn Sportbuchungs-Bot

Dieses Skript bucht automatisch einen Sportkurs beim Hochschulsport der Uni Bonn. Es braucht keinen Browser — es läuft auf jedem Rechner, auch ohne grafische Oberfläche.

---

## Schritt 1 — Python installieren

Python ist die Programmiersprache, in der das Skript geschrieben ist. Prüfe zuerst, ob es bereits installiert ist:

**Windows:** Öffne die Eingabeaufforderung (`Win + R` → `cmd` → Enter) und tippe:
```
python --version
```

**Mac:** Öffne das Terminal (Spotlight: `Cmd + Leertaste` → „Terminal") und tippe:
```
python3 --version
```

**Linux:** Öffne ein Terminal und tippe:
```
python3 --version
```

Wenn eine Versionsnummer erscheint (z. B. `Python 3.11.2`), ist Python bereits installiert — weiter mit Schritt 2.

Falls nicht:

- **Windows:** Gehe auf [python.org/downloads](https://www.python.org/downloads/), lade den Installer herunter und führe ihn aus. **Wichtig:** Setze beim ersten Installationsschritt den Haken bei „Add Python to PATH".
- **Mac:** Installiere [Homebrew](https://brew.sh) und führe dann `brew install python3` im Terminal aus. Alternativ ebenfalls über [python.org/downloads](https://www.python.org/downloads/).
- **Linux (Ubuntu/Debian):** `sudo apt install python3 python3-pip`

---

## Schritt 2 — Dateien herunterladen

### Option A — Mit Git (empfohlen)

Falls Git installiert ist, öffne ein Terminal / die Eingabeaufforderung und führe aus:

```
git clone https://github.com/pascal05/anmeldungunihandball
cd anmeldungunihandball
```

### Option B — Als ZIP

Klicke oben auf dieser GitHub-Seite auf den grünen Button **Code → Download ZIP**, entpacke das Archiv und öffne den Ordner.

---

## Schritt 3 — Abhängigkeiten installieren

Das Skript benötigt zwei kleine Zusatzpakete. Installiere sie mit einem einzigen Befehl:

**Windows (Eingabeaufforderung im Projektordner):**
```
pip install requests beautifulsoup4
```

**Mac / Linux (Terminal im Projektordner):**
```
pip3 install requests beautifulsoup4
```

> Kein Browser, kein Chrome, nichts weiteres nötig.

---

## Schritt 4 — Skript konfigurieren

Öffne die Datei `anmeldung.py` mit einem Texteditor (z. B. Notepad auf Windows, TextEdit auf Mac, oder gedit/nano auf Linux).

Passe die folgenden Felder oben in der Datei an:

### Kurs-URL und Kursnummer

```python
URL = "https://www.sportangebot.uni-bonn.de/angebote/aktueller_zeitraum/_Handball.html"
TARGET_KURS_NR = "121401"
```

Die Kursnummer (6-stellig) findest du auf der Buchungsseite des Hochschulsports in der Kursübersicht.
Die URL bestimmst du anhand der Sportart — ersetze `_Handball` durch z. B. `_Fussball` oder `_Yoga`.

### Persönliche Daten

```python
USER_DATA = {
    "sex": "m",           # "m" = männlich, "w" = weiblich, "d" = divers, "x" = keine Angabe
    "vorname": "Max",
    "name": "Mustermann",
    "strasse": "Musterstraße 1",
    "ort": "53111 Bonn",
    "status": "S-UNIB",   # Studierende Uni Bonn — andere Optionen siehe unten
    "matnr": "123456",    # Matrikelnummer (nur für S-UNIB)
    "email": "deine@email.de",
    "telefon": "0151123456",
}
```

**Mögliche Werte für `status`:**

| Wert | Bedeutung |
|---|---|
| `S-UNIB` | Studierende Uni Bonn |
| `B-UNIB` | Beschäftigte Uni Bonn |
| `B-UKB` | Beschäftigte Universitätsklinikum Bonn |
| `S-FH` | Studierende Hochschule Bonn-Rhein-Sieg |
| `S-aH` | Studierende anderer Hochschulen |
| `Extern` | Inhaber Teilnehmerausweis |

---

## Schritt 5 — Bot starten

**Windows:**
```
python anmeldung.py
```

**Mac / Linux:**
```
python3 anmeldung.py
```

Der Bot bucht den Kurs vollautomatisch. Du erhältst eine Bestätigungs-E-Mail vom Hochschulsport an die angegebene Adresse.

---

## Was passiert bei einem Fehler?

Schlägt eine der Buchungsschritte fehl, speichert das Skript die Serverantwort als `fehler.html` im selben Ordner. Öffne diese Datei in einem Browser, um zu sehen, was schiefgelaufen ist (z. B. Kurs bereits ausgebucht, falsche Kursnummer, Buchung noch nicht geöffnet).

Bei erfolgreicher Buchung wird die Bestätigungsseite als `bestaetigung.html` gespeichert.

---

## Hinweis

Die Buchung wird **sofort und verbindlich** abgesendet, sobald du das Skript startest. Stelle sicher, dass alle Angaben korrekt sind, bevor du es ausführst.
