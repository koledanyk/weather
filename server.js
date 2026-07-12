// Minimal Node server for the lovepup+ weather demo.
// - Serves index.html (injecting the Google Maps key from env at startup).
// - /api/history and /api/log persist the reading log in Cloudflare D1.
// D1 is reached over its HTTP API using server-only env vars, so no secret
// ever reaches the browser. If D1 env is missing, the API degrades gracefully
// and the page falls back to its localStorage history.
//
// Env: PORT (default 80), GOOGLE_MAPS_API_KEY,
//      CF_ACCOUNT_ID, D1_DATABASE_ID, CF_API_TOKEN.

const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 80;
const MAPS_KEY = process.env.GOOGLE_MAPS_API_KEY || "";
const ACCOUNT = process.env.CF_ACCOUNT_ID;
const DB = process.env.D1_DATABASE_ID;
const TOKEN = process.env.CF_API_TOKEN;
const D1_READY = Boolean(ACCOUNT && DB && TOKEN);

// Load the page once and inject the Maps key (replaces the old inject-key.sh).
let html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
if (MAPS_KEY) {
  html = html.replace('const GOOGLE_MAPS_API_KEY = "";',
    `const GOOGLE_MAPS_API_KEY = ${JSON.stringify(MAPS_KEY)};`);
}

async function d1(sql, params = []) {
  const r = await fetch(
    `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT}/d1/database/${DB}/query`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${TOKEN}`, "Content-Type": "application/json" },
      body: JSON.stringify({ sql, params }),
    }
  );
  const j = await r.json();
  if (!j.success) throw new Error(JSON.stringify(j.errors || j));
  return j.result[0].results;
}

function readBody(req) {
  return new Promise((resolve) => {
    let b = "";
    req.on("data", (c) => (b += c));
    req.on("end", () => resolve(b));
  });
}

function json(res, code, obj) {
  res.writeHead(code, { "Content-Type": "application/json" });
  res.end(JSON.stringify(obj));
}

const server = http.createServer(async (req, res) => {
  try {
    const url = (req.url || "/").split("?")[0];

    if (req.method === "GET" && (url === "/" || url === "/index.html")) {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      return res.end(html);
    }

    if (url === "/api/health") {
      return json(res, 200, { ok: true, d1: D1_READY });
    }

    if (url === "/api/history" && req.method === "GET") {
      if (!D1_READY) return json(res, 200, []);
      const rows = await d1(
        "SELECT ts, text, place FROM readings ORDER BY ts ASC LIMIT 1000"
      );
      return json(res, 200, rows);
    }

    if (url === "/api/log" && req.method === "POST") {
      if (!D1_READY) return json(res, 503, { error: "D1 not configured" });
      const body = JSON.parse((await readBody(req)) || "{}");
      if (!body.t || !body.text) return json(res, 400, { error: "t and text required" });
      await d1("INSERT INTO readings (ts, text, place) VALUES (?, ?, ?)", [
        String(body.t),
        String(body.text),
        String(body.place || ""),
      ]);
      return json(res, 200, { ok: true });
    }

    res.writeHead(404);
    res.end("Not found");
  } catch (e) {
    json(res, 500, { error: String((e && e.message) || e) });
  }
});

server.listen(PORT, () =>
  console.log(`weather server on :${PORT} (d1=${D1_READY})`)
);
