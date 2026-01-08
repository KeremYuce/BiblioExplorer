import cv2 as cv
import numpy as np
import json

ecken = []

# Funktion zum Zeichnen des 4-Ecks mit der Maus
def mausklick(event, x, y, flags, param):
    global scaled_image, ecken, frame_width, frame_height

    if event == cv.EVENT_LBUTTONDOWN:
        # 1. Speichere Klick für Anzeige
        ecken.append((x, y))
        
        # 2. Wenn 4 Ecken voll sind: Umrechnen und Speichern
        if len(ecken) == 4:
            echte_ecken = []
            for ex, ey in ecken:
                orig_x, orig_y = umrechnung_koordinaten(ex, ey, frame_width, frame_height, 1920, 1080)
                echte_ecken.append((orig_x, orig_y))
            
            with open("ecken.json", "w") as f:
                json.dump(echte_ecken, f)
                print(f"Erfolg: 4K-Koordinaten gespeichert: {echte_ecken}")
            exit(0)
        
        # Zeichnen
        cv.ellipse(scaled_image, (x, y), (10, 10), 0, 0, 360, (255, 0, 0), 5)
        eckeni32 = np.array(ecken, np.int32)
        eckeni32_shaped = eckeni32.reshape((-1, 1, 2))
        cv.polylines(scaled_image, [eckeni32_shaped], isClosed=False, color=(0, 255, 0), thickness=3)
        cv.imshow("Bild mit Auswahl", scaled_image)

    elif event == cv.EVENT_MOUSEMOVE:  # <-- Dieses 'elif' muss bündig mit 'if event == cv.EVENT_LBUTTONDOWN:' sein
        if len(ecken) > 0:
            line_start = ecken[-1]
            line_end = (x, y)
            temp_image = scaled_image.copy()
            cv.line(temp_image, line_start, line_end, (255, 255, 0), 3)
            cv.imshow("Bild mit Auswahl", temp_image)

def umrechnung_koordinaten(x, y, original_width, original_height, scaled_width, scaled_height):
    # Berechnet die Originalkoordinaten aus den skalierten Koordinaten
    orig_x = int(x * original_width / scaled_width)
    orig_y = int(y * original_height / scaled_height)
    return orig_x, orig_y
    

    


# Hauptprogramm
if __name__ == "__main__":

    cap = cv.VideoCapture(0, cv.CAP_V4L2)
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        exit(1)

    cap.set(cv.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 2160)
    cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    frame_height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
    frame_width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
    print(f"Frame Höhe: {frame_height}")
    print(f"Frame Breite: {frame_width}")
        
    ret, image = cap.read()
    if not ret:
        print("Fehler: Kein Bild von der Kamera erhalten.")
        exit(1)

    
    scaled_image = cv.resize(image, (1920, 1080))

    
    cv.imshow("Bild mit Auswahl", scaled_image)
    cv.setMouseCallback("Bild mit Auswahl", mausklick)

    while True:
        if cv.waitKey(1) & 0xFF == ord('q'):  # 'q' zum Beenden
            break
        if cv.getWindowProperty("Bild mit Auswahl", cv.WND_PROP_VISIBLE) < 1:
            break

    cv.destroyAllWindows()  # Fenster schließen
    exit(0)
