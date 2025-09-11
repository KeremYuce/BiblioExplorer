import cv2

# Haar-Cascade laden
face_cascade = cv2.CascadeClassifier(
    "/home/yz/Kamera/haarcascade_frontalface_default.xml"
)

# Kamera starten
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Kamera nicht gefunden!")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Graustufen-Bild für die Erkennung
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Gesichter erkennen
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # Kästchen um die Gesichter zeichnen
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Fenster anzeigen
    cv2.imshow("Gesichtserkennung", frame)

    # Mit 'q' beenden
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

