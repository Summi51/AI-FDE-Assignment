"""Read-only access to the client warehouse extract."""
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "case-pack" / "fde-case-study" / "sales-analyst" / "data" / "warehouse.duckdb"

# Canonical territory lives on the distributor, not on the invoice line.
# Old CRM codes, missing dashes and lower case still appear on transactions.
CLEAN_ORDERS = """
select o.* exclude (territory_code),
       d.territory_code as territory_code,
       d.currency as billing_currency,
       o.territory_code as booked_territory_code
from (
  select * exclude (rn)
  from (
    select *, row_number() over (partition by line_id order by invoice_date desc) as rn
    from sell_in_orders
  )
  where rn = 1
) o
join distributors d on d.distributor_id = o.distributor_id
where o.quantity > 0
  and o.invoice_amount_local > 0
"""


def connect():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Warehouse extract not found at {DB_PATH}")
    return duckdb.connect(str(DB_PATH), read_only=True)


def freshness(con, region_code: str) -> dict:
    row = con.execute(
        """
        select max(max_business_date) as as_of
        from table_load_log
        where region = ?
          and table_name = 'sell_in_orders'
          and status = 'Success'
        """,
        [region_code],
    ).fetchone()
    aging = con.execute(
        """
        select max(max_business_date)
        from table_load_log
        where region = ?
          and table_name = 'receivables_aging'
          and status = 'Success'
        """,
        [region_code],
    ).fetchone()
    return {
        "orders_as_of": str(row[0])[:10] if row and row[0] else None,
        "aging_as_of": str(aging[0])[:10] if aging and aging[0] else None,
    }
