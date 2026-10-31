// Fusion Farm — progressive enhancement only. Site reads fine without JS
// except the email addresses, which are assembled here to keep them out of
// plain-text HTML (scraper resistance).
(function () {
  "use strict";

  var host = ["fusionfarm", "net"].join(".");
  var addr = function (box) { return box + "@" + host; };

  // Contact desks
  document.querySelectorAll("[data-mail]").forEach(function (el) {
    var box = el.getAttribute("data-mail");
    el.setAttribute("href", "mailto:" + addr(box));
  });
  document.querySelectorAll("[data-addr]").forEach(function (el) {
    el.textContent = addr(el.getAttribute("data-addr"));
  });

  // Domain inquiry links go straight to a prefilled email
  document.querySelectorAll("[data-topic][data-subject]").forEach(function (el) {
    var subj = encodeURIComponent(el.getAttribute("data-subject"));
    el.setAttribute("href", "mailto:" + addr(el.getAttribute("data-topic")) + "?subject=" + subj);
  });

  // Mobile nav
  var toggle = document.querySelector(".nav__toggle");
  var links = document.getElementById("nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    links.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        links.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  var yr = document.getElementById("yr");
  if (yr) yr.textContent = new Date().getFullYear();
})();
