<?php
// php tests/contact-test.php   (ported from PR #1)
declare(strict_types=1);
require dirname(__DIR__) . '/src/static/api/common.php';

function check(bool $condition, string $label): void {
    if (!$condition) throw new RuntimeException("FAIL $label");
    echo "PASS $label\n";
}

$valid = ['name' => 'A visitor', 'company' => 'Example', 'email' => 'visitor@example.com', 'message' => 'A decision about a new market.'];
foreach (['project' => 'research', 'research' => 'research', 'domains' => 'domains', 'support' => 'support'] as $topic => $inbox) {
    $result = ff_message($valid + ['topic' => $topic]);
    check($result['to'] === "$inbox@fusionfarm.net", "Routes $topic to $inbox@");
    check($result['reply_to'] === $valid['email'], "Reply-To is the visitor ($topic)");
}
$bad = [
    ['topic' => 'arbitrary@example.com'],
    ['email' => "a@example.com\r\nBcc: bad@example.com"],
    ['name' => ['array']],
    ['company' => "x\r\nBcc: injected"],
    ['message' => 'short'],
    ['message' => str_repeat('x', 5001)],
    ['email' => 'not-an-email'],
];
foreach ($bad as $change) {
    try {
        ff_message(array_replace($valid + ['topic' => 'project'], $change));
        throw new RuntimeException('FAIL invalid submission accepted: ' . key($change));
    } catch (InvalidArgumentException $e) {
        echo 'PASS Rejects invalid ' . key($change) . "\n";
    }
}
check(!ff_ready([]), 'Unconfigured form stays disabled');
check(!ff_ready(['enabled' => true, 'site_key' => 'p', 'secret_key' => 's', 'hostname' => 'fusionfarm.net', 'from_email' => 'attacker@example.com']), 'Rejects a sender outside fusionfarm.net');
check(ff_ready(['enabled' => true, 'site_key' => 'p', 'secret_key' => 's', 'hostname' => 'fusionfarm.net', 'from_email' => 'web@fusionfarm.net']), 'Complete config is ready');
echo "all contact tests passed\n";
