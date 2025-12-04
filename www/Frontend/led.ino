#include <Adafruit_NeoPixel.h>

#define LED_PIN    6    // Der Pin, an dem der NeoPixel-Streifen angeschlossen ist
#define LED_COUNT  3    // Anzahl der LEDs: 3 LEDs

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

String inputString = "";
bool stringComplete = false;

void setup() {
  Serial.begin(115200);   // Seriellen Monitor starten
  strip.begin();          // NeoPixel-Streifen initialisieren
  strip.show();           // Alle LEDs aus
}

void loop() {
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

// Funktion, die den serialEvent verarbeitet (Eingaben aus dem seriellen Monitor)
void serialEvent() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n') {    // Wenn der Benutzer Enter drückt, wird der Befehl verarbeitet
      stringComplete = true;
    } else {
      inputString += c;  // Der eingegebene Befehl wird zur Eingabe hinzugefügt
    }
  }
}

// Funktion zum Verarbeiten der seriellen Eingaben
void processCommand(String cmd) {
  cmd.trim();   // Entferne alle überflüssigen Leerzeichen

  // Alle LEDs ausschalten
  if (cmd == "*") {
    for (int i = 0; i < LED_COUNT; i++) {
      strip.setPixelColor(i, 0, 0, 0);  // Alle LEDs auf "aus" setzen
    }
    strip.show();  // Alle LEDs aktualisieren
    return;
  }

  // Befehl zum Ein- oder Ausschalten einer einzelnen LED (+ oder - vor der LED-Nummer)
  if (cmd.startsWith("+") || cmd.startsWith("-")) {
    int index = cmd.substring(1).toInt();  // Die LED-Nummer extrahieren

    if (index >= 0 && index < LED_COUNT) {
      if (cmd.startsWith("+")) {
        strip.setPixelColor(index, strip.Color(255, 255, 255)); // LED einschalten (weiß)
      } else {
        strip.setPixelColor(index, 0, 0, 0); // LED ausschalten
      }
      strip.show();  // LEDs aktualisieren
    }
    return;
  }

  // Befehl zum Setzen einer LED auf eine spezifische Farbe, z.B. "1:255,0,0"
  int colonIndex = cmd.indexOf(':');
  if (colonIndex > 0) {
    int ledIndex = cmd.substring(0, colonIndex).toInt();
    String rgb = cmd.substring(colonIndex + 1);
    int r = rgb.substring(0, rgb.indexOf(',')).toInt();
    int gStart = rgb.indexOf(',') + 1;
    int gEnd   = rgb.indexOf(',', gStart);
    int g = rgb.substring(gStart, gEnd).toInt();
    int b = rgb.substring(gEnd + 1).toInt();
// helligkeit noch machen
    if (ledIndex >= 0 && ledIndex < LED_COUNT) {
      strip.setPixelColor(ledIndex, strip.Color(r, g, b)); // Setze die Farbe der LED
      strip.show();  // LEDs aktualisieren
    }
  }
}
