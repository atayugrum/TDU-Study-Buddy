# 📚 StudyBuddy – Smarter Studienassistent

Ein Raspberry Pi-basiertes IoT-Projekt, das die Qualität der Lernumgebung in Echtzeit bewertet, um die Konzentrationsbedingungen für Lernende und im Homeoffice Tätige zu optimieren.

> Dieses Projekt wurde im Rahmen des INF208 Abschlussprojekts an der Türkisch-Deutschen Universität entwickelt. Es erfasst und analysiert Umgebungsdaten wie Temperatur, Licht und Geräuschpegel, um die Effizienz der Lernumgebung zu steigern. Abweichungen von idealen Bedingungen werden dem Nutzer sowohl visuell über ein LED-System als auch per Benachrichtigung über einen Telegram-Bot mitgeteilt.

---

## 📑 Inhaltsverzeichnis
1. [Ziel des Projekts](#1-ziel-des-projekts)  
2. [Funktionen und Merkmale](#2-funktionen-und-merkmale)  
3. [Verwendete Hardware](#3-verwendete-hardware)  
4. [Software und Installation](#4-software-und-installation)  
5. [Ausführung](#5-ausführung)  
6. [Code-Struktur](#6-code-struktur)  
7. [Zukünftige Erweiterungen](#7-zukünftige-erweiterungen)  
8. [Projektteam](#8-projektteam)  
9. [Lizenz](#9-lizenz)  

---

## 1. Ziel des Projekts

In der heutigen Zeit ist die physische Umgebung ein entscheidender Faktor für effizientes Lernen. Eine ungeeignete Umgebung kann die Konzentration stören und die Lernqualität erheblich beeinträchtigen.  
Das Hauptziel von **StudyBuddy** ist es, diese Lücke zu schließen, indem es eine **kostengünstige** und **benutzerfreundliche** Lösung zur Analyse und Verbesserung der Lernumgebung bietet.

Das System richtet sich insbesondere an:
- Studierende  
- Bibliotheksnutzer  
- Personen im Homeoffice  
- Lehrkräfte und Eltern (zur Bewertung von Lernbedingungen)

---

## 2. Funktionen und Merkmale

### 🕒 Echtzeit-Analyse
Das System erfasst und analysiert **alle 5 Sekunden** die Umgebungsdaten, um ein kontinuierliches Feedback zu gewährleisten.

### 📡 Ganzheitliche Sensordaten-Auswertung
Simultane Auswertung von:
- Temperatur (DHT11)
- Licht (LDR)
- Geräusch (KY-038)

### 🌡️ Stabile Temperaturmessung
Ein **gleitender Mittelwertfilter** glättet die Temperaturdaten, um kurzfristige Schwankungen zu minimieren.

### 💡 Intuitives LED-Feedback (Farbleitsystem)
- 🟢 **Grüne LED**: Alle Bedingungen sind ideal  
- 🟡 **Gelbe LED**: Eine Bedingung weicht vom Idealzustand ab  
- 🔴 **Rote LED**: Zwei oder mehr Bedingungen sind nicht ideal  

### 🤖 Intelligente Telegram-Bot-Integration
- **Proaktive Warnmeldungen**: Automatisch bei Verschlechterung einer Bedingung  
- **Statusabfrage**: Befehl `/status` liefert aktuellen Umgebungsstatus  
- **Robuste Fehlerbehandlung**: Try-Except bei Temperaturmessung  

### 🧠 Optimierte Leistung
- CPU-Auslastung: unter 70%  
- RAM-Auslastung: unter 80%  
- Sensorabfrage läuft in einem separaten Thread (keine Bot-Blockade)

---

## 3. Verwendete Hardware

| Komponente          | Beschreibung                     |
|---------------------|----------------------------------|
| Raspberry Pi        | Hauptprozessor                   |
| DHT11               | Temperatursensor                 |
| KY-038              | Geräuschsensor                   |
| LDR                 | Lichtsensor                      |
| LEDs                | Grün, Gelb, Rot als Aktoren      |
| Sonstiges           | Breadboard, Jumper-Kabel, Widerstände |

---

## 4. Software und Installation

### Voraussetzungen
- Raspberry Pi mit Raspberry Pi OS  
- Internetverbindung  

### Installationsschritte

```bash
# 1. Klonen des Projekts
git clone https://github.com/atayugrum/TDU-Study-Buddy.git
cd TDU-Study-Buddy

# 2. Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate

# 3. Erforderliche Bibliotheken installieren
pip install RPi.GPIO adafruit-circuitpython-dht python-telegram-bot requests

# 4. Konfiguration
# Öffne die Datei config.py mit einem Texteditor
# Füge deinen Telegram-Bot-Token und deine Chat-ID ein

```
## 5. Ausführung


# Stelle sicher, dass die virtuelle Umgebung aktiv ist
python StudyBuddy.py
💡 Hinweis: Ersetze StudyBuddy.py durch den tatsächlichen Dateinamen deiner Hauptdatei.
❌ Beenden: Drücke STRG + C im Terminal, um das Programm zu stoppen.

## 6. Code-Struktur

Die Software wurde nach dem Prinzip der **modularen Programmierung** entwickelt, um Lesbarkeit und Wartbarkeit zu maximieren. Die Hauptfunktionen sind:

- `setup_gpio()`: Initialisiert alle GPIO-Pins.
- `get_sensor_states()`: Liest die Rohdaten aller Sensoren, wendet Filter an und gibt verarbeitete Zustände zurück.
- `update_leds(states)`: Steuert die LEDs basierend auf der Anzahl der nicht-idealen Bedingungen.
- `check_and_send_alerts(states)`: Vergleicht den aktuellen Zustand mit dem vorherigen und sendet bei Bedarf Telegram-Warnungen.
- `send_telegram_alert(message)`: Hilfsfunktion zum Versenden von Nachrichten über die Telegram API.
- `start(), status()`: Asynchrone Funktionen zur Verarbeitung von Benutzerbefehlen im Telegram-Bot.
- `sensor_loop()`: Hauptschleife, die in einem separaten Thread läuft, um kontinuierliche Sensorüberwachung zu gewährleisten.

---

## 7. Zukünftige Erweiterungen

Dank des modularen Aufbaus bietet das Projekt eine solide Grundlage für weitere Entwicklungen. Mögliche Erweiterungen:

- 🌫️ **Integration zusätzlicher Sensoren:**
  - Luftfeuchtigkeit (z. B. DHT22)
  - Luftqualität (z. B. CO₂, VOC)
- ☁️ **Cloud-Anbindung:**
  - Über MQTT oder HTTP-Protokolle zur externen Datenspeicherung und Analyse
- 📱 **Mobile Anwendung:**
  - Zur Visualisierung der Daten, Push-Benachrichtigungen und Fernsteuerung
- 🧠 **Machine Learning:**
  - Erkennung von Mustern und Vorhersage von Konzentrationsstörungen

---

## 8. Projektteam

**Dieses Projekt wurde im Sommersemester 2024–25** im Rahmen des Kurses INF208 an der **Türkisch-Deutschen Universität** entwickelt.

**Teammitglieder:**

- Engin DENİZ (190504033)  
- Arda ARIK (190504042)  
- Ata YÜĞRÜM (190501037)  
- Sude BALKAN (200504050)  

👨‍🏫 **Betreuer:** Prof. Dr. Murat BEKEN

---

## 9. Lizenz

Dieses Projekt steht unter der **MIT License**.  
Die genauen Lizenzbedingungen findest du in der Datei `LICENSE` im Repository.

