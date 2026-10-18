"""One-off warehouse profile. Not part of the prototype."""
import duckdb

DB = "case-pack/fde-case-study/sales-analyst/data/warehouse.duckdb"
con = duckdb.connect(DB, read_only=True)

def q(sql):
    print("\n>>", sql.strip().split("\n")[0][:90])
    try:
        df = con.execute(sql).df()
        print(df.to_string(max_rows=30, max_cols=12))
    except Exception as exc:
        print("ERR", exc)

q("show tables")
q("select * from territories where territory_code = 'IN-W01'")
q("""
select distributor_id, distributor_name, territory_code, currency, tier, credit_limit_local
from distributors where territory_code = 'IN-W01'
""")
q("select doc_type, count(*) n from sell_in_orders group by 1 order by n desc")
q("select count(*) rows, count(distinct line_id) ids from sell_in_orders")
q("""
select line_id, count(*) c
from sell_in_orders
group by 1
having count(*) > 1
order by c desc
limit 8
""")
q("""
select count(*) bad
from sell_in_orders s
where s.territory_code not in (select territory_code from territories)
""")
q("""
select territory_code, count(*) n
from sell_in_orders
where territory_code not in (select territory_code from territories)
group by 1
order by n desc
limit 12
""")
q("select status, count(*) n from schemes_and_credits group by 1")
q("""
select max(snapshot_date) from receivables_aging
""")
q("""
select region, table_name, status, max(max_business_date) latest
from table_load_log
group by 1, 2, 3
order by 1, 2
""")
