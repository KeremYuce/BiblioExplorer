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

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $isbn = $_POST['isbn']; // ISBN von der POST-Anfrage

    // API-Aufruf für Buchdaten (Open Library API)
    $response = file_get_contents("http://openlibrary.org/api/books?bibkeys=ISBN:$isbn&format=json");
    $data = json_decode($response, true); // Antwort in Array umwandeln

    // Überprüfen, ob Buchdaten vorhanden sind
    if (isset($data["ISBN:$isbn"])) {
        $book_data = $data["ISBN:$isbn"];
        
        // Buchtitel, Autor und andere Details aus der API-Antwort extrahieren
        $title = $book_data['title'] ?? 'Unknown';
        $author = isset($book_data['author_name']) ? implode(', ', $book_data['author_name']) : 'Unknown';
        
        // Angenommene author_id (hier hartkodiert für das Beispiel)
        $author_id = 4; // Du solltest den author_id aus einer Autoren-Tabelle holen oder einen Wert zuweisen
        
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

// Verbindung schließen
$conn->close();
?>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Entry Form</title>
</head>
<body>
    <h1>Fuege ein neues Buch hinzu</h1>
    <form action="" method="POST">
        ISBN: <input type="text" name="isbn" required><br><br>
        <input type="submit" value="Buch hinzufuegen">
    </form>
</body>
</html>
