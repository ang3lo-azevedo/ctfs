<?php
if (!isset($_GET["name"])) {
    show_source(__FILE__); exit();
}

$f = "/tmp/" . $_SERVER['REMOTE_ADDR'] . ".txt";
if (strpos($f, '..') !== false) {
    echo "🤕"; exit();
}

if (isset($_GET["name"])) {
    file_put_contents($f, "Hello, " . $_GET["name"] . "! Enjoy the source code.");
}

if (strpos(file_get_contents($f), '<') !== false) {
    echo "🤕"; exit();
}
include $f;
?>