# Brainstorming 4.9.2025

## Arbeitsteile:

1. Datenbank
1. Kamera verbinden
1. Segmentieren
	- Buchrücken
	- Ort
1. OCR eines Buchrückens
1. DB mit Büchern
1. DB-Oberfläche

## User Stories:

- Ich suche ein Buch "xyz" und bekomme die Information, wo das Buch ist.
- Ich nehme ein Buch weg
- Ich bringe ein bekanntes Buch zurück
- Ich stelle ein neues Buch hinein
- Ich will ein Buch permanent wegnehmen.

## Systemkomponenten:

1. Kamera
1. Computer für die Kamera + ML
1. Computer Datenbank
1. Computer Webseite / Display

## Werkzeuge

- Programmiersprache für Kamera und OCR mit ML
- Web-Programmier-Sprache
- Versionverwaltung
	- git und github
	- github desktop
	- Maintainer: Yüce
	- Contributoren: Saleh, Özcifci, Nikolic, WOR

 ## Infos zur Projektion:

 [ChatGPT richtig gefragt](https://chatgpt.com/share/68c7bf1a-b96c-8002-810a-71add16e1886)

PS: ```git clone ssh://git@github.com/KeremYuce/BiblioExplorer.git```
 
 
# Arbeitsauftrag 25.9.2025:

*Aus der Email-Konversation:*

Ja, ich bin leider krank geworden. Ein Virus streckt mich für diese Woche nieder.

## Die Punkte-Erkennung sollte in 2 Phasen laufen:

1. Ein Programm z.B. „setup_corners.py“ misst die Ecken aus und speichert die Koordinaten in einer Setup-Datei.
  Zu große Bilder sollen in der Darstellung auf maximal Bildschirmgröße skaliert werden,
  die Koordinaten beziehen sich natürlich auf die Original-Auflösung (Mauskoordinaten zurückscalieren)

2. Ein anderes Programm z.B. „image_scan.py“ liest die Einstellungen und wandelt die Bilder
  permanent um. Endlos, bis es gestoppt wird.
  Als Ausgabe könnte man ein Fenster machen, in dem
	- das Original-Bild und
	- der rechteckige Ausschnitt dargestellt wird.
  Die Framerate sollte hoch sein. Die Zeit zwischen den Frames (inverse der Framerate) könnte
  man auf der Konsole (print) oder auch auf dem Schirm ausgeben.

**Neu und separat:**

3. Machen Sie ein Foto von einem Stapel Bücher. Dieses Foto soll mit OpenCV
  eingelesen werden und mit Hilfe einer OCR sollen alle Texte extrahiert werden.
  Schnelle google-Suche:
  https://www.geeksforgeeks.org/python/text-detection-and-extraction-using-opencv-and-ocr/

4. Welche Daten liefert die OCR? Kann man die einzelnen Texte sinnvoll trennen?

5. Das Bild im Original, dann 90, 180 und 270 Grad gedreht analysieren (alles in OpenCV)

## Die Datenbank-Gruppe

kann sich darum kümmern, in Python (flask) oder Javascript (node.js) oder PHP (apache2) eine
Web-Oberfläche laufen zu lassen.

Zeichnen Sie zuerst ein vereinfachtes Datenbank-Schema für eine SQL-Datenbank (z.B. sqlite), die
Bücher und Standorte verwaltet.

Die Weboberfläche soll dann einen einfachen Zugriff darauf haben.

# Arbeit 2.10.2025

**OCR-Gruppe**

1. Git organisieren + Namen Ändern 

2. Testfoto: OCR anstoßen (in python) und versuchen, alle vorkommenden Textblöcke zu erfassen. -> Liste mit Text und bounding-box 

3. Integration der OCR in das Programm "image_scan.py"
   (regelmäßig wird ein Bild gescannt und die OCR angeschubst)

**DB-Gruppe**

1. DB-Schema in SQL

2. Wahl der Software: python mit flask und sqlite3

3. **User-Stories** für die Verwendung der Datenbank

4. **Frontend**: Evtl. ein kleines Framework (javascript) oder in Handarbeit w3schools.com

# Arbeit 9.10.2025

**OCR-Gruppe**

1. Vereinfachen der mehreren Programme (S/W und W/S) in eines

2. Versuche, das `dict` Dictioanry mit den Ergennissen auszugeben

3. Räumliches Clustering der Texte mit einem K-Means Algorithmus

**DB-Gruppe**

1. Installation XAMPP

2. Erstellen einer Demo-DB mit phpmyadmin

3. 2 Varianten:

    A. Eine PHP-Seite "altmodisch.php", die die Daten direkt in eine HTML-Tabelle schreibt.
    
    B. Eine Leere HTML-Seite "neumodisch.html" mit Javascript. Das Script holt die Daten über eine Hilfs-PHP-Seite "daten.json.php", welche die Daten als JSON verpackt ausliefert. Im Client (JS) werden die Daten in die leere Tabelle eingefügt.

# Arbeit 16.10.2025

**OCR-Gruppe**

- Gruppierung der Wortfetzen mit dem K-Means Algorithmus (siehe Vorwoche)

- Readme.md um die Software installieren und starten zu können (mit venv)
 
**DB-Gruppe**

- Erstellen einer sauberen Datenbank mit Probebüchern

- Eintragen von 4 Büchern über eine DB-Oberfläche

- evtl. Eintragen über die ISBN und holen der Daten aus dem Internet via z.B. Amazon-API

# Arbeiten 27.11.2025

**DB-Gruppe**

- DB-Probleme korrigieren