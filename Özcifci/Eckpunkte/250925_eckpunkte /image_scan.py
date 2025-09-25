import cv2
import json
import numpy as np
import time

# Funktion: Perspektive korrigieren
def rectify_rectangle(img, points):
    pts = np.array(points, dtype="float32")

    # Zielgröße (kannst du anpassen je nach Buchformat)
    width, height = 500, 700
    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")

    # Transformationsmatrix & Warping
    M = cv2.getPerspectiveTransform(pts, dst)
    warped = cv2.warpPerspective(img, M, (width, height))
    return warped

# --- Schritt 1: Setup-Datei laden ---
with open("setup_corners.json", "r") as f:
    points = json.load(f)

print("Geladene Punkte:", points)

# --- Schritt 2: Bild laden ---
img = cv2.imread("buch.jpg")

# --- Schritt 3: Framerate messen (ein Frame) ---
start = time.time()
rectified = rectify_rectangle(img, points)
end = time.time()
fps = 1.0 / (end - start)
print(f"FPS (nur für dieses Frame): {fps:.2f}")

# --- Schritt 4: Fenster anzeigen ---
cv2.putText(img, f"FPS: {fps:.2f}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

cv2.imshow("Original", img)
cv2.imshow("Rectified", rectified)

cv2.waitKey(0)
cv2.destroyAllWindows()
