// Fusion Farm contact form endpoint — Cloudflare Worker.
//
// Receives the /contact form (multipart or urlencoded), drops honeypot hits,
// verifies Cloudflare Turnstile when a secret is set, and emails the message to
// the inbox that matches the chosen topic. Mail is sent through Resend's HTTP
// API, which only needs DNS records on fusionfarm.net (it does not touch MX, so
// the existing mailboxes keep working).
//
// Secrets / vars (see wrangler.toml and README):
//   RESEND_API_KEY     secret  required
//   TURNSTILE_SECRET   secret  optional; when set, a valid token is required
//   MAIL_FROM          var     e.g. "Fusion Farm website <web@fusionfarm.net>"
//   ALLOWED_ORIGIN     var     e.g. "https://fusionfarm.net"

const ROUTES = {
  project: "pete@fusionfarm.net",
  research: "research@fusionfarm.net",
  domains: "domains@fusionfarm.net",
  support: "support@fusionfarm.net",
};
const LABELS = { project: "Project", research: "Research", domains: "Digital assets", support: "Support" };
const LIMITS = { name: 120, company: 160, email: 200, message: 5000 };

export default {
  async fetch(request, env) {
    const origin = env.ALLOWED_ORIGIN || "https://fusionfarm.net";
    const cors = {
      "Access-Control-Allow-Origin": origin,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Accept",
      Vary: "Origin",
    };
    const reply = (status, body) =>
      new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (request.method !== "POST") return reply(405, { ok: false, error: "Method not allowed" });

    const reqOrigin = request.headers.get("Origin");
    if (reqOrigin && reqOrigin !== origin) return reply(403, { ok: false, error: "Forbidden" });

    let form;
    try {
      form = await request.formData();
    } catch {
      return reply(400, { ok: false, error: "Bad request" });
    }
    const get = (k) => String(form.get(k) || "").trim();

    // Honeypot: pretend success so bots learn nothing.
    if (get("website")) return reply(200, { ok: true });

    const data = {
      name: get("name").slice(0, LIMITS.name),
      company: get("company").slice(0, LIMITS.company),
      email: get("email").slice(0, LIMITS.email),
      topic: ROUTES[get("topic")] ? get("topic") : "project",
      message: get("message").slice(0, LIMITS.message),
    };
    if (!data.name || !data.message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      return reply(422, { ok: false, error: "Please include your name, a valid email and a message." });
    }

    if (env.TURNSTILE_SECRET) {
      const body = new FormData();
      body.append("secret", env.TURNSTILE_SECRET);
      body.append("response", get("cf-turnstile-response"));
      const ip = request.headers.get("CF-Connecting-IP");
      if (ip) body.append("remoteip", ip);
      const check = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body });
      const result = await check.json().catch(() => ({}));
      if (!result.success) return reply(403, { ok: false, error: "Spam check failed. Please try again." });
    }

    const subject = `Website inquiry: ${LABELS[data.topic]}${data.company ? ` (${data.company})` : ""}`;
    const text = [
      `Topic:   ${LABELS[data.topic]}`,
      `Name:    ${data.name}`,
      `Company: ${data.company || "-"}`,
      `Email:   ${data.email}`,
      "",
      "What decision are you trying to make?",
      data.message,
      "",
      "-- sent from fusionfarm.net/contact",
    ].join("\n");

    const send = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        from: env.MAIL_FROM || "Fusion Farm website <web@fusionfarm.net>",
        to: [ROUTES[data.topic]],
        reply_to: data.email,
        subject,
        text,
      }),
    });
    if (!send.ok) return reply(502, { ok: false, error: "Mail delivery failed" });
    return reply(200, { ok: true });
  },
};
