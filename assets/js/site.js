'use strict';
document.documentElement.classList.add('js');
const host = ['fusionfarm', 'net'].join('.');
const inboxes = ['pete', 'research', 'domains', 'support'];
for (const user of inboxes) {
  const address = `${user}@${host}`;
  document.querySelectorAll(`[data-mail="${user}"]`).forEach(a => { a.href = `mailto:${address}`; });
  document.querySelectorAll(`[data-address="${user}"]`).forEach(el => { el.textContent = address; });
}
for (const a of document.querySelectorAll('[data-phone]')) {
  a.href = `tel:+${[1, 312, 219, 3001].join('')}`;
  a.textContent = `+1 ${[312, 219, 3001].join('-')}`;
}
const toggle = document.querySelector('.menu-toggle');
const nav = document.getElementById('nav-links');
function closeMenu() { toggle.setAttribute('aria-expanded', 'false'); nav.removeAttribute('data-open'); }
toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  nav.toggleAttribute('data-open', open);
});
nav.addEventListener('click', e => { if (e.target.closest('a')) closeMenu(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { closeMenu(); toggle.focus(); } });
const form = document.getElementById('contact-form');
if (form) {
  const status = document.getElementById('form-status');
  const button = document.getElementById('send-button');
  const topics = ['Project', 'Research', 'Digital assets', 'Support'];
  const params = new URLSearchParams(location.search);
  if (topics.includes(params.get('topic'))) form.elements.topic.value = params.get('topic');
  const domain = params.get('domain');
  if (['bonghit.cloud', 'rotablesales.com', 'sparekraft.com', 'damnyum.com'].includes(domain)) form.elements.message.value = `I’m interested in ${domain}.\n\n`;
  let widget;
  let configured = false;
  function unavailable() { configured = false; button.disabled = true; status.textContent = 'The form is temporarily unavailable. Please use one of the email addresses or call us.'; }
  async function setup() {
    try {
      const res = await fetch('/api/config.php', { headers: { Accept: 'application/json' } });
      if (!res.ok) throw new Error('unavailable');
      const config = await res.json();
      if (!config.enabled || !config.siteKey) throw new Error('unavailable');
      const script = document.createElement('script');
      script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
      script.async = true;
      script.onerror = unavailable;
      script.onload = () => {
        configured = true;
        widget = window.turnstile.render('#turnstile-widget', {
          sitekey: config.siteKey, action: 'contact', theme: 'dark',
          callback: () => { button.disabled = false; status.textContent = 'Ready to send.'; },
          'expired-callback': () => { button.disabled = true; status.textContent = 'Please complete the security check again.'; },
          'error-callback': () => { button.disabled = true; status.textContent = 'Security check unavailable. Please try again or email us directly.'; }
        });
      };
      document.head.append(script);
      status.textContent = 'Please complete the security check.';
    } catch { unavailable(); }
  }
  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (!configured || button.disabled || !form.reportValidity()) return;
    button.disabled = true;
    status.removeAttribute('data-error');
    status.textContent = 'Sending your message…';
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 25000);
    try {
      const res = await fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' }, signal: controller.signal });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data.message || 'Message could not be sent. Please try again or email us directly.');
      form.reset();
      status.textContent = data.message;
    } catch (err) {
      status.setAttribute('data-error', '');
      status.textContent = err.name === 'AbortError' ? 'Delivery has not been confirmed. Please email us directly if needed.' : err.message;
    } finally { clearTimeout(timer); if (window.turnstile && widget !== undefined) window.turnstile.reset(widget); }
  });
  setup();
}
