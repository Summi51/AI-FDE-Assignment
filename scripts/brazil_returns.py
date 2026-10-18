"""Did dealer scans slow before the Brazil South returns? Exploration only."""
import duckdb

con = duckdb.connect(
    "case-pack/fde-case-study/sales-analyst/data/warehouse.duckdb",
    read_only=True,
)

def show(title, sql):
    print("\n====", title)
    print(con.execute(sql).df().to_string(max_rows=40))

show("returns by sub-region and month, late FY2026", """
select t.sub_region, date_trunc('month', r.return_date) m, sum(r.quantity) qty
from returns r
join distributors d on d.distributor_id = r.distributor_id
join territories t on t.territory_code = d.territory_code
where r.return_date >= date '2026-01-01'
group by 1, 2
order by qty desc
limit 12
""")

show("BR-S scans vs sell-in by month", """
with scans as (
  select date_trunc('month', week_start) m, sum(packs_scanned) packs
  from dealer_scans s
  join dealers dl on dl.dealer_id = s.dealer_id
  join distributors d on d.distributor_id = dl.distributor_id
  where d.territory_code like 'BR-S%'
  group by 1
),
sell as (
  select date_trunc('month', order_date) m, sum(quantity) qty
  from sell_in_orders o
  join distributors d on d.distributor_id = o.distributor_id
  where d.territory_code like 'BR-S%' and o.quantity > 0
  group by 1
)
select coalesce(sc.m, se.m) m, se.qty sell_in_qty, sc.packs scans
from sell se
full join scans sc on sc.m = se.m
where coalesce(sc.m, se.m) >= date '2025-06-01'
order by 1
""")
