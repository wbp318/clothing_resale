# tools

| File | Runs where | Does |
|---|---|---|
| `inv.py` | Your PC, Python 3.8+, no deps | Inventory CLI over `inventory/inventory.csv` |
| `sync_ebay.py` | Your PC, scheduled every 30 min | Marks eBay orders sold via the Sell Fulfillment API |
| `gmail_sales_watcher.gs` | Google Apps Script, every 10 min | Parses sale emails from the no-API platforms, emails delist reminders |

## How they fit together

```mermaid
flowchart TD
    U[You] -->|add, listed, sold, ship, report| INV[inv.py]
    SY[sync_ebay.py] -->|imports| INV
    INV <--> CSV[(inventory/inventory.csv)]
    GS[gmail_sales_watcher.gs] --> SH[(Google Sheet<br/>inventory + sales_inbox)]
    CSV -.weekly import.-> SH
    SY --> CFG[tools/ebay_config.json<br/>git-ignored]
```

## inv.py command order

```mermaid
flowchart LR
    init --> add --> listed --> sold --> ship --> report
    list -.any time.-> report
```

## inv.py internals

```mermaid
classDiagram
    class inv_py {
        CSV_PATH
        FIELDS
        PLATFORMS
        +load() rows
        +save(rows)
        +add(args)
        +listed(sku, platforms)
        +sold(sku, platform, price, fees)
        +ship(sku, cost)
        +report()
    }
    class sync_ebay_py {
        CONFIG_PATH
        +get_token()
        +fetch_orders(days)
        +main(dry_run)
    }
    sync_ebay_py --> inv_py : calls sold()
```

Setup for `sync_ebay.py` and the Gmail script is in `docs/07-automation.md`.
