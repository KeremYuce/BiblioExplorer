import cv2
import pytesseract
import numpy as np
import json

        

# Funktion zur Verbesserung des Bildes für schwarzen Text auf hellem Hintergrund
def preprocess_black_text(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

# Funktion zur Verbesserung des Bildes für weißen Text auf dunklem Hintergrund
def preprocess_white_text(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    alpha, beta = 2.0, 50
    adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
    inverted = cv2.bitwise_not(adjusted)
    _, thresh = cv2.threshold(inverted, 150, 255, cv2.THRESH_BINARY)
    return thresh

# Funktion zur Durchführung der OCR innerhalb des markierten Bereichs
def perform_ocr(image):
    global rect_start, rect_end
    
    # Bild für schwarzen Text verarbeiten
    processed_black = preprocess_black_text(image)
    # OCR für schwarzen Text
    dpm_black = pytesseract.image_to_data(processed_black, output_type=pytesseract.Output.DICT)
    
    # Bild für weißen Text verarbeiten
    processed_white = preprocess_white_text(image)
    # OCR für weißen Text
    dpm_white = pytesseract.image_to_data(processed_white, output_type=pytesseract.Output.DICT)

    # Die Textinformationen und Bounding-Boxen extrahieren
    num_boxes_black = len(dpm_black['text'])
    for i in range(num_boxes_black):
        text = dpm_black['text'][i]
        if text.strip():  # Textblock ignorieren, wenn der Text leer ist
            (x, y, w, h) = (dpm_black['left'][i], dpm_black['top'][i], dpm_black['width'][i], dpm_black['height'][i])
            x1, y1 = rect_start
            x2, y2 = rect_end
            if (x + w >= x1 and x <= x2) and (y + h >= y1 and y <= y2):
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    num_boxes_white = len(dpm_white['text'])
    for i in range(num_boxes_white):
        text = dpm_white['text'][i]
        if text.strip():  # Textblock ignorieren, wenn der Text leer ist
            (x, y, w, h) = (dpm_white['left'][i], dpm_white['top'][i], dpm_white['width'][i], dpm_white['height'][i])
            x1, y1 = rect_start
            x2, y2 = rect_end
            if (x + w >= x1 and x <= x2) and (y + h >= y1 and y <= y2):
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Rote Farbe für weißen Text
                cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Zeige das Bild mit den Bounding-Boxen an
    cv2.imshow("OCR Output", image)
    cv2.waitKey(0)  # Warten, bis eine Taste gedrückt wird
    cv2.destroyAllWindows()  # Fenster schließen

# Funktion, um das Bild regelmäßig zu scannen und OCR auszuführen
def scan_image_regularly(image_path):
    global image
    image = cv2.imread(image_path)  # Bild einlesen
    if image is None:
        print("Fehler: Bild konnte nicht geladen werden.")
        return

    # Zeige das Bild an und ermögliche das Zeichnen eines Rechtecks
    cv2.imshow("Bild mit Auswahl", image)
    cv2.setMouseCallback("Bild mit Auswahl", draw_rectangle)
    cv2.waitKey(0)  # Warten auf eine Taste
    cv2.destroyAllWindows()  # Fenster schließen

    # OCR auf das Bild innerhalb des markierten Bereichs anwenden
    perform_ocr(image)



# lese Koordinaten ein
def koordinaten():
	with open("ecken.json", "r") as f:
		ecken = json.load(f)  # JSON-Daten einlesen
		print(f"Ecken aus der JSON-Datei: {ecken}")
		return ecken


def entzerren_bild(frame, ecken, sz=1024):

    w = np.sqrt((ecken[1][0] - ecken[0][0])**2 + (ecken[1][1] - ecken[0][1])**2)

    h = np.sqrt((ecken[3][0] - ecken[0][0])**2 + (ecken[3][1] - ecken[0][1])**2)
    
    aspekt = h / w
    
    breite = sz
    hoehe = int(sz * aspekt)
    ziel_koordinaten = np.array([
        [0, 0], 
        [breite - 1, 0], 
        [breite - 1, hoehe - 1], 
        [0, hoehe - 1]
    ], dtype=np.float32)

    ecken_array = np.array(ecken, np.float32)
    homographie_matrix, _ = cv2.findHomography(ecken_array, ziel_koordinaten)
    entzerrtes_bild = cv2.warpPerspective(frame, homographie_matrix, (breite, hoehe))

    return entzerrtes_bild




# Hauptprogramm
if __name__ == "__main__":

	
	cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Standardkamera
	if not cap.isOpened():
		print("Fehler: Kamera konnte nicht geöffnet werden.")
		exit(1)
		
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)  # Setze die Breite auf 1920 Pixel
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)

	cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
	

	frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
	frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

	print(f"Frame Höhe: {frame_height}")
	print(f"Frame Breite: {frame_width}")


	ecken = koordinaten()

	while True:
		ret, frame = cap.read()

		if not ret:
			print("Fehler: Kein Bild von der Kamera erhalten.")
			break
			
		quadrat = entzerren_bild(frame, ecken)
		# Zeige das Bild an
		cv2.imshow("Kamera Stream", quadrat)
		
		# OCR auf quadrat
		#perform_ocr(frame)

		# Beenden, wenn 'q' gedrückt wird
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

		if cv2.getWindowProperty("Kamera Stream", cv2.WND_PROP_VISIBLE) < 1:
			break

	cap.release()
	cv2.destroyAllWindows()

	# json-datei mit 4 Ecken einlesen
	
	# stream önnen
	
	# ewig bilder einlesen
	
	# bild mit Entzerrer entzeren 
	
	# anzeige des inneren.
	
	# OCR durchführen
