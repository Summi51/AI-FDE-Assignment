"""Numbers for the notes and deck. Exploration only."""
import duckdb

con = duckdb.connect(
    "case-pack/fde-case-study/sales-analyst/data/warehouse.duckdb",
    read_only=True,
)

def show(title, sql):
    print("\n====", title)
    try:
        print(con.execute(sql).df().to_string(max_rows=25))
    except Exception as exc:
        print("ERR", type(exc).__name__, exc)

show("old bot weekly users vs questions", """
select date_trunc('week', asked_at) wk,
       count(*) questions,
       count(distinct user_id) users,
       sum(case when status = 'Answered' then 1 else 0 end) answered
from old_bot_usage_log
group by 1
order by questions desc
limit 8
""")

show("old bot status and feedback", """
select status, count(*) n,
       round(avg(response_seconds),1) secs,
       sum(case when feedback = 'down' then 1 else 0 end) down
from old_bot_usage_log
group by 1
""")

show("languages that failed", """
select language_detected, status, count(*) n
from old_bot_usage_log
group by 1, 2
order by n desc
limit 12
""")

show("credit age, accrued still open", """
select count(*) credits,
       sum(amount_local) amount,
       currency,
       round(avg(date '2026-09-30' - accrual_date), 0) avg_days
from schemes_and_credits
where status = 'Accrued'
group by currency
order by amount desc
""")

show("vidarbha pending INR and days", """
select count(*) n, sum(amount_local) inr,
       min(accrual_date) oldest,
       date '2026-09-30' - min(accrual_date) oldest_days
from schemes_and_credits c
join distributors d on d.distributor_id = c.distributor_id
where d.territory_code = 'IN-W01' and c.status = 'Accrued'
""")

show("BR-South returns packs Feb-Apr 2026", """
select sum(r.quantity) packs, count(distinct r.distributor_id) distributors
from returns r
join distributors d on d.distributor_id = r.distributor_id
where d.territory_code like 'BR-S%'
  and r.return_date >= date '2026-02-01'
  and r.return_date < date '2026-05-01'
""")
