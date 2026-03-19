import cv2
import pytesseract
import numpy as np
import json
import os
import mysql.connector
import time
import threading

# --- GLOBALE VARIABLEN FÜR THREADING ---
is_scanning = False
letzte_ergebnisse = []

# --- PREPROCESSING FUNKTIONEN ---
'''
def preprocess_gray(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def preprocess_black_text(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    return thresh

def preprocess_white_text(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(gray)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(inverted)
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    return thresh

def preprocess_color_agnostic(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    nodes_enhanced = clahe.apply(gray)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    gradient = cv2.morphologyEx(nodes_enhanced, cv2.MORPH_GRADIENT, kernel)
    _, thresh = cv2.threshold(gradient, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    final_for_ocr = cv2.bitwise_not(thresh)
    return final_for_ocr

def preprocess_gemini(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Wandelt das Bild in echtes Schwarz-Weiß um
    # cv2.THRESH_BINARY_INV nutzen, falls der Text hell auf dunklem Grund ist
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh

def preprocess_mono(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Wandelt das Bild in echtes Schwarz-Weiß um
    # cv2.THRESH_BINARY_INV nutzen, falls der Text hell auf dunklem Grund ist
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, thresh_inv = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    return thresh, thresh_inv
'''
def preprocess(image):
    # 1. Farbraum-Wechsel: LAB trennt Helligkeit (L) von Farbinformation (A, B)
    # Das ist oft stabiler gegen Schatten als BGR-Graustufen.
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    # 2. Kontrast-Begrenztes Adaptives Histogramm-Equalization (CLAHE)
    # Verbessert den lokalen Kontrast, ohne das Rauschen extrem zu verstärken.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced_l = clahe.apply(l_channel)

    # 3. Kanten erhalten durch Bilateral Filter (besser als Gaussian für OCR)
    # Er macht Flächen glatt, lässt die Buchstabenränder aber knallhart.
    filtered = cv2.bilateralFilter(enhanced_l, 9, 75, 75)

    # 4. Adaptives Thresholding (Statt globalem Otsu)
    # Das ist der "Killer" für Buchrücken, da es mit Licht/Schatten-Gradienten umgeht.
    thresh = cv2.adaptiveThreshold(
        filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Invertierte Version für hellen Text auf dunklem Grund
    thresh_inv = cv2.bitwise_not(thresh)

    return thresh, thresh_inv



def save_to_mysql(ergebnisse):
    if not ergebnisse:
        return
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="web",      
            password="123web",      
            database="biblio" 
        )
        cursor = conn.cursor()
        
        sql = """
            INSERT INTO ocr_fragments (ocr_text, pos_x, pos_y) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            pos_x = VALUES(pos_x), 
            pos_y = VALUES(pos_y),
            last_seen = CURRENT_TIMESTAMP
        """
        
        for item in ergebnisse:
            val = (str(item['wort']), str(item['x_relativ_prozent']), str(item['y_achse']))
            cursor.execute(sql, val)
        
        cursor.execute("DELETE FROM ocr_fragments WHERE last_seen < NOW() - INTERVAL 60 SECOND")
            
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[SQL Fehler] {e}")

def perform_ocr_thread(img_original):
    """ Diese Funktion läuft im Hintergrund """
    global is_scanning, letzte_ergebnisse
    
    h_orig, w_orig = img_original.shape[:2]
    image, invers = preprocess(img_original)
    
    custom_config = r'--oem 3 --psm 11'
    ergebnisse_liste = []
    erkannte_woerter_lokal = set()

    # Wir rotieren hier im Hintergrund-Thread
    variants = [
        (image, 0, ""),                                     
        (cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE), 90, ""), 
        (cv2.rotate(image, cv2.ROTATE_180), 180, ""), 
        (cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE), 270, ""),

        #(invers, 0, "inv"),                                     
        #(cv2.rotate(invers, cv2.ROTATE_90_CLOCKWISE), 90, "inv"), 
        #(cv2.rotate(invers, cv2.ROTATE_180), 180, "inv"), 
        #(cv2.rotate(invers, cv2.ROTATE_90_COUNTERCLOCKWISE), 270, "inv") 
    ]

    for img_rot, angle, neg in variants:
        
        d = pytesseract.image_to_data(img_rot, config=custom_config, output_type=pytesseract.Output.DICT)
        
        for i in range(len(d['text'])):
            text = d['text'][i].strip()
            conf = int(d['conf'][i])

            if conf > 65 and len(text) > 2: # and text not in erkannte_woerter_lokal:
                x_ocr, y_ocr = d['left'][i], d['top'][i]
                w_box, h_box = d['width'][i], d['height'][i]

                # Koordinaten-Berechnung
                if angle == 90:
                    new_x, new_y = y_ocr, h_orig - x_ocr - w_box
                    target_w, target_h = h_box, w_box
                elif angle == 270:
                    new_x, new_y = w_orig - y_ocr - h_box, x_ocr
                    target_w, target_h = h_box, w_box
                elif angle == 180:
                    new_x, new_y = w_orig-x_ocr- w_box, h_orig-y_ocr- h_box
                    target_w, target_h = w_box, h_box
                else:
                    new_x, new_y = x_ocr, y_ocr
                    target_w, target_h = w_box, h_box

                drittel = h_orig / 3
                lade = "1" if new_y < drittel else "2" if new_y < (2 * drittel) else "3"

                ergebnisse_liste.append({
                    "wort": text,
                    "y_achse": lade,
                    "x_pixel": new_x,
                    "y_pixel": new_y,
                    "w": target_w,
                    "h": target_h,
                    "x_relativ_prozent": round((new_x / w_orig) * 100, 1)
                })
                erkannte_woerter_lokal.add(text)
                print(f"{neg} {angle} {conf} {text}")

    
    # Ergebnisse für die Anzeige im Hauptthread spiegeln
    letzte_ergebnisse = ergebnisse_liste
    save_to_mysql(ergebnisse_liste)
    is_scanning = False # Thread fertig!

# --- GEOMETRIE ---

def koordinaten():
    try:
        with open("ecken.json", "r") as f:
            return json.load(f)
    except Exception:
        return []

def sortiere_ecken(pts):
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
        ziel_koordinaten = np.array([[ziel_w - 1, 0], [ziel_w - 1, ziel_h - 1], [0, ziel_h - 1], [0, 0]], dtype=np.float32)
    else:
        ziel_w = sz
        ziel_h = int(sz * (hoehe_original / breite_original))
        ziel_koordinaten = np.array([[0, 0], [ziel_w - 1, 0], [ziel_w - 1, ziel_h - 1], [0, ziel_h - 1]], dtype=np.float32)

    matrix = cv2.getPerspectiveTransform(ecken_sortiert, ziel_koordinaten)
    return cv2.warpPerspective(frame, matrix, (ziel_w, ziel_h))



class FreshFrameReader:
    def __init__(self, uri):
        self.cap = cv2.VideoCapture(uri, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        # Thread starten, der permanent liest
        threading.Thread(target=self.update, args=(), daemon=True).start()

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame # Überschreibt den alten Frame sofort

    def get_frame(self):
        return self.frame

    def stop(self):
        self.stopped = True


# --- MAIN ---

if __name__ == "__main__":
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    # cap = FreshFrameReader(0)

    
    ecken = koordinaten()

    while True:
        #frame = cap.get_frame() # Liefert garantiert den neuesten Frame
        ret, frame = cap.read()
        if not ret: break
            
        if not ecken:
            cv2.imshow("Kamera Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            continue

        quadrat = entzerren_bild(frame, ecken)
        scale = 75
        width = int(quadrat.shape[1] * scale / 100)
        height = int(quadrat.shape[0] * scale / 100)
        resized = cv2.resize(quadrat, (width, height), interpolation=cv2.INTER_AREA)
        original = cv2.rotate(resized, cv2.ROTATE_180)

        # --- MULTITHREADING LOGIK ---
        if not is_scanning:
            is_scanning = True
            # Starte OCR im Hintergrund mit einer Kopie des aktuellen Bildes
            t = threading.Thread(target=perform_ocr_thread, args=(original.copy(),))
            t.daemon = True
            t.start()

        # Zeichne die letzten erkannten Wörter (damit es nicht flackert)
        for res in letzte_ergebnisse:
            color = (0, 255, 0)
            cv2.rectangle(original, (res['x_pixel'], res['y_pixel']), 
                          (res['x_pixel'] + res['w'], res['y_pixel'] + res['h']), color, 2)
            cv2.putText(original, res['wort'], (res['x_pixel'], res['y_pixel'] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Status-Anzeige
        status_text = "SCANNING..." if is_scanning else "WAITING..."
        cv2.putText(original, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Kamera Stream", original)
        
        if cv2.waitKey(1) & 0xFF == ord('q'): break
        if cv2.getWindowProperty("Kamera Stream", cv2.WND_PROP_VISIBLE) < 1: break

    cap.release()
    cv2.destroyAllWindows()
