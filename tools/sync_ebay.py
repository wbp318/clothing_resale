#!/usr/bin/env python3
"""Pull recent eBay orders and mark matching SKUs sold in inventory/inventory.csv.

Uses the eBay Sell Fulfillment API (official). Needs a one-time setup, see docs/07-automation.md.
Set these in tools/ebay_config.json (git-ignored):
  {"client_id": "...", "client_secret": "...", "refresh_token": "...", "lookback_days": 7}

Run manually or on a schedule:
  python tools/sync_ebay.py           # sync
  python tools/sync_ebay.py --dry-run # show what would change

Match rule: the eBay listing's "Custom label (SKU)" field must equal the tracker SKU (e.g. CR-0042).
Orders with no matching SKU are listed as "unmatched" so you can fix them by hand.
"""
import argparse
import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv  # noqa: E402

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ebay_config.json")
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
ORDERS_URL = "https://api.ebay.com/sell/fulfillment/v1/order"
SCOPE = "https://api.ebay.com/oauth/api_scope/sell.fulfillment"


def load_config():
    if not os.path.exists(CONFIG_PATH):
        sys.exit(f"Missing {CONFIG_PATH}. See docs/07-automation.md for setup.")
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def access_token(cfg):
    creds = base64.b64encode(f"{cfg['client_id']}:{cfg['client_secret']}".encode()).decode()
    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": cfg["refresh_token"],
        "scope": SCOPE,
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=body, headers={
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/x-www-form-urlencoded",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["access_token"]


def fetch_orders(token, lookback_days):
    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    orders, offset, limit = [], 0, 50
    while True:
        q = urllib.parse.urlencode({
            "filter": f"creationdate:[{since}..]",
            "limit": limit, "offset": offset,
        })
        req = urllib.request.Request(f"{ORDERS_URL}?{q}", headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        orders.extend(data.get("orders", []))
        if offset + limit >= data.get("total", 0):
            return orders
        offset += limit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    token = access_token(cfg)
    orders = fetch_orders(token, cfg.get("lookback_days", 7))
    rows = inv.load()
    by_sku = {r["sku"].upper(): r for r in rows}

    changed, unmatched, already = [], [], []
    for o in orders:
        if o.get("orderFulfillmentStatus") == "CANCELLED" or o.get("cancelStatus", {}).get("cancelState") == "CANCELED":
            continue
        for li in o.get("lineItems", []):
            sku = (li.get("sku") or "").strip().upper()
            title = li.get("title", "")
            price = float(li.get("lineItemCost", {}).get("value", 0))
            r = by_sku.get(sku)
            if not r:
                unmatched.append(f"  order {o['orderId']}: '{title}' (sku field: '{sku or 'none'}') ${price:.2f}")
                continue
            if r["status"] == "sold":
                already.append(r["sku"])
                continue
            fees = li.get("totalMarketplaceFee", {}).get("value")
            r.update({
                "status": "sold", "sold_platform": "ebay", "sold_price": f"{price:.2f}",
                "sold_date": o["creationDate"][:10],
            })
            if fees is not None:
                r["fees"] = f"{float(fees):.2f}"
            others = sorted(set(filter(None, r["listed_on"].split("|"))) - {"ebay"})
            changed.append((r["sku"], title, price, others))

    if changed and not args.dry_run:
        inv.save(rows)

    print(f"eBay orders checked: {len(orders)}  |  newly marked sold: {len(changed)}  |  already sold: {len(already)}")
    for sku, title, price, others in changed:
        line = f"  {sku} ${price:.2f}  {title[:50]}"
        if others:
            line += f"   *** DELIST from {', '.join(others).upper()} ***"
        print(line)
    if unmatched:
        print("Unmatched line items (add the SKU to the eBay custom label field, or mark sold by hand):")
        print("\n".join(unmatched))
    if args.dry_run and changed:
        print("(dry run, nothing written)")


if __name__ == "__main__":
    main()
