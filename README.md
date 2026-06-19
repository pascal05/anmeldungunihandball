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

**So findest du die URL:**

1. Gehe auf [sportangebot.uni-bonn.de](https://www.sportangebot.uni-bonn.de/angebote/aktueller_zeitraum/_alle.html)
2. Klicke links in der Sportartenliste auf deine gewünschte Sportart (z. B. „Handball")
3. Kopiere die URL aus der Adressleiste deines Browsers — sie endet auf etwas wie `_Handball.html`
4. Trage diese URL in das Skript ein

**So findest du die Kursnummer:**

1. Du bist jetzt auf der Seite deiner Sportart und siehst eine Tabelle mit allen Kursen
2. In der ersten Spalte steht die 6-stellige Kursnummer (z. B. `121401`)
3. Such den Kurs mit dem passenden Wochentag und der Uhrzeit
4. Trage diese Nummer als `TARGET_KURS_NR` ein

> Die Buchungsseite öffnet sich erst zu einem bestimmten Datum und Uhrzeit — vorher erscheint kein „buchen"-Button. Das Skript meldet in diesem Fall einen Fehler. Starte es erst, wenn die Buchung geöffnet ist.

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

## Schritt 6 — Automatisch zur richtigen Zeit starten (Crontab / Aufgabenplanung)

Die Buchung öffnet zu einem festen Zeitpunkt (z. B. 22.06.2026 um 07:00 Uhr). Mit einem Cron-Job läuft das Skript automatisch genau dann — du musst nicht selbst am Rechner sitzen.

### Mac / Linux

**1. Vollständigen Pfad zu Python und zum Skript ermitteln:**

```bash
which python3          # z. B. /usr/bin/python3
realpath anmeldung.py  # z. B. /home/pascal/anmeldungunihandball/anmeldung.py
```

**2. Crontab öffnen:**

```bash
crontab -e
```

Es öffnet sich ein Texteditor. Füge am Ende eine neue Zeile hinzu:

```
# Format: Minute Stunde Tag Monat Wochentag Befehl
# Wochentag: 1 = Montag, 0 = Sonntag, 6 = Samstag
0 7 * * 1 /usr/bin/python3 /home/pascal/anmeldungunihandball/anmeldung.py >> /home/pascal/anmeldungunihandball/cron.log 2>&1
```

Dieser Eintrag startet das Skript **jeden Montag um 07:00 Uhr**. Die Ausgabe (inkl. Fehlermeldungen) landet in `cron.log` im Projektordner.

> Passe die Pfade an deinen Rechner an. Den vollständigen Pfad zu python3 findest du mit `which python3`.

**3. Speichern und schließen** (in nano: `Ctrl + O`, dann `Ctrl + X`).

**4. Eintrag prüfen:**

```bash
crontab -l
```

**Cron-Job wieder entfernen:**

```bash
crontab -e
```

Lösche die hinzugefügte Zeile, speichere und schließe.

---

### Windows — Aufgabenplanung

1. `Win + S` → „Aufgabenplanung" → Enter
2. Rechts: **Einfache Aufgabe erstellen…**
3. Name vergeben (z. B. „Handball Buchung"), weiter
4. Trigger: **Wöchentlich**, Wochentag **Montag**, Uhrzeit des Buchungsstarts eintragen, weiter
5. Aktion: **Programm starten**, weiter
6. Programm/Skript: Pfad zu `python.exe` (z. B. `C:\Python311\python.exe`)
7. Argumente: `C:\Pfad\zu\anmeldungunihandball\anmeldung.py`
8. Starten in: `C:\Pfad\zu\anmeldungunihandball\`
9. Fertig stellen

> Wichtig: Haken bei **„Aufgabe mit höchsten Rechten ausführen"** setzen, damit die Aufgabe auch im Hintergrund läuft, wenn du nicht angemeldet bist.

---

## Was passiert bei einem Fehler?

Schlägt eine der Buchungsschritte fehl, speichert das Skript die Serverantwort als `fehler.html` im selben Ordner. Öffne diese Datei in einem Browser, um zu sehen, was schiefgelaufen ist (z. B. Kurs bereits ausgebucht, falsche Kursnummer, Buchung noch nicht geöffnet).

Bei erfolgreicher Buchung wird die Bestätigungsseite als `bestaetigung.html` gespeichert.

---

## Hinweis

Die Buchung wird **sofort und verbindlich** abgesendet, sobald du das Skript startest. Stelle sicher, dass alle Angaben korrekt sind, bevor du es ausführst.
