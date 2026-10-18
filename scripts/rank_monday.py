"""Compare ranking signals for the Monday list. Exploration only."""
import duckdb

con = duckdb.connect(
    "case-pack/fde-case-study/sales-analyst/data/warehouse.duckdb",
    read_only=True,
)
print(con.execute("""
with pending as (
  select distributor_id, sum(amount_local) pending, min(accrual_date) oldest
  from schemes_and_credits where status = 'Accrued'
  group by 1
),
aging as (
  select * from receivables_aging
  where snapshot_date = (select max(snapshot_date) from receivables_aging)
)
select d.distributor_name,
       coalesce(p.pending, 0) pending,
       coalesce(a.disputed_local, 0) disputed,
       coalesce(a.overdue_1_30_local,0)+coalesce(a.overdue_31_60_local,0)
         +coalesce(a.overdue_61_90_local,0)+coalesce(a.overdue_90_plus_local,0) overdue,
       p.oldest
from distributors d
left join pending p on p.distributor_id = d.distributor_id
left join aging a on a.distributor_id = d.distributor_id
where d.territory_code = 'IN-W01'
order by coalesce(p.pending, 0) desc
""").df().to_string())
