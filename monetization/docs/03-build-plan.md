# 03 – Build plan (30 days, free tier)

## Stack

| Layer | Pick | Cost |
|---|---|---|
| Compute | Cloudflare Workers (JavaScript) | Free to 100k req/day |
| Database | Cloudflare D1 (SQLite) for comps and tag DB | Free to 5 GB |
| Cache / tables | Cloudflare KV for fee and shipping tables | Free to 100k reads/day |
| Billing, agents | Monetization Gateway + x402 | Waitlist; cut unpublished |
| Billing, humans | API key + Stripe payment link, 1,000 calls for $5 | Stripe 2.9% + 30¢ |
| Docs | OpenAPI JSON served at `/openapi.json` | Free |
| Domain | something short, on Cloudflare registrar | ~$10/yr |

## Request flow inside the Worker

```mermaid
flowchart TD
    R[Incoming request] --> H{Path}
    H -->|/health, /openapi.json| F[Free, respond]
    H -->|/v1/*| K{Has valid API key<br/>or arrived via paid gateway?}
    K -->|no| E402[402 with price headers<br/>and a Stripe link for humans]
    K -->|yes| Q{Which product}
    Q -->|/v1/tag| T[Match tag rules in D1] --> J[JSON + usage log]
    Q -->|/v1/comps| C[Query comps table<br/>fallback: eBay Insights API, cache 24h] --> J
    Q -->|/v1/net| N[Fee + USPS table math from KV] --> J
    Q -->|/v1/title| G[Title formula] --> J
```

## Schedule

```mermaid
gantt
    title Monetization build, Oct–Nov 2026
    dateFormat  YYYY-MM-DD
    section Setup
    Cloudflare acct, domain, waitlist      :a1, 2026-10-20, 2d
    Worker skeleton + /health + openapi    :a2, after a1, 2d
    section Products
    /v1/net fee calculator                 :b1, after a2, 2d
    /v1/tag identifier (seed 60 tags)      :b2, after b1, 5d
    /v1/title generator                    :b3, after b2, 2d
    /v1/comps via eBay Insights + cache    :b4, after b3, 7d
    section Go live
    API keys + Stripe link                 :c1, after b2, 3d
    Post on RapidAPI, r/Flipping, X        :c2, after b4, 3d
    Flip gateway pricing on when invited   :milestone, c3, after c2, 0d
    section Later
    MCP server wrapper                     :d1, after c2, 5d
    Monthly dataset export                 :d2, after d1, 3d
```

## Day-by-day for week one

1. Create Cloudflare account, buy domain, join the Monetization Gateway waitlist, install `wrangler`.
2. `wrangler init` the Worker in `monetization/worker/`, deploy `/health`.
3. Load `docs/02` fee table and `docs/04` USPS table into KV. Ship `/v1/net`.
4. Seed D1 with the tag list from `docs/06`. Ship `/v1/tag` with exact and fuzzy match.
5. Add API-key check, usage log in D1, Stripe payment link for keys.
6. Write `/openapi.json` by hand. Post the free tier in r/Flipping and the Depop sellers Discord.
7. Rest. Log every tag from the first tee lot into D1 as you list them.

## Growing the data for free

Every item you list for the clothing business adds a row to the tag DB and, when it sells, a comp. The resale business feeds the API and the API feeds the resale business.

```mermaid
flowchart LR
    I[List an item<br/>tools/inv.py add] --> T[(tag DB row)]
    S[Item sells<br/>tools/inv.py sold] --> C[(comps row)]
    T & C --> API[/v1/tag and /v1/comps/]
    API --> M[Paid calls]
    API --> P[Better pricing for our own listings]
```
