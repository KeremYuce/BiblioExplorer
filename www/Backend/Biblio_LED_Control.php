<?php
// --- KONFIGURATION ---
$port = "/dev/ttyACM0"; // Dein Port
$baud = 115200;         // Muss exakt zum Arduino Code passen!

$message = "";
$messageType = ""; 

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $raw_command = $_POST['command']; 
    
    if (!empty($raw_command)) {
        
        // 1. Prüfen ob Port existiert
        if (!file_exists($port)) {
            $message = "FEHLER: Der Port <code>$port</code> wurde nicht gefunden.";
            $messageType = "error";
        } else {
            // 2. Prüfen ob wir Rechte haben
            if (!is_writable($port)) {
                $message = "FEHLER: Der Webserver darf nicht auf <code>$port</code> schreiben.<br>" .
                           "<small>Bitte führe aus: <code>sudo usermod -a -G dialout www-data</code> und starte Apache neu.</small>";
                $messageType = "error";
            } else {
                // 3. Port konfigurieren (Linux stty)
                // 'raw' verhindert, dass Linux Zeichen verändert
                // '-hupcl' versucht Auto-Reset zu verhindern (klappt aber oft nicht, daher sleep)
                $cmd = "stty -F " . escapeshellarg($port) . " raw speed $baud cs8 -cstopb -parenb -hupcl";
                exec($cmd);
                
                // 4. Port öffnen
                $fp = @fopen($port, "c+"); // "c+" ist stabiler als "w"
                
                if ($fp) {
                    // WICHTIG: Arduino startet beim Öffnen neu!
                    // Wir müssen warten, bis er bereit ist.
                    sleep(2); 

                    // Befehl senden + Zeilenumbruch (\n)
                    fwrite($fp, $raw_command . "\n");
                    
                    fclose($fp);
                    
                    $message = "Erfolg: Befehl <strong>'$raw_command'</strong> gesendet (nach 2s Wartezeit).";
                    $messageType = "success";
                } else {
                    $message = "Konnte Port nicht öffnen (fopen failed).";
                    $messageType = "error";
                }
            }
        }
    }
}
?>

<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LED Control</title>
    <style>
        body { font-family: sans-serif; background: #222; color: #fff; display: flex; justify-content: center; padding-top: 50px; }
        .card { background: #333; padding: 20px; border-radius: 8px; width: 100%; max-width: 400px; text-align: center; }
        input { padding: 10px; font-size: 1.2rem; text-align: center; width: 70%; border-radius: 4px; border:none; }
        button { padding: 10px 20px; font-size: 1.2rem; background: #2e7d32; color: white; border: none; cursor: pointer; margin-top: 10px; border-radius: 4px; }
        .status { margin-top: 20px; padding: 10px; border-radius: 4px; }
        .success { background: #1b5e20; }
        .error { background: #b71c1c; }
        code { background: #000; padding: 2px 4px; font-family: monospace; }
    </style>
</head>
<body>

<div class="card">
    <h1>💡 LED Steuerung</h1>
    <p style="color:#aaa;">Port: <?php echo $port; ?></p>

    <form method="POST">
        <input type="text" name="command" placeholder="z.B. +0" autofocus>
        <br>
        <button type="submit">Senden</button>
    </form>

    <?php if ($message): ?>
        <div class="status <?php echo $messageType; ?>">
            <?php echo $message; ?>
        </div>
    <?php endif; ?>
    
    <div style="text-align:left; margin-top:20px; color:#aaa; font-size:0.9rem;">
        <strong>Befehle:</strong><br>
        <code>+0</code> LED 0 an (Weiß)<br>
        <code>-0</code> LED 0 aus<br>
        <code>0:255,0,0</code> LED 0 Rot<br>
        <code>*</code> Alle aus
    </div>
</div>

</body>
</html>
