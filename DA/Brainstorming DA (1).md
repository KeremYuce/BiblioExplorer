


# DA

## Themenbereiche

- Gesamtsystem
	- Regal
		- Plan, Aufbau, Warum ist es so groß wie es ist? Grund: Kamera und **Auflösung**
	- Server-PC mit OCR, Backend, Frontend
	- Kamera
	- Ressourcen / Arbeitsmittel:
		- Linux
		- PHP (auch xampp), Python
		- git mit github
		- Verwendung von LLMs
		- Arduino-IDE
		- Excel für Zeitpläne
		- Irgendwas für PSP
		- WeeklyReports
- OCR
	- Bilderfassung
		- **Auflösung**
		- Kamera anbindung Linux / Treiber / etc.
	- Bildentzerrung
		- 4 Eckpunkte erfassen
		- Entzerren im Stream
	- OCR
		- tesseract
		- Wortfetzen Gruppieren XXX
- DB
	- Backend
		- mysql
		- Tabellen für Bücher
		- Tabellen für Wortfetzen
		- Web-Backend in PHP
	- Frontend (auf externem Web-Browser)
		- HTML
		- authentisierung?
		- Suche mit Leventshtein (?) XXX
		- Anbindung an Signalisierung
- Signalisierung
	- Arduino Unor
	- NeoPixel 
- Stromversorgung und andere Probleme

## Grundaufbau

1. Einleitung
2. Überblick
3. Alle Themenbereiche
4. Ausblick (wie geht es weiter)
5. Schluss

## Code-Bespiel:

Datenbankverbindung aufbauen:
```
<!DOCTYPE html>
<?php
$servername = "localhost";
$username = "web";  // Benutzername für die Datenbank
$password = "123web";      // Passwort für die Datenbank
$dbname = "biblio";  // Name der erstellten Datenbank


// Verbindung zu MySQL herstellen
$conn = new mysqli($servername, $username, $password, $dbname);

// Verbindung überprüfen
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
```
ISBN über POST-Request empfangen:
```
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $isbn = $_POST['isbn']; // ISBN von der POST-Anfrage

    // API-Aufruf für Buchdaten (Open Library API)
    $response = file_get_contents("http://openlibrary.org/api/books?bibkeys=ISBN:$isbn&format=json");
    $data = json_decode($response, true); // Antwort in Array umwandeln

    // Überprüfen, ob Buchdaten vorhanden sind
    if (isset($data["ISBN:$isbn"])) {
        $book_data = $data["ISBN:$isbn"];

```
Büchersuche mit auswerten und blblblba...
```
        
        // Buchtitel, Autor und andere Details aus der API-Antwort extrahieren
        $title = $book_data['title'] ?? 'Unknown';
        $author = isset($book_data['author_name']) ? implode(', ', $book_data['author_name']) : 'Unknown';
        
        // Angenommene author_id (hier hartkodiert für das Beispiel)
        $author_id = 4; // Du solltest den author_id aus einer Autoren-Tabelle holen oder einen Wert zuweisen
        
```
Datenbankstatement aufbauen und Sicherheit bedenken...
```
        // SQL-Abfrage zum Hinzufügen des Buches in die Datenbank (ohne buch_id, da diese automatisch vergeben wird)
        // Vermeide SQL-Injection durch vorbereitete Anweisungen
        $stmt = $conn->prepare("INSERT INTO buecher (ISBN, titel, autor_id) VALUES (?, ?, ?)");
        $stmt->bind_param("ssi", $isbn, $title, $author_id); // 'ssi' -> string, string, integer
        
        if ($stmt->execute()) {
            echo "Book '$title' added successfully!";
        } else {
            echo "Error: " . $stmt->error;
        }

        // Schließe die vorbereitete Anweisung
        $stmt->close();
    } else {
        echo "No data found for the given ISBN.";
    }
}
```
