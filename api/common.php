<?php
declare(strict_types=1);
// Never place real credentials under the public document root.
function ff_config(): array {
    $file = dirname(__DIR__, 2) . '/fusionfarm-contact-config.php';
    if (!is_file($file)) return [];
    $config = require $file;
    return is_array($config) ? $config : [];
}
function ff_ready(array $config): bool {
    return !empty($config['enabled']) && !empty($config['site_key']) && !empty($config['secret_key'])
        && !empty($config['hostname']) && !empty($config['from_email'])
        && filter_var($config['from_email'], FILTER_VALIDATE_EMAIL) !== false
        && str_ends_with($config['from_email'], '@fusionfarm.net');
}
function ff_json(int $status, array $data): never {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    header('X-Content-Type-Options: nosniff');
    echo json_encode($data, JSON_UNESCAPED_SLASHES);
    exit;
}
function ff_value(array $data, string $key, int $max, bool $required = false): string {
    if (!isset($data[$key])) $data[$key] = '';
    if (!is_string($data[$key])) throw new InvalidArgumentException('Please check the form fields.');
    $value = trim($data[$key]);
    if (strlen($value) > $max || ($required && $value === '')) throw new InvalidArgumentException('Please check the form fields.');
    return $value;
}
function ff_message(array $data): array {
    $routes = ['Project' => 'pete', 'Research' => 'research', 'Digital assets' => 'domains', 'Support' => 'support'];
    $name = ff_value($data, 'name', 120, true);
    $company = ff_value($data, 'company', 180);
    $email = ff_value($data, 'email', 254, true);
    $topic = ff_value($data, 'topic', 30, true);
    $message = ff_value($data, 'message', 10000, true);
    if (!isset($routes[$topic]) || !filter_var($email, FILTER_VALIDATE_EMAIL) || preg_match('/[\r\n\x00]/', $email . $name . $company) || strlen($message) < 10) {
        throw new InvalidArgumentException('Please check your email, topic and message.');
    }
    return ['to' => $routes[$topic] . '@fusionfarm.net', 'reply_to' => $email,
        'subject' => 'Fusion Farm website: ' . $topic,
        'body' => "Name: $name\nCompany: $company\nEmail: $email\nTopic: $topic\n\n$message"];
}
