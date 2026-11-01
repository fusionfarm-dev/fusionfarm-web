<?php
declare(strict_types=1);
require dirname(__DIR__) . '/api/common.php';
function check(bool $condition, string $label): void {
    if (!$condition) throw new RuntimeException($label);
    echo "PASS $label\n";
}
$valid = ['name' => 'A visitor', 'company' => 'Example', 'email' => 'visitor@example.com', 'message' => 'A decision about a new market.'];
foreach (['Project' => 'pete', 'Research' => 'research', 'Digital assets' => 'domains', 'Support' => 'support'] as $topic => $inbox) {
    $result = ff_message($valid + ['topic' => $topic]);
    check($result['to'] === "$inbox@fusionfarm.net", "Routes $topic to $inbox");
    check($result['reply_to'] === $valid['email'], 'Reply-To is the validated visitor email');
}
foreach ([['topic' => 'arbitrary@example.com'], ['email' => "a@example.com\r\nBcc: bad@example.com"], ['name' => ['array']], ['company' => "x\r\nBcc: injected"], ['message' => 'short'], ['message' => str_repeat('x',10001)]] as $change) {
    try { ff_message(array_replace($valid + ['topic' => 'Project'], $change)); throw new RuntimeException('Invalid submission accepted'); }
    catch (InvalidArgumentException $e) { echo 'PASS Rejects invalid ' . key($change) . "\n"; }
}
check(!ff_ready([]), 'Unconfigured form stays disabled');
check(!ff_ready(['enabled'=>true,'site_key'=>'public','secret_key'=>'secret','hostname'=>'fusionfarm.net','from_email'=>'attacker@example.com']), 'Rejects unauthorized sender domain');
