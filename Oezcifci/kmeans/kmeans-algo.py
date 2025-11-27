import cv2
import pytesseract
import numpy as np
from sklearn.cluster import KMeans

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

def calculate_center(x, y, w, h):
    center_x = x + w / 2
    center_y = y + h / 2
    return center_x, center_y



# Funktion zur Durchführung der OCR innerhalb des markierten Bereichs
def perform_ocr(image, output_file):
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
                # Berechne den Mittelpunkt der Bounding-Box
                center_x, center_y = calculate_center(x, y, w, h)
                
                # Koordinaten anzeigen und Kästchen im Bild zeichnen
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, f"({x}, {y})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(image, f"({int(center_x)}, {int(center_y)})", (int(center_x), int(center_y) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # Formatierte Ausgabe in die Ausgabedatei schreiben
                with open(output_file, 'a') as file:
                    file.write(f"----------------------------------------\n")
                    file.write(f"Erkannter Text: '{text}'\n")
                    file.write(f"Koordinaten: ({x}, {y}) - ({x + w}, {y + h})\n")
                    file.write(f"Mittelpunkt: ({int(center_x)}, {int(center_y)})\n")
                    file.write(f"----------------------------------------\n\n")

    num_boxes_white = len(dpm_white['text'])
    for i in range(num_boxes_white):
        text = dpm_white['text'][i]
        if text.strip():  # Textblock ignorieren, wenn der Text leer ist
            (x, y, w, h) = (dpm_white['left'][i], dpm_white['top'][i], dpm_white['width'][i], dpm_white['height'][i])
            x1, y1 = rect_start
            x2, y2 = rect_end
            if (x + w >= x1 and x <= x2) and (y + h >= y1 and y <= y2):
                # Berechne den Mittelpunkt der Bounding-Box
                center_x, center_y = calculate_center(x, y, w, h)
                
                # Koordinaten anzeigen und Kästchen im Bild zeichnen
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Rote Farbe für weißen Text
                cv2.putText(image, f"({x}, {y})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                cv2.putText(image, f"({int(center_x)}, {int(center_y)})", (int(center_x), int(center_y) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                
                # Formatierte Ausgabe in die Ausgabedatei schreiben
                with open(output_file, 'a') as file:
                    file.write(f"----------------------------------------\n")
                    file.write(f"Erkannter Text: '{text}'\n")
                    file.write(f"Koordinaten: ({x}, {y}) - ({x + w}, {y + h})\n")
                    file.write(f"Mittelpunkt: ({int(center_x)}, {int(center_y)})\n")
                    file.write(f"----------------------------------------\n\n")

    # Zeige das Bild mit den Bounding-Boxen und Mittelpunkten an
    cv2.imshow("OCR Output", image)
    cv2.waitKey(0)  # Warten, bis eine Taste gedrückt wird
    cv2.destroyAllWindows()  # Fenster schließen



def perform_clustering_with_buch(text_data, image, output_file):
    # Extrahiere die Y-Koordinaten der Bounding-Boxen
    y_coords = [data["y"] for data in text_data]
    bounding_boxes = [(data["x"], data["y"], data["w"], data["h"], data["text"], data["center_x"], data["center_y"]) for data in text_data]

    # K-Means Clustering auf den Y-Koordinaten durchführen
    kmeans = KMeans(n_clusters=3)  # Passe die Anzahl der Cluster nach Bedarf an
    y_coords = np.array(y_coords).reshape(-1, 1)  # Umwandeln in 2D für K-Means
    kmeans.fit(y_coords)

    # Cluster-Labels für die Bounding-Boxen
    labels = kmeans.labels_

    # Gruppiere die Boxen nach Clustern und zeichne sie auf das Bild
    sorted_boxes = sorted(zip(bounding_boxes, labels), key=lambda x: x[0][1], reverse=True)  # Sortiere nach der Y-Koordinate, von unten nach oben
    
    buch_number = 1  # Start der Buchnummer (von unten nach oben)

    for (x, y, w, h, text, center_x, center_y), cluster_label in sorted_boxes:
        # Bestimme die Farbe basierend auf dem Cluster
        color = (0, 255, 0) if cluster_label == 0 else (0, 0, 255) if cluster_label == 1 else (255, 0, 0)
        
        # Zeichne das Rechteck auf dem Bild
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

        # Berechne den Mittelpunkt der Bounding-Box
        cv2.putText(image, f"({x}, {y})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.putText(image, f"({int(center_x)}, {int(center_y)})", (int(center_x), int(center_y) - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Schreibe die OCR-Ergebnisse in die Ausgabedatei
        with open(output_file, 'a') as file:
            file.write(f"----------------------------------------\n")
            file.write(f"Erkannter Text: '{text}'\n")
            file.write(f"Koordinaten: ({x}, {y}) - ({x + w}, {y + h})\n")
            file.write(f"Mittelpunkt: ({int(center_x)}, {int(center_y)})\n")
            file.write(f"Buch : {buch_number}\n")  # Die Buchnummer hinzufügen
            file.write(f"----------------------------------------\n\n")

        buch_number += 1  # Erhöhe die Buchnummer für den nächsten Cluster

    # Rückgabe des Bildes mit den gezeichneten Bounding-Boxen
    return image









# Funktion, um das Bild regelmäßig zu scannen und OCR auszuführen
def scan_image_regularly(image_path, output_file):
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
    perform_ocr(image, output_file)




# Hauptprogramm
if __name__ == "__main__":
    image_path = 'stapel2.jpg'  # Bilddatei anpassen, falls nötig
    output_file = 'ocr_output.txt'  # Ausgabedatei

    # Die Ausgabedatei leeren, bevor neue Daten hinzugefügt werden
    open(output_file, 'w').close()

    # Bild regelmäßig scannen und den Bereich auswählen
    scan_image_regularly(image_path, output_file)
