<?php
// --- Datenbankverbindung ---
$host = 'localhost';
$db   = 'biblio';
$user = 'web';
$pass = '123web';
$charset = 'utf8mb4';

$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,
];

try {
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (\PDOException $e) {
    die("Verbindungsfehler: " . $e->getMessage());
}

// 1. DEINE existierende Tabelle 'buecher' laden
// Wir holen nur den Titel (und die ID), da wir die autor_id ohne Join noch nicht auflösen können
$stmt = $pdo->query("SELECT buch_id, titel FROM buecher");
$realBooks = $stmt->fetchAll();

// 2. OCR Fragmente laden
$stmt = $pdo->query("SELECT * FROM ocr_fragments");
$ocrFragments = $stmt->fetchAll();

$searchTerm = $_GET['q'] ?? '';
$foundBooks = [];

// --- MATCHING FUNKTION: OCR-Salat -> Saubere 'buecher' Tabelle ---
function findBestRealTitle($ocrText, $catalog) {
    $bestMatchTitle = $ocrText . " (Nicht im Katalog)"; // Fallback
    $highestSimilarity = 0;
    $found = false;

    foreach ($catalog as $book) {
        $realTitle = $book['titel']; // <-- Hier nutzen wir deine Spalte 'titel'
        
        // Vergleich: Wie ähnlich ist der OCR-Text dem echten Titel?
        similar_text(strtolower($ocrText), strtolower($realTitle), $percent);
        
        // Wort-Check: Bonus-Punkte, wenn Wörter übereinstimmen
        $realWords = explode(' ', strtolower($realTitle));
        $ocrLower = strtolower($ocrText);
        $wordHits = 0;
        foreach($realWords as $rw) {
            // Nur Wörter länger als 2 Zeichen prüfen
            if (strlen($rw) > 2 && strpos($ocrLower, $rw) !== false) {
                $wordHits++;
            }
        }
        
        // Score berechnen: Prozentuale Ähnlichkeit + (10 Punkte pro Wort-Treffer)
        $totalScore = $percent + ($wordHits * 10);

        if ($totalScore > $highestSimilarity) {
            $highestSimilarity = $totalScore;
            $bestMatchTitle = $book['titel'];
            $found = true;
        }
    }

    // Nur zurückgeben, wenn der Score okay ist (über 40)
    if ($found && $highestSimilarity > 40) { 
        return $bestMatchTitle;
    }
    
    // Wenn kein Buch aus der Tabelle 'buecher' passt, geben wir nichts zurück (oder den OCR text)
    return null; 
}

// --- SUCHE ---
if ($searchTerm) {
    // Suchbegriff zerlegen (z.B. "system developers")
    $searchKeywords = explode(' ', strtolower(trim($searchTerm)));
    $searchKeywords = array_filter($searchKeywords);

    foreach ($ocrFragments as $frag) {
        $dbText = strtolower($frag['ocr_text']); 
        $dbWords = explode(' ', $dbText);
        
        $matches = 0;
        
        // Prüfen: Finden wir die Suchwörter im OCR-Text? (Die tolerante Suche von vorhin)
        foreach ($searchKeywords as $sWord) {
            $wordFound = false;
            foreach ($dbWords as $dWord) {
                // Beidseitiger Check + Levenshtein (Tippfehler)
                if (strpos($sWord, $dWord) !== false || strpos($dWord, $sWord) !== false) {
                    $wordFound = true; break;
                }
                $maxErrors = (strlen($sWord) > 4) ? 2 : 1;
                if (levenshtein($sWord, $dWord) <= $maxErrors) {
                    $wordFound = true; break;
                }
            }
            if ($wordFound) $matches++;
        }

        // Wenn der User-Suchbegriff im OCR-Text gefunden wurde...
        if ($matches > 0) {
            // ... dann suchen wir jetzt den SCHÖNEN Titel aus deiner 'buecher' Tabelle
            $cleanTitle = findBestRealTitle($frag['ocr_text'], $realBooks);

            // Falls wir einen sauberen Titel gefunden haben, nehmen wir den.
            // Falls nicht, zeigen wir zur Not den OCR-Text an (oder filtern es raus)
            $displayTitle = $cleanTitle ? $cleanTitle : "Unbekanntes Buch (" . $frag['ocr_text'] . ")";

            $percentage = ($matches / count($searchKeywords)) * 100;

            $foundBooks[] = [
                'display_title' => $displayTitle,
                'x' => $frag['pos_x'],
                'y' => $frag['pos_y'],
                'score' => $percentage
            ];
        }
    }

    // Sortieren nach Relevanz
    usort($foundBooks, function($a, $b) { return $b['score'] <=> $a['score']; });
}
?>

<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Bibliothek Suche</title>
    <style>
        body { font-family: sans-serif; padding: 20px; max-width: 800px; margin: auto; }
        .result { 
            border: 1px solid #ccc; padding: 20px; margin-bottom: 15px; 
            border-radius: 8px; background-color: #f9f9f9;
            border-left: 5px solid #28a745;
        }
        .title { font-size: 1.5em; font-weight: bold; color: #333; }
        .coords { color: #666; margin-top: 10px; font-size: 0.9em; }
    </style>
</head>
<body>

    <h1>🔍 Buch finden</h1>
    <form method="GET">
        <input type="text" name="q" value="<?= htmlspecialchars($searchTerm) ?>" placeholder="Buchtitel suchen..." style="padding:10px; width:70%;">
        <button type="submit" style="padding:10px;">Suchen</button>
    </form>
    <br>

    <?php if ($searchTerm): ?>
        <?php if (empty($foundBooks)): ?>
            <p>Nichts gefunden.</p>
        <?php else: ?>
            <?php foreach ($foundBooks as $book): ?>
                <div class="result">
                    <div class="title"><?= htmlspecialchars($book['display_title']) ?></div>
                    
                    <div class="coords">
                        📍 Standort: Regalhöhe <b><?= $book['y'] ?></b>, Position <b><?= $book['x'] ?></b>
                    </div>
                </div>
            <?php endforeach; ?>
        <?php endif; ?>
    <?php endif; ?>

</body>
</html>
