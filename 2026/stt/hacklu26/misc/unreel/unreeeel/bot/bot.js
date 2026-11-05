'use strict';

const express = require('express');
const puppeteer = require('puppeteer-core');
const { once } = require('node:events');
const { setTimeout: delay } = require('node:timers/promises');

const APP_URL = process.env.INSTANCE_HOST
  ? `https://${process.env.INSTANCE_HOST}`
  : 'http://unreel.internal';
const ADMIN_NAME = process.env.ADMIN_NAME || 'admin';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;
const PORT = Number(process.env.PORT || 8080);
const VISIT_MS = Number(process.env.VISIT_MS || 10000);
const CHROMIUM = process.env.CHROMIUM_PATH || '/usr/bin/chromium';
const ORIGIN = new URL(APP_URL).origin;
const MAX_PENDING_VISITS = 32;

async function visit(browser, url) {
  const context = await browser.createBrowserContext();
  try {
    const page = await context.newPage();
    page.setDefaultNavigationTimeout(VISIT_MS);

    await page.goto(APP_URL, { waitUntil: 'domcontentloaded' });
    const status = await page.evaluate(async (name, password, timeout) => {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ name, password }),
        signal: AbortSignal.timeout(timeout),
      });
      return response.status;
    }, ADMIN_NAME, ADMIN_PASSWORD, VISIT_MS);
    if (status < 200 || status >= 300) throw new Error(`admin login returned ${status}`);

    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await delay(VISIT_MS);
  } finally {
    await context.close();
  }
}

function parseVisitUrl(value) {
  if (typeof value !== 'string') return null;
  try {
    const url = new URL(value);
    return url.protocol === 'http:' || url.protocol === 'https:' ? url.href : null;
  } catch {
    return null;
  }
}

const PAGE = `<!doctype html>
<meta charset="utf-8">
<title>Admin bot</title>
<h1>Admin bot</h1>
<p>Paste a URL and the admin will visit it while logged in to ${ORIGIN}.</p>
<form method="POST" action="visit">
  <input name="url" size="60" placeholder="https://..." required>
  <button type="submit">Send</button>
</form>`;

function createApp(visitUrl) {
  const app = express();
  app.use(express.urlencoded({ extended: false, limit: '4kb' }));

  app.get('/', (req, res) => {
    res.type('html').send(PAGE);
  });

  let queue = Promise.resolve();
  let pending = 0;
  app.post('/visit', (req, res) => {
    const url = parseVisitUrl(req.body?.url);
    if (url === null) {
      res.status(400).type('text').send('url must be http or https\n');
      return;
    }
    if (pending >= MAX_PENDING_VISITS) {
      res.status(503).type('text').send('the visit queue is full, try again later\n');
      return;
    }
    pending++;
    queue = queue
      .then(() => visitUrl(url))
      .catch((err) => console.error('visit failed:', err.message))
      .finally(() => { pending--; });
    res.type('text').send('the admin will visit your url shortly\n');
  });

  return app;
}

async function main() {
  if (!ADMIN_PASSWORD) throw new Error('ADMIN_PASSWORD must be set');
  if (!Number.isInteger(PORT) || PORT < 0 || PORT > 65535) throw new Error('PORT must be between 0 and 65535');
  if (!Number.isInteger(VISIT_MS) || VISIT_MS < 1 || VISIT_MS > 2147483647) {
    throw new Error('VISIT_MS must be between 1 and 2147483647');
  }
  const browser = await puppeteer.launch({
    executablePath: CHROMIUM,
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });
  let stopping = false;
  const app = createApp((url) => stopping ? undefined : visit(browser, url));
  let server;
  try {
    server = app.listen(PORT);
    await once(server, 'listening');
  } catch (err) {
    await browser.close();
    throw err;
  }
  console.log(`admin bot on :${PORT}, app ${APP_URL}`);

  const shutdown = () => {
    if (stopping) return;
    stopping = true;
    server.close();
    browser.close().catch(fail);
  };
  process.once('SIGINT', shutdown);
  process.once('SIGTERM', shutdown);
  browser.once('disconnected', () => {
    if (stopping) return;
    fail(new Error('browser disconnected'));
    shutdown();
  });
}

function fail(err) {
  console.error('admin bot failed:', err.message);
  process.exitCode = 1;
}

if (require.main === module) main().catch(fail);

module.exports = { createApp, visit };
