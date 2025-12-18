<?php
// --- KONFIGURATION ---
$servername = "localhost";
$username = "web";
$password = "123web";
$dbname = "biblio";

// Verbindung herstellen
$conn = new mysqli($servername, $username, $password, $dbname);

// Check Connection
if ($conn->connect_error) {
    die("Verbindung fehlgeschlagen: " . $conn->connect_error);
}

// UTF-8 setzen, damit Namen korrekt angezeigt werden
$conn->set_charset("utf8mb4");

$message = "";
$messageType = ""; 

// --- LOGIK: BUCH HINZUFÜGEN ---
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['isbn_add'])) {
    
    $isbn_input = trim($_POST['isbn']);
    $isbn_clean = str_replace('-', '', $isbn_input);

    if (!empty($isbn_clean)) {
        
        // 1. DUPLIKAT-CHECK (Buch)
        $checkStmt = $conn->prepare("SELECT ISBN FROM buecher WHERE ISBN = ?");
        $checkStmt->bind_param("s", $isbn_clean);
        $checkStmt->execute();
        $checkStmt->store_result();

        if ($checkStmt->num_rows > 0) {
            $message = "Dieses Buch (ISBN: $isbn_clean) ist bereits in der Datenbank!";
            $messageType = "error";
        } else {
            // 2. API ABFRAGE
            $apiUrl = "https://openlibrary.org/api/books?bibkeys=ISBN:" . $isbn_clean . "&jscmd=data&format=json";
            $jsonResponse = @file_get_contents($apiUrl);

            if ($jsonResponse === FALSE) {
                $message = "Fehler bei der Verbindung zur Open Library API.";
                $messageType = "error";
            } else {
                $data = json_decode($jsonResponse, true);
                $key = "ISBN:" . $isbn_clean;

                if (isset($data[$key])) {
                    $bookData = $data[$key];
                    $title = $bookData['title'];
                    
                    // Autor Name aus API holen
                    $authorName = "Unbekannt";
                    if (isset($bookData['authors']) && is_array($bookData['authors'])) {
                        $authorName = $bookData['authors'][0]['name'];
                    }

                    // --- AUTOR LOGIK (NEU) ---
                    $author_id = 0;

                    // Prüfen ob Autor schon existiert (in Tabelle 'autor')
                    // HIER GEÄNDERT: Tabelle heißt jetzt 'autor'
                    $stmtAuthCheck = $conn->prepare("SELECT id FROM autor WHERE name = ?");
                    $stmtAuthCheck->bind_param("s", $authorName);
                    $stmtAuthCheck->execute();
                    $resAuth = $stmtAuthCheck->get_result();

                    if ($rowAuth = $resAuth->fetch_assoc()) {
                        // Autor existiert -> ID nehmen
                        $author_id = $rowAuth['id'];
                    } else {
                        // Autor existiert nicht -> Neu anlegen
                        // HIER GEÄNDERT: Tabelle heißt jetzt 'autor'
                        $stmtAuthInsert = $conn->prepare("INSERT INTO autor (name) VALUES (?)");
                        $stmtAuthInsert->bind_param("s", $authorName);
                        if ($stmtAuthInsert->execute()) {
                            $author_id = $conn->insert_id; // Die neue ID holen
                        } else {
                            $message = "Fehler beim Anlegen des Autors: " . $stmtAuthInsert->error;
                            $messageType = "error";
                        }
                        $stmtAuthInsert->close();
                    }
                    $stmtAuthCheck->close();

                    // --- BUCH SPEICHERN ---
                    if ($author_id > 0) {
                        // Hier speichern wir die autor_id
                        $insertStmt = $conn->prepare("INSERT INTO buecher (ISBN, titel, autor_id) VALUES (?, ?, ?)");
                        $insertStmt->bind_param("ssi", $isbn_clean, $title, $author_id);

                        if ($insertStmt->execute()) {
                            $message = "Erfolg! '$title' gespeichert (Autor-ID: $author_id).";
                            $messageType = "success";
                        } else {
                            $message = "Datenbank-Fehler beim Buch: " . $insertStmt->error;
                            $messageType = "error";
                        }
                        $insertStmt->close();
                    }

                } else {
                    $message = "Keine Daten für ISBN $isbn_clean gefunden.";
                    $messageType = "error";
                }
            }
        }
        $checkStmt->close();
    } else {
        $message = "Bitte eine gültige ISBN eingeben.";
        $messageType = "error";
    }
}

// --- LOGIK: BÜCHERLISTE LADEN ---
// Wir holen uns den Namen des Autors über einen JOIN, damit die Anzeige hübsch ist
$books = [];
// SQL: Verbinde Bücher mit Autoren über die ID
// HIER GEÄNDERT: Tabelle heißt jetzt 'autor'
$sql = "SELECT b.ISBN, b.titel, b.autor_id, a.name AS autor_name 
        FROM buecher b 
        LEFT JOIN autor a ON b.autor_id = a.autor_id 
        ORDER BY b.titel ASC";

$result = $conn->query($sql);
if ($result && $result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $books[] = $row;
    }
}

$conn->close();
?>

<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smarte Bibliothek</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; padding-top: 50px; }
        .container { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; max-width: 700px; }
        h1 { text-align: center; color: #333; }
        
        .form-group { margin-bottom: 1rem; display: flex; gap: 10px; }
        input[type="text"] { flex-grow: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
        button { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
        button:hover { background-color: #0056b3; }

        .message { padding: 15px; margin-bottom: 20px; border-radius: 4px; text-align: center; }
        .message.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .message.error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }

        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: 600; }
        tr:hover { background-color: #f1f1f1; }
        .empty-list { text-align: center; color: #777; margin-top: 20px; }
        .id-badge { font-size: 0.8em; color: #666; background: #eee; padding: 2px 6px; border-radius: 4px; margin-right: 5px; }
    </style>
</head>
<body>

<div class="container">
    <h1>📚 Buch Import (Relationale DB)</h1>

    <?php if (!empty($message)): ?>
        <div class="message <?php echo $messageType; ?>">
            <?php echo $message; ?>
        </div>
    <?php endif; ?>

    <form method="POST">
        <div class="form-group">
            <input type="text" name="isbn" placeholder="ISBN (z.B. 9780451524935)" required autofocus>
            <button type="submit" name="isbn_add">Suchen & Speichern</button>
        </div>
        <small style="color: #666;">API Check -> Autor Check (ID/Neu) -> Speichern</small>
    </form>

    <hr style="margin: 30px 0; border: 0; border-top: 1px solid #eee;">

    <h2>Gespeicherte Bücher</h2>
    <?php if (count($books) > 0): ?>
        <table>
            <thead>
                <tr>
                    <th>ISBN</th>
                    <th>Titel</th>
                    <th>Autor (ID & Name)</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($books as $book): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($book['ISBN']); ?></td>
                        <td><?php echo htmlspecialchars($book['titel']); ?></td>
                        <td>
                            <span class="id-badge">ID: <?php echo $book['autor_id']; ?></span>
                            <?php echo htmlspecialchars($book['autor_name'] ?? 'Unbekannt'); ?>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    <?php else: ?>
        <p class="empty-list">Noch keine Bücher in der Datenbank.</p>
    <?php endif; ?>

</div>

</body>
</html>
