# Worker skeleton

Minimal Cloudflare Worker for the first two routes. No payment code: the Monetization Gateway handles x402 in front of it, and the API-key check covers human developers.

## Files

| File | Purpose |
|---|---|
| `src/index.js` | Router, API-key check, `/health`, `/v1/net`, `/v1/tag` |
| `wrangler.toml` | Worker name, D1 and KV bindings |
| `seed/tags.sql` | Tag rules seeded from `docs/06-pricing-and-grading.md` |

## Run

```
npm create cloudflare@latest -- --template hello-world   # once, then replace src/index.js
npx wrangler d1 create resale                            # paste the id into wrangler.toml
npx wrangler d1 execute resale --file seed/tags.sql
npx wrangler kv namespace create TABLES
npx wrangler dev
npx wrangler deploy
```

## Routes

```mermaid
flowchart LR
    H[GET /health] --> H2[200 ok]
    N[GET /v1/net?platform=ebay&price=45&oz=12] --> N2[200 fees, shipping, net, margin]
    T[GET /v1/tag?text=Nutmeg+Mills&stitch=single] --> T2[200 era, maker, band, confidence]
```

## Module layout

```mermaid
classDiagram
    class index_js {
        +fetch(req, env)
        -authorized(req, env)
        -shipCost(oz)
        -json(obj, status)
        FEES
        USPS
    }
    class D1_resale {
        tags(keyword, maker, era, band_low, band_high, note)
        api_keys(key, calls_left, email)
    }
    class KV_TABLES {
        fees.json
        usps.json
    }
    index_js --> D1_resale : tag lookup, key check
    index_js --> KV_TABLES : fee and shipping tables (later)
```
