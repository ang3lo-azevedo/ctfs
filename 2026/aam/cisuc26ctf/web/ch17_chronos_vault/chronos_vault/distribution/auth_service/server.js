const express = require('express');
const jwt = require('jsonwebtoken');
const cookieParser = require('cookie-parser');
const crypto = require('crypto');
const path = require('path');

const canaryToken = crypto.createHash('md5').update(Math.random().toString()).digest('hex');

const app = express();
const PORT = 3000;

const JWT_SECRET = process.env.CHRONOS_SIGNING_ORACLE_KEY || 'secret_local_de_teste';
let ADMIN_PASSWORD = crypto.randomBytes(16).toString('hex');

const ADMIN_USER = {
  username: 'admin',
  password: ADMIN_PASSWORD,
  role: 'admin'
};

console.log('( INFO ) Chronos Vault - Auth Service initialized');
console.log('( INFO ) Initialization credentials:');
console.log('  Username: ' + ADMIN_USER.username);
console.log('  Password: ' + ADMIN_PASSWORD);
console.log('( INFO ) JWT_SECRET generated (stored in memory)');

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

function verifyJWT(req, res, next) {
  const token = req.cookies.auth_token;

  if (!token) {
    return next();
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
  } catch (err) {
    console.log('( WARN ) JWT verification attempt failed: ' + err.message);
  }

  next();
}

app.use(verifyJWT);

app.get('/', (req, res) => {
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <meta name="description" content="Chronos Private Collections - Discrete Asset Procurement">
  <meta name="robots" content="noindex, nofollow">
  <title>Chronos Private Collections</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');

    :root {
      --midnight-black: #050505;
      --titanium: #2a2a2a;
      --titanium-light: #3a3a3a;
      --champagne-gold: #d4af37;
      --gold-muted: #a08860;
      --platinum: #e8e8e8;
      --text-primary: #f0ede5;
      --text-secondary: #b8b0a0;
      --text-muted: #8a8278;
      --gold-accent: rgba(212, 175, 55, 0.15);
      --shadow-premium: 0 30px 80px rgba(0, 0, 0, 0.95);
      --shadow-subtle: 0 10px 30px rgba(0, 0, 0, 0.8);
      --transition: 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      font-family: 'Georgia', 'Garamond', serif;
      background: linear-gradient(135deg, var(--midnight-black) 0%, #0a0a0a 50%, var(--titanium) 100%);
      background-attachment: fixed;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      color: var(--text-primary);
      overflow: hidden;
      position: relative;
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
        radial-gradient(circle at 80% 80%, rgba(212, 175, 55, 0.02) 0%, transparent 50%),
        repeating-linear-gradient(90deg, transparent 0px, rgba(212, 175, 55, 0.01) 1px, transparent 2px, transparent 4px);
      pointer-events: none;
      z-index: 0;
    }

    @keyframes shimmer {
      0%, 100% { opacity: 0.8; filter: brightness(1); }
      50% { opacity: 1; filter: brightness(1.05); }
    }

    .gold-shimmer {
      animation: shimmer 8s ease-in-out infinite;
    }

    .page-wrapper {
      z-index: 1;
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 2rem;
      gap: 2.5rem;
      position: relative;
    }

    .nda-notice {
      width: 100%;
      max-width: 900px;
      background: var(--titanium);
      border: 1px solid var(--champagne-gold);
      border-radius: 0;
      padding: 2.5rem 3rem;
      box-shadow: var(--shadow-subtle), inset 0 1px 2px rgba(212, 175, 55, 0.1);
      position: relative;
      overflow: hidden;
      backdrop-filter: blur(10px);
    }

    .nda-notice::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--champagne-gold), transparent);
      opacity: 0.6;
    }

    .nda-notice::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--champagne-gold), transparent);
      opacity: 0.6;
    }

    .nda-title {
      color: var(--champagne-gold);
      font-size: 10px;
      font-weight: 900;
      letter-spacing: 4px;
      text-transform: uppercase;
      margin-bottom: 1rem;
      font-family: 'Courier New', monospace;
    }

    .nda-text {
      color: var(--text-secondary);
      font-size: 12px;
      line-height: 1.8;
      letter-spacing: 0.3px;
    }

    .private-portal {
      width: 100%;
      max-width: 550px;
      background: linear-gradient(135deg, var(--titanium) 0%, var(--titanium-light) 100%);
      border: 2px solid var(--champagne-gold);
      border-radius: 0;
      padding: 3.5rem;
      box-shadow: var(--shadow-premium), inset 0 1px 3px rgba(212, 175, 55, 0.12);
      position: relative;
    }

    .private-portal::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, transparent, var(--champagne-gold), transparent);
      opacity: 0.8;
      animation: shimmer 6s ease-in-out infinite;
    }

    .private-portal::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, transparent, var(--champagne-gold), transparent);
      opacity: 0.6;
    }

    .portal-header {
      text-align: center;
      margin-bottom: 2.5rem;
      border-bottom: 1px solid rgba(212, 175, 55, 0.3);
      padding-bottom: 2rem;
    }

    .collections-title {
      font-family: 'Playfair Display', serif;
      font-size: 42px;
      font-weight: 900;
      color: var(--champagne-gold);
      letter-spacing: 2px;
      margin-bottom: 0.5rem;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.7);
    }

    .collections-subtitle {
      color: var(--text-secondary);
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      font-family: 'Courier New', monospace;
    }

    .form-section {
      display: flex;
      flex-direction: column;
      gap: 1.8rem;
      margin-bottom: 2rem;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }

    .form-label {
      font-size: 10px;
      font-weight: bold;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--champagne-gold);
      font-family: 'Courier New', monospace;
    }

    input {
      background: var(--midnight-black);
      border: 1px solid var(--champagne-gold);
      border-radius: 0;
      padding: 1rem 1.2rem;
      color: var(--text-primary);
      font-size: 13px;
      font-family: 'Georgia', serif;
      transition: var(--transition);
      letter-spacing: 0.5px;
    }

    input:focus {
      outline: none;
      box-shadow: inset 0 0 0 2px var(--champagne-gold), 0 0 20px rgba(212, 175, 55, 0.3);
      background: rgba(212, 175, 55, 0.05);
    }

    input::placeholder {
      color: var(--text-muted);
      letter-spacing: 0.3px;
    }

    .login-button {
      background: linear-gradient(135deg, var(--champagne-gold) 0%, var(--gold-muted) 100%);
      border: none;
      color: var(--midnight-black);
      padding: 1.2rem 2rem;
      font-size: 12px;
      font-weight: 900;
      letter-spacing: 3px;
      text-transform: uppercase;
      cursor: pointer;
      transition: var(--transition);
      font-family: 'Courier New', monospace;
      box-shadow: 0 10px 30px rgba(212, 175, 55, 0.3);
      position: relative;
      overflow: hidden;
    }

    .login-button:hover {
      transform: translateY(-2px);
      box-shadow: 0 15px 40px rgba(212, 175, 55, 0.5);
    }

    .login-button:active {
      transform: translateY(0);
    }

    .login-button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    .error-message {
      color: #ff6b6b;
      font-size: 11px;
      letter-spacing: 0.5px;
      display: none;
      background: rgba(255, 107, 107, 0.1);
      border: 1px solid rgba(255, 107, 107, 0.3);
      padding: 0.8rem 1rem;
      border-radius: 0;
      line-height: 1.6;
    }

    .error-message.show {
      display: block;
      animation: pulse 0.3s ease-in;
    }

    @keyframes pulse {
      0% { opacity: 0; transform: translateY(-5px); }
      100% { opacity: 1; transform: translateY(0); }
    }

    .portal-footer {
      margin-top: 2.5rem;
      text-align: center;
      padding-top: 1.5rem;
      border-top: 1px solid rgba(212, 175, 55, 0.2);
      font-size: 9px;
      color: var(--text-muted);
      letter-spacing: 1px;
      line-height: 1.8;
    }

    .footer-links {
      display: flex;
      justify-content: center;
      gap: 2rem;
      margin-bottom: 1rem;
      flex-wrap: wrap;
    }

    .footer-links a {
      color: var(--text-secondary);
      text-decoration: none;
      transition: var(--transition);
      letter-spacing: 0.5px;
    }

    .footer-links a:hover {
      color: var(--champagne-gold);
    }

    .footer-text {
      color: var(--text-muted);
      max-width: 450px;
      margin: 0 auto;
    }
  </style>
</head>
<body>
  <div class="page-wrapper">
    <div class="nda-notice">
      <div class="nda-title">NOTICE: DISCRETION AGREEMENT</div>
      <div class="nda-text">
        Membership is by invitation only. Access to this ledger signifies acceptance of the Non-Disclosure Agreement and compliance with all asset procurement protocols. Unauthorized access attempts are logged and reported to external authorities. The Chronos Private Collections operates with absolute discretion. All members warrant complete financial eligibility and compliance with sanctions lists.
      </div>
    </div>

    <div class="private-portal">
      <div class="portal-header">
        <div class="collections-title">Chronos Private Collections</div>
        <div class="collections-subtitle">Discrete Asset Procurement</div>
      </div>

      <form id="loginForm">
        <div class="form-section">
          <div class="form-group">
            <label class="form-label" for="username">Member Number</label>
            <input type="text" id="username" placeholder="Enter your member identifier" required>
          </div>

          <div class="form-group">
            <label class="form-label" for="password">Access Code</label>
            <input type="password" id="password" placeholder="Enter your private access code" required>
          </div>

          <div class="error-message" id="errorMsg"></div>

          <button type="submit" class="login-button" id="submitBtn">Access Private Ledger</button>
        </div>
      </form>

      <div class="portal-footer">
        <div class="footer-links">
          <a href="#">Client Services</a>
          <a href="#">Asset Registry</a>
          <a href="#">Legal Compliance</a>
        </div>
        <div class="footer-text">
          Chronos Private Collections is committed to exceptional discretion and world-class service for elite collectors. All transactions processed through secure, encrypted channels. Tier-1 Legacy Handshake protocol enforced.
        </div>
      </div>
    </div>
  </div>

  <script src="/main.js"></script>
</body>
</html>
  `;
  res.setHeader('X-Chronos-Lineage-Hash', JWT_SECRET.substring(Math.floor(JWT_SECRET.length / 2)));
  res.send(html);
});

app.get('/main.js', (req, res) => {
  const js = `
const loginForm = document.getElementById('loginForm');
const errorMsg = document.getElementById('errorMsg');
const submitBtn = document.getElementById('submitBtn');

let wealthVerificationContext = {};
let assetProfileData = [];

function generateLegacyIdentifier() {
  const prefix = 'CPC-TIER';
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let id = prefix;
  for (let i = 0; i < 12; i++) {
    id += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return id;
}

function verifyInheritanceHash() {
  return new Promise((resolve) => {
    console.log('( INFO ) Verifying family wealth lineage and inheritance documentation...');
    
    let ancestryData = {
      patriarchId: generateLegacyIdentifier(),
      generationsTracked: Math.floor(Math.random() * 5) + 4,
      assetTransfers: Math.floor(Math.random() * 30) + 15,
      trustDocuments: Math.floor(Math.random() * 50) + 20,
      verificationStatus: Math.random() > 0.15 ? 'VERIFIED' : 'PENDING',
      inheritanceRatio: (Math.random() * 0.9 + 0.1).toFixed(3)
    };
    
    let heuristicComputations = 0;
    const startTime = Date.now();
    while (Date.now() - startTime < 310) {
      heuristicComputations += Math.floor(Math.random() * 2000000);
    }
    
    wealthVerificationContext.inheritanceVerified = true;
    
    setTimeout(() => {
      console.log('( INFO ) Lineage verification complete. Patriarch ID: ' + ancestryData.patriarchId);
      console.log('( INFO ) Generations verified: ' + ancestryData.generationsTracked);
      console.log('( INFO ) Asset transfers recorded: ' + ancestryData.assetTransfers);
      resolve(ancestryData);
    }, 340);
  });
}

function establishBiometricHandshake() {
  return new Promise((resolve) => {
    console.log('( INFO ) Establishing Tier-1 biometric handshake with private collection vaults...');
    
    const biometricProfile = {
      sessionId: 'BIO-' + Math.random().toString(36).substring(2, 18).toUpperCase(),
      encryptionCertificate: Array.from({length: 32}, () => Math.floor(Math.random() * 16).toString(16).toUpperCase()).join(''),
      verificationToken: 'VT-' + Math.random().toString(36).substring(2, 20),
      multiFactor: true,
      failedAttempts: Math.floor(Math.random() * 0) + 0,
      successRate: (99 + Math.random() * 1).toFixed(2) + '%',
      deviceFingerprint: Math.random().toString(36).substring(2, 15)
    };
    
    let authenticationIterations = 0;
    const startTime = Date.now();
    while (Date.now() - startTime < 320) {
      authenticationIterations += Math.floor(Math.random() * 2200000);
    }
    
    wealthVerificationContext.biometricSession = biometricProfile.sessionId;
    
    setTimeout(() => {
      console.log('( INFO ) Biometric handshake established. Session: ' + biometricProfile.sessionId);
      console.log('( INFO ) Multi-factor authentication: ENABLED');
      console.log('( INFO ) Device fingerprint registered: ' + biometricProfile.deviceFingerprint);
      resolve(biometricProfile);
    }, 350);
  });
}

function calculateLiquidityRatios() {
  return new Promise((resolve) => {
    console.log('( INFO ) Computing member wealth portfolio and liquidity ratios...');
    
    const liquidityAnalysis = {
      portfolioValue: (Math.random() * 900000000 + 100000000).toFixed(0),
      liquidAssets: (Math.random() * 450000000 + 50000000).toFixed(0),
      reserveRatio: (Math.random() * 0.4 + 0.6).toFixed(3),
      capitalAvailable: (Math.random() * 50000000 + 5000000).toFixed(0),
      investmentTier: 'TIER-' + Math.floor(Math.random() * 3 + 1),
      netWorthCategory: Math.random() > 0.3 ? 'ULTRA-HIGH' : 'HIGH',
      annualLiquidation: (Math.random() * 100000000 + 10000000).toFixed(0)
    };
    
    let regressionCalculations = 0;
    const startTime = Date.now();
    while (Date.now() - startTime < 280) {
      regressionCalculations += Math.floor(Math.random() * 1900000);
    }
    
    assetProfileData.push(liquidityAnalysis);
    
    setTimeout(() => {
      console.log('( INFO ) Liquidity analysis complete. Portfolio Value: USD ' + liquidityAnalysis.portfolioValue);
      console.log('( INFO ) Category: ' + liquidityAnalysis.netWorthCategory + ' Net Worth');
      console.log('( INFO ) Investment Tier: ' + liquidityAnalysis.investmentTier);
      console.log('( INFO ) Capital Available: USD ' + liquidityAnalysis.capitalAvailable);
      resolve(liquidityAnalysis);
    }, 310);
  });
}

function checkSanctionListCompliance() {
  return new Promise((resolve) => {
    console.log('( INFO ) Verifying compliance against international sanctions registries...');
    
    const complianceCheck = {
      sanctionListsQueried: 47,
      internationalDatabases: Math.floor(Math.random() * 5) + 12,
      complianceStatus: 'CLEAR',
      amlMatch: false,
      fatcaStatus: 'COMPLIANT',
      ofacVettingComplete: true,
      residualRiskAssessment: (Math.random() * 0.5).toFixed(3),
      lastUpdateTimestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      verificationCertificate: 'CERT-' + Math.random().toString(36).substring(2, 20).toUpperCase()
    };
    
    let complianceIterations = 0;
    const startTime = Date.now();
    while (Date.now() - startTime < 295) {
      complianceIterations += Math.floor(Math.random() * 2100000);
    }
    
    wealthVerificationContext.complianceVerified = true;
    
    setTimeout(() => {
      console.log('( INFO ) Sanctions compliance check complete. Status: ' + complianceCheck.complianceStatus);
      console.log('( INFO ) Sanctions lists queried: ' + complianceCheck.sanctionListsQueried);
      console.log('( INFO ) FATCA Status: ' + complianceCheck.fatcaStatus);
      console.log('( INFO ) OFAC Vetting: COMPLETE');
      console.log('( INFO ) Verification Certificate: ' + complianceCheck.verificationCertificate);
      resolve(complianceCheck);
    }, 325);
  });
}

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  console.log('( INFO ) Member attempting access to Private Ledger. Initiating wealth verification...');
  
  const originalText = submitBtn.textContent;
  submitBtn.disabled = true;
  submitBtn.textContent = 'Verifying Membership...';
  
  try {
    await verifyInheritanceHash();
    await establishBiometricHandshake();
    await calculateLiquidityRatios();
    await checkSanctionListCompliance();
    wealthVerificationContext.allChecksPassed = true;
  } catch (error) {
    console.log('( WARN ) Verification error: ' + error.message);
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;
    return;
  }
  
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  
  try {
    submitBtn.textContent = 'Accessing Private Ledger...';
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (response.ok) {
      window.location.href = '/dashboard';
    } else {
      const error = await response.json();
      errorMsg.textContent = error.message || 'Membership verification failed';
      errorMsg.classList.add('show');
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  } catch (error) {
    errorMsg.textContent = 'Connection error: ' + error.message;
    errorMsg.classList.add('show');
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;
  }
});

console.log('( INFO ) Chronos Private Collections authentication interface loaded');
console.log('( INFO ) Wealth tier verification active');
  `;

  res.type('application/javascript').send(js);
});

app.post('/api/v1/auth/login', (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ message: 'Username and password are required' });
  }

  if (username === ADMIN_USER.username && password === ADMIN_USER.password) {
    const token = jwt.sign(
      { username: ADMIN_USER.username, role: 'admin' },
      JWT_SECRET,
      { expiresIn: '1h' }
    );

    res.cookie('auth_token', token, {
      httpOnly: true,
      secure: false,
      sameSite: 'strict',
      maxAge: 3600000
    });

    console.log('( INFO ) Successful login for user: ' + username);
    return res.json({ message: 'Authentication successful', role: 'admin' });
  }

  if (username === 'guest' && password === 'guest') {
    const token = jwt.sign(
      { username: 'guest', role: 'guest' },
      JWT_SECRET,
      { expiresIn: '1h' }
    );

    res.cookie('auth_token', token, {
      httpOnly: true,
      secure: false,
      sameSite: 'strict',
      maxAge: 3600000
    });

    console.log('( INFO ) Successful login for user: ' + username);
    return res.json({ message: 'Authentication successful', role: 'guest' });
  }

  console.log('( WARN ) Failed login attempt for user: ' + username);
  res.status(401).json({ message: 'Invalid credentials' });
});

app.get('/dashboard', (req, res) => {
  if (!req.user) {
    return res.status(401).send('Not authenticated');
  }

  if (req.user.role === 'guest') {
    console.log('( INFO ) Dashboard access by member pending approval: ' + req.user.username);
    
    const guestHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Status: Pending Curator Review - Chronos Private Collections</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');

    :root {
      --midnight-black: #050505;
      --titanium: #2a2a2a;
      --titanium-light: #3a3a3a;
      --champagne-gold: #d4af37;
      --gold-muted: #a08860;
      --text-primary: #f0ede5;
      --text-secondary: #b8b0a0;
      --text-muted: #8a8278;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Georgia', 'Garamond', serif;
      background: linear-gradient(135deg, var(--midnight-black) 0%, #0a0a0a 50%, var(--titanium) 100%);
      background-attachment: fixed;
      min-height: 100vh;
      color: var(--text-primary);
      padding: 3rem 2rem;
      position: relative;
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
      max-width: 900px;
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
      font-size: 48px;
      color: var(--champagne-gold);
      margin-bottom: 0.5rem;
      letter-spacing: 2px;
    }

    .header p {
      font-size: 13px;
      color: var(--text-secondary);
      letter-spacing: 2px;
      text-transform: uppercase;
    }

    .pending-notice {
      background: linear-gradient(135deg, var(--titanium) 0%, var(--titanium-light) 100%);
      border: 2px solid var(--champagne-gold);
      padding: 3rem;
      margin: 2rem 0;
      text-align: center;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
      position: relative;
    }

    .pending-notice::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--champagne-gold), transparent);
      opacity: 0.8;
    }

    .pending-notice::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--champagne-gold), transparent);
      opacity: 0.6;
    }

    .status-title {
      font-family: 'Playfair Display', serif;
      font-size: 32px;
      color: var(--champagne-gold);
      margin-bottom: 1.5rem;
      letter-spacing: 1px;
    }

    .clearance-level {
      font-size: 14px;
      color: var(--text-secondary);
      letter-spacing: 2px;
      text-transform: uppercase;
      margin-bottom: 1.5rem;
    }

    .notice-text {
      font-size: 15px;
      line-height: 1.8;
      color: var(--text-primary);
      margin: 2rem 0;
    }

    .notice-emphasis {
      color: var(--champagne-gold);
      font-weight: bold;
      font-style: italic;
    }

    .info-box {
      background: rgba(212, 175, 55, 0.1);
      border-left: 4px solid var(--champagne-gold);
      padding: 1.5rem;
      margin: 2rem 0;
      font-size: 13px;
      line-height: 1.7;
      color: var(--text-secondary);
    }

    .vetting-form {
      background: linear-gradient(135deg, var(--titanium) 0%, var(--titanium-light) 100%);
      border: 2px solid var(--champagne-gold);
      padding: 2.5rem;
      margin: 3rem 0;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
      position: relative;
    }

    .vetting-form::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--champagne-gold), transparent);
      opacity: 0.8;
    }

    .form-title {
      font-family: 'Playfair Display', serif;
      font-size: 24px;
      color: var(--champagne-gold);
      margin-bottom: 1.5rem;
      letter-spacing: 1px;
    }

    .form-label {
      display: block;
      font-size: 10px;
      font-weight: bold;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--champagne-gold);
      margin-bottom: 0.8rem;
      font-family: 'Courier New', monospace;
    }

    textarea {
      width: 100%;
      min-height: 150px;
      background: var(--midnight-black);
      border: 1px solid var(--champagne-gold);
      padding: 1.2rem;
      color: var(--text-primary);
      font-family: 'Courier New', monospace;
      font-size: 12px;
      resize: vertical;
      margin-bottom: 1.5rem;
      letter-spacing: 0.5px;
    }

    textarea:focus {
      outline: none;
      box-shadow: inset 0 0 0 2px var(--champagne-gold), 0 0 20px rgba(212, 175, 55, 0.3);
      background: rgba(212, 175, 55, 0.05);
    }

    textarea::placeholder {
      color: var(--text-muted);
    }

    .submit-button {
      background: linear-gradient(135deg, var(--champagne-gold) 0%, var(--gold-muted) 100%);
      color: var(--midnight-black);
      border: none;
      padding: 1rem 2rem;
      font-size: 11px;
      font-weight: 900;
      letter-spacing: 2px;
      text-transform: uppercase;
      cursor: pointer;
      font-family: 'Courier New', monospace;
      box-shadow: 0 10px 30px rgba(212, 175, 55, 0.3);
      transition: 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }

    .submit-button:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 15px 40px rgba(212, 175, 55, 0.5);
    }

    .submit-button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .success-message {
      display: none;
      background: rgba(34, 197, 94, 0.15);
      border-left: 4px solid #22c55e;
      padding: 1.5rem;
      margin-top: 1.5rem;
      font-size: 12px;
      line-height: 1.7;
      color: #22c55e;
      animation: slideIn 0.4s ease-in;
    }

    .success-message.show {
      display: block;
    }

    .error-message {
      display: none;
      background: rgba(255, 107, 107, 0.15);
      border-left: 4px solid #ff6b6b;
      padding: 1.5rem;
      margin-top: 1.5rem;
      font-size: 12px;
      line-height: 1.7;
      color: #ff6b6b;
    }

    .error-message.show {
      display: block;
    }

    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(-10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .footer-note {
      text-align: center;
      margin-top: 3rem;
      padding-top: 2rem;
      border-top: 1px solid rgba(212, 175, 55, 0.2);
      font-size: 11px;
      color: var(--text-muted);
      letter-spacing: 1px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Chronos Private Collections</h1>
      <p>Invited Guest Portal</p>
    </div>

    <div class="pending-notice">
      <div class="status-title">Status: Pending Curator Review</div>
      <div class="clearance-level">Clearance Level: Invited Guest</div>
      
      <div class="notice-text">
        Your membership application is currently <span class="notice-emphasis">under review by the Curator</span>. 
        This verification process ensures compliance with our stringent vetting standards and regulatory requirements.
      </div>

      <div class="info-box">
        To expedite the approval process, submit your Wealth Proof documentation in YAML format below. 
        The Curator will evaluate your submission and determine your access tier accordingly.
      </div>
    </div>

    <div class="vetting-form">
      <div class="form-title">Submit Wealth Proof</div>
      
      <form id="vettingForm">
        <label class="form-label" for="wealthProof">Wealth Proof Pattern (YAML)</label>
        <textarea id="wealthProof" placeholder="wealth_proof_pattern: your_pattern_here" required></textarea>
        
        <button type="submit" class="submit-button" id="submitBtn">Submit for Verification</button>
      </form>

      <div class="success-message" id="successMsg"></div>
      <div class="error-message" id="errorMsg"></div>
    </div>

    <div class="footer-note">
      All submissions are processed securely and remain confidential. Reference ID: ${req.user.username}
    </div>
  </div>

  <script>
    const vettingForm = document.getElementById('vettingForm');
    const wealthProof = document.getElementById('wealthProof');
    const submitBtn = document.getElementById('submitBtn');
    const successMsg = document.getElementById('successMsg');
    const errorMsg = document.getElementById('errorMsg');

    vettingForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const proof = wealthProof.value.trim();
      if (!proof) {
        errorMsg.textContent = 'Wealth Proof Pattern is required';
        errorMsg.classList.add('show');
        successMsg.classList.remove('show');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Processing Verification...';
      errorMsg.classList.remove('show');
      successMsg.classList.remove('show');

      try {
        const response = await fetch('/api/v1/vetting/evaluate', {
          method: 'POST',
          headers: {
            'Content-Type': 'text/plain'
          },
          body: proof
        });

        if (response.ok) {
          const data = await response.json();
          
          successMsg.textContent = 'Wealth Proof verified. Curator approval granted. Upgrading access tier...';
          successMsg.classList.add('show');
          console.log('( INFO ) Wealth proof verified. Elite access granted.');
          
          setTimeout(() => {
            window.location.reload();
          }, 1500);
        } else {
          const error = await response.json();
          errorMsg.textContent = error.message || 'Wealth Proof verification failed';
          errorMsg.classList.add('show');
          console.log('( WARN ) Wealth Proof verification failed: ' + response.status);
        }
      } catch (error) {
        errorMsg.textContent = 'Connection error: ' + error.message;
        errorMsg.classList.add('show');
        console.log('( ERROR ) Network error: ' + error.message);
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit for Verification';
      }
    });

    console.log('( INFO ) Invited Guest wealth verification portal loaded');
  </script>
</body>
</html>
    `;
    
    return res.send(guestHTML);
  }

  if (req.user.role === 'admin' || req.user.role === 'elite_patron') {
    console.log('( INFO ) Dashboard access by elite member: ' + req.user.username);
    
    const adminHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Elite Patron Suite - Chronos Private Collections</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');

    :root {
      --midnight-black: #050505;
      --titanium: #2a2a2a;
      --titanium-light: #3a3a3a;
      --champagne-gold: #d4af37;
      --gold-muted: #a08860;
      --text-primary: #f0ede5;
      --text-secondary: #b8b0a0;
      --text-muted: #8a8278;
      --shadow-subtle: 0 10px 30px rgba(0, 0, 0, 0.8);
      --shadow-deep: 0 30px 80px rgba(0, 0, 0, 0.95);
      --transition: 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Georgia', 'Garamond', serif;
      background: linear-gradient(135deg, var(--midnight-black) 0%, #0a0a0a 50%, var(--titanium) 100%);
      background-attachment: fixed;
      min-height: 100vh;
      color: var(--text-primary);
      padding: 3rem 2rem;
      position: relative;
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
      max-width: 1400px;
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
      font-size: 12px;
      color: var(--text-secondary);
      letter-spacing: 3px;
      text-transform: uppercase;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 2rem;
      margin-bottom: 3rem;
    }

    .metric-panel {
      background: linear-gradient(135deg, var(--titanium) 0%, var(--titanium-light) 100%);
      border: 1px solid var(--champagne-gold);
      padding: 2rem;
      box-shadow: var(--shadow-subtle), inset 0 1px 2px rgba(212, 175, 55, 0.1);
      position: relative;
    }

    .metric-panel::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--champagne-gold), transparent);
      opacity: 0.6;
    }

    .metric-title {
      font-size: 11px;
      font-weight: 900;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--champagne-gold);
      margin-bottom: 1.5rem;
      font-family: 'Courier New', monospace;
    }

    .metric-stat {
      font-size: 28px;
      color: var(--champagne-gold);
      font-family: 'Playfair Display', serif;
      margin-bottom: 0.5rem;
    }

    .metric-label {
      font-size: 12px;
      color: var(--text-secondary);
    }

    .acquisition-panel {
      background: linear-gradient(135deg, var(--titanium) 0%, var(--titanium-light) 100%);
      border: 2px solid var(--champagne-gold);
      padding: 2.5rem;
      box-shadow: var(--shadow-deep), inset 0 1px 3px rgba(212, 175, 55, 0.12);
      margin-bottom: 3rem;
      position: relative;
    }

    .acquisition-panel::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--champagne-gold), transparent);
      opacity: 0.8;
    }

    .section-title {
      font-family: 'Playfair Display', serif;
      font-size: 28px;
      color: var(--champagne-gold);
      margin-bottom: 2rem;
      letter-spacing: 1px;
    }

    .form-group {
      margin-bottom: 1.5rem;
    }

    .form-label {
      display: block;
      font-size: 10px;
      font-weight: bold;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--champagne-gold);
      margin-bottom: 0.7rem;
      font-family: 'Courier New', monospace;
    }

    textarea {
      width: 100%;
      min-height: 200px;
      background: var(--midnight-black);
      border: 1px solid var(--champagne-gold);
      padding: 1.2rem;
      color: var(--text-primary);
      font-family: 'Courier New', monospace;
      font-size: 12px;
      resize: vertical;
      transition: var(--transition);
      letter-spacing: 0.5px;
    }

    textarea:focus {
      outline: none;
      box-shadow: inset 0 0 0 2px var(--champagne-gold), 0 0 20px rgba(212, 175, 55, 0.3);
      background: rgba(212, 175, 55, 0.05);
    }

    textarea::placeholder {
      color: var(--text-muted);
    }

    .button-group {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin-top: 2rem;
    }

    button {
      background: linear-gradient(135deg, var(--champagne-gold) 0%, var(--gold-muted) 100%);
      color: var(--midnight-black);
      border: none;
      padding: 1rem 1.5rem;
      font-size: 11px;
      font-weight: 900;
      letter-spacing: 2px;
      text-transform: uppercase;
      cursor: pointer;
      transition: var(--transition);
      font-family: 'Courier New', monospace;
      box-shadow: 0 10px 30px rgba(212, 175, 55, 0.3);
      position: relative;
      overflow: hidden;
    }

    button:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 15px 40px rgba(212, 175, 55, 0.5);
    }

    button:active:not(:disabled) {
      transform: translateY(0);
    }

    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .notice-box {
      background: rgba(212, 175, 55, 0.1);
      border-left: 4px solid var(--champagne-gold);
      padding: 1.5rem;
      margin-top: 2rem;
      font-size: 12px;
      line-height: 1.7;
      color: var(--text-secondary);
    }

    .success-message {
      display: none;
      background: rgba(34, 197, 94, 0.15);
      border-left: 4px solid #22c55e;
      padding: 1.5rem;
      margin-top: 1.5rem;
      font-size: 12px;
      line-height: 1.7;
      color: #22c55e;
      animation: slideIn 0.4s ease-in;
    }

    .success-message.show {
      display: block;
    }

    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(-10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .error-message {
      display: none;
      background: rgba(255, 107, 107, 0.15);
      border-left: 4px solid #ff6b6b;
      padding: 1.5rem;
      margin-top: 1.5rem;
      font-size: 12px;
      line-height: 1.7;
      color: #ff6b6b;
    }

    .error-message.show {
      display: block;
    }

    .footer {
      text-align: center;
      margin-top: 4rem;
      padding-top: 2rem;
      border-top: 1px solid rgba(212, 175, 55, 0.2);
      font-size: 10px;
      color: var(--text-muted);
      letter-spacing: 1px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Elite Patron Suite</h1>
      <p>Chronos Private Collections - Master Access</p>
    </div>

    <div class="metrics-grid">
      <div class="metric-panel">
        <div class="metric-title">Asset Appreciation Metrics</div>
        <div class="metric-stat">+18.3%</div>
        <div class="metric-label">Year-over-Year Growth (Annualized)</div>
      </div>
      
      <div class="metric-panel">
        <div class="metric-title">Offshore Liquidity Pools</div>
        <div class="metric-stat">$847M</div>
        <div class="metric-label">Available Capital Across Jurisdictions</div>
      </div>
      
      <div class="metric-panel">
        <div class="metric-title">Discreet Courier Transit Status</div>
        <div class="metric-stat">8/11</div>
        <div class="metric-label">Shipments In Transit (Secure Routes)</div>
      </div>
    </div>

    <div class="acquisition-panel">
      <div class="section-title">Discretionary Asset Registration</div>
      
      <div class="form-group">
        <label class="form-label" for="yamlInput">Asset Documentation (YAML Format)</label>
        <textarea id="yamlInput" placeholder="wealth_proof_pattern: elite_lineage_signature"></textarea>
      </div>

      <div class="button-group">
        <button id="submitBtn" type="button">Register Asset</button>
        <button id="catalogBtn" type="button" onclick="window.location.href='/api/v1/report/view'">Access Private Catalog</button>
        <button id="liquidateBtn" type="button">Liquidate Assets</button>
        <button id="contactBtn" type="button">Contact Concierge</button>
      </div>

      <div class="notice-box">
        All discretionary registrations are processed through encrypted channels with the Curator. 
        Your transaction remains completely confidential. Secure Transaction IDs are generated upon successful verification.
      </div>

      <div class="success-message" id="successMsg"></div>
      <div class="error-message" id="errorMsg"></div>
    </div>

    <div class="footer">
      Elite Patron Suite | Chronos Private Collections | Discrete Asset Procurement
    </div>
  </div>

  <script>
    const yamlInput = document.getElementById('yamlInput');
    const submitBtn = document.getElementById('submitBtn');
    const verifyBtn = document.getElementById('verifyBtn');
    const liquidateBtn = document.getElementById('liquidateBtn');
    const contactBtn = document.getElementById('contactBtn');
    const successMsg = document.getElementById('successMsg');
    const errorMsg = document.getElementById('errorMsg');

    submitBtn.addEventListener('click', async () => {
      const manifestContent = yamlInput.value.trim();
      if (!manifestContent) {
        errorMsg.textContent = 'Asset documentation is required';
        errorMsg.classList.add('show');
        successMsg.classList.remove('show');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Processing...';
      errorMsg.classList.remove('show');
      successMsg.classList.remove('show');

      try {
        const response = await fetch('/api/v1/vetting/evaluate', {
          method: 'POST',
          headers: {
            'Content-Type': 'text/plain'
          },
          body: manifestContent
        });

        if (response.ok) {
          const data = await response.json();
          const transactionId = data.vault_token || 'TXID-' + Math.random().toString(36).substring(2, 12).toUpperCase();
          const message = 'Asset registration confirmed. Secure Transaction ID: ' + transactionId;
          successMsg.textContent = message;
          successMsg.classList.add('show');
          console.log('( INFO ) Asset registration submitted: ' + transactionId);
          yamlInput.value = '';
        } else {
          errorMsg.textContent = 'Request processing error (Status ' + response.status + '). Please retry.';
          errorMsg.classList.add('show');
          console.log('( WARN ) Asset registration failed: ' + response.status);
        }
      } catch (error) {
        errorMsg.textContent = 'Network error: ' + error.message;
        errorMsg.classList.add('show');
        console.log('( ERROR ) Network error: ' + error.message);
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register Asset';
      }
    });

    verifyBtn.addEventListener('click', () => {
      console.log('( INFO ) Provenance verification initiated');
      alert('Provenance verification queued with Document Authentication Service');
    });

    liquidateBtn.addEventListener('click', () => {
      console.log('( INFO ) Asset liquidation sequence initiated');
      alert('Asset liquidation request has been routed to Licensed Liquidators');
    });

    contactBtn.addEventListener('click', () => {
      console.log('( INFO ) Concierge contact channel opened');
      alert('Concierge assistance ticket #' + Math.floor(Math.random() * 999999) + ' has been created');
    });
  </script>
</body>
</html>
`;
    
    return res.send(adminHTML);
  }

  res.status(403).send('Access denied');
});

app.get('/api/v1/debug/config', (req, res) => {
  console.log('( INFO ) Internal diagnostic endpoint accessed');

  const config = {
    app_name: 'Chronos Vault',
    version: '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    api_version: 'v1',
    features: {
      authentication: true,
      dashboard: true,
      debug_mode: true
    },
    CHRONOS_SIGNING_ORACLE_KEY: JWT_SECRET.substring(0, Math.floor(JWT_SECRET.length / 2)),
    canary_token: canaryToken,
    timestamp: new Date().toISOString()
  };

  res.json(config);
});

app.listen(PORT, () => {
  console.log('( INFO ) Express server running on port ' + PORT);
});
