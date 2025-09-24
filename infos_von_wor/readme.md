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

1) Ein Programm z.B. „setup_corners.py“ misst die Ecken aus und speichert die Koordinaten in einer Setup-Datei.
  Zu große Bilder sollen in der Darstellung auf maximal Bildschirmgröße skaliert werden,
  die Koordinaten beziehen sich natürlich auf die Original-Auflösung (Mauskoordinaten zurückscalieren)

2) Ein anderes Programm z.B. „image_scan.py“ liest die Einstellungen und wandelt die Bilder
  permanent um. Endlos, bis es gestoppt wird.
  Als Ausgabe könnte man ein Fenster machen, in dem
	- das Original-Bild und
	- der rechteckige Ausschnitt dargestellt wird.
  Die Framerate sollte hoch sein. Die Zeit zwischen den Frames (inverse der Framerate) könnte
  man auf der Konsole (print) oder auch auf dem Schirm ausgeben.

**Neu und separat:**

3) Machen Sie ein Foto von einem Stapel Bücher. Dieses Foto soll mit OpenCV
  eingelesen werden und mit Hilfe einer PCR sollen alle Texte extrahiert werden.
  Schnelle google-Suche:
  https://www.geeksforgeeks.org/python/text-detection-and-extraction-using-opencv-and-ocr/

4) Welche Daten liefert die OCR? Kann man die einzelnen Texte sinnvoll trennen?

5) Das Bild im Original, dann 90, 180 und 270 Grad gedreht analysieren (alles in OpenCV)

## Die Datenbank-Gruppe

kann sich darum kümmern, in Python (flask) oder Javascript (node.js) oder PHP (apache2) eine
Web-Oberfläche laufen zu lassen.

Zeichnen Sie zuerst ein vereinfachtes Datenbank-Schema für eine SQL-Datenbank (z.B. sqlite), die
Bücher und Standorte verwaltet.

Die Weboberfläche soll dann einen einfachen Zugriff darauf haben.
