import cv2 as cv
import numpy as np
import json

ecken = []
maus_pos = (0, 0) 

def mausklick(event, x, y, flags, param):
    global ecken, maus_pos, frame_width, frame_height
    
    if event == cv.EVENT_MOUSEMOVE:
        maus_pos = (x, y)

    if event == cv.EVENT_LBUTTONDOWN:
        ecken.append((x, y))
        
        if len(ecken) == 4:
            echte_ecken = []
            for ex, ey in ecken:
                orig_x, orig_y = umrechnung_koordinaten(ex, ey, frame_width, frame_height, 1920, 1080)
                echte_ecken.append((orig_x, orig_y))
            
            with open("ecken.json", "w") as f:
                json.dump(echte_ecken, f)
                print(f"Erfolg: 4K-Koordinaten gespeichert: {echte_ecken}")
          
            cv.destroyAllWindows()
            exit(0)

def umrechnung_koordinaten(x, y, original_width, original_height, scaled_width, scaled_height):
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
    
    cv.namedWindow("Bild mit Auswahl")
    cv.setMouseCallback("Bild mit Auswahl", mausklick)

    while True:
        ret, image = cap.read()
        if not ret:
            break

        scaled_live = cv.resize(image, (1920, 1080))

    
        for i, pkt in enumerate(ecken):
            cv.ellipse(scaled_live, pkt, (10, 10), 0, 0, 360, (255, 0, 0), 5)
            if i > 0:
                cv.line(scaled_live, ecken[i-1], ecken[i], (0, 255, 0), 3)

        # Gummiband-Effekt zur aktuellen Mausposition
        if 0 < len(ecken) < 4:
            cv.line(scaled_live, ecken[-1], maus_pos, (255, 255, 0), 3)

        cv.imshow("Bild mit Auswahl", scaled_live)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break
            
        if cv.getWindowProperty("Bild mit Auswahl", cv.WND_PROP_VISIBLE) < 1:
            break


    cv.destroyAllWindows()
