import cv2 as cv
import numpy as np
import json
import sys

ecken = []
maus_pos = (0, 0)
scale_percent = 25 # Hier definieren!

def mausklick(event, x, y, flags, param):
    global ecken, maus_pos, frame_width, frame_height, scale_percent
    
    if event == cv.EVENT_MOUSEMOVE:
        maus_pos = (x, y)

    if event == cv.EVENT_LBUTTONDOWN:
        ecken.append((x, y))
        
        if len(ecken) == 4:
            echte_ecken = []
            # Umrechnung zurück auf 4K
            faktor = scale_percent / 100
            
            for ex, ey in ecken:
                orig_x = int(ex / faktor)
                orig_y = int(ey / faktor)
                echte_ecken.append((orig_x, orig_y))
            
            with open("ecken.json", "w") as f:
                json.dump(echte_ecken, f)
                print(f"Erfolg: 4K-Koordinaten gespeichert: {echte_ecken}")
          
            cv.destroyAllWindows()
            sys.exit(0) # Sicherer Exit für Skripte

def umrechnung_koordinaten(x, y, original_width, original_height, scaled_width, scaled_height):
    orig_x = int(x * original_width / scaled_width)
    orig_y = int(y * original_height / scaled_height)
    return orig_x, orig_y

# Hauptprogramm
if __name__ == "__main__":
    cap = cv.VideoCapture(0, cv.CAP_V4L2)
    if not cap.isOpened():
        print("Error: Kamera nicht gefunden.")
        sys.exit(1)

    # 4K Auflösung setzen
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 2160)
    cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    # Tatsächliche Werte von der Kamera abfragen
    frame_width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
    frame_height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
    
    cv.namedWindow("Bild mit Auswahl")
    cv.setMouseCallback("Bild mit Auswahl", mausklick)

    while True:
        ret, image = cap.read()
        if not ret or image is None: 
            break

        
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        resized_view = cv.resize(image, (width, height), interpolation=cv.INTER_AREA)

       
        for i, pkt in enumerate(ecken):
            cv.circle(resized_view, pkt, 5, (255, 0, 0), -1)
            if i > 0:
                cv.line(resized_view, ecken[i-1], ecken[i], (0, 255, 0), 2)

       
        if 0 < len(ecken) < 4:
            cv.line(resized_view, ecken[-1], maus_pos, (255, 255, 0), 2)

        cv.imshow("Bild mit Auswahl", resized_view)

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
            

        if cv.getWindowProperty("Bild mit Auswahl", cv.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv.destroyAllWindows()
