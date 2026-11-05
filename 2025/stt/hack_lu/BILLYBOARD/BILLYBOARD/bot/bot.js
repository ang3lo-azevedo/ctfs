const express = require('express');
const puppeteer = require('puppeteer');
const net = require('net');
const rateLimit = require('express-rate-limit');


const FLAG = process.env.FLAG || 'flag{**************************}';
const APP_DOMAIN = process.env.APP_DOMAIN || 'apache';
const PORT = process.env.PORT || 1337;


const app = express();
app.use(express.json());
app.set('trust proxy', 1);

const reportLimiter = rateLimit({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 2,
    message: { error: 'Too many requests, please try again later.' }
});


function sleep(ms) {
    return new Promise(res => setTimeout(res, ms));
}

async function visit(url, ip) {

    const browser = await puppeteer.launch({
        headless: true,
        pipe: true,
        args: [
            '--disable-extensions',
            '--disable-gpu',
            '--disable-software-rasterizer',
            '--js-flags=--noexpose_wasm,--jitless',
            '--no-sandbox',
            `--host-resolver-rules=MAP ${APP_DOMAIN} ${ip},EXCLUDE localhost`,

            // # The real server uses VALID letsencrypt certs !!!!
            // so this is only enabled in the local testing with the self-signed certs
            '--ignore-certificate-errors',
        ]
    });
    console.log('Browser launched');
    console.log('Visiting URL:', url, 'with IP:', ip);


    try {
        const page = await browser.newPage();

        page.on('console', msg => {
            console.log(msg.type(), msg.text());
        });

        // very secure
        const cookies = [{
            name: 'flag',
            value: FLAG,
            url: `https://${APP_DOMAIN}`,
            secure: true,
            httpOnly: true,
            sameSite: 'Strict'
        }];

        await page.setCookie(...cookies);

        await page.goto(url, { waitUntil: [] });


        await sleep(10_000);
        // whew... enough of that.
    } catch (err) {
        console.error('Error visiting page:', err);
    } finally {
        await browser.close();
    }
}

app.post('/report', reportLimiter, async (req, res) => {
    const { url, ip } = req.body;

    const PREFIX = 'https://'
    if (!url || typeof url !== 'string' || !url.startsWith(PREFIX)) {
        return res.status(400).json({ error: `Invalid URL. Url should be a string and start with ${PREFIX}.` });
    }

    if (!ip || typeof ip !== 'string' || !net.isIP(ip)) {
        return res.status(400).json({ error: 'Invalid IP address.' });
    }

    try {
        await visit(url, ip);
        res.json({ success: true });
    } catch (err) {
        console.error('Error on /report', err);
        res.status(500).json({ error: 'Failed to visit URL.' });
    }
});

app.get('/', (req, res) => {
    res.sendFile('bot.html', { 'root':__dirname });
})

app.get('/ip', (request, response) => {
    response.send(`${request.ip}, ${request.headers['x-forwarded-for']}`)
});

app.listen(PORT, () => {
    console.log(`Bot is running on port http://127.0.0.1:${PORT}`);
})