<?php
// --- KONFIGURATION & DB ---
$servername = "localhost";
$username = "web"; 
$password = "123web";       
$dbname = "biblio";

$conn = new mysqli($servername, $username, $password, $dbname);
$conn->set_charset("utf8mb4");

$isbn = $_GET['isbn'] ?? '';
$book = null;
$coords = null;
$led_status = "";

if (!empty($isbn)) {
    // 1. Buchdaten laden
    $stmt = $conn->prepare("SELECT b.*, a.name AS autor_name FROM buecher b LEFT JOIN autor a ON b.autor_id = a.autor_id WHERE b.ISBN = ?");
    $stmt->bind_param("s", $isbn);
    $stmt->execute();
    $book = $stmt->get_result()->fetch_assoc();

    // 2. Standort aus OCR-Daten ermitteln
    // Wir holen den Titel des aktuellen Buches
$buchtitel = $book['titel'] ?? '';

// Wir suchen in ocr_fragments nach einem Text, der im Buchtitel vorkommt
$stmtCoords = $conn->prepare("SELECT pos_x, pos_y FROM ocr_fragments WHERE LOWER(?) LIKE CONCAT('%', LOWER(ocr_text), '%') LIMIT 1");
$stmtCoords->bind_param("s", $buchtitel);
$stmtCoords->execute();
$coords = $stmtCoords->get_result()->fetch_assoc();
if (!$coords) {
    echo "";
    // Teste eine manuelle Abfrage zum Debuggen:
    $testResult = $conn->query("SELECT ocr_text FROM ocr_fragments LIMIT 5");
    while($row = $testResult->fetch_assoc()) {
        echo "";
    }
}
}

// --- HARDWARE TRIGGER NUR BEI BUTTON-KLICK ---
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['action_locate'])) {
    if ($coords && isset($coords['pos_x'])) {
        $port = "/dev/ttyACM0"; 
        $baud = 115200;
        $command = "+" . $coords['pos_y'] . "," . $coords['pos_x'] . "\n";
        
        if (file_exists($port) && is_writable($port)) {
            exec("stty -F $port raw speed $baud cs8 -cstopb -parenb -hupcl");
            $fp = @fopen($port, "c+");
            if ($fp) {
                sleep(2); // Wartezeit für Arduino-Reboot
                fwrite($fp, $command);
                fclose($fp);
                $led_status = "LED an Position " . $coords['pos_x'] . " wurde aktiviert!";
            }
        } else {
            $led_status = "Hardware-Fehler: Port nicht bereit.";
        }
    }
}

// --- AUTOMATISCHES COVER LADEN (Open Library API) ---
$coverURL = "https://via.placeholder.com/300x450?text=Kein+Cover+gefunden";
if (!empty($book['ISBN'])) {
    // Wir generieren die URL direkt über die ISBN
    $clean_isbn = str_replace('-', '', $book['ISBN']);
    $coverURL = "https://covers.openlibrary.org/b/isbn/" . $clean_isbn . "-L.jpg?default=false";
    
    // Kleiner Check, ob das Bild existiert (optional, sonst zeigt er den Default)
}
?>

<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title><?php echo htmlspecialchars($book['titel'] ?? 'Buch Details'); ?></title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #f0f2f5; margin: 0; padding: 40px; }
        .container { max-width: 850px; margin: auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); display: flex; gap: 50px; }
        .cover-section { flex: 0 0 280px; }
        .cover-image { width: 100%; border-radius: 8px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); background: #eee; min-height: 400px; object-fit: cover; }
        .details-section { flex: 1; }
        h1 { font-size: 2.5rem; margin-bottom: 5px; color: #1c1e21; }
        .author { font-size: 1.2rem; color: #0066c0; margin-bottom: 30px; }
        
        .locate-btn { 
            background-color: #0071b7; color: white; border: none; padding: 15px 30px; 
            font-size: 1.2rem; border-radius: 8px; cursor: pointer; width: 100%;
            display: flex; align-items: center; justify-content: center; gap: 12px;
            transition: all 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .locate-btn:hover { background-color: #005a91; transform: translateY(-2px); }
        .locate-btn:active { transform: translateY(0); }

        .status-msg { margin-top: 20px; padding: 15px; border-radius: 8px; background: #e7f3ff; color: #1877f2; font-weight: bold; text-align: center; }
        .back-link { display: inline-block; margin-bottom: 25px; color: #65676b; text-decoration: none; }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>

<a href="biblio4.php" class="back-link">← Zurück zur Übersicht</a>

<div class="container">
    <div class="cover-section">
        <img src="<?php echo $coverURL; ?>" 
             onerror="this.src='https://via.placeholder.com/300x450?text=Cover+nicht+verfügbar'" 
             alt="Buch Cover" class="cover-image">
    </div>

    <div class="details-section">
        <h1><?php echo htmlspecialchars($book['titel']); ?></h1>
        <div class="author">von <strong><?php echo htmlspecialchars($book['autor_name'] ?? 'Unbekannt'); ?></strong></div>

        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
            <p><strong>ISBN-13:</strong> <?php echo htmlspecialchars($book['ISBN']); ?></p>
            <p><strong>Regal-Ebene:</strong> <?php echo $coords['pos_y'] ?? 'Nicht erfasst'; ?></p>
            <p><strong>X-Koordinate:</strong> <?php echo $coords['pos_x'] ?? 'Nicht erfasst'; ?></p>
        </div>

        <form method="POST">
            <button type="submit" name="action_locate" class="locate-btn">
                <span>Locate</span>
                <svg width="24" height="24" fill="white" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
            </button>
        </form>

        <?php if ($led_status): ?>
            <div class="status-msg">
                ✨ <?php echo $led_status; ?>
            </div>
        <?php endif; ?>
    </div>
</div>

</body>
</html>
