# 04 – Shipping with USPS

You have a USPS account. Use it for pickups and free Priority supplies, but **buy labels through the marketplace or a commercial-rate tool**, not retail Click-N-Ship. Commercial rates run 5–30% below retail.

## Which service

| Item | Service | Why |
|---|---|---|
| Tee, hat, dress, leggings (under 1 lb) | **USPS Ground Advantage** | Cheapest for light parcels, 2–5 days, $100 insurance included |
| Crewneck, jeans, jersey, light jacket (1–3 lb) | **Ground Advantage** | Still cheaper than Priority in almost every zone |
| Heavy jacket, boots, bundles (3 lb+) going far (zone 7–8) | **Priority Mail Flat Rate** (padded envelope or medium box) | Flat rate wins once weight and distance climb |
| Anything sold over $100 | Priority Mail + extra insurance | Faster, and buyers expect it |

Default: **Ground Advantage for everything**, check Priority Flat Rate only when heavy or cross-country.

## Where to buy labels

- **eBay, Depop, Poshmark, Whatnot, Mercari in-app labels** – discounted commercial rates, tracking auto-uploads. Use first. (Poshmark gives a prepaid Priority label the buyer pays for.)
- **Pirate Ship** (free, pirateship.com) – commercial Ground Advantage and Priority rates for off-platform sales. Link your USPS account for pickups.
- **Click-N-Ship (business account)** – backup, usually slightly pricier than Pirate Ship.

## Packaging

- **Poly mailers** (10x13 and 14.5x19), ~$0.10–$0.20 each in 100-packs.
- **Priority Mail Flat Rate padded envelopes and boxes** are free from USPS under your account. Only for Priority shipments; never use them for Ground Advantage.
- Fold tight, bag in a clear poly bag inside the mailer, add a thank-you card with your handles.
- **$20 kitchen scale.** Weigh every package, round up to the next ounce.

## Workflow

1. Sale comes in. Run the sale rule (delist elsewhere).
2. Weigh the packed item, buy the label in-app or on Pirate Ship.
3. Print on a thermal label printer (Rollo or Munbyn, ~$100–$150) or plain paper + tape.
4. Schedule a free **USPS Package Pickup** (usps.com/pickup) or drop at the counter.
5. Record cost: `python tools/inv.py ship CR-0042 6.40`.

## Pricing shipping into the sale

- Depop and Whatnot buyers expect low or free shipping. Bake ~$5 in and offer free shipping.
- eBay: free shipping on anything $40+ (ranks better). Under $40, calculated Ground Advantage.
- Poshmark: buyer pays the flat label, nothing to do.
- Ship within 1 business day. Handling time is a ranking factor.

Sources: [Ground Advantage vs Priority 2026](https://www.ship.com/post/usps-ground-advantage-vs-priority-mail-2026), [Shippo Ground Advantage guide](https://goshippo.com/blog/usps-parcel-select-ground-cost-sizes-and-how-it-works), [2026 rate changes](https://shippinglabel.co/blog/usps-ground-advantage-vs-priority-mail).
