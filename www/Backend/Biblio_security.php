<?php
session_start();
mysqli_report(MYSQLI_REPORT_OFF);

// --- SICHERHEITSCHECK ---
// Wenn nicht eingeloggt, sofort zurück zur Startseite
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    header("Location: Biblio3.php");
    exit;
}

// --- LOGOUT ---
if (isset($_GET['action']) && $_GET['action'] == 'logout') {
    session_destroy();
    header("Location: Biblio3.php");
    exit;
}

// --- DB CONNECTION ---
$servername = "localhost";
$username = "web"; 
$password = "123web";       
$dbname = "biblio";

$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) { die("DB Error: " . $conn->connect_error); }
$conn->set_charset("utf8mb4");

$message = "";
$messageType = ""; 

// --- FUNKTION: BUCH SPEICHERN ---
function saveBook($conn, $isbn, $title, $authorName) {
    global $message, $messageType;
    
    // Autor Check
    $author_id = 0;
    $stmtAuthCheck = $conn->prepare("SELECT autor_id FROM autor WHERE name = ?");
    $stmtAuthCheck->bind_param("s", $authorName);
    $stmtAuthCheck->execute();
    $resAuth = $stmtAuthCheck->get_result();

    if ($rowAuth = $resAuth->fetch_assoc()) {
        $author_id = $rowAuth['autor_id'];
    } else {
        $stmtAuthInsert = $conn->prepare("INSERT INTO autor (name) VALUES (?)");
        $stmtAuthInsert->bind_param("s", $authorName);
        $stmtAuthInsert->execute();
        $author_id = $conn->insert_id;
        $stmtAuthInsert->close();
    }
    $stmtAuthCheck->close();

    // Buch speichern
    if ($author_id > 0) {
        $insertStmt = $conn->prepare("INSERT INTO buecher (ISBN, titel, autor_id) VALUES (?, ?, ?)");
        $insertStmt->bind_param("ssi", $isbn, $title, $author_id);
        if ($insertStmt->execute()) {
            $message = "'$title' erfolgreich gespeichert.";
            $messageType = "success";
        } else {
            $message = "Fehler: " . $insertStmt->error;
            $messageType = "error";
        }
        $insertStmt->close();
    }
}

// --- LOGIK: LÖSCHEN ---
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['delete_isbn'])) {
    $del_isbn = $_POST['delete_isbn'];
    $stmtDel = $conn->prepare("DELETE FROM buecher WHERE ISBN = ?");
    $stmtDel->bind_param("s", $del_isbn);
    if ($stmtDel->execute()) {
        $message = "Buch gelöscht."; $messageType = "success";
    }
    $stmtDel->close();
}

// --- LOGIK: AUTO IMPORT ---
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['isbn_add'])) {
    $isbn_clean = str_replace('-', '', trim($_POST['isbn']));
    if (!empty($isbn_clean)) {
        // Dubletten Check
        $check = $conn->query("SELECT ISBN FROM buecher WHERE ISBN = '$isbn_clean'");
        if ($check->num_rows > 0) {
            $message = "Buch existiert bereits!"; $messageType = "error";
        } else {
            $json = @file_get_contents("https://openlibrary.org/api/books?bibkeys=ISBN:$isbn_clean&jscmd=data&format=json");
            $data = json_decode($json, true);
            $key = "ISBN:" . $isbn_clean;
            if (isset($data[$key])) {
                $book = $data[$key];
                $author = isset($book['authors']) ? $book['authors'][0]['name'] : "Unbekannt";
                saveBook($conn, $isbn_clean, $book['title'], $author);
            } else {
                $message = "ISBN online nicht gefunden."; $messageType = "error";
            }
        }
    }
}

// --- LOGIK: MANUELL EINTRAGEN ---
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['manual_add'])) {
    $title = trim($_POST['manual_title']);
    $author = trim($_POST['manual_author']);
    $isbn = trim($_POST['manual_isbn']);
    
    if (empty($isbn)) { $isbn = "MAN-" . strtoupper(uniqid()); } // Generiere ID wenn leer

    $check = $conn->query("SELECT ISBN FROM buecher WHERE ISBN = '$isbn'");
    if ($check->num_rows > 0) {
        $message = "ISBN/ID existiert bereits!"; $messageType = "error";
    } else {
        saveBook($conn, $isbn, $title, $author);
    }
}

// --- LOGIK: SUCHE & LISTE ---
$books = [];
$search_term = $_GET['search'] ?? "";
$sql = "SELECT b.ISBN, b.titel, b.autor_id, a.name AS autor_name FROM buecher b LEFT JOIN autor a ON b.autor_id = a.autor_id";
if (!empty($search_term)) {
    $sql .= " WHERE b.titel LIKE '%$search_term%' OR b.ISBN LIKE '%$search_term%' OR a.name LIKE '%$search_term%'";
}
$sql .= " ORDER BY b.titel ASC";
$result = $conn->query($sql);
if ($result) { while($r = $result->fetch_assoc()) $books[] = $r; }

$conn->close();
?>

<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BiblioExplorer - Admin</title>
    <style>
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f0f2f5; color: #333; margin:0; padding:0; }
        
        .admin-header { background: #222; color: white; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; }
        .logo { color: #4caf50; font-weight: bold; font-size: 1.2rem; text-decoration: none; display: flex; align-items: center; gap: 10px;}
        .btn-logout { background: #d32f2f; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; font-size: 14px; }
        
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; display: grid; grid-template-columns: 1fr 2fr; gap: 30px; }
        
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h2 { margin-top: 0; font-size: 1.3rem; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px; }
        
        /* Tabs für Hinzufügen */
        .tabs { display: flex; margin-bottom: 15px; border-bottom: 1px solid #ddd; }
        .tab-btn { padding: 10px 15px; cursor: pointer; background: none; border: none; font-weight: bold; color: #666; border-bottom: 3px solid transparent; }
        .tab-btn.active { color: #2e7d32; border-bottom-color: #2e7d32; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        input[type="text"] { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .btn-green { width: 100%; padding: 10px; background: #2e7d32; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn-green:hover { background: #1b5e20; }
        
        table { width: 100%; border-collapse: collapse; background: white; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        .btn-del { background: none; border: none; cursor: pointer; font-size: 1.2rem; }
        
        .message { padding: 15px; background: #fff; margin: 20px 40px; border-radius: 8px; border-left: 5px solid #ccc; }
        .message.success { border-color: #2e7d32; background: #e8f5e9; }
        .message.error { border-color: #d32f2f; background: #ffebee; }
    </style>
    <script>
        function openTab(name) {
            document.querySelectorAll('.tab-content').forEach(d => d.style.display = 'none');
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(name).style.display = 'block';
            document.getElementById('btn-' + name).classList.add('active');
        }
    </script>
</head>
<body>

<div class="admin-header">
    <a href="Biblio3.php" class="logo">
        <svg viewBox="0 0 24 24" width="24" fill="currentColor"><path d="M12 2L2 7l10 5 10-5-10-5zm0 9l2.5-1.25L12 8.5l-2.5 1.25L12 11zm0 2.5l-5-2.5-5 2.5L12 22l10-8.5-5-2.5-5 2.5z"/></svg>
        BiblioExplorer Admin
    </a>
    <div style="display:flex; gap:15px; align-items:center;">
        <span>Angemeldet als: <strong><?php echo htmlspecialchars($_SESSION['username'] ?? 'Admin'); ?></strong></span>
        <a href="Biblio_security.php?action=logout" class="btn-logout">Abmelden</a>
    </div>
</div>

<?php if (!empty($message)): ?>
    <div class="message <?php echo $messageType; ?>"><?php echo $message; ?></div>
<?php endif; ?>

<div class="container">
    
    <!-- LINKER BEREICH: HINZUFÜGEN -->
    <div>
        <div class="card">
            <div class="tabs">
                <button id="btn-auto" class="tab-btn active" onclick="openTab('auto')">Auto-Import</button>
                <button id="btn-manual" class="tab-btn" onclick="openTab('manual')">Manuell</button>
            </div>

            <!-- TAB 1: Auto Import -->
            <div id="auto" class="tab-content" style="display:block;">
                <p style="font-size:0.9rem; color:#666; margin-bottom:10px;">ISBN eingeben, Rest kommt von OpenLibrary.</p>
                <form method="POST">
                    <input type="text" name="isbn" placeholder="ISBN (Scan)" required>
                    <button type="submit" name="isbn_add" class="btn-green">Importieren</button>
                </form>
            </div>

            <!-- TAB 2: Manuell -->
            <div id="manual" class="tab-content">
                <p style="font-size:0.9rem; color:#666; margin-bottom:10px;">Daten von Hand eintragen.</p>
                <form method="POST">
                    <input type="text" name="manual_title" placeholder="Titel" required>
                    <input type="text" name="manual_author" placeholder="Autor" required>
                    <input type="text" name="manual_isbn" placeholder="ISBN/ID (Optional)">
                    <button type="submit" name="manual_add" class="btn-green">Speichern</button>
                </form>
            </div>
        </div>
    </div>

    <!-- RECHTER BEREICH: LISTE & LÖSCHEN -->
    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <h2>Verwaltung</h2>
            <form method="GET" style="display:flex; gap:5px;">
                <input type="text" name="search" placeholder="Admin-Suche..." value="<?php echo htmlspecialchars($search_term); ?>" style="margin:0; padding:5px;">
                <button type="submit" style="padding:5px 10px;">🔍</button>
            </form>
        </div>

        <?php if (count($books) > 0): ?>
            <table>
                <thead>
                    <tr>
                        <th>Titel</th>
                        <th>Autor</th>
                        <th>ISBN</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($books as $book): ?>
                        <tr>
                            <td><strong><?php echo htmlspecialchars($book['titel']); ?></strong></td>
                            <td><?php echo htmlspecialchars($book['autor_name'] ?? '-'); ?></td>
                            <td style="color:#777; font-size:0.85rem;"><?php echo htmlspecialchars($book['ISBN']); ?></td>
                            <td style="text-align:right;">
                                <form method="POST" onsubmit="return confirm('Wirklich löschen?');" style="margin:0;">
                                    <input type="hidden" name="delete_isbn" value="<?php echo $book['ISBN']; ?>">
                                    <button type="submit" class="btn-del" title="Löschen">🗑️</button>
                                </form>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php else: ?>
            <p style="color:#777; padding:20px;">Nichts gefunden.</p>
        <?php endif; ?>
    </div>
</div>

</body>
</html>
