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
 *   4. <website root>/cms-config.php, <website root>/cms-private/cms-config.php or
 *      <website root>/admin/cms-config.php                             (blocked by .htaccess)
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
    // Inside the website folder (public_html): blocked from download by .htaccess, and PHP
    // files only ever return their settings to the CMS, they never print them.
    $webRoot = dirname(__DIR__, 2);
    $list[] = $webRoot . '/cms-config.php';                 // public_html/cms-config.php
    $list[] = $webRoot . '/cms-private/cms-config.php';     // public_html/cms-private/cms-config.php
    $list[] = dirname(__DIR__) . '/cms-config.php';         // public_html/admin/cms-config.php
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
    // Never write the log inside the public website folder.
    $webRoot = realpath(dirname(__DIR__, 2));
    $realDir = realpath($dir);
    if ($webRoot && $realDir && strpos($realDir . '/', $webRoot . '/') === 0) {
        $dir = sys_get_temp_dir();
    }
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

// ------------------------------------------------------------------------------------------------
// GitHub settings helpers
// ------------------------------------------------------------------------------------------------

/**
 * Accept the repository written in several ways and return "owner/name":
 *   owner/name, owner/name.git, https://github.com/owner/name(.git), git@github.com:owner/name.git
 */
function cms_normalize_repo(string $repo): string
{
    $repo = trim($repo);
    $repo = preg_replace('#^(https?://)?(www\.)?github\.com/#i', '', $repo);
    $repo = preg_replace('#^git@github\.com:#i', '', $repo);
    $repo = preg_replace('#\.git$#i', '', rtrim($repo, '/'));
    return trim($repo, '/');
}

function cms_repo(): string
{
    $config = cms_config() ?? [];
    return cms_normalize_repo((string) ($config['github']['repo'] ?? ''));
}

/**
 * Folder inside the repository that holds the website (the folder with content/, admin/, index.html …).
 * Default '' = the top level of the repository.
 */
function cms_root_dir(): string
{
    $config = cms_config() ?? [];
    // Not set = website files at the top level of the repository (e.g. infoyasska-design/irenew).
    $dir = (string) ($config['github']['root_dir'] ?? '');
    return trim(str_replace('\\', '/', $dir), "/ \t");
}

function cms_branch(): string
{
    $config = cms_config() ?? [];
    $branch = trim((string) ($config['github']['branch'] ?? ''));
    return $branch !== '' ? $branch : 'main';
}

/** GET a GitHub API path with the token. Returns [status, decoded body] or null if the server can't reach GitHub. */
function cms_github_get(string $path, string $token): ?array
{
    $base = getenv('CMS_GITHUB_API') ?: 'https://api.github.com';   // override only used for testing
    $url = rtrim($base, '/') . $path;
    $headers = [
        'Accept: application/vnd.github+json',
        'Authorization: Bearer ' . $token,
        'User-Agent: Top10IrishCasino-CMS',
        'X-GitHub-Api-Version: 2022-11-28',
    ];
    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_TIMEOUT => 8,
            CURLOPT_CONNECTTIMEOUT => 5,
        ]);
        $body = curl_exec($ch);
        $status = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        if ($body === false || $status === 0) {
            return null;
        }
        return [$status, json_decode((string) $body, true)];
    }
    if (filter_var(ini_get('allow_url_fopen'), FILTER_VALIDATE_BOOLEAN)) {
        $ctx = stream_context_create(['http' => [
            'method' => 'GET', 'header' => implode("\r\n", $headers), 'timeout' => 8, 'ignore_errors' => true,
        ]]);
        $body = @file_get_contents($url, false, $ctx);
        if ($body === false || empty($http_response_header[0])) {
            return null;
        }
        preg_match('#\s(\d{3})\s#', $http_response_header[0] . ' ', $m);
        return [(int) ($m[1] ?? 0), json_decode($body, true)];
    }
    return null;
}

/**
 * Check the repository, branch and token in cms-config.php with GitHub.
 * Returns a plain-English problem description, or '' if everything is fine (or GitHub can't be reached
 * from the server, in which case the CMS itself will report any problem).
 */
function cms_github_problem(): string
{
    $config = cms_config() ?? [];
    $token = (string) ($config['github']['token'] ?? '');
    $repo = cms_repo();
    $branch = cms_branch();
    $fix = "Open cms-config.php and check the 'repo' line. It should be exactly: 'repo' => 'owner/repository-name', "
         . "e.g. 'infoyasska-design/irenew' (no https://, no .git).";
    if (!preg_match('#^[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+$#', $repo)) {
        return "The repository \"$repo\" in cms-config.php is not in the form owner/repository-name. $fix";
    }
    $r = cms_github_get('/repos/' . $repo, $token);
    if ($r === null) {
        return '';
    }
    [$status, $body] = $r;
    if ($status === 401) {
        return 'GitHub did not accept the access token in cms-config.php: it is mistyped, expired or was deleted. '
             . 'Create a new fine-grained token (Contents: Read and write) and paste it into the \'token\' line.';
    }
    if ($status === 404 || $status === 403) {
        return "GitHub can't find the repository \"$repo\" with this token. Either the name is wrong, or the token "
             . "wasn't given access to it (fine-grained token → Repository access → Only select repositories → "
             . "choose this repository). $fix";
    }
    if ($status >= 200 && $status < 300 && empty($body['permissions']['push'])) {
        return "The access token can read \"$repo\" but can't save to it. Edit the token on GitHub and set "
             . 'Repository permissions → Contents to "Read and write".';
    }
    $b = cms_github_get('/repos/' . $repo . '/branches/' . rawurlencode($branch), $token);
    if ($b !== null && $b[0] === 404) {
        return "The branch \"$branch\" doesn't exist in \"$repo\". Check the 'branch' line in cms-config.php "
             . "(for example 'main').";
    }
    $root = cms_root_dir();
    $contentPath = ($root !== '' ? $root . '/' : '') . 'content/settings.json';
    $encoded = implode('/', array_map('rawurlencode', explode('/', $contentPath)));
    $c = cms_github_get('/repos/' . $repo . '/contents/' . $encoded . '?ref=' . rawurlencode($branch), $token);
    if ($c !== null && $c[0] === 404) {
        $where = $root !== '' ? "inside the folder \"$root\"" : 'at the top level';
        return "The website's content files were not found $where of \"$repo\" (branch \"$branch\"): "
             . "GitHub has no \"$contentPath\". If the website files (content/, admin/, index.html …) are at the top "
             . "of the repository, set 'root_dir' => '' in cms-config.php; if they are in a folder, put that folder's "
             . "name there. If the repository doesn't contain the website's content/ folder yet, it has to be "
             . "copied in first.";
    }
    return '';
}
