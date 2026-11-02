// Fusion Farm — progressive enhancement. Pages read fine without JS, except
// email addresses and the phone number, which are assembled here so they never
// appear as plain text in the HTML (scraper resistance).
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.remove("no-js");
  doc.classList.add("js");

  var host = ["fusionfarm", "net"].join(".");
  var addr = function (box) { return box + "@" + host; };
  var BOX = { project: "research", research: "research", domains: "domains", support: "support" };

  // ---- emails ----
  document.querySelectorAll("[data-mail]").forEach(function (el) {
    el.setAttribute("href", "mailto:" + addr(el.getAttribute("data-mail")));
  });
  document.querySelectorAll("[data-addr]").forEach(function (el) {
    el.textContent = addr(el.getAttribute("data-addr"));
  });

  // ---- phone ----
  var tel = ["312", "219", "3001"];
  document.querySelectorAll("[data-tel]").forEach(function (el) {
    el.setAttribute("href", "tel:+1" + tel.join(""));
    el.textContent = "+1 " + tel.join("-");
  });

  // ---- year ----
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  // ---- back links: return to the previous page on this site, else go home ----
  document.querySelectorAll("[data-back]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      var ref = document.referrer;
      if (ref && ref.indexOf(location.origin) === 0 && history.length > 1) { e.preventDefault(); history.back(); }
    });
  });

  // ---- fusion orbit: data points travel their orbits; hold still for reduced motion ----
  var orbitSvg = document.querySelector(".orbit");
  if (orbitSvg && window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches && orbitSvg.pauseAnimations) {
    orbitSvg.pauseAnimations();
  }

  // ---- mobile nav ----
  var toggle = document.querySelector(".nav__toggle");
  var links = document.getElementById("nav-links");
  if (toggle && links) {
    var close = function () { links.classList.remove("open"); toggle.setAttribute("aria-expanded", "false"); };
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    links.addEventListener("click", function (e) { if (e.target.closest("a")) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
  }

  // ---- contact form ----
  // Asks /api/config.php whether the server-side mailer is configured. If it is,
  // renders Cloudflare Turnstile and posts to /api/contact.php. If not (or PHP is
  // unavailable), Send opens a pre-addressed email to the right desk instead.
  var form = document.getElementById("contact-form");
  if (!form) return;
  var status = form.querySelector(".form__status");
  var btn = form.querySelector("button[type=submit]");
  var topic = form.elements.topic;
  var msg = form.elements.message;
  var tsBox = document.getElementById("ts");
  var live = false;     // server mailer enabled
  var tsWidget = null;

  // prefill from links such as /contact/?topic=domains&about=sparekraft.com
  var q = new URLSearchParams(location.search);
  if (q.get("topic") && BOX[q.get("topic")]) topic.value = q.get("topic");
  if (q.get("about") && !msg.value) {
    var about = q.get("about").replace(/[^a-z0-9.\-]/gi, "").slice(0, 80);
    if (about) msg.value = "I'm interested in " + about + ". ";
  }

  var say = function (text, kind) {
    status.textContent = text;
    status.className = "form__status" + (kind ? " form__status--" + kind : "");
  };

  var cfgUrl = form.getAttribute("data-config");
  if (cfgUrl && window.fetch) {
    fetch(cfgUrl, { headers: { Accept: "application/json" }, cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (cfg) {
        if (!cfg || !cfg.enabled || !cfg.siteKey) return;
        window.ffTurnstileReady = function () {
          tsBox.hidden = false;
          tsWidget = window.turnstile.render(tsBox, { sitekey: cfg.siteKey, action: "contact", theme: "dark" });
          live = true;
        };
        var s = document.createElement("script");
        s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=ffTurnstileReady";
        s.async = true;
        document.head.appendChild(s);
      })
      .catch(function () { /* stay on the email fallback */ });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (form.elements.website.value) return; // honeypot tripped: drop silently

    var bad = null;
    ["name", "email", "message"].forEach(function (n) {
      var f = form.elements[n];
      var v = f.value.trim();
      var ok = v !== "" && (n !== "email" || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) && (n !== "message" || v.length >= 10);
      f.setAttribute("aria-invalid", ok ? "false" : "true");
      if (!ok && !bad) bad = f;
    });
    if (bad) { say("Please add your name, a valid email and a message of at least a sentence.", "err"); bad.focus(); return; }

    var data = {
      name: form.elements.name.value.trim(),
      company: form.elements.company.value.trim(),
      email: form.elements.email.value.trim(),
      topic: topic.value,
      message: msg.value.trim()
    };
    var label = topic.options[topic.selectedIndex].text;
    var desk = addr(BOX[data.topic] || "research");

    if (!live) {
      var subject = "Website inquiry: " + label + (data.company ? " (" + data.company + ")" : "");
      var body = data.message + "\n\n— " + data.name + (data.company ? ", " + data.company : "") + "\n" + data.email;
      location.href = "mailto:" + desk + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
      say("Your email app should open with the message ready to send.", "ok");
      return;
    }

    var fd = new FormData(form);
    if (!fd.get("cf-turnstile-response")) { say("Please complete the security check.", "err"); return; }
    btn.disabled = true;
    say("Sending…");
    fetch(form.getAttribute("action"), { method: "POST", body: fd, headers: { Accept: "application/json" } })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok && j.ok === true, j: j }; }); })
      .then(function (res) {
        if (!res.ok) throw new Error((res.j && res.j.message) || "");
        form.reset();
        say("Thanks. Your message is with our " + label.toLowerCase() + " desk.", "ok");
      })
      .catch(function (err) {
        say((err && err.message) ? err.message + " (" + desk + ")" : "That didn't send. Please email " + desk + " directly.", "err");
      })
      .then(function () {
        btn.disabled = false;
        if (window.turnstile && tsWidget !== null) window.turnstile.reset(tsWidget);
      });
  });
})();
