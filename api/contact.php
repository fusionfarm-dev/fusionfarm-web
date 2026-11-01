<?php
declare(strict_types=1);
require __DIR__ . '/common.php';
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Allow: POST'); ff_json(405, ['ok' => false, 'message' => 'Please submit the contact form.']); }
if ((int)($_SERVER['CONTENT_LENGTH'] ?? 0) > 24000) ff_json(413, ['ok' => false, 'message' => 'Please shorten your message.']);
$config = ff_config();
if (!ff_ready($config) || !function_exists('curl_init')) ff_json(503, ['ok' => false, 'message' => 'The form is temporarily unavailable. Please email us directly.']);
$allowedOrigin = 'https://' . $config['hostname'];
if (isset($_SERVER['HTTP_ORIGIN']) && $_SERVER['HTTP_ORIGIN'] !== $allowedOrigin) ff_json(403, ['ok' => false, 'message' => 'Please use the form on our website.']);
try {
    if (ff_value($_POST, 'website', 1000) !== '') ff_json(400, ['ok' => false, 'message' => 'Your message could not be accepted.']);
    $mail = ff_message($_POST);
    $token = ff_value($_POST, 'cf-turnstile-response', 2048, true);
} catch (InvalidArgumentException $e) { ff_json(400, ['ok' => false, 'message' => $e->getMessage()]); }
$curl = curl_init('https://challenges.cloudflare.com/turnstile/v0/siteverify');
curl_setopt_array($curl, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => http_build_query(['secret' => $config['secret_key'], 'response' => $token]), CURLOPT_RETURNTRANSFER => true, CURLOPT_CONNECTTIMEOUT => 5, CURLOPT_TIMEOUT => 12]);
$raw = curl_exec($curl);
$code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
curl_close($curl);
$check = is_string($raw) ? json_decode($raw, true) : null;
if ($code !== 200 || !is_array($check)) ff_json(503, ['ok' => false, 'message' => 'Security verification is unavailable. Please try again or email us directly.']);
if (empty($check['success']) || ($check['hostname'] ?? '') !== $config['hostname'] || ($check['action'] ?? '') !== 'contact') ff_json(400, ['ok' => false, 'message' => 'Please complete the security check again.']);
$headers = ['From' => 'Fusion Farm website <' . $config['from_email'] . '>', 'Reply-To' => $mail['reply_to'], 'MIME-Version' => '1.0', 'Content-Type' => 'text/plain; charset=UTF-8', 'Content-Transfer-Encoding' => 'base64'];
$sent = mail($mail['to'], $mail['subject'], chunk_split(base64_encode($mail['body'])), $headers);
if (!$sent) ff_json(503, ['ok' => false, 'message' => 'Your message could not be sent. Please email us directly.']);
ff_json(200, ['ok' => true, 'message' => 'Your message has been accepted for delivery. Thank you for contacting Fusion Farm.']);
