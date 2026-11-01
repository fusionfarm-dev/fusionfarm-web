<?php
// Development only: PHP's built-in server does not read Apache .htaccess.
$root = dirname(__DIR__);
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
if (in_array($path, ['/contact', '/assets', '/privacy'], true)) {
    header('Content-Type: text/html; charset=utf-8');
    readfile($root . $path . '/index.html');
    return true;
}
if ($path === '/' || (is_string($path) && is_file($root . $path))) return false;
http_response_code(404);
header('Content-Type: text/html; charset=utf-8');
readfile($root . '/404.html');
