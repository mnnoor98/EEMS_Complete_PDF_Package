const http = require('http');

const reqData = JSON.stringify({
  tenantId: '1000000000',
  username: 'noor',
  password: 'EEMS@123456!'
});

const req = http.request({
  hostname: 'localhost',
  port: 5131,
  path: '/api/v1/auth/login',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(reqData)
  }
}, res => {
  let body = '';
  res.on('data', chunk => body += chunk);
  res.on('end', () => {
    const data = JSON.parse(body);
    console.log('Login response candidateName:', data.candidateName);
    const token = data.accessToken;
    const part = token.split('.')[1];
    let base64 = part.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4) base64 += '=';
    
    // Test browser method:
    const binaryStr = Buffer.from(base64, 'base64').toString('binary');
    const bytes = Uint8Array.from(binaryStr, c => c.charCodeAt(0));
    const json = new TextDecoder('utf-8').decode(bytes);
    const payload = JSON.parse(json);
    console.log('Decoded candidate_name from JWT:', payload.candidate_name);
  });
});

req.write(reqData);
req.end();

