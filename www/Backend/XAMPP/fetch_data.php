<?php

// Header für JSON setzen
header('Content-Type: application/json; charset=utf-8');

// Datenbankverbindung
$servername = "localhost";
$username = "www"; // Dein Benutzername
$password = "wwwwww";     // Dein Passwort
$dbname = "biblio"; // Deine Datenbankname

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    echo json_encode(["error" => "Verbindung fehlgeschlagen"]);
    exit;
}

$conn->set_charset("utf8mb4");

// SQL-Abfrage
$sql = "SELECT b.Buecher_ID, b.Buechername, b.Autor, b.ISBN, b.Verfuegbar, l.Reihe, l.Spalte, l.Standort 
        FROM buecher b 
        JOIN locations l ON b.Locations = l.Reihe";

$result = $conn->query($sql);

$books = [];
if ($result && $result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $books[] = $row;
    }
}

echo json_encode($books, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);

// Verbindung schließen
$conn->close();
?>