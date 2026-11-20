<?php
/*
 * Full Moon Play Style Guide: password gate.
 * Put this file next to index.php and add this as the very first line of index.php:
 *   <?php require __DIR__ . '/gate.php'; ?>
 * Change the password below.
 */
const GUIDE_PASSWORD = 'change-me';        // <-- set your password here
const GUIDE_SESSION_HOURS = 12;            // stay logged in for this many hours

session_set_cookie_params(['lifetime' => GUIDE_SESSION_HOURS * 3600, 'path' => '/', 'httponly' => true, 'samesite' => 'Lax', 'secure' => !empty($_SERVER['HTTPS'])]);
session_start();
header('X-Robots-Tag: noindex, nofollow');

if (isset($_GET['logout'])) {
    $_SESSION = [];
    session_destroy();
    header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?'));
    exit;
}

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['guide_password'])) {
    $_SESSION['guide_tries'] = ($_SESSION['guide_tries'] ?? 0) + 1;
    if ($_SESSION['guide_tries'] > 5 && time() - ($_SESSION['guide_last'] ?? 0) < 60) {
        $error = 'Too many attempts. Please wait a minute and try again.';
    } elseif (hash_equals(GUIDE_PASSWORD, (string)$_POST['guide_password'])) {
        session_regenerate_id(true);
        $_SESSION['guide_ok'] = time();
        unset($_SESSION['guide_tries']);
        header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?'));
        exit;
    } else {
        $error = 'Incorrect password. Please try again.';
    }
    $_SESSION['guide_last'] = time();
}

if (!empty($_SESSION['guide_ok']) && time() - $_SESSION['guide_ok'] < GUIDE_SESSION_HOURS * 3600) {
    return; // logged in: show the style guide
}
?><!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Full Moon Play Style Guide · Sign in</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;display:grid;place-items:center;padding:16px;background:#000816;color:#fff;font-family:Poppins,system-ui,sans-serif;
  background-image:radial-gradient(60% 50% at 20% 10%,rgba(4,245,229,.12),transparent 70%),radial-gradient(60% 50% at 85% 90%,rgba(180,77,255,.16),transparent 70%)}
.gate{width:100%;max-width:420px;padding:32px 28px;border:2px solid transparent;border-radius:24px;
  background:linear-gradient(#0A0F24,#0A0F24) padding-box,linear-gradient(120deg,#04F5E5,#B44DFF) border-box;
  box-shadow:0 0 28px rgba(4,245,229,.18),0 0 40px rgba(180,77,255,.18)}
.brand{margin:0 0 4px;font:800 22px/1.2 Poppins,sans-serif;letter-spacing:.02em}
.sub{margin:0 0 26px;color:#04F5E5;font:600 11px/1.4 Poppins,sans-serif;letter-spacing:.22em;text-transform:uppercase}
label{display:block;margin:0 0 8px;font:500 15px Poppins,sans-serif}
.field{position:relative}
input{width:100%;min-height:50px;padding:0 48px 0 16px;border:1.5px solid #3A4A70;border-radius:12px;background:#060B1C;color:#fff;font:400 16px Poppins,sans-serif;outline:none;transition:border-color .2s,box-shadow .2s}
input:focus{border-color:#04F5E5;box-shadow:0 0 12px rgba(4,245,229,.35)}
.eye{position:absolute;right:8px;top:50%;transform:translateY(-50%);width:36px;height:36px;display:grid;place-items:center;border:0;border-radius:8px;background:transparent;color:#A8B4C7;cursor:pointer}
.eye:hover{color:#fff}
.err{margin:10px 0 0;color:#FF5C9A;font-size:14px}
button.go{width:100%;min-height:50px;margin-top:20px;border:0;border-radius:12px;background:linear-gradient(100deg,#00D9C9,#18FFE0);color:#00151C;font:600 16px Poppins,sans-serif;box-shadow:0 0 18px rgba(4,245,229,.45);cursor:pointer;transition:transform .2s,box-shadow .2s}
button.go:hover{transform:translateY(-2px);box-shadow:0 0 26px rgba(4,245,229,.7)}
.note{margin:18px 0 0;color:#8FA0B7;font-size:12.5px;text-align:center}
</style>
</head>
<body>
<form class="gate" method="post" autocomplete="off">
  <p class="brand">FULL MOON PLAY</p>
  <p class="sub">Style guide · private</p>
  <label for="pw">Password</label>
  <div class="field">
    <input id="pw" name="guide_password" type="password" required autofocus aria-describedby="<?= $error ? 'err' : '' ?>">
    <button class="eye" type="button" aria-label="Show password" onclick="var i=document.getElementById('pw');i.type=i.type==='password'?'text':'password';this.setAttribute('aria-label',i.type==='password'?'Show password':'Hide password')">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>
    </button>
  </div>
  <?php if ($error): ?><p class="err" id="err" role="alert"><?= htmlspecialchars($error) ?></p><?php endif; ?>
  <button class="go" type="submit">View Style Guide</button>
  <p class="note">Ask the Full Moon Play team for access.</p>
</form>
</body>
</html>
<?php exit; ?>
