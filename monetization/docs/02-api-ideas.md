# 02 – What we can sell behind the gateway

Ranked by: do we already have the data, is there an agent that would call it, and can it ship in a week.

| # | Product | Input | Output | Price per call | Data source we already have | Ship in |
|---|---|---|---|---|---|---|
| 1 | **Vintage tag identifier** | Tag text or photo OCR, stitch type, fabric blend | Era, maker, authenticity score, value band | $0.01 | `docs/06` tag list, grown with every item we log | 1 week |
| 2 | **Resale comps** | Brand, item, size, condition | 25th / 50th / 75th sold price, days-to-sell | $0.02 | eBay Marketplace Insights API + our `inventory.csv` sales | 2 weeks |
| 3 | **Net-profit calculator** | Platform, sale price, weight, zone | Fees, shipping, net, margin | $0.005 | `docs/02` fee table, `docs/04` USPS table | 3 days |
| 4 | **Listing title generator** | Brand, item, era, size, flaws | Platform-specific title and description with SKU line | $0.01 | `docs/08` title formula | 3 days |
| 5 | **Reseller datasets** | none | Monthly CSV: comps, tag DB, fee tables | $2.00 per download | Products 1–3 | After 1–3 |
| 6 | **MCP tool server** | tool calls | Same as 1–4 as agent tools | $0.01 per tool call | Products 1–4 | 1 week after 4 |
| 7 | **Louisiana thrift and estate-sale feed** | zip radius | Upcoming sales, store half-off days | $0.01 | Hand-curated to start | 2 weeks |
| 8 | **Paid pages, not APIs** | n/a | The book chapters and sell-fast playbook, charged per page crawl | $0.005 per page | `book/`, `docs/` | 1 day once gateway opens |

## Who pays

```mermaid
flowchart TD
    subgraph Buyers
        A[AI shopping agents<br/>is this jacket worth $80?]
        B[Reseller tools and crosslisters<br/>need comps and fee math]
        C[Indie developers<br/>building thrift apps]
        D[AI crawlers<br/>training on resale content]
    end
    A --> P1[Tag identifier] & P2[Comps]
    B --> P2 & P3[Net-profit calc] & P4[Title generator]
    C --> P5[Datasets] & P6[MCP server]
    D --> P8[Paid pages]
```

## Scoring

```mermaid
quadrantChart
    title Effort vs likely demand
    x-axis Low effort --> High effort
    y-axis Low demand --> High demand
    quadrant-1 Build second
    quadrant-2 Build first
    quadrant-3 Skip for now
    quadrant-4 Only if asked
    Tag identifier: [0.3, 0.8]
    Comps: [0.6, 0.9]
    Net-profit calc: [0.15, 0.5]
    Title generator: [0.2, 0.45]
    Datasets: [0.4, 0.4]
    MCP server: [0.5, 0.7]
    LA sale feed: [0.7, 0.25]
    Paid pages: [0.1, 0.3]
```

## Ideas we are not doing

- Scraping Depop, Poshmark, or eBay HTML for comps. Against their terms and the gateway's own rules.
- Anything that needs us to hold customer money or ship a physical good.
- Reselling other people's datasets.
