<?php
// Tells the contact page whether the form backend is configured, and which
// public Turnstile site key to render. Never exposes the secret.
declare(strict_types=1);
require __DIR__ . '/common.php';
if ($_SERVER['REQUEST_METHOD'] !== 'GET') { header('Allow: GET'); ff_json(405, ['enabled' => false]); }
$config = ff_config();
$ready = ff_ready($config) && function_exists('curl_init');
ff_json(200, ['enabled' => $ready, 'siteKey' => $ready ? $config['site_key'] : null]);
