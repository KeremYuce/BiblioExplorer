import cv2
import pytesseract
import numpy as np
import json

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

# Funktion zur Durchführung der OCR innerhalb des markierten Bereichs
def perform_ocr(image):
    # 1. Vorverarbeitung
    processed_black = preprocess_black_text(image)
    processed_white = preprocess_white_text(image)
    
    # 2. OCR Daten extrahieren (als Dictionary)
    dpm_black = pytesseract.image_to_data(processed_black, output_type=pytesseract.Output.DICT)
    dpm_white = pytesseract.image_to_data(processed_white, output_type=pytesseract.Output.DICT)

    # 3. Schwarzen Text verarbeiten (Grüne Boxen)
    for i in range(len(dpm_black['text'])):
        text = dpm_black['text'][i]
        conf = int(dpm_black['conf'][i])
        
        if text.strip() and conf > 40: # Nur Text mit über 40% Sicherheit
            (x, y, w, h) = (dpm_black['left'][i], dpm_black['top'][i], dpm_black['width'][i], dpm_black['height'][i])
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # 4. Weißen Text verarbeiten (Rote Boxen)
    for i in range(len(dpm_white['text'])):
        text = dpm_white['text'][i]
        conf = int(dpm_white['conf'][i])
        
        if text.strip() and conf > 40:
            (x, y, w, h) = (dpm_white['left'][i], dpm_white['top'][i], dpm_white['width'][i], dpm_white['height'][i])
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    return image

# Lese Koordinaten ein
def koordinaten():
    with open("ecken.json", "r") as f:
        ecken = json.load(f)  # JSON-Daten einlesen
        print(f"Ecken aus der JSON-Datei: {ecken}")
        return ecken

def sortiere_ecken(pts):
    # Sortiert die Punkte: [Oben-Links, Oben-Rechts, Unten-Rechts, Unten-Links]
    pts = np.array(pts, dtype="float32")
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def entzerren_bild(frame, ecken, sz=1280):
    ecken_sortiert = sortiere_ecken(ecken)

    w1 = np.linalg.norm(ecken_sortiert[1] - ecken_sortiert[0])
    w2 = np.linalg.norm(ecken_sortiert[2] - ecken_sortiert[3])
    h1 = np.linalg.norm(ecken_sortiert[3] - ecken_sortiert[0])
    h2 = np.linalg.norm(ecken_sortiert[2] - ecken_sortiert[1])
    
    breite_original = max(int(w1), int(w2))
    hoehe_original = max(int(h1), int(h2))

    if breite_original > hoehe_original:
        ziel_w = int(sz * (hoehe_original / breite_original))
        ziel_h = sz

        ziel_koordinaten = np.array([
            [ziel_w - 1, 0],        
            [ziel_w - 1, ziel_h - 1],  
            [0, ziel_h - 1],            
            [0, 0]                
        ], dtype=np.float32)
    else:
        # Falls es schon hochkant ist, nur skalieren
        ziel_w = sz
        ziel_h = int(sz * (hoehe_original / breite_original))
        ziel_koordinaten = np.array([
            [0, 0],
            [ziel_w - 1, 0],
            [ziel_w - 1, ziel_h - 1],
            [0, ziel_h - 1]
        ], dtype=np.float32)

    # 4. Transformation
    matrix = cv2.getPerspectiveTransform(ecken_sortiert, ziel_koordinaten)
    entzerrtes_bild = cv2.warpPerspective(frame, matrix, (ziel_w, ziel_h))

    return entzerrtes_bild

# Hauptprogramm
if __name__ == "__main__":
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Standardkamera
    if not cap.isOpened():
        print("Fehler: Kamera konnte nicht geöffnet werden.")
        exit(1)
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    
    frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    print(f"Frame Höhe: {frame_height}")
    print(f"Frame Breite: {frame_width}")

    ecken = koordinaten()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Fehler: Kein Bild von der Kamera erhalten.")
            break
            
        quadrat = entzerren_bild(frame, ecken)
        
        # Skalierung für die Anzeige
        scale_percent = 75
        width = int(quadrat.shape[1] * scale_percent / 100)
        height = int(quadrat.shape[0] * scale_percent / 100)
        display_size = (width, height)
        resized_quadrat = cv2.resize(quadrat, display_size, interpolation=cv2.INTER_AREA)

        rotated_image = cv2.rotate(resized_quadrat, cv2.ROTATE_180)
        
        # 3. OCR auf dem gedrehten Bild durchführen
        ocr_bild = perform_ocr(rotated_image)
        
        # 4. Bild anzeigen
        cv2.imshow("Kamera Stream", ocr_bild)
        
        # Beenden, wenn 'q' gedrückt wird oder Fenster geschlossen wird
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if cv2.getWindowProperty("Kamera Stream", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()
