<?php
/**
 * Shared helpers for the Top 10 Irish Casino CMS login (auth.php, backend.php, make-password.php).
 *
 * The private settings file (cms-config.php) holds the GitHub account details the CMS saves content
 * with, and the CMS usernames/passwords. It is looked for in these places, in order:
 *
 *   1. The path in the CMS_CONFIG_FILE environment variable (if your host lets you set one)
 *   2. <folder above the website root>/cms-private/cms-config.php      <- recommended
 *   3. <website root>/../cms-private/cms-config.php                     (same, found from this file)
 *   4. <website root>/admin/cms-config.php                              (fallback, blocked by .htaccess)
 */

declare(strict_types=1);

if (PHP_VERSION_ID < 70400) {
    http_response_code(500);
    exit('The CMS login needs PHP 7.4 or newer.');
}

function cms_config_candidates(): array
{
    $list = [];
    $env = getenv('CMS_CONFIG_FILE');
    if ($env) {
        $list[] = $env;
    }
    if (!empty($_SERVER['DOCUMENT_ROOT'])) {
        $list[] = dirname(rtrim((string) $_SERVER['DOCUMENT_ROOT'], '/\\')) . '/cms-private/cms-config.php';
    }
    $list[] = dirname(__DIR__, 3) . '/cms-private/cms-config.php';
    $list[] = dirname(__DIR__) . '/cms-config.php';
    return array_values(array_unique($list));
}

/** Load the private settings file, or return null if it does not exist yet. */
function cms_config(): ?array
{
    static $config = false;
    if ($config !== false) {
        return $config;
    }
    $config = null;
    foreach (cms_config_candidates() as $path) {
        if (is_file($path) && is_readable($path)) {
            $loaded = require $path;
            if (is_array($loaded)) {
                $config = $loaded;
                $config['_path'] = $path;
            }
            break;
        }
    }
    return $config;
}

function cms_is_https(): bool
{
    if (!empty($_SERVER['HTTPS']) && strtolower((string) $_SERVER['HTTPS']) !== 'off') {
        return true;
    }
    if (strtolower((string) ($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '')) === 'https') {
        return true;
    }
    return (string) ($_SERVER['SERVER_PORT'] ?? '') === '443';
}

/** Origin of the current request, e.g. https://top10irishcasino.site */
function cms_origin(): string
{
    $host = (string) ($_SERVER['HTTP_HOST'] ?? 'localhost');
    if (!preg_match('/^[A-Za-z0-9.\-]+(:\d+)?$/', $host)) {
        $host = 'localhost';
    }
    return (cms_is_https() ? 'https' : 'http') . '://' . $host;
}

/** URL path of the admin folder, e.g. /admin */
function cms_admin_path(): string
{
    $dir = str_replace('\\', '/', dirname((string) ($_SERVER['SCRIPT_NAME'] ?? '/admin/x.php')));
    return rtrim($dir, '/');
}

function cms_nonce(): string
{
    static $nonce = null;
    if ($nonce === null) {
        $nonce = base64_encode(random_bytes(16));
    }
    return $nonce;
}

function cms_security_headers(): void
{
    $n = cms_nonce();
    header('Cache-Control: no-store, max-age=0');
    header('Pragma: no-cache');
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: DENY');
    header('Referrer-Policy: no-referrer');
    header('X-Robots-Tag: noindex, nofollow');
    header("Content-Security-Policy: default-src 'none'; script-src 'nonce-$n'; style-src 'nonce-$n'; "
        . "img-src 'self' data:; form-action 'self'; base-uri 'none'; frame-ancestors 'none'");
}

function cms_session_start(): void
{
    if (session_status() === PHP_SESSION_ACTIVE) {
        return;
    }
    session_name('T10CMS');
    session_set_cookie_params([
        'lifetime' => 0,
        'path' => cms_admin_path() . '/',
        'secure' => cms_is_https(),
        'httponly' => true,
        'samesite' => 'Strict',
    ]);
    session_start();
}

function h(string $s): string
{
    return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

// ------------------------------------------------------------------------------------------------
// Brute-force protection: failed sign-ins are counted per IP address in a small file.
// ------------------------------------------------------------------------------------------------

function cms_attempts_file(): string
{
    $config = cms_config();
    $dir = $config && !empty($config['_path']) ? dirname($config['_path']) : sys_get_temp_dir();
    if (!is_writable($dir)) {
        $dir = sys_get_temp_dir();
    }
    return rtrim($dir, '/\\') . '/.cms-login-attempts.json';
}

function cms_client_key(): string
{
    return hash('sha256', (string) ($_SERVER['REMOTE_ADDR'] ?? 'unknown'));
}

/** Run $fn with the attempts data loaded and locked; whatever $fn returns as 'data' is saved. */
function cms_with_attempts(callable $fn)
{
    $file = cms_attempts_file();
    $fp = @fopen($file, 'c+');
    if (!$fp) {
        $result = $fn([]);
        return $result['return'] ?? null;
    }
    flock($fp, LOCK_EX);
    $raw = stream_get_contents($fp);
    $data = json_decode($raw ?: '[]', true);
    if (!is_array($data)) {
        $data = [];
    }
    $now = time();
    foreach ($data as $k => $entry) {           // forget old entries
        if (($entry['until'] ?? 0) < $now && ($entry['last'] ?? 0) < $now - 86400) {
            unset($data[$k]);
        }
    }
    $result = $fn($data);
    ftruncate($fp, 0);
    rewind($fp);
    fwrite($fp, json_encode($result['data'] ?? $data));
    fflush($fp);
    flock($fp, LOCK_UN);
    fclose($fp);
    @chmod($file, 0600);
    return $result['return'] ?? null;
}

/** Seconds the current client must still wait, 0 if it may try. */
function cms_lockout_remaining(): int
{
    $key = cms_client_key();
    return (int) cms_with_attempts(function (array $data) use ($key) {
        $until = (int) ($data[$key]['until'] ?? 0);
        return ['data' => $data, 'return' => max(0, $until - time())];
    });
}

function cms_record_failure(): void
{
    $config = cms_config() ?? [];
    $max = max(1, (int) ($config['max_attempts'] ?? 5));
    $minutes = max(1, (int) ($config['lockout_minutes'] ?? 15));
    $key = cms_client_key();
    cms_with_attempts(function (array $data) use ($key, $max, $minutes) {
        $entry = $data[$key] ?? ['count' => 0, 'until' => 0, 'last' => 0];
        if (($entry['last'] ?? 0) < time() - $minutes * 60) {
            $entry['count'] = 0;               // reset the window
        }
        $entry['count']++;
        $entry['last'] = time();
        if ($entry['count'] >= $max) {
            $entry['until'] = time() + $minutes * 60;
            $entry['count'] = 0;
        }
        $data[$key] = $entry;
        return ['data' => $data];
    });
}

function cms_clear_failures(): void
{
    $key = cms_client_key();
    cms_with_attempts(function (array $data) use ($key) {
        unset($data[$key]);
        return ['data' => $data];
    });
}

/** Check a username/password against the users in cms-config.php (constant-time-ish). */
function cms_check_login(string $username, string $password): bool
{
    $config = cms_config() ?? [];
    $users = is_array($config['users'] ?? null) ? $config['users'] : [];
    $hash = null;
    foreach ($users as $name => $userHash) {
        if (is_string($name) && hash_equals(strtolower($name), strtolower($username))) {
            $hash = (string) $userHash;
        }
    }
    // Always run password_verify so a wrong username takes as long as a wrong password.
    $dummy = '$2y$10$usesomesillystringfore7hnbRJHxXVLeakoG8K30oukPsA.ztMG';
    $ok = password_verify($password, $hash ?? $dummy);
    return $ok && $hash !== null;
}
