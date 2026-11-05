<?php
// SUPER SECURE SESSION MANAGEMENT
session_set_cookie_params([
    'secure' => true,
    'httponly' => true,
    'samesite' => 'Strict'
]);
session_start();

if (!isset($_SESSION['notes'])) {
    $_SESSION['notes'] = [];
}

// Handle form submission
if (isset($_POST['note']) && is_string($_POST['note'])) {
    $_SESSION['notes'][] = $_POST['note'];
    header('Location: /');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/style.css">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🗒️</text></svg>">
    <title>BILLY BOARD</title>
</head>
<body>
    <div class="container">
        <h3>BILLY BOARD</h3>
        <form method="POST">
            <textarea name="note" placeholder="Enter your Note" required></textarea>
            <button type="submit">Save</button>
        </form>
        <?php if (!empty($_SESSION['notes'])): ?>
            <ul>
                <?php foreach ($_SESSION['notes'] as $note): ?>
                    <li><?= $note ?></li>
                <?php endforeach; ?>
            </ul>
        <?php endif; ?>
    </div>
</body>
</html>
