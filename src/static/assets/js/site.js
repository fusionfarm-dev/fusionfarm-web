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
  var BOX = { project: "pete", research: "research", domains: "domains", support: "support" };

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

  // ---- network arcs: stagger the draw-in ----
  document.querySelectorAll(".world .arc").forEach(function (p, i) {
    p.style.animationDelay = (0.25 + i * 0.09).toFixed(2) + "s";
  });

  // ---- contact form ----
  var form = document.getElementById("contact-form");
  if (!form) return;
  var status = form.querySelector(".form__status");
  var btn = form.querySelector("button[type=submit]");
  var topic = form.elements.topic;
  var msg = form.elements.message;

  // prefill from links such as /contact/?topic=domains&about=bonghit.cloud
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

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (form.elements.website.value) return; // honeypot tripped: drop silently

    var bad = null;
    ["name", "email", "message"].forEach(function (n) {
      var f = form.elements[n];
      var ok = f.value.trim() !== "" && (n !== "email" || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.value.trim()));
      f.setAttribute("aria-invalid", ok ? "false" : "true");
      if (!ok && !bad) bad = f;
    });
    if (bad) { say("Please fill in your name, a valid email and your message.", "err"); bad.focus(); return; }

    var data = {
      name: form.elements.name.value.trim(),
      company: form.elements.company.value.trim(),
      email: form.elements.email.value.trim(),
      topic: topic.value,
      message: msg.value.trim()
    };
    var label = topic.options[topic.selectedIndex].text;
    var endpoint = form.getAttribute("data-endpoint");

    if (!endpoint) {
      // No form backend configured yet: open a pre-addressed email to the right desk.
      var subject = "Website inquiry: " + label + (data.company ? " (" + data.company + ")" : "");
      var body = data.message + "\n\n— " + data.name + (data.company ? ", " + data.company : "") + "\n" + data.email;
      location.href = "mailto:" + addr(BOX[data.topic] || "pete") +
        "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
      say("Your email app should open with the message ready to send.", "ok");
      return;
    }

    var fd = new FormData(form);
    fd.set("_subject", "Website inquiry: " + label);
    btn.disabled = true;
    say("Sending…");
    fetch(endpoint, { method: "POST", body: fd, headers: { Accept: "application/json" } })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok && j.ok !== false, j: j }; }); })
      .then(function (res) {
        if (!res.ok) throw new Error((res.j && res.j.error) || "send failed");
        form.reset();
        say("Thanks. Your message is with our " + label.toLowerCase() + " desk.", "ok");
        if (window.turnstile) window.turnstile.reset();
      })
      .catch(function () {
        say("That didn't send. Please email " + addr(BOX[data.topic] || "pete") + " directly.", "err");
      })
      .then(function () { btn.disabled = false; });
  });
})();
