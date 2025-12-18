<!DOCTYPE html>
<?php
$servername = "localhost";
$username = "web";  // Benutzername für die Datenbank
$password = "123web";      // Passwort für die Datenbank
$dbname = "biblio";  // Name der Datenbank

// Verbindung zu MySQL herstellen
$conn = new mysqli($servername, $username, $password, $dbname);

// Verbindung überprüfen
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['isbn_search'])) {
        $isbn_search = $_POST['isbn'];  // ISBN vom Benutzer zur Suche

        // Suche nach einem Buch mit der angegebenen ISBN
        $sql = "SELECT * FROM buecher WHERE ISBN = '$isbn_search'";
        $result = $conn->query($sql);
        
        if ($result->num_rows > 0) {
            $book_data = $result->fetch_assoc();
            $message = "Buch gefunden: " . $book_data['titel'];
        } else {
            $message = "Kein Buch mit der ISBN $isbn_search gefunden.";
        }
    }
    
    if (isset($_POST['isbn_add'])) {
        $isbn_add = $_POST['isbn'];  // ISBN vom Benutzer zum Hinzufügen
        $title = $_POST['title'];    // Titel vom Benutzer
        $author = $_POST['author'];  // Autor vom Benutzer
        
        // Hinzufügen eines neuen Buches
        $stmt = $conn->prepare("INSERT INTO buecher (ISBN, titel, autor_id) VALUES (?, ?, ?)");
        $stmt->bind_param("ssi", $isbn_add, $title, $author);
        
        if ($stmt->execute()) {
            $message = "Buch '$title' erfolgreich hinzugefügt!";
        } else {
            $message = "Fehler: " . $stmt->error;
        }
        $stmt->close();
    }
}

// Abrufen und Anzeigen aller Bücher aus der Datenbank
$sql = "SELECT * FROM buecher";
$result = $conn->query($sql);
$books = [];
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $books[] = $row;
    }
}

// Verbindung schließen
$conn->close();
?>

<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bibliothekssystem</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }

        .container {
            width: 100%;
            max-width: 800px;
            margin: auto;
        }

        .form-group {
            margin-bottom: 15px;
        }

        label {
            font-weight: bold;
        }

        input[type="text"], input[type="submit"] {
            padding: 8px;
            font-size: 14px;
            width: 100%;
        }

        input[type="submit"] {
            width: auto;
            cursor: pointer;
        }

        .book-list {
            margin-top: 20px;
        }

        .book-item {
            padding: 10px;
            border-bottom: 1px solid #ccc;
        }

        .message {
            margin: 20px 0;
            padding: 10px;
            background-color: #f8d7da;
            color: #721c24;
            border-radius: 5px;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Bibliothekssystem</h1>
    
    <!-- Formular für die ISBN-Eingabe -->
    <form method="POST">
        <div class="form-group">
            <label for="isbn">ISBN Nummer:</label>
            <input type="text" name="isbn" id="isbn" required>
        </div>
        
        <!-- Buttons für die Aktionen -->
        <div class="form-group">
            <input type="submit" name="isbn_search" value="Buch suchen">
            <input type="submit" name="isbn_add" value="Buch hinzufügen">
        </div>

        <!-- Eingabefelder für Buchdetails, wenn ein Buch hinzugefügt werden soll -->
        <div class="form-group" id="book-details" style="display:none;">
            <label for="title">Buchtitel:</label>
            <input type="text" name="title" id="title" required>

            <label for="author">Autor:</label>
            <input type="text" name="author" id="author" required>
        </div>
    </form>

    <!-- Anzeige von Statusnachrichten -->
    <?php if (isset($message)): ?>
        <div class="message"><?php echo $message; ?></div>
    <?php endif; ?>

    <!-- Anzeige der Bücher aus der Datenbank -->
    <div class="book-list">
        <h2>Verfügbare Bücher</h2>
        <?php if (count($books) > 0): ?>
            <?php foreach ($books as $book): ?>
                <div class="book-item">
                    <strong>ISBN:</strong> <?php echo $book['ISBN']; ?><br>
                    <strong>Titel:</strong> <?php echo $book['titel']; ?><br>
                    <strong>Autor ID:</strong> <?php echo $book['autor_id']; ?>
                </div>
            <?php endforeach; ?>
        <?php else: ?>
            <p>Keine Bücher gefunden.</p>
        <?php endif; ?>
    </div>
</div>

<script>
    // Dynamisches Anzeigen des Formulars zum Hinzufügen eines Buches
    document.querySelector('input[name="isbn_add"]').addEventListener('click', function() {
        document.getElementById('book-details').style.display = 'block';
    });
</script>

</body>
</html>
