export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const { url } = req.query;
  if (!url) {
    return res.status(400).json({ error: 'Missing target url parameter' });
  }

  let cleanUrl = url.trim();
  if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://')) {
    cleanUrl = 'https://' + cleanUrl;
  }

  let parsedUrl;
  try {
    parsedUrl = new URL(cleanUrl);
  } catch (err) {
    return res.status(400).json({ error: 'Invalid URL format' });
  }

  // SSRF Protection: Deny internal hostnames/IPs
  const hostname = parsedUrl.hostname.toLowerCase();
  if (
    hostname === 'localhost' ||
    hostname.endsWith('.localhost') ||
    hostname === '127.0.0.1' ||
    hostname === '0.0.0.0' ||
    hostname.startsWith('192.168.') ||
    hostname.startsWith('10.') ||
    hostname.startsWith('172.16.') ||
    hostname.endsWith('.internal') ||
    hostname.endsWith('.local')
  ) {
    return res.status(403).json({ error: 'SSRF check: target host is private or forbidden' });
  }

  try {
    const startTime = Date.now();
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 9000);

    const response = await fetch(cleanUrl, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 SearchSignalAudit/2.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
      },
    });
    clearTimeout(timeoutId);

    const ttfbMs = Date.now() - startTime;
    const finalUrl = response.url || cleanUrl;
    const statusCode = response.status;
    const headers = {};
    response.headers.forEach((val, key) => {
      headers[key.toLowerCase()] = val;
    });

    const html = await response.text();
    const totalFetchTimeMs = Date.now() - startTime;

    return res.status(200).json({
      success: true,
      url: cleanUrl,
      finalUrl,
      statusCode,
      headers,
      ttfbMs,
      totalFetchTimeMs,
      htmlLength: html.length,
      html: html.slice(0, 500000), // safe limit
    });
  } catch (err) {
    return res.status(200).json({
      success: false,
      url: cleanUrl,
      error: err.name === 'AbortError' ? 'Target timed out after 9 seconds' : err.message,
    });
  }
}
