# inventory

`inventory.csv` is the single source of truth for every item. Never edit `sku` or `status` by hand; use `tools/inv.py`. Everything else can be edited in Excel or Sheets.

## Columns

```mermaid
erDiagram
    ITEM {
        string sku PK "CR-0001"
        date date_added
        string brand
        string item
        string category "mens | womens | unisex | kids"
        string item_type
        string size
        string era
        string condition "NWT | Excellent | Very good | Good | Fair"
        float cost "paid incl. share of lot shipping"
        float list_price
        string listed_on "ebay|depop|vinted"
        string location "bin number"
        string status "draft | listed | sold | returned | donated"
        string sold_platform
        float sold_price
        date sold_date
        float fees
        float shipping_cost
        string notes
    }
```

## Who writes to it

```mermaid
flowchart LR
    Y[You via inv.py] --> CSV[(inventory.csv)]
    E[sync_ebay.py] --> CSV
    CSV --> R[inv.py report<br/>revenue, COGS, fees, profit]
    CSV -.-> G[Google Sheet copy<br/>for the Gmail watcher]
```

`sync.log` is written by the scheduled eBay sync and is git-ignored.
