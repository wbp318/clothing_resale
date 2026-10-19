// Resale API Worker. Payment is handled upstream by the Cloudflare Monetization Gateway (x402).
// For human developers without an x402 wallet, a plain API key in the X-Api-Key header is accepted.

const FEES = {
  // final value fee as a fraction, plus a flat per-order fee. Mirror docs/02-platforms.md.
  ebay: { pct: 0.136, flat: 0.30 },
  depop: { pct: 0.0, flat: 0.0 },        // buyer-paid fee model; keep in KV so it can change without a deploy
  poshmark: { pct: 0.20, flat: 0.0 },    // 20% over $15, $2.95 flat under
  vinted: { pct: 0.0, flat: 0.0 },
  mercari: { pct: 0.10, flat: 0.0 },
};

// USPS Ground Advantage rough retail by weight (oz), zones 1-4. Mirror docs/04-shipping-usps.md.
const USPS = [[4, 4.5], [8, 5.0], [12, 5.6], [16, 6.4], [32, 8.5], [48, 10.5]];

function shipCost(oz) {
  for (const [limit, cost] of USPS) if (oz <= limit) return cost;
  return 14.0;
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });
}

async function authorized(req, env) {
  // Requests that arrive through the paid gateway carry a verified-payment header set by Cloudflare.
  // Exact header name is TBD until gateway access; adjust here only.
  if (req.headers.get('cf-payment-verified') === 'true') return true;
  const key = req.headers.get('x-api-key');
  if (!key) return false;
  const row = await env.DB.prepare('SELECT calls_left FROM api_keys WHERE key = ?').bind(key).first();
  if (!row || row.calls_left <= 0) return false;
  await env.DB.prepare('UPDATE api_keys SET calls_left = calls_left - 1 WHERE key = ?').bind(key).run();
  return true;
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const p = url.pathname;

    if (p === '/health') return json({ ok: true });
    if (p === '/openapi.json') {
      return json({
        openapi: '3.0.0',
        info: { title: 'Resale API', version: '0.1' },
        paths: {
          '/v1/net': { get: { summary: 'Net profit after fees and shipping' } },
          '/v1/tag': { get: { summary: 'Identify vintage era and value band from tag text' } },
        },
      });
    }

    if (!p.startsWith('/v1/')) return json({ error: 'not found' }, 404);

    if (!(await authorized(req, env))) {
      return json({ error: 'payment required', price_usd: 0.01, buy_key: 'https://buy.stripe.com/PASTE' }, 402);
    }

    if (p === '/v1/net') {
      const platform = (url.searchParams.get('platform') || 'ebay').toLowerCase();
      const price = parseFloat(url.searchParams.get('price') || '0');
      const cost = parseFloat(url.searchParams.get('cost') || '0');
      const oz = parseFloat(url.searchParams.get('oz') || '12');
      const f = FEES[platform];
      if (!f || !price) return json({ error: 'need platform and price' }, 400);
      const fees = +(price * f.pct + f.flat).toFixed(2);
      const ship = shipCost(oz);
      const net = +(price - fees - ship - cost).toFixed(2);
      return json({ platform, price, fees, shipping: ship, cost, net, margin_pct: +((net / price) * 100).toFixed(1) });
    }

    if (p === '/v1/tag') {
      const text = (url.searchParams.get('text') || '').toLowerCase();
      const stitch = url.searchParams.get('stitch') || '';
      if (!text) return json({ error: 'need text' }, 400);
      const { results } = await env.DB.prepare(
        "SELECT maker, era, band_low, band_high, note FROM tags WHERE ? LIKE '%' || keyword || '%' ORDER BY LENGTH(keyword) DESC LIMIT 3"
      ).bind(text).all();
      let confidence = results.length ? 0.6 : 0.2;
      if (stitch === 'single') confidence += 0.2;
      return json({ matches: results, stitch, confidence: Math.min(confidence, 0.95) });
    }

    return json({ error: 'not found' }, 404);
  },
};
