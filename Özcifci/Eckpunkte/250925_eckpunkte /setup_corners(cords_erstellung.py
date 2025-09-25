import cv2
import json

points = []
scale = 1.0

def click_event(event, x, y, flags, param):
    global points, scale
    if event == cv2.EVENT_LBUTTONDOWN:
        # Nur Punkte hinzufügen, wenn weniger als 4 ausgewählt sind
        if len(points) < 4:
            # Mauskoordinaten zurückrechnen auf Originalgröße
            orig_x, orig_y = int(x / scale), int(y / scale)
            points.append((orig_x, orig_y))  

            # Punkt im Anzeige-Bild markieren
            cv2.circle(display_img, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Select Points", display_img)
        
        # Sobald 4 Punkte ausgewählt sind
        if len(points) == 4:
            print("Ausgewählte Punkte (Originalauflösung):", points)

            # Setup-Datei speichern
            with open("setup_corners.json", "w") as f:
                json.dump(points, f, indent=4)
            print("Setup-Datei gespeichert: setup_corners.json")

            # Beispiel: Perspektive korrigieren
            # rectified = rectify_rectangle(img, points)
            # cv2.imshow("Rectified Image", rectified)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

# Bild einlesen
img = cv2.imread('buch.jpg')

# Bildschirmgrenze festlegen
max_width, max_height = 1280, 720
h, w = img.shape[:2]
scale = min(max_width / w, max_height / h, 1.0)

# Bild für Anzeige skalieren
display_img = cv2.resize(img, (int(w * scale), int(h * scale)))

# Bild anzeigen und Punkte auswählen
cv2.imshow("Select Points", display_img)
cv2.setMouseCallback("Select Points", click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()
