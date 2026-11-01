<?php
// Copy outside the web root: /home/USER/fusionfarm-contact-config.php
// when the web root is /home/USER/fusionfarm.net. Never commit real secrets.
return [
    'enabled' => false,
    'hostname' => 'fusionfarm.net',
    'site_key' => '',
    'secret_key' => '',
    'from_email' => '', // An existing, authorized @fusionfarm.net sender mailbox.
];
