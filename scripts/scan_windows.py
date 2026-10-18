"""Scan vs sell-in windows. Exploration only."""
import duckdb

con = duckdb.connect(
    "case-pack/fde-case-study/sales-analyst/data/warehouse.duckdb",
    read_only=True,
)
print("max scan week", con.execute("select max(week_start) from dealer_scans").fetchone())
print(con.execute("""
with bounds as (
  select date '2026-09-28' as as_of
),
dist as (
  select distributor_id, distributor_name from distributors
  where territory_code = 'IN-W01'
),
scans as (
  select dl.distributor_id,
    sum(case when s.week_start > date '2026-09-28' - 56
              and s.week_start <= date '2026-09-28' then s.packs_scanned else 0 end) recent,
    sum(case when s.week_start > date '2026-09-28' - 112
              and s.week_start <= date '2026-09-28' - 56 then s.packs_scanned else 0 end) prior_packs
  from dealer_scans s
  join dealers dl on dl.dealer_id = s.dealer_id
  group by 1
),
enrolled as (
  select distributor_id,
         count(*) dealers,
         sum(case when in_loyalty_program then 1 else 0 end) enrolled
  from dealers group by 1
)
select d.distributor_name,
       coalesce(e.enrolled,0) enrolled, coalesce(e.dealers,0) dealers,
       coalesce(sc.recent,0) recent_scans, coalesce(sc.prior_packs,0) prior_scans
from dist d
left join scans sc on sc.distributor_id = d.distributor_id
left join enrolled e on e.distributor_id = d.distributor_id
order by 1
""").df().to_string())
print("\ndealers columns", con.execute("describe dealers").df()["column_name"].tolist())
