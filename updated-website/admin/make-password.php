<?php
/**
 * Helper to create a CMS login line for cms-config.php.
 *
 * Type a username and password; the page shows a line like
 *     'rachel' => '$2y$10$....',
 * to paste into the 'users' list in cms-config.php. Nothing is saved or logged.
 */

declare(strict_types=1);

require __DIR__ . '/includes/cms-lib.php';

cms_security_headers();
cms_session_start();

$line = '';
$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $csrf = (string) ($_POST['csrf'] ?? '');
    $username = trim((string) ($_POST['username'] ?? ''));
    $password = (string) ($_POST['password'] ?? '');
    if (empty($_SESSION['csrf_pw']) || !hash_equals((string) $_SESSION['csrf_pw'], $csrf)) {
        $error = 'The form expired, please try again.';
    } elseif (!preg_match('/^[A-Za-z0-9_.@\-]{3,40}$/', $username)) {
        $error = 'Usernames can use letters, numbers, dots, dashes, underscores and @ (3–40 characters).';
    } elseif (strlen($password) < 12) {
        $error = 'Please use a password of at least 12 characters.';
    } else {
        $line = var_export($username, true) . ' => ' . var_export(password_hash($password, PASSWORD_DEFAULT), true) . ',';
    }
}
$_SESSION['csrf_pw'] = bin2hex(random_bytes(32));
$nonce = cms_nonce();
?><!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Create a CMS login</title>
<style nonce="<?= h($nonce) ?>">
  body { margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center; background:#0E0F11;
         font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; color:#9E9FA0; padding:16px; }
  .card { width:100%; max-width:520px; background:#18191B; border:1px solid #313131; border-radius:18px; padding:28px; }
  h1 { color:#fff; font-size:20px; margin:0 0 8px; }
  label { display:block; color:#fff; font-size:14px; margin:14px 0 6px; }
  input { width:100%; box-sizing:border-box; padding:12px 14px; border-radius:10px; border:1px solid #313131; background:#0E0F11; color:#fff; font-size:16px; }
  button { margin-top:20px; padding:12px 24px; border:0; border-radius:30px; background:#9CFE4F; color:#1A1A1A; font-weight:700; cursor:pointer; }
  code { display:block; white-space:pre-wrap; word-break:break-all; background:#0E0F11; border:1px solid #9CFE4F; color:#fff; padding:12px; border-radius:10px; margin-top:16px; }
  .error { border:1px solid #e5484d; color:#ffb4b6; border-radius:10px; padding:10px 12px; margin-top:12px; }
  ol { padding-left:20px; font-size:14px; }
</style>
</head>
<body>
<main class="card">
  <h1>Create a CMS login</h1>
  <p>This creates a line to paste into the <strong>users</strong> list of your private <strong>cms-config.php</strong>. Nothing is saved.</p>
<?php if ($error !== ''): ?><div class="error"><?= h($error) ?></div><?php endif; ?>
<?php if ($line !== ''): ?>
  <p>Copy this line into the <strong>'users' =&gt; [ … ]</strong> list in cms-config.php:</p>
  <code><?= h($line) ?></code>
  <ol>
    <li>Open cms-config.php on your server (cPanel → File Manager).</li>
    <li>Paste the line inside <strong>'users' =&gt; [ … ]</strong> and save.</li>
    <li>Sign in at <strong>/admin/</strong> with this username and password.</li>
  </ol>
<?php endif; ?>
  <form method="post" action="make-password.php" autocomplete="off">
    <input type="hidden" name="csrf" value="<?= h((string) $_SESSION['csrf_pw']) ?>">
    <label for="username">Username</label>
    <input id="username" name="username" required>
    <label for="password">Password (at least 12 characters)</label>
    <input id="password" name="password" type="password" minlength="12" required autocomplete="new-password">
    <button type="submit">Create login line</button>
  </form>
</main>
</body>
</html>
