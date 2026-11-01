<?php
// Contact form configuration for DreamHost.
// Copy this file OUTSIDE the web root, next to the site folder:
//   /home/USER/fusionfarm-contact-config.php   (web root: /home/USER/fusionfarm.net)
// Fill it in, set 'enabled' => true. Never commit the real file.
return [
    'enabled'    => false,
    'hostname'   => 'fusionfarm.net',
    'site_key'   => '',  // Cloudflare Turnstile site key (public)
    'secret_key' => '',  // Cloudflare Turnstile secret key
    'from_email' => '',  // an existing @fusionfarm.net mailbox on DreamHost, e.g. web@fusionfarm.net
];
