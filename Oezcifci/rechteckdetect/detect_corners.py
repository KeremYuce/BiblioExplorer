import cv2
import numpy as np

# Kamera öffnen
cap = cv2.VideoCapture(0)

while True:
    # Ein Bild von der Kamera erfassen
    ret, frame = cap.read()
    
    if not ret:
        print("Fehler: Kamera konnte nicht geöffnet werden.")
        break

    # Bild in Graustufen umwandeln
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Rauschunterdrückung
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Kanten mit Canny Edge Detection erkennen
    edges = cv2.Canny(blurred, 50, 150)

    # Konturen im Bild finden
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Durch alle gefundenen Konturen iterieren
    for contour in contours:
        # Um jedes Rechteck im Bild ein Rechteck ziehen
        epsilon = 0.02 * cv2.arcLength(contour, True)  # Genauigkeit anpassen
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Wenn es 4 Ecken hat, dann ist es ein Rechteck
        if len(approx) == 4:
            # Berechne die Fläche des Rechtecks
            area = cv2.contourArea(contour)
            
            # Filtere kleine Rechtecke heraus (z.B. Rauschen)
            if area > 1000:  # Mindestfläche, z.B. 1000 Pixel (je nach Bildgröße anpassen)
                # Rechteck zeichnen (x, y, Breite, Höhe)
                cv2.drawContours(frame, [approx], 0, (0, 255, 0), 3)

    # Bild anzeigen
    cv2.imshow('Detected Rectangles', frame)

    # Mit 'q' das Programm beenden
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Ressourcen freigeben und Fenster schließen
cap.release()
cv2.destroyAllWindows()
