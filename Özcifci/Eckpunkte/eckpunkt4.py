import cv2
import numpy as np
import math

# Variable für die Ecken
points = []

# Funktion, um die Punkte im Uhrzeigersinn zu sortieren
def order_points_clockwise(pts):
    pts = np.array(pts, dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1).reshape(4)
    tl = pts[np.argmin(s)]  # Oben links
    br = pts[np.argmax(s)]  # Unten rechts
    tr = pts[np.argmin(diff)]  # Oben rechts
    bl = pts[np.argmax(diff)]  # Unten links
    return np.array([tl, tr, br, bl], dtype="float32")

# Berechnung der euklidischen Distanz
def euclid(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# Funktion für die Perspektivkorrektur
def rectify_rectangle(image, src_pts):
    src = order_points_clockwise(src_pts)  # Ecken im Uhrzeigersinn sortieren

    # Berechnung der Kantenlängen
    widthA = euclid(src[2], src[3])  # br-bl
    widthB = euclid(src[1], src[0])  # tr-tl
    measured_w = max(widthA, widthB)

    heightA = euclid(src[1], src[2])  # tr-br
    heightB = euclid(src[0], src[3])  # tl-bl
    measured_h = max(heightA, heightB)

    # Bestimmen der Zielgröße des Rechtecks
    W = max(1, int(round(measured_w)))
    H = max(1, int(round(measured_h)))

    # Zielrechteck definieren
    dst = np.array([
        [0, 0],  # Oben links
        [W - 1, 0],  # Oben rechts
        [W - 1, H - 1],  # Unten rechts
        [0, H - 1]  # Unten links
    ], dtype="float32")

    # Berechnung der Homographie-Matrix
    H_mat, _ = cv2.findHomography(src, dst, cv2.RANSAC)

    # Anwendung der Perspektivtransformation
    warped = cv2.warpPerspective(image, H_mat, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    return warped

# Funktion, um die Punkte interaktiv auszuwählen
def click_event(event, x, y, flags, param):
    global points
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Nur Punkte hinzufügen, wenn weniger als 4 ausgewählt sind
        if len(points) < 4:
            points.append((x, y))  # Punkt hinzufügen
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)  # Punkt auf dem Bild markieren
            cv2.imshow("Select Points", img)
        
        # Sobald 4 Punkte ausgewählt sind, die Perspektive korrigieren
        if len(points) == 4:
            print("Ausgewählte Punkte:", points)  # Debugging: Punkte ausgeben
            rectified = rectify_rectangle(img, points)
            
            # Das resultierende Bild in Originalgröße anzeigen
            cv2.imshow("Rectified Image", rectified)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

# Bild einlesen
img = cv2.imread('buch.jpg')

# Bild anzeigen und Punkte auswählen
cv2.imshow("Select Points", img)
cv2.setMouseCallback("Select Points", click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()
