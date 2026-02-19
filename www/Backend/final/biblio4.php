<?php
session_start();
mysqli_report(MYSQLI_REPORT_OFF);

// --- KONFIGURATION ---
$servername = "localhost";
$username = "web"; 
$password = "123web";       
$dbname = "biblio";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("<div style='color:red; padding:20px;'><strong>Verbindungsfehler:</strong> " . $conn->connect_error . "</div>");
}
$conn->set_charset("utf8mb4");

$message = "";
$messageType = ""; 

// --- LOGIN LOGIK ---
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['login_submit'])) {
    $user = $_POST['user'];
    $pass = $_POST['pass'];

    // Einfache Überprüfung laut Vorlage
    if ($user === 'web' && $pass === '123web') {
        $_SESSION['loggedin'] = true;
        $_SESSION['username'] = $user;
        header("Location: Biblio_security.php");
        exit;
    } else {
        $message = "Falsche Zugangsdaten!";
        $messageType = "error";
    }
}

// --- HOCHPRÄZISE LEVENSHTEIN-SUCHE ---
$books = [];
$search_term = isset($_GET['search']) ? trim($_GET['search']) : "";

// Wir holen zuerst alle Bücher, um sie in PHP mit Levenshtein zu verarbeiten
$sql = "SELECT b.ISBN, b.titel, b.autor_id, a.name AS autor_name 
        FROM buecher b 
        LEFT JOIN autor a ON b.autor_id = a.autor_id";

$result = $conn->query($sql);

if ($result) {
    while($row = $result->fetch_assoc()) {
        if (!empty($search_term)) {
            $searchLower = mb_strtolower($search_term, 'UTF-8');
            $titelLower = mb_strtolower($row['titel'], 'UTF-8');
            $autorLower = mb_strtolower($row['autor_name'] ?? '', 'UTF-8');
            
            // 1. Direkter Treffer (Priorität 0)
            if (strpos($titelLower, $searchLower) !== false || strpos($row['ISBN'], $searchLower) !== false) {
                $row['score'] = 0;
                $books[] = $row;
            } else {
                // 2. Levenshtein Wort-für-Wort Vergleich
                $wordsInTitle = explode(' ', $titelLower);
                $bestWordScore = 999;

                foreach ($wordsInTitle as $word) {
                    if (strlen($word) > 2) { // Kurze Wörter wie "der/die/das" ignorieren
                        $lev = levenshtein($searchLower, $word);
                        if ($lev < $bestWordScore) {
                            $bestWordScore = $lev;
                        }
                    }
                }

                // Schwellenwert: Nur anzeigen, wenn max. 2 Steps Unterschied (z.B. "hary" -> "harry")
                if ($bestWordScore <= 2) {
                    $row['score'] = $bestWordScore;
                    $books[] = $row;
                }
            }
        } else {
            // Wenn keine Suche aktiv ist, alle Bücher mit Standard-Score anzeigen
            $row['score'] = 100;
            $books[] = $row;
        }
    }

    // Sortierung: Beste Treffer (niedrigster Score) zuerst
    usort($books, function($a, $b) {
        if ($a['score'] === $b['score']) {
            return strcasecmp($a['titel'], $b['titel']);
        }
        return $a['score'] <=> $b['score'];
    });
}
$conn->close();
?>

<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BiblioExplorer - Public</title>
    <style>
        /* --- STYLES (Identisch zum Design) --- */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #ffffff; color: #333; line-height: 1.6; }
        
        header { display: flex; align-items: center; justify-content: space-between; padding: 15px 40px; border-bottom: 1px solid #eee; position: sticky; top: 0; background: white; z-index: 100; }
        .logo-small { display: flex; align-items: center; font-weight: bold; font-size: 18px; color: #2e7d32; text-decoration: none; }
        .logo-small svg { height: 24px; margin-right: 8px; fill: currentColor; }

        .search-bar-container { flex-grow: 1; display: flex; justify-content: center; margin: 0 20px; }
        .search-form { position: relative; width: 100%; max-width: 500px; }
        .search-form input { width: 100%; padding: 10px 40px 10px 20px; border-radius: 20px; border: 1px solid #ddd; background-color: #f1f3f4; outline: none; transition: background 0.2s; }
        .search-form input:focus { background-color: white; box-shadow: 0 1px 6px rgba(0,0,0,0.1); }
        .search-icon { position: absolute; right: 15px; top: 50%; transform: translateY(-50%); color: #777; pointer-events: none; }

        .login-area { display: flex; gap: 10px; align-items: center; }
        .login-input { padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; width: 120px; }
        .btn-login { background-color: #333; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; }
        .btn-login:hover { background-color: #000; }

        .hero { display: flex; align-items: center; justify-content: space-between; padding: 10px 10%; min-height: 60vh; }
        .hero-text { max-width: 50%; }
        .hero h1 { font-size: 4rem; font-weight: 800; margin-bottom: 20px; letter-spacing: -1px; color: #000; }
        .hero p { font-size: 1.1rem; color: #555; margin-bottom: 30px; max-width: 400px; }
        .hero p { font-size: 1.1rem; color: #555; margin-bottom: 30px; max-width: 400px; } 
	.hero-image {
    	width: 50%;       /* Der Bereich für das Bild nimmt die rechte Hälfte ein */
    	display: flex;    /* Hilft beim Zentrieren */
    	justify-content: center; 
	}

	.hero-image img {
    	width: 600px;     /* <--- HIER STELLST DU DIE GRÖSSE EIN */
    	max-width: 100%;  /* Damit es auf Handys nicht über den Rand geht */
    	height: auto;     /* Verhindert Verzerrung */
	}
        .content-section { background-color: #fafafa; padding: 40px 10%; border-top: 1px solid #eee; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }
        th { color: #888; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; }
        tr:hover { background-color: #f9f9f9; }

        .message { position: fixed; top: 80px; right: 20px; padding: 15px 25px; border-radius: 8px; color: white; animation: slideIn 0.5s; z-index: 1000; }
        .message.error { background-color: #d32f2f; }
        @keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
</style>
</head>
<body>

<header>
    <a href="biblio4.php" class="logo-small">
        <svg viewBox="0 0 24 24"><path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/></svg>
        BiblioExplorer
    </a>

    <div class="search-bar-container">
        <form method="GET" class="search-form">
            <input type="text" name="search" placeholder="Suche..." value="<?php echo htmlspecialchars($search_term); ?>">
            <span class="search-icon">🔍</span>
        </form>
    </div>

    <!-- Login Formular direkt im Header -->
    <div class="login-area">
        <form method="POST" style="display:flex; gap:5px;">
            <input type="text" name="user" class="login-input" placeholder="User" required>
            <input type="password" name="pass" class="login-input" placeholder="Pass" required>
            <button type="submit" name="login_submit" class="btn-login">Login</button>
        </form>
    </div>
</header>

<?php if (!empty($message)): ?>
    <div class="message <?php echo $messageType; ?>">
        <?php echo $message; ?>
    </div>
<?php endif; ?>

<section class="hero">
    <div class="hero-text">
        <h1>Willkommen</h1>
        <p>
            BiblioExplorer - Das moderne System für unsere Schulbibliothek. 
            Suche nach Büchern, Autoren oder ISBNs.
            <br><br>
            <strong>Melde dich oben an, um Bücher zu verwalten.</strong>
        </p>
    </div>
    <div class="hero-image">
    <img src="logo.png" alt="BiblioExplorer Logo" class="my-logo">
    </div>
</section>

<section class="content-section">
    <div class="card">
        <h2>Bücherbestand</h2>
        <?php if (count($books) > 0): ?>
            <table>
                <thead>
                    <tr>
                        <th>Titel</th>
                        <th>Autor</th>
                        <th>ISBN</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($books as $book): ?>
                        <tr>
                           	<td>
 			   <a href="buch_detail.php?isbn=<?php echo urlencode($book['ISBN']); ?>" style="text-decoration:none; color:#2e7d32; font-weight:bold;">
        			<?php echo htmlspecialchars($book['titel']); ?>
			    		</a>
				</td>
                            <td><?php echo htmlspecialchars($book['autor_name'] ?? '-'); ?></td>
                            <td style="color:#777; font-size:0.9rem;"><?php echo htmlspecialchars($book['ISBN']); ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php else: ?>
            <p style="color:#777; text-align:center;">Keine Bücher gefunden.</p>
        <?php endif; ?>
    </div>
</section>

</body>
</html>

