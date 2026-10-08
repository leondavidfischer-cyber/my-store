/* Dependency-free development server. No commerce or payment endpoints. */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const allowed = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/index.html', ['index.html', 'text/html; charset=utf-8']],
  ['/styles.css', ['styles.css', 'text/css; charset=utf-8']],
  ['/preview.js', ['preview.js', 'text/javascript; charset=utf-8']],
  ['/Vivies.png', ['Vivies.png', 'image/png']],
]);
const port = Number(process.env.PORT || 4173);
http.createServer((req, res) => {
  const resource = allowed.get(new URL(req.url, 'http://localhost').pathname);
  if (!resource || !['GET', 'HEAD'].includes(req.method)) {
    res.writeHead(404); res.end('Not found'); return;
  }
  res.setHeader('Content-Type', resource[1]);
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'HEAD') { res.end(); return; }
  fs.createReadStream(path.join(__dirname, resource[0])).pipe(res);
}).listen(port, '0.0.0.0', () => console.log(`VIVIES prototype listening on port ${port}`));
