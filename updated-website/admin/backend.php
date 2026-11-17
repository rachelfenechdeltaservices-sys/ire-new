<?php
/**
 * Serves the `backend` part of the Sveltia CMS configuration, read from the private cms-config.php:
 * which GitHub repository and branch the content is saved to, and where the username & password
 * sign-in page is. Sveltia CMS merges this with config.yml.
 *
 * Nothing secret is returned here: the GitHub token is only handed over after signing in (auth.php).
 */

declare(strict_types=1);

require __DIR__ . '/includes/cms-lib.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, max-age=0');
header('X-Content-Type-Options: nosniff');
header('X-Robots-Tag: noindex, nofollow');

$config = cms_config();
if ($config === null || empty($config['github']['repo'])) {
    http_response_code(503);
    echo json_encode([
        'error' => 'CMS not set up: create cms-config.php from cms-config.example.php (see CMS-SETUP.md).',
    ]);
    exit;
}

$repo = (string) $config['github']['repo'];
$branch = (string) ($config['github']['branch'] ?? 'main');
if (!preg_match('#^[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+$#', $repo)) {
    http_response_code(500);
    echo json_encode(['error' => 'cms-config.php: github.repo must look like "owner/repository".']);
    exit;
}

$origin = cms_origin();
$adminPath = cms_admin_path();                       // e.g. /admin
$sitePath = rtrim(dirname($adminPath), '/');          // e.g. '' when the site is at the domain root

echo json_encode([
    'backend' => [
        'repo' => $repo,
        'branch' => $branch,
        'base_url' => $origin,
        'auth_endpoint' => ltrim($adminPath . '/auth.php', '/'),
    ],
    'site_url' => $origin . $sitePath . '/',
    'display_url' => $origin . $sitePath . '/',
], JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
