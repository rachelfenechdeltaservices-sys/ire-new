<?php
/**
 * Username & password sign-in for Sveltia CMS.
 *
 * Sveltia CMS opens this page in a popup when you click "Sign In". After a correct username and
 * password, the page hands the GitHub access token from cms-config.php back to the CMS window using
 * Sveltia's standard popup handshake (authorizing:github -> authorization:github:success:{token}).
 * The token never appears in the website's public files.
 */

declare(strict_types=1);

require __DIR__ . '/includes/cms-lib.php';

cms_security_headers();
cms_session_start();

$provider = (string) ($_REQUEST['provider'] ?? 'github');
$config = cms_config();
$error = '';
$success = false;
$wait = 0;

if ($provider !== 'github') {
    $error = 'Unsupported sign-in provider.';
} elseif ($config === null) {
    $error = 'The CMS is not set up yet: the private settings file cms-config.php was not found. See CMS-SETUP.md.';
} elseif (empty($config['github']['token']) || empty($config['github']['repo'])
    || strpos((string) $config['github']['token'], 'PASTE_YOUR') !== false) {
    $error = 'The GitHub access token in cms-config.php has not been filled in yet (see the CMS login guide).';
} elseif (empty($config['users']) || !is_array($config['users'])) {
    $error = 'No CMS users are set up in cms-config.php.';
} elseif ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $wait = cms_lockout_remaining();
    $csrf = (string) ($_POST['csrf'] ?? '');
    if ($wait > 0) {
        $error = 'Too many failed attempts. Please try again in ' . (int) ceil($wait / 60) . ' minute(s).';
    } elseif (empty($_SESSION['csrf']) || !hash_equals((string) $_SESSION['csrf'], $csrf)) {
        $error = 'Your sign-in form expired. Please try again.';
    } else {
        $username = trim((string) ($_POST['username'] ?? ''));
        $password = (string) ($_POST['password'] ?? '');
        if ($username !== '' && $password !== '' && cms_check_login($username, $password)) {
            cms_clear_failures();
            session_regenerate_id(true);
            $success = true;
        } else {
            cms_record_failure();
            usleep(random_int(400000, 900000));   // slow down guessing
            $error = 'Incorrect username or password.';
        }
    }
}

if (!$success) {
    $_SESSION['csrf'] = bin2hex(random_bytes(32));
} else {
    unset($_SESSION['csrf']);
}

$nonce = cms_nonce();
$jsonFlags = JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_UNESCAPED_SLASHES;
?><!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Sign in – Top 10 Irish Casino CMS</title>
<style nonce="<?= h($nonce) ?>">
  :root { --bg:#0E0F11; --card:#18191B; --border:#313131; --text:#9E9FA0; --white:#fff; --green:#9CFE4F; --red:#e5484d; }
  * { box-sizing: border-box; }
  body { margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center; background:var(--bg);
         font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; color:var(--text); padding:16px; }
  .card { width:100%; max-width:380px; background:var(--card); border:1px solid var(--border); border-radius:18px; padding:28px; }
  .logo { display:block; margin:0 auto 14px; height:72px; }
  h1 { color:var(--white); font-size:20px; margin:0 0 4px; text-align:center; }
  p.sub { margin:0 0 22px; text-align:center; font-size:14px; }
  label { display:block; color:var(--white); font-size:14px; margin:14px 0 6px; }
  input { width:100%; padding:12px 14px; border-radius:10px; border:1px solid var(--border); background:var(--bg);
          color:var(--white); font-size:16px; }
  input:focus { outline:2px solid var(--green); outline-offset:1px; }
  button { width:100%; margin-top:22px; padding:12px; border:0; border-radius:30px; background:var(--green); color:#1A1A1A;
           font-weight:700; font-size:16px; cursor:pointer; }
  .error { background:rgba(229,72,77,.12); border:1px solid var(--red); color:#ffb4b6; border-radius:10px; padding:10px 12px; font-size:14px; }
  .ok { text-align:center; color:var(--white); }
</style>
</head>
<body>
<main class="card">
  <img class="logo" src="../assets/images/loader.png" alt="Top 10 Irish Casino">
<?php if ($success): ?>
  <h1>Signed in</h1>
  <p class="sub ok" id="status">Connecting to the CMS…</p>
  <script nonce="<?= h($nonce) ?>">
  (function () {
    var token = <?= json_encode((string) $config['github']['token'], $jsonFlags) ?>;
    var provider = 'github';
    var origin = window.location.origin;
    var status = document.getElementById('status');
    var sent = false;
    if (!window.opener) {
      status.textContent = 'Please open the CMS at /admin/ and sign in from there.';
      return;
    }
    function onMessage(event) {
      if (event.origin !== origin || event.source !== window.opener || sent) return;
      if (event.data === 'authorizing:' + provider) {
        sent = true;
        window.removeEventListener('message', onMessage);
        window.opener.postMessage(
          'authorization:' + provider + ':success:' + JSON.stringify({ token: token, provider: provider }),
          origin
        );
        token = null;
        status.textContent = 'Signed in. This window will close automatically.';
      }
    }
    window.addEventListener('message', onMessage);
    window.opener.postMessage('authorizing:' + provider, origin);
  })();
  </script>
<?php else: ?>
  <h1>Top 10 Irish Casino CMS</h1>
  <p class="sub">Sign in to edit the website</p>
<?php if ($error !== ''): ?>
  <div class="error" role="alert"><?= h($error) ?></div>
<?php endif; ?>
<?php if ($error === '' || $error === 'Incorrect username or password.' || strpos($error, 'expired') !== false): ?>
  <form method="post" action="auth.php?provider=github" autocomplete="on">
    <input type="hidden" name="csrf" value="<?= h((string) $_SESSION['csrf']) ?>">
    <label for="username">Username</label>
    <input id="username" name="username" type="text" autocomplete="username" required autofocus
           value="<?= h((string) ($_POST['username'] ?? '')) ?>">
    <label for="password">Password</label>
    <input id="password" name="password" type="password" autocomplete="current-password" required>
    <button type="submit">Sign in</button>
  </form>
<?php endif; ?>
<?php endif; ?>
</main>
</body>
</html>
