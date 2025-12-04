import cv2
import pytesseract
import numpy as np

# Globale Variablen für die rechteckige Auswahl
rect_start = None
rect_end = None
drawing = False
image = None

# Funktion zum Zeichnen des Rechtecks mit der Maus
def draw_rectangle(event, x, y, flags, param):
    global rect_start, rect_end, drawing, image

    if event == cv2.EVENT_LBUTTONDOWN:
        # Wenn der linke Button gedrückt wird, Start des Rechtecks
        drawing = True
        rect_start = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        # Temporäres Rechteck beim Ziehen anzeigen
        if drawing:
            rect_end = (x, y)
            temp_image = image.copy()
            cv2.rectangle(temp_image, rect_start, rect_end, (0, 255, 0), 2)
            cv2.imshow("Bild mit Auswahl", temp_image)

    elif event == cv2.EVENT_LBUTTONUP:
        # Wenn der Button losgelassen wird, das Rechteck finalisieren
        drawing = False
        rect_end = (x, y)
        cv2.rectangle(image, rect_start, rect_end, (0, 255, 0), 2)
        cv2.imshow("Bild mit Auswahl", image)

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

# Hauptprogramm
if __name__ == "__main__":
    image_path = 'stapel2.jpg'  # Bilddatei anpassen, falls nötig

    # Bild regelmäßig scannen und den Bereich auswählen
    scan_image_regularly(image_path)
