import cv2 as cv
import pytesseract
import numpy as np
import json



ecken = []

# Funktion zum Zeichnen des 4-Eck mit der Maus
def mausklick(event, x, y, flags, param):
    global rect_start, rect_end, drawing, image

    if event == cv.EVENT_LBUTTONDOWN:
        # Wenn der linke Button gedrückt wird, Start des Rechtecks
        drawing = True
        ecken.append((x,y))
        
        if len(ecken) == 4:
            with open("ecken.json", "w") as f:
                json.dump(ecken, f)
                print("Corners Writte into ecken.json")
            exit(0)
        
        cv.ellipse(image, (x,y), (10,10), 0, 0, 360, (255, 0, 0) , 5)
        
        eckeni32 = np.array(ecken, np.int32)

        # Reshape für die cv.polylines Funktion (NumPy Array muss 1D für die Polylines-Funktion sein)
        eckeni32_shaped = eckeni32.reshape((-1, 1, 2))

        # Zeichne das Polygon
        cv.polylines(image, [eckeni32_shaped], isClosed=False, color=(0, 255, 0), thickness=3)

        
        cv.imshow("Bild mit Auswahl", image)
    # elis event == cv.
    elif event == cv.EVENT_MOUSEMOVE:
        # Temporäres Rechteck beim Ziehen anzeigen
        if len(ecken)>0:
            line_start = ecken[-1]  # letztes Element
            line_end = (x, y)
            temp_image = image.copy()
            cv.line(temp_image, line_start, line_end, (255, 255, 0), 3)
            cv.imshow("Bild mit Auswahl", temp_image)

global image

# Hauptprogramm
if __name__ == "__main__":

    # XXX: Kamera

    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        exit(1)

    ret, image = cap.read()  # Bild von der Kamera lesen
    
    if not ret:
        print("Fehler: Kein Bild von der Kamera erhalten.")
        exit(1)

    # Zeige das Bild an und ermögliche das Zeichnen eines Rechtecks
    cv.imshow("Bild mit Auswahl", image)
    cv.setMouseCallback("Bild mit Auswahl", mausklick)

    while True:
        if cv.waitKey(1) & 0xFF == ord('q'):  # 'q' zum Beenden
            break
        # Get the current status of the window (property 1 is the window visibility)
        if cv.getWindowProperty("Bild mit Auswahl", cv.WND_PROP_VISIBLE) < 1:
            break
    cv.destroyAllWindows()  # Fenster schließen
    exit(0)
