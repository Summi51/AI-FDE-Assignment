"""Visit-brief numbers for Vidarbha (IN-W01). Exploration only."""
import duckdb

con = duckdb.connect(
    "case-pack/fde-case-study/sales-analyst/data/warehouse.duckdb",
    read_only=True,
)

def show(title, sql):
    print("\n====", title)
    print(con.execute(sql).df().to_string(max_rows=40))

show("users in IN-W01", """
select user_id, role, primary_language, territory_code
from users_and_roles
where territory_code = 'IN-W01'
""")

show("pending credits by distributor", """
select d.distributor_id, d.distributor_name,
       count(*) credits,
       sum(c.amount_local) pending_inr,
       min(c.accrual_date) oldest_accrual
from schemes_and_credits c
join distributors d on d.distributor_id = c.distributor_id
where d.territory_code = 'IN-W01'
  and c.status = 'Accrued'
group by 1, 2
order by pending_inr desc
""")

show("latest aging vs pending credits", """
with latest as (
  select * from receivables_aging
  where snapshot_date = (select max(snapshot_date) from receivables_aging)
),
pending as (
  select distributor_id, sum(amount_local) pending
  from schemes_and_credits
  where status = 'Accrued'
  group by 1
)
select d.distributor_name,
       a.total_outstanding_local outstanding,
       a.overdue_1_30_local + a.overdue_31_60_local
         + a.overdue_61_90_local + a.overdue_90_plus_local as overdue,
       a.disputed_local,
       coalesce(p.pending, 0) pending_credit,
       a.currency
from distributors d
left join latest a on a.distributor_id = d.distributor_id
left join pending p on p.distributor_id = d.distributor_id
where d.territory_code = 'IN-W01'
order by overdue desc nulls last
""")

show("fy2026 vs fy2025 gross sell-in INR", """
select d.distributor_name,
  sum(case when o.order_date >= date '2025-10-01' and o.quantity > 0
           then o.invoice_amount_local else 0 end) fy26,
  sum(case when o.order_date >= date '2024-10-01' and o.order_date < date '2025-10-01'
           and o.quantity > 0
           then o.invoice_amount_local else 0 end) fy25
from distributors d
left join sell_in_orders o on o.distributor_id = d.distributor_id
where d.territory_code = 'IN-W01'
group by 1
order by fy26 desc
""")
