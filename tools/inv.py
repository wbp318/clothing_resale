#!/usr/bin/env python3
"""Minimal inventory tracker for cross-platform reselling.

Single source of truth: inventory/inventory.csv. No dependencies beyond the stdlib.

  python tools/inv.py init
  python tools/inv.py add --brand Starter --item "Bulls satin jacket" --cat mens --type jacket --size XL --cost 12 --price 85
  python tools/inv.py listed CR-0001 ebay depop        # record where it's listed
  python tools/inv.py list [--status listed]
  python tools/inv.py sold CR-0001 ebay 79.99 [--fees 11.20]
  python tools/inv.py ship CR-0001 6.40
  python tools/inv.py report
"""
import argparse
import csv
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "inventory", "inventory.csv")
FIELDS = [
    "sku", "date_added", "brand", "item", "category", "item_type", "size", "era", "condition",
    "cost", "list_price", "listed_on", "location", "status",
    "sold_platform", "sold_price", "sold_date", "fees", "shipping_cost", "notes",
]
PLATFORMS = {"ebay", "depop", "whatnot", "grailed", "mercari", "poshmark", "vinted", "instagram", "other"}
PREFIX = "CR"


def load():
    if not os.path.exists(CSV_PATH):
        sys.exit(f"No inventory file at {CSV_PATH}. Run: python tools/inv.py init")
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(rows):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def find(rows, sku):
    for r in rows:
        if r["sku"].upper() == sku.upper():
            return r
    sys.exit(f"SKU {sku} not found.")


def money(x):
    try:
        return float(x) if x not in ("", None) else 0.0
    except ValueError:
        return 0.0


def days_listed(r):
    return (date.today() - date.fromisoformat(r["date_added"])).days if r["date_added"] else 0


def cmd_init(_):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    if os.path.exists(CSV_PATH):
        print(f"Already exists: {CSV_PATH}")
        return
    save([])
    print(f"Created {CSV_PATH}")


def cmd_add(a):
    rows = load()
    nums = [int(r["sku"].split("-")[1]) for r in rows if r["sku"].startswith(PREFIX + "-")]
    sku = f"{PREFIX}-{(max(nums) + 1 if nums else 1):04d}"
    rows.append({
        "sku": sku, "date_added": date.today().isoformat(), "brand": a.brand, "item": a.item,
        "category": a.cat, "item_type": a.type, "size": a.size, "era": a.era, "condition": a.condition,
        "cost": f"{a.cost:.2f}", "list_price": f"{a.price:.2f}", "listed_on": "",
        "location": a.location, "status": "draft", "notes": a.notes,
    })
    save(rows)
    print(f"Added {sku}: {a.brand} {a.item} ({a.cat} {a.type} {a.size}) | cost ${a.cost:.2f} list ${a.price:.2f}")
    print("Write this SKU on the tag and in every listing.")


def cmd_listed(a):
    rows = load()
    r = find(rows, a.sku)
    bad = [p for p in a.platforms if p.lower() not in PLATFORMS]
    if bad:
        sys.exit(f"Unknown platform(s) {bad}. Use: {sorted(PLATFORMS)}")
    current = set(filter(None, r["listed_on"].split("|")))
    current |= {p.lower() for p in a.platforms}
    r["listed_on"] = "|".join(sorted(current))
    if r["status"] == "draft":
        r["status"] = "listed"
    save(rows)
    print(f"{r['sku']} listed on: {r['listed_on']}")


def cmd_list(a):
    rows = load()
    if a.status:
        rows = [r for r in rows if r["status"] == a.status]
    else:
        rows = [r for r in rows if r["status"] in ("draft", "listed")]
    print(f"{'SKU':8} {'Status':7} {'Brand':12} {'Item':22} {'Cat':6} {'Sz':4} {'Cost':>7} {'List':>7} {'Days':>4}  Listed on")
    for r in rows:
        d = days_listed(r)
        flag = " !" if d >= 60 and r["status"] == "listed" else ""
        print(f"{r['sku']:8} {r['status']:7} {r['brand'][:12]:12} {r['item'][:22]:22} {r['category'][:6]:6} "
              f"{r['size'][:4]:4} {money(r['cost']):7.2f} {money(r['list_price']):7.2f} {d:4}  {r['listed_on']}{flag}")
    print(f"\n{len(rows)} items. '!' = listed 60+ days: drop price or send to Whatnot.")


def cmd_sold(a):
    rows = load()
    r = find(rows, a.sku)
    if r["status"] == "sold":
        sys.exit(f"{r['sku']} already marked sold on {r['sold_platform']} {r['sold_date']}.")
    plat = a.platform.lower()
    r.update({"status": "sold", "sold_platform": plat, "sold_price": f"{a.price:.2f}",
              "sold_date": date.today().isoformat()})
    if a.fees is not None:
        r["fees"] = f"{a.fees:.2f}"
    save(rows)
    others = sorted(set(filter(None, r["listed_on"].split("|"))) - {plat})
    print(f"{r['sku']} SOLD on {plat} for ${a.price:.2f} (cost ${money(r['cost']):.2f}).")
    if others:
        print(f"*** DELIST NOW from: {', '.join(others).upper()} ***")
    else:
        print("Not listed anywhere else. Pack it.")


def cmd_ship(a):
    rows = load()
    r = find(rows, a.sku)
    r["shipping_cost"] = f"{a.cost:.2f}"
    save(rows)
    print(f"{r['sku']} shipping cost ${a.cost:.2f} recorded.")


def cmd_report(_):
    rows = load()
    sold = [r for r in rows if r["status"] == "sold"]
    active = [r for r in rows if r["status"] in ("draft", "listed")]
    inv_cost = sum(money(r["cost"]) for r in active)
    rev = sum(money(r["sold_price"]) for r in sold)
    cogs = sum(money(r["cost"]) for r in sold)
    fees = sum(money(r["fees"]) for r in sold)
    ship = sum(money(r["shipping_cost"]) for r in sold)
    profit = rev - cogs - fees - ship
    print(f"Active items:        {len(active):>5}   (cost tied up ${inv_cost:,.2f})")
    print(f"Sold items:          {len(sold):>5}")
    print(f"Revenue:             ${rev:>10,.2f}")
    print(f"Cost of goods sold:  ${cogs:>10,.2f}")
    print(f"Fees:                ${fees:>10,.2f}")
    print(f"Shipping:            ${ship:>10,.2f}")
    print(f"Net profit:          ${profit:>10,.2f}")
    if sold:
        print(f"Avg sale ${rev/len(sold):.2f}, avg profit/item ${profit/len(sold):.2f}")
        total = len(sold) + len(active)
        print(f"Sell-through: {len(sold)/total*100:.0f}%")
        by_plat = {}
        for r in sold:
            by_plat[r["sold_platform"]] = by_plat.get(r["sold_platform"], 0) + 1
        print("Sales by platform: " + ", ".join(f"{k} {v}" for k, v in sorted(by_plat.items(), key=lambda x: -x[1])))
        by_cat = {}
        for r in sold:
            by_cat[r["category"]] = by_cat.get(r["category"], 0) + money(r["sold_price"])
        print("Revenue by category: " + ", ".join(f"{k} ${v:.0f}" for k, v in sorted(by_cat.items(), key=lambda x: -x[1])))
        by_brand = {}
        for r in sold:
            by_brand[r["brand"]] = by_brand.get(r["brand"], 0) + money(r["sold_price"])
        top = sorted(by_brand.items(), key=lambda x: -x[1])[:5]
        print("Top brands by revenue: " + ", ".join(f"{k} ${v:.0f}" for k, v in top))
    stale = [r for r in active if r["status"] == "listed" and days_listed(r) >= 60]
    if stale:
        print(f"\n{len(stale)} items listed 60+ days: " + ", ".join(r["sku"] for r in stale))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    a = sub.add_parser("add")
    a.add_argument("--brand", required=True)
    a.add_argument("--item", required=True, help='short description, e.g. "Bulls satin jacket" or "floral midi dress"')
    a.add_argument("--cat", required=True, choices=["mens", "womens", "unisex", "kids"])
    a.add_argument("--type", required=True, help="tee, crewneck, hoodie, jacket, jersey, dress, jeans, hat, shoes, bag ...")
    a.add_argument("--size", required=True)
    a.add_argument("--cost", type=float, required=True)
    a.add_argument("--price", type=float, required=True)
    a.add_argument("--era", default="")
    a.add_argument("--condition", default="Very good")
    a.add_argument("--location", default="")
    a.add_argument("--notes", default="")
    a.set_defaults(fn=cmd_add)
    l = sub.add_parser("listed"); l.add_argument("sku"); l.add_argument("platforms", nargs="+"); l.set_defaults(fn=cmd_listed)
    ls = sub.add_parser("list"); ls.add_argument("--status"); ls.set_defaults(fn=cmd_list)
    s = sub.add_parser("sold"); s.add_argument("sku"); s.add_argument("platform"); s.add_argument("price", type=float)
    s.add_argument("--fees", type=float); s.set_defaults(fn=cmd_sold)
    sh = sub.add_parser("ship"); sh.add_argument("sku"); sh.add_argument("cost", type=float); sh.set_defaults(fn=cmd_ship)
    sub.add_parser("report").set_defaults(fn=cmd_report)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
