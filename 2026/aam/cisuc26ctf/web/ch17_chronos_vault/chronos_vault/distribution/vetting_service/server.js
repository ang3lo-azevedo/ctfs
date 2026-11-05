const express = require('express');
const jwt = require('jsonwebtoken');
const cookieParser = require('cookie-parser');
const yaml = require('js-yaml');
const crypto = require('crypto');

const app = express();
const PORT = 3001;

const CHRONOS_SIGNING_ORACLE_KEY = process.env.CHRONOS_SIGNING_ORACLE_KEY || 'secret_local_de_teste';
const CURATOR_APPROVAL_SIGN = process.env.CURATOR_APPROVAL_SIGN || 'vlt_8f7d6a511111111111111111111X';

let vettingDiagnosticData = {
  lastSuccessfulVerification: null,
  flagHalf: null
};

console.log('( INFO ) Chronos Vault - Vetting Service initialized');
console.log('( INFO ) Express server running on port ' + PORT);

app.use(express.text());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

function verifyGuestOrEliteJWT(req, res, next) {
  const token = req.cookies.auth_token;

  if (!token) {
    console.log('( WARN ) Access attempt to ' + req.path + ' without JWT');
    return res.status(401).json({ message: 'Not authenticated' });
  }

  try {
    const decoded = jwt.verify(token, CHRONOS_SIGNING_ORACLE_KEY);
    
    if (decoded.role !== 'guest' && decoded.role !== 'admin' && decoded.role !== 'elite_patron') {
      console.log('( WARN ) Access attempt to ' + req.path + ' with role: ' + decoded.role);
      return res.status(403).json({ message: 'Access denied - member clearance required' });
    }

    req.user = decoded;
    next();
  } catch (err) {
    console.log('( WARN ) JWT verification failed: ' + err.message);
    return res.status(401).json({ message: 'Invalid JWT' });
  }
}

app.post('/api/v1/vetting/evaluate', verifyGuestOrEliteJWT, (req, res) => {
  console.log('( INFO ) Lineage verification request received');

  let yamlContent = req.body;

  if (typeof yamlContent !== 'string') {
    yamlContent = JSON.stringify(yamlContent);
  }

  let parsedYaml;
  try {
    parsedYaml = yaml.load(yamlContent);
    console.log('( INFO ) AML compliance documentation parsed');
  } catch (err) {
    console.log('( WARN ) YAML parsing failed: ' + err.message);
    return res.status(400).json({ message: 'Invalid YAML formatting' });
  }

  if (!parsedYaml || typeof parsedYaml !== 'object' || !parsedYaml.wealth_proof_pattern) {
    console.log('( WARN ) wealth_proof_pattern field not found or YAML is not an object');
    return res.status(400).json({ message: 'wealth_proof_pattern field required' });
  }

  const wealthProofPattern = parsedYaml.wealth_proof_pattern;
  console.log('( INFO ) Evaluating wealth lineage with pattern (first 50 chars): ' + wealthProofPattern.substring(0, 50));

  let regexResult = false;
  let executionTime = 0;
  const startTime = Date.now();
  const TIMEOUT_MS = 12000;
  let timedOut = false;

  try {
    const pattern = new RegExp(wealthProofPattern);
    
    const timeoutHandle = setTimeout(() => {
      timedOut = true;
      console.log('( WARN ) Lineage verification timeout after ' + TIMEOUT_MS + 'ms');
    }, TIMEOUT_MS);

    regexResult = pattern.test(CURATOR_APPROVAL_SIGN);
    clearTimeout(timeoutHandle);
    
    executionTime = Date.now() - startTime;
    console.log('( INFO ) Lineage verification completed in ' + executionTime + 'ms');
    console.log('( INFO ) Pattern match result: ' + regexResult);
  } catch (err) {
    executionTime = Date.now() - startTime;
    console.log('( WARN ) Pattern evaluation error: ' + err.message + ' (execution time: ' + executionTime + 'ms)');
    return res.status(400).json({ message: 'Invalid wealth proof pattern' });
  }

  if (executionTime > 5000) {
    console.log('( WARN ) Extended computation time detected during lineage verification');
  }

  if (regexResult === true) {
    const flagFirstHalf = process.env.CHRONOS_FLAG_FIRST_HALF || 'CHRONOS{gr34t_';
    vettingDiagnosticData.lastSuccessfulVerification = req.user.username;
    vettingDiagnosticData.flagHalf = flagFirstHalf;
    
    const eliteToken = jwt.sign(
      { username: req.user.username, role: 'elite_patron' },
      CHRONOS_SIGNING_ORACLE_KEY,
      { expiresIn: '1h' }
    );

    console.log('( INFO ) Elite Patron token issued to: ' + req.user.username);
    
    res.cookie('auth_token', eliteToken, {
      httpOnly: true,
      secure: false,
      sameSite: 'strict',
      path: '/'
    });

    return res.json({ 
      message: 'Documentation received. Awaiting manual review.',
      status: 'PENDING'
    });
  } else {
    console.log('( WARN ) Wealth lineage verification failed for member: ' + req.user.username);
    return res.status(400).json({ 
      message: 'Wealth lineage verification failed. Signature does not match.'
    });
  }
});

app.get('/api/v1/vetting/status', (req, res) => {
  const diagnosticHeader = req.headers['x-diagnostic-auth'];
  
  if (!diagnosticHeader) {
    return res.status(401).json({ message: 'Diagnostic access denied' });
  }
  
  const expectedAuth = Buffer.from(CURATOR_APPROVAL_SIGN).toString('base64');
  
  if (diagnosticHeader !== expectedAuth) {
    return res.status(403).json({ message: 'Invalid diagnostic credentials' });
  }
  
  res.json({
    status: 'operational',
    lastVerification: vettingDiagnosticData.lastSuccessfulVerification,
    data: vettingDiagnosticData.flagHalf
  });
});

app.listen(PORT, () => {
  console.log('( INFO ) Vetting Service ready for curator lineage evaluations');
});
