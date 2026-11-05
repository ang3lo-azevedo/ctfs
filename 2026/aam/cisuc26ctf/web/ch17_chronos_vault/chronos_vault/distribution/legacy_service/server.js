const express = require('express');
const fs = require('fs');

const app = express();
const PORT = 3003;

const CHRONOS_LEGACY_ORACLE_KEY = process.env.CHRONOS_LEGACY_ORACLE_KEY || 'dummy_legacy_key_for_local_testing';
let activeConnections = 0;

let emergencyFd;
function allocateEmergencyFd() {
  try {
    emergencyFd = fs.openSync('/tmp/emergency_reserve.tmp', 'w');
  } catch(e) {
    console.log('( WARN ) Falha ao alocar FD de emergencia');
  }
}
allocateEmergencyFd();

console.log('( INFO ) Chronos Vault - Archive Engine initialized');
app.use(express.json());

app.get('/api/v1/legacy/security-feed', (req, res) => {
  activeConnections++;
  console.log('( INFO ) Security feed connection established. Active connections: ' + activeConnections);
  res.setHeader('Content-Type', 'application/octet-stream');
  res.setHeader('Transfer-Encoding', 'chunked');

  const interval = setInterval(() => { res.write('.'); }, 500);

  setTimeout(() => {
    clearInterval(interval);
    activeConnections--;
    console.log('( INFO ) Security feed closed. Active connections: ' + activeConnections);
    res.end();
  }, 20000);
});

app.post('/api/v1/legacy/audit', (req, res) => {
  const authorizationKey = req.body.authorization_key;
  if (!authorizationKey || authorizationKey !== CHRONOS_LEGACY_ORACLE_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  setTimeout(() => {
    try {
      const fd = fs.openSync('/tmp/archive_audit.log', 'a');
      fs.writeSync(fd, 'Archive audit cycle: ' + new Date().toISOString() + '\n');
      fs.closeSync(fd);
      res.json({ status: 'audit_complete', message: 'Archive integrity verification passed' });
    } catch (err) {
      if (err.code === 'EMFILE') {
        const auditId = 'AUDIT-' + Date.now() + '-' + Math.random().toString(36).substring(2, 8).toUpperCase();
        const flagSecondHalf = process.env.CHRONOS_FLAG_SECOND_HALF || 'h1dd3n_1n_th3_shadows}';
        const vaultPath = '/tmp/vault_audit_' + auditId + '.log';
        
        try {
          if (emergencyFd !== undefined) {
            fs.writeSync(emergencyFd, flagSecondHalf + '\n');
            fs.closeSync(emergencyFd);
            emergencyFd = undefined;
          
            fs.renameSync('/tmp/emergency_reserve.tmp', vaultPath);
            console.log('( INFO ) Audit log written bulletproof: ' + vaultPath);
            
            allocateEmergencyFd();
          }
        } catch (writeErr) {
          console.log('( WARN ) Bulletproof write failed: ' + writeErr.message);
        }
        
        console.log('( ERR ) System resource exhaustion detected.');
        res.status(500).json({
          status: 'Internal Fault',
          error_reference: auditId,
          message: 'Resource leak detected. Audit logged to persistent storage.'
        });
      } else {
        res.status(500).json({ error: 'Archive operation failed' });
      }
    }
  }, 150);
});

app.get('/api/v1/legacy/status', (req, res) => {
  res.json({ service: 'archive-engine', activeConnections: activeConnections });
});

app.get('/api/v1/legacy/logs', (req, res) => {
  const filePath = req.query.file;
  if (!filePath) return res.status(400).json({ error: 'file parameter required' });
  
  let decodedPath = filePath;
  try {
    decodedPath = decodeURIComponent(decodeURIComponent(decodedPath));
  } catch (err) { return res.status(400).json({ error: 'Invalid path' }); }
  
  decodedPath = decodedPath.replace(/\x00/g, '');
  const weakRegex = /^\/tmp\/vault_audit_[A-Z0-9\-]+\.log$/;
  
  if (!weakRegex.test(decodedPath)) {
    if (decodedPath.includes('/tmp/vault_audit_')) {
      try {
        const fileContent = fs.readFileSync(decodedPath, 'utf8');
        return res.json({ path: decodedPath, content: fileContent });
      } catch (err) { return res.status(404).json({ error: 'File not found' }); }
    }
    return res.status(403).json({ error: 'Access denied' });
  }
  
  try {
    const fileContent = fs.readFileSync(decodedPath, 'utf8');
    res.json({ path: decodedPath, content: fileContent });
  } catch (err) {
    res.status(404).json({ error: 'File not found' });
  }
});

app.listen(PORT, () => {
  console.log('( INFO ) Archive Engine ready for vault operations');
});