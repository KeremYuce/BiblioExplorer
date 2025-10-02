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

# Funktion zur Verbesserung des Bildes vor der OCR
def preprocess_image(image):
    # Umwandlung in Graustufen
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Schwellwert, um den Kontrast zu verbessern
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    return thresh

# Funktion zur Durchführung der OCR innerhalb des markierten Bereichs
def perform_ocr(image):
    global rect_start, rect_end
    
    # Bild vorverarbeiten
    processed_image = preprocess_image(image)
    
    # OCR auf das gesamte Bild anwenden und Text sowie Positionen der Textblöcke extrahieren
    dpm = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)

    # Die Textinformationen und Bounding-Boxen extrahieren
    num_boxes = len(dpm['text'])
    for i in range(num_boxes):
        text = dpm['text'][i]
        if text.strip():  # Textblock ignorieren, wenn der Text leer ist
            # Extrahiere die Koordinaten der Bounding-Box
            (x, y, w, h) = (dpm['left'][i], dpm['top'][i], dpm['width'][i], dpm['height'][i])

            # Überprüfe, ob die Bounding-Box innerhalb des markierten Bereichs liegt (flexibler)
            x1, y1 = rect_start
            x2, y2 = rect_end
            if (x + w >= x1 and x <= x2) and (y + h >= y1 and y <= y2):  # Überlappung statt vollständiger Eingrenzung
                # Zeichne das Rechteck auf dem Bild
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # Zeichne den erkannten Text über der Bounding-Box
                cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Zeige das Bild mit den Bounding-Boxen an
    cv2.imshow("OCR Output", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

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
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # OCR auf das Bild innerhalb des markierten Bereichs anwenden
    perform_ocr(image)

# Hauptprogramm
if __name__ == "__main__":
    image_path = 'stapel2.jpg'  # Bilddatei anpassen, falls nötig

    # Bild regelmäßig scannen und den Bereich auswählen
    scan_image_regularly(image_path)
