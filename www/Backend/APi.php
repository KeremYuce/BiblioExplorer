<?php
$servername = "localhost";
$username = "root";  // Standardbenutzername für XAMPP
$password = "";      // Standardpasswort für XAMPP ist leer
$dbname = "biblio";  // Name der erstellten Datenbank

// Verbindung zu MySQL herstellen
$conn = new mysqli($servername, $username, $password, $dbname);

// Verbindung überprüfen
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $isbn = $_POST['isbn'];

    // API-Aufruf für Buchdaten (Open Library API)
    $response = file_get_contents("http://openlibrary.org/api/books?bibkeys=ISBN:$isbn&format=json");
    $data = json_decode($response, true);

    // Überprüfen, ob Buchdaten vorhanden sind
    if (isset($data["ISBN:$isbn"])) {
        $book_data = $data["ISBN:$isbn"];
        
        $title = $book_data['title'] ?? 'Unknown';
        $author = isset($book_data['author_name']) ? implode(', ', $book_data['author_name']) : 'Unknown';
        
        // Angenommene author_id (hier hartkodiert für das Beispiel)
        $author_id = 4 ;  // Du solltest den author_id aus einer Autoren-Tabelle holen oder einen Wert zuweisen
        
        // SQL-Abfrage zum Hinzufügen des Buches in die Datenbank (ohne buch_id, da diese automatisch vergeben wird)
        $sql = "INSERT INTO buecher (ISBN, titel, autor_id)
                VALUES ('$isbn', '$title', '$author_id')";

        if ($conn->query($sql) === TRUE) {
            echo "Book '$title' added successfully!";
        } else {
            echo "Error: " . $sql . "<br>" . $conn->error;
        }
    } else {
        echo "No data found for the given ISBN.";
    }
}

$conn->close();
?>

<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Entry Form</title>
</head>
<body>
    <h1>Füge ein neues Buch hinzu</h1>
    <form action="" method="POST">
        ISBN: <input type="text" name="isbn" required><br><br>
        <input type="submit" value="Buch hinzufügen">
    </form>
</body>
</html>

