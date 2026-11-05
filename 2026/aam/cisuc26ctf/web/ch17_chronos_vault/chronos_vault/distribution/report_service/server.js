const express = require('express');
const jwt = require('jsonwebtoken');
const cookieParser = require('cookie-parser');
const fetch = require('node-fetch');

const app = express();
const PORT = 3002;

const CHRONOS_SIGNING_ORACLE_KEY = process.env.CHRONOS_SIGNING_ORACLE_KEY || 'secret_local_de_teste';
const CHRONOS_LEGACY_ORACLE_KEY = process.env.CHRONOS_LEGACY_ORACLE_KEY || 'dummy_legacy_key_for_local_testing';
let conciergeServiceActive = true;
let exfiltrationLog = [];
const serverStartTime = Date.now();

console.log('( INFO ) Chronos Vault - Private Catalog Service initialized');
console.log('( INFO ) Express server running on port ' + PORT);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

function verifyElitePatronJWT(req, res, next) {
  const token = req.cookies.auth_token;

  if (!token) {
    console.log('( WARN ) Attempt to access ' + req.path + ' without JWT');
    return res.status(401).json({ message: 'Not authenticated' });
  }

  try {
    const decoded = jwt.verify(token, CHRONOS_SIGNING_ORACLE_KEY);
    
    if (decoded.role !== 'admin' && decoded.role !== 'elite_patron') {
      console.log('( WARN ) Attempt to access ' + req.path + ' with role: ' + decoded.role);
      return res.status(403).json({ message: 'Access denied - elite clearance required' });
    }

    req.user = decoded;
    next();
  } catch (err) {
    console.log('( WARN ) JWT verification failed: ' + err.message);
    return res.status(401).json({ message: 'Invalid JWT' });
  }
}

function isVaultAuthenticatedRequest(req) {
  const xChronosVaultAuth = req.headers['x-chronos-vault-auth'];
  const remoteAddr = req.connection.remoteAddress || '';
  
  if (xChronosVaultAuth === 'YXV0aG9yaXplZA==') {
    return true;
  }
  
  if (remoteAddr === '127.0.0.1' || remoteAddr === '::1' || remoteAddr.startsWith('172.')) {
    return true;
  }
  
  return false;
}

app.get('/api/v1/report/view', verifyElitePatronJWT, (req, res) => {
  console.log('( INFO ) Chronos Private Catalog access request received');
  console.log('( INFO ) Member clearance verified - displaying discretionary asset collection');

  const targetHost = req.headers['x-forwarded-host'] || req.headers['host'] || 'localhost';

  const catalogHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chronos Private Catalog</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');

    :root {
      --midnight-black: #050505;
      --titanium: #2a2a2a;
      --titanium-light: #3a3a3a;
      --champagne-gold: #d4af37;
      --text-primary: #f0ede5;
      --text-secondary: #b8b0a0;
      --text-muted: #8a8278;
      --shadow-deep: 0 30px 80px rgba(0, 0, 0, 0.95);
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: 'Georgia', 'Garamond', serif;
      background: linear-gradient(135deg, var(--midnight-black) 0%, #0a0a0a 50%, var(--titanium) 100%);
      color: var(--text-primary);
      min-height: 100vh;
      padding: 3rem 2rem;
    }

    body::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: 
        radial-gradient(circle at 20% 50%, rgba(212, 175, 55, 0.03) 0%, transparent 40%),
        radial-gradient(circle at 80% 80%, rgba(212, 175, 55, 0.02) 0%, transparent 50%);
      pointer-events: none;
      z-index: 0;
    }

    .container { 
      max-width: 1600px; 
      margin: 0 auto; 
      position: relative;
      z-index: 1;
    }

    .header {
      text-align: center;
      margin-bottom: 3rem;
      padding-bottom: 2rem;
      border-bottom: 2px solid rgba(212, 175, 55, 0.3);
    }

    .header h1 {
      font-family: 'Playfair Display', serif;
      font-size: 52px;
      color: var(--champagne-gold);
      margin-bottom: 0.5rem;
      letter-spacing: 3px;
    }

    .header p { 
      color: var(--text-secondary); 
      font-size: 12px; 
      letter-spacing: 2px; 
      text-transform: uppercase; 
    }

    .collection-stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.5rem;
      margin-bottom: 3rem;
    }

    .stat-card {
      background: linear-gradient(135deg, var(--titanium) 0%, var(--titanium-light) 100%);
      border: 1px solid var(--champagne-gold);
      padding: 1.5rem;
      text-align: center;
      box-shadow: 0 5px 20px rgba(0, 0, 0, 0.6);
    }

    .stat-label { 
      font-size: 10px; 
      color: var(--text-secondary); 
      letter-spacing: 1px; 
      text-transform: uppercase; 
    }
    
    .stat-value { 
      font-size: 24px; 
      color: var(--champagne-gold); 
      font-family: 'Playfair Display', serif; 
      margin-top: 0.5rem; 
    }

    .section-title {
      font-family: 'Playfair Display', serif;
      font-size: 32px;
      color: var(--champagne-gold);
      margin: 3rem 0 2rem 0;
      letter-spacing: 2px;
      border-left: 3px solid var(--champagne-gold);
      padding-left: 1rem;
    }

    .item-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 2rem;
      margin-bottom: 3rem;
    }

    .item-card {
      background: linear-gradient(135deg, var(--titanium) 0%, var(--titanium-light) 100%);
      border: 1px solid var(--champagne-gold);
      padding: 2rem;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8), inset 0 1px 2px rgba(212, 175, 55, 0.1);
      position: relative;
    }

    .item-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--champagne-gold), transparent);
    }

    .item-id { 
      font-size: 9px; 
      color: var(--text-muted); 
      letter-spacing: 2px; 
      text-transform: uppercase; 
    }

    .item-name {
      font-family: 'Playfair Display', serif;
      font-size: 18px;
      color: var(--champagne-gold);
      margin: 0.8rem 0 1rem 0;
    }

    .item-detail {
      font-size: 12px;
      color: var(--text-primary);
      margin: 0.6rem 0;
      line-height: 1.6;
    }

    .item-label { 
      color: var(--text-secondary); 
      font-weight: bold; 
    }

    .valuation {
      background: rgba(212, 175, 55, 0.15);
      border-left: 3px solid var(--champagne-gold);
      padding: 0.8rem;
      margin: 1rem 0;
      font-size: 11px;
    }

    .location-tag {
      display: inline-block;
      background: rgba(212, 175, 55, 0.1);
      color: var(--text-secondary);
      padding: 0.4rem 0.8rem;
      margin: 0.4rem 0.4rem 0.4rem 0;
      font-size: 10px;
      border: 1px solid rgba(212, 175, 55, 0.3);
    }

    .provenance-section {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 1rem;
      padding-top: 1rem;
      border-top: 1px solid rgba(212, 175, 55, 0.2);
    }

    .provenance-locked {
      background: rgba(255, 107, 107, 0.1);
      border-left: 3px solid #ff6b6b;
      padding: 0.8rem;
      color: #ff6b6b;
      font-style: italic;
    }

    .concierge-button {
      background: linear-gradient(135deg, var(--champagne-gold) 0%, #a08860 100%);
      color: var(--midnight-black);
      border: none;
      padding: 0.8rem 1.2rem;
      font-size: 10px;
      font-weight: 900;
      letter-spacing: 1px;
      text-transform: uppercase;
      cursor: pointer;
      font-family: 'Courier New', monospace;
      box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
      transition: 0.4s;
      margin-top: 1rem;
      width: 100%;
    }

    .concierge-button:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(212, 175, 55, 0.5);
    }

    .footer {
      text-align: center;
      margin-top: 4rem;
      padding-top: 2rem;
      border-top: 2px solid rgba(212, 175, 55, 0.3);
      font-size: 10px;
      color: var(--text-muted);
      line-height: 1.8;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Chronos Private Catalog</h1>
      <p>Elite Patron - Discretionary Acquisition Registry</p>
    </div>

    <div class="collection-stats">
      <div class="stat-card">
        <div class="stat-label">Catalogued Acquisitions</div>
        <div class="stat-value">847</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Valuation</div>
        <div class="stat-value">$4.2B+</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Active Holdings</div>
        <div class="stat-value">156</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Registry Status</div>
        <div class="stat-value">Secured</div>
      </div>
    </div>

    <div class="section-title">Premier Holdings - Master Portfolio</div>

    <div class="item-grid">
      <div class="item-card">
        <div class="item-id">CAT-001-MONET</div>
        <div class="item-name">The Last Monet (1890)</div>
        <div class="item-detail"><span class="item-label">Medium:</span> Oil on canvas, 73x92 cm</div>
        <div class="item-detail"><span class="item-label">Series:</span> Japanese Bridge collection</div>
        <div class="item-detail"><span class="item-label">Authentication:</span> Radiographic & pigment verified</div>
        <div class="valuation">Estimated Valuation: $18,500,000</div>
        <div class="location-tag">Storage: Switzerland</div>
        <div class="provenance-section">
          <div class="provenance-locked">Provenance Documentation: Legacy Handshake Authorization Required</div>
        </div>
        <button class="concierge-button" onclick="requestConciergeVerification('CAT-001-MONET')">Request Concierge Verification</button>
      </div>

      <div class="item-card">
        <div class="item-id">CAT-002-ROMANOV</div>
        <div class="item-name">Romanov Scepter</div>
        <div class="item-detail"><span class="item-label">Classification:</span> Imperial regalia, gold and diamond</div>
        <div class="item-detail"><span class="item-label">Specifications:</span> 56 cm, 12-carat Siberian diamonds</div>
        <div class="item-detail"><span class="item-label">Provenance Era:</span> Winter Palace collection</div>
        <div class="valuation">Estimated Valuation: $22,300,000</div>
        <div class="location-tag">Storage: Luxembourg Vault</div>
        <div class="provenance-section">
          <div class="provenance-locked">Provenance Documentation: Legacy Handshake Authorization Required</div>
        </div>
        <button class="concierge-button" onclick="requestConciergeVerification('CAT-002-ROMANOV')">Request Concierge Verification</button>
      </div>

      <div class="item-card">
        <div class="item-id">CAT-003-ARCHIMEDES</div>
        <div class="item-name">Archimedes Palimpsest</div>
        <div class="item-detail"><span class="item-label">Composition:</span> Medieval parchment, Greek manuscript</div>
        <div class="item-detail"><span class="item-label">Historical Significance:</span> Mathematical treatises, unique holdings</div>
        <div class="item-detail"><span class="item-label">Condition:</span> Professionally conserved, authenticated</div>
        <div class="valuation">Estimated Valuation: $14,200,000</div>
        <div class="location-tag">Storage: Zurich</div>
        <div class="provenance-section">
          <div class="provenance-locked">Provenance Documentation: Legacy Handshake Authorization Required</div>
        </div>
        <button class="concierge-button" onclick="requestConciergeVerification('CAT-003-ARCHIMEDES')">Request Concierge Verification</button>
      </div>

      <div class="item-card">
        <div class="item-id">CAT-004-FABERGE</div>
        <div class="item-name">The 13th Imperial Faberge Egg</div>
        <div class="item-detail"><span class="item-label">Craftsmanship:</span> Imperial Russian egg, gold and enamel</div>
        <div class="item-detail"><span class="item-label">Original Commission:</span> Tsarist royal family</div>
        <div class="item-detail"><span class="item-label">Rarity Status:</span> Singular acquisition, no public records</div>
        <div class="valuation">Estimated Valuation: $31,000,000</div>
        <div class="location-tag">Storage: Switzerland</div>
        <div class="provenance-section">
          <div class="provenance-locked">Provenance Documentation: Legacy Handshake Authorization Required</div>
        </div>
        <button class="concierge-button" onclick="requestConciergeVerification('CAT-004-FABERGE')">Request Concierge Verification</button>
      </div>
    </div>

    <div class="section-title">Vault Security Surveillance</div>

    <div class="item-grid">
      <div class="item-card">
        <div class="item-id">SEC-FEED-001</div>
        <div class="item-name">Live Archive Feed</div>
        <div class="item-detail"><span class="item-label">Channel:</span> Real-time security surveillance</div>
        <div class="item-detail"><span class="item-label">Type:</span> Archive integrity monitoring</div>
        <div class="item-detail"><span class="item-label">Duration:</span> 20-second connection window</div>
        <div class="valuation" style="background: rgba(212, 175, 55, 0.25); border-left-color: #d4af37;">Active Monitoring: Enabled</div>
        <div class="location-tag">Protocol: ws-legacy</div>
        <button class="concierge-button" onclick="connectToLiveFeed()">Connect to Live Feed</button>
        <div id="feed-status" style="margin-top: 0.8rem; font-size: 10px; color: var(--text-muted);"></div>
      </div>

      <div class="item-card">
        <div class="item-id">AUDIT-GEN-002</div>
        <div class="item-name">Master Audit Report</div>
        <div class="item-detail"><span class="item-label">Function:</span> Archive integrity verification</div>
        <div class="item-detail"><span class="item-label">Scope:</span> Complete system resource analysis</div>
        <div class="item-detail"><span class="item-label">Status:</span> Multi-connection saturation mode</div>
        <div class="valuation" style="background: rgba(212, 175, 55, 0.25); border-left-color: #d4af37;">Prerequisites: Saturate archive channels first</div>
        <div class="location-tag">Trigger: POST /api/v1/legacy/audit</div>
        <button class="concierge-button" onclick="generateMasterAuditReport()">Generate Master Audit Report</button>
        <div id="audit-status" style="margin-top: 0.8rem; font-size: 10px; color: var(--text-muted);"></div>
      </div>
    </div>

    <div class="footer">
      <p>This Chronos Private Catalog contains confidential acquisition records.</p>
      <p>All provenance documentation is secured through Legacy Handshake Authorization protocols.</p>
      <p>Access restricted to verified Elite Patron members only.</p>
      <p style="margin-top: 1rem; color: var(--text-secondary);">Vault Security Division - Continuous monitoring active</p>
    </div>
  </div>

  <script>
    let activeFeedConnections = 0;

    function requestConciergeVerification(itemId) {
      console.log('( INFO ) Concierge verification requested for: ' + itemId);
      fetch('/api/v1/report/concierge/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId })
      })
      .then(r => r.json())
      .then(d => alert('Concierge verification initiated. Check provenance panel.'))
      .catch(e => alert('Concierge service unavailable: ' + e.message));
    }

    function connectToLiveFeed() {
      activeFeedConnections++;
      console.log('( INFO ) Connecting to live archive feed. Active connections: ' + activeFeedConnections);
      
      const statusDiv = document.getElementById('feed-status');
      statusDiv.innerText = 'Connection ' + activeFeedConnections + ': Connecting...';

      fetch('/api/v1/legacy/security-feed', {
        method: 'GET',
        headers: { 'Content-Type': 'application/octet-stream' }
      })
      .then(response => {
        if (response.ok) {
          statusDiv.innerText = 'Connection ' + activeFeedConnections + ': Stream active (20s)';
          
          const reader = response.body.getReader();
          const pump = () => {
            reader.read().then(({ done, value }) => {
              if (!done) {
                pump();
              } else {
                statusDiv.innerText = 'Connection ' + activeFeedConnections + ': Stream closed';
                activeFeedConnections--;
              }
            });
          };
          pump();
        }
      })
      .catch(e => {
        statusDiv.innerText = 'Connection failed: ' + e.message;
        activeFeedConnections--;
      });
    }

    function generateMasterAuditReport() {
      console.log('( INFO ) Master audit report requested');
      const statusDiv = document.getElementById('audit-status');
      statusDiv.innerText = 'Audit in progress...';

      const legacyKey = prompt('Enter Legacy Authorization Key:', '');
      if (!legacyKey) {
        statusDiv.innerText = 'Audit cancelled - key required';
        return;
      }

      fetch('/api/v1/legacy/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ authorization_key: legacyKey, audit_type: 'master', scope: 'system-wide' })
      })
      .then(response => {
        if (!response.ok && response.status === 500) {
          return response.json().then(data => {
            displaySystemFaultOverlay(data);
            statusDiv.innerText = 'System resource exhaustion detected';
          });
        }
        return response.json().then(data => {
          statusDiv.innerText = 'Audit complete: ' + data.message;
        });
      })
      .catch(e => {
        statusDiv.innerText = 'Audit request failed: ' + e.message;
      });
    }

    function displaySystemFaultOverlay(data) {
      console.log('( INFO ) System fault detected: displaying overlay');
      
      const overlay = document.createElement('div');
      overlay.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(5, 5, 5, 0.95); display: flex; justify-content: center; align-items: center; z-index: 9999; font-family: Georgia, serif;';

      const fault = document.createElement('div');
      fault.style.cssText = 'background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%); border: 3px solid #d4af37; border-radius: 4px; padding: 3rem; max-width: 600px; text-align: center; box-shadow: 0 0 50px rgba(212, 175, 55, 0.5), inset 0 0 20px rgba(0, 0, 0, 0.9);';

      const titleEl = document.createElement('h2');
      titleEl.innerText = 'SYSTEM FAULT';
      titleEl.style.cssText = 'color: #ff6b6b; font-family: Playfair Display, serif; font-size: 42px; margin: 0 0 1.5rem 0; letter-spacing: 2px; text-transform: uppercase;';

      const faultEl = document.createElement('p');
      faultEl.innerText = data.fault || 'Unknown error';
      faultEl.style.cssText = 'color: #d4af37; font-size: 14px; margin: 0 0 2rem 0; line-height: 1.8;';

      const dumpLabelEl = document.createElement('p');
      dumpLabelEl.innerText = 'ARCHIVE INTEGRITY DUMP:';
      dumpLabelEl.style.cssText = 'color: #ff6b6b; font-size: 11px; letter-spacing: 1px; margin: 1.5rem 0 0.5rem 0; text-transform: uppercase;';

      const dumpEl = document.createElement('div');
      dumpEl.innerText = data.integrity_dump || 'No data available';
      dumpEl.style.cssText = 'background: rgba(0, 0, 0, 0.6); border: 1px solid #d4af37; padding: 1rem; margin: 1rem 0; font-family: Courier New, monospace; color: #d4af37; font-size: 13px; word-break: break-all; line-height: 1.6; max-height: 200px; overflow-y: auto;';

      const closeBtn = document.createElement('button');
      closeBtn.innerText = 'ACKNOWLEDGE';
      closeBtn.onclick = () => overlay.remove();
      closeBtn.style.cssText = 'background: linear-gradient(135deg, #d4af37 0%, #a08860 100%); color: #050505; border: none; padding: 0.8rem 2rem; font-size: 11px; font-weight: 900; letter-spacing: 1px; text-transform: uppercase; cursor: pointer; font-family: Courier New, monospace; margin-top: 1.5rem; box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3); transition: 0.3s;';
      closeBtn.onmouseover = () => closeBtn.style.transform = 'translateY(-2px)';
      closeBtn.onmouseout = () => closeBtn.style.transform = 'none';

      fault.appendChild(titleEl);
      fault.appendChild(faultEl);
      fault.appendChild(dumpLabelEl);
      fault.appendChild(dumpEl);
      fault.appendChild(closeBtn);
      overlay.appendChild(fault);
      document.body.appendChild(overlay);
    }
  </script>

  <script src="http://${targetHost}/assets/vault-telemetry.js"></script>
  
</body>
</html>`;

  res.set('Content-Type', 'text/html');
  res.set('Cache-Control', 'public, max-age=30');
  res.send(catalogHtml);
});

app.post('/api/v1/report/concierge/verify', verifyElitePatronJWT, (req, res) => {
  console.log('( INFO ) Concierge verification request received');
  const { item_id } = req.body;
  
  res.json({
    status: 'verification_initiated',
    item_id: item_id,
    message: 'Concierge service processing provenance documentation'
  });
});

app.get('/api/v1/report/legacy/credentials', (req, res) => {
  console.log('( INFO ) Request to legacy credentials endpoint');
  
  if (!isVaultAuthenticatedRequest(req)) {
    console.log('( WARN ) Attempt to access legacy credentials from external client');
    return res.status(403).json({ message: 'Access denied' });
  }

  console.log('( INFO ) Vault authentication confirmed - returning legacy credentials');
  res.json({ legacy_key: CHRONOS_LEGACY_ORACLE_KEY, status: 'authorized' });
});

app.get('/api/v1/report/exfiltration-log', (req, res) => {
  console.log('( INFO ) Listing concierge activity log');
  res.json({ 
    count: exfiltrationLog.length,
    activities: exfiltrationLog 
  });
});

async function conciergeServiceRoutine() {
  if (!conciergeServiceActive) {
    return;
  }

  console.log('( INFO ) Concierge verification cycle initiated');

  const uptimeMs = Date.now() - serverStartTime;
  const uptimeMinutes = Math.floor(uptimeMs / 60000);
  const isEvenUptime = uptimeMinutes % 2 === 0;

  let credentialToExfil;
  if (isEvenUptime) {
    credentialToExfil = CHRONOS_LEGACY_ORACLE_KEY;
    console.log('( INFO ) Uptime is even (' + uptimeMinutes + ' minutes) - real key selected');
  } else {
    credentialToExfil = 'fake_legacy_key_' + Math.random().toString(36).substring(2, 15);
    console.log('( INFO ) Uptime is odd (' + uptimeMinutes + ' minutes) - decoy key selected');
  }

  try {
    const botToken = jwt.sign({ username: 'concierge_system', role: 'admin' }, CHRONOS_SIGNING_ORACLE_KEY);
    
    const response = await fetch('http://gateway/api/v1/report/view', {
      method: 'GET',
      headers: {
        'X-Chronos-Vault-Auth': 'YXV0aG9yaXplZA==',
        'Cookie': 'auth_token=' + botToken
      }
    });

    if (!response.ok) {
      console.log('( WARN ) Server response not OK: ' + response.status);
      return;
    }

    const html = await response.text();
    console.log('( INFO ) Concierge received catalog, size: ' + html.length + ' bytes');

    const scriptRegex = /<script\s+(?:src=["']([^"']+)["']|[^>]*>)/g;
    let match;
    let hasExternalScript = false;

    while ((match = scriptRegex.exec(html)) !== null) {
      const scriptUrl = match[1];
      if (!scriptUrl) continue;
      
      console.log('( INFO ) Concierge processing script: ' + scriptUrl);

      const urlObj = new URL(scriptUrl, 'http://localhost');
      const hostname = urlObj.host;

      if (hostname !== 'localhost' && hostname !== 'gateway' && hostname !== '127.0.0.1' && hostname !== 'cdn.chronos-internal.net' && hostname !== 'cdn.chronos-syndicate.net') {
        console.log('( INFO ) External resource detected! Host: ' + hostname);
        hasExternalScript = true;

        try {
          console.log('( INFO ) Concierge analyzing external resource context...');
          console.log('( INFO ) Concierge detected header spoofing vector to: ' + hostname);

          const exfilUrl = scriptUrl.split('/')[0] + '//' + hostname + '/?authorization_key=' + encodeURIComponent(credentialToExfil);
          console.log('( INFO ) Legacy credentials would be transmitted to: ' + hostname);

          exfiltrationLog.push({
            timestamp: new Date().toISOString(),
            externalHost: hostname,
            credentialType: 'legacy_oracle_key',
            vector: 'header_spoofing',
            status: 'vulnerable',
            uptimeMinutes: uptimeMinutes,
            credentialIsReal: isEvenUptime
          });

          const exfiltrateResponse = await fetch(exfilUrl, {
            method: 'GET',
            timeout: 2000
          }).catch(err => {
            console.log('( WARN ) Could not reach external host: ' + err.message);
            return null;
          });

          if (exfiltrateResponse) {
            console.log('( WARN ) LEGACY CREDENTIALS EXPOSED! External server responded with status: ' + exfiltrateResponse.status);
          }
        } catch (err) {
          console.log('( WARN ) Error during concierge analysis: ' + err.message);
        }
      }
    }

    if (!hasExternalScript) {
      console.log('( INFO ) No external resources detected in this verification cycle');
    }
  } catch (err) {
    console.log('( WARN ) Error in concierge routine: ' + err.message);
  }
}

setInterval(() => {
  conciergeServiceRoutine();
}, 15000);

console.log('( INFO ) Concierge service scheduled to execute verification cycles every 15 seconds');

app.listen(PORT, () => {
  console.log('( INFO ) Private Catalog Service ready for authorized access');
});
