"""Monday / visit brief for one distributor. Answers the field questions."""
from app.access import assert_distributor_in_scope, load_user
from app.metrics import METRICS
from app.warehouse import CLEAN_ORDERS, freshness


def stock_risk(con, distributor_id: str, as_of: str) -> dict:
    """Scan slowdown vs the distributor's own prior window. Not a cross-distributor compare."""
    row = con.execute(
        f"""
        with scans as (
          select
            sum(case when s.week_start > cast(? as date) - 56
                      and s.week_start <= cast(? as date)
                     then s.packs_scanned else 0 end) recent_packs,
            sum(case when s.week_start > cast(? as date) - 112
                      and s.week_start <= cast(? as date) - 56
                     then s.packs_scanned else 0 end) prior_packs
          from dealer_scans s
          join dealers dl on dl.dealer_id = s.dealer_id
          where dl.distributor_id = ?
        ),
        enrolled as (
          select count(*) dealers,
                 sum(case when in_loyalty_program then 1 else 0 end) enrolled
          from dealers
          where distributor_id = ?
        ),
        sell as (
          select sum(quantity) packs
          from ({CLEAN_ORDERS}) o
          where o.distributor_id = ?
            and o.order_date > cast(? as date) - 56
            and o.order_date <= cast(? as date)
        )
        select sc.recent_packs, sc.prior_packs, e.dealers, e.enrolled, se.packs
        from scans sc, enrolled e, sell se
        """,
        [as_of, as_of, as_of, as_of, distributor_id, distributor_id, distributor_id, as_of, as_of],
    ).fetchone()
    recent = float(row[0] or 0)
    prior = float(row[1] or 0)
    dealers = int(row[2] or 0)
    enrolled = int(row[3] or 0)
    sell_in = float(row[4] or 0)
    drop = None if prior < 200 else round((recent - prior) / prior, 3)
    if enrolled == 0:
        flag = "No scan coverage"
        line = "No enrolled dealers. Do not infer stock from scans."
    elif prior < 200:
        flag = "Too thin to call"
        line = "Prior 8 weeks of scans are too small to call a slowdown."
    elif drop is not None and drop <= -0.25 and sell_in > 0:
        flag = "Do not push"
        line = (
            f"Scans fell {abs(round(drop * 100))}% versus the prior 8 weeks, "
            f"while sell-in is still coming in. Do not load another truck."
        )
    else:
        flag = "Moving"
        line = "Scans are not down sharply against this distributor's own prior window."
    return {
        "flag": flag,
        "line": line,
        "recent_scans": recent,
        "prior_scans": prior,
        "scan_change": drop,
        "recent_sell_in_packs": sell_in,
        "enrolled_dealers": enrolled,
        "dealers": dealers,
        "coverage": f"{enrolled} of {dealers} dealers enrolled",
        "as_of": as_of,
        "rule": "Own history only. A 25% scan drop with continued sell-in. Not comparable across distributors.",
    }


def money(amount, currency: str) -> str:
    if amount is None:
        return f"— {currency}"
    return f"{currency} {amount:,.0f}"


def visit_brief(con, user_id: str, distributor_id: str) -> dict:
    user = load_user(con, user_id)
    dist = assert_distributor_in_scope(con, user, distributor_id)
    fresh = freshness(con, dist["region_code"])

    credits = con.execute(
        """
        select credit_id, scheme_name, scheme_type, status,
               accrual_date, issue_date, amount_local, currency
        from schemes_and_credits
        where distributor_id = ?
          and status = 'Accrued'
        order by accrual_date
        """,
        [distributor_id],
    ).df()

    aging = con.execute(
        """
        select snapshot_date, total_outstanding_local, not_due_local,
               overdue_1_30_local, overdue_31_60_local, overdue_61_90_local,
               overdue_90_plus_local, disputed_local, currency
        from receivables_aging
        where distributor_id = ?
        order by snapshot_date desc
        limit 1
        """,
        [distributor_id],
    ).fetchone()

    sales = con.execute(
        f"""
        with orders as ({CLEAN_ORDERS})
        select
          sum(case when order_date >= date '2025-10-01'
                    and order_date < date '2026-10-01'
                   then invoice_amount_local else 0 end) fy26,
          sum(case when order_date >= date '2024-10-01' and order_date < date '2025-10-01'
                   then invoice_amount_local else 0 end) fy25
        from orders
        where distributor_id = ?
        """,
        [distributor_id],
    ).fetchone()

    pending = float(credits["amount_local"].sum()) if len(credits) else 0.0
    overdue = 0.0
    disputed = 0.0
    outstanding = 0.0
    snapshot = None
    if aging:
        snapshot = str(aging[0])[:10]
        outstanding = float(aging[1] or 0)
        overdue = float((aging[3] or 0) + (aging[4] or 0) + (aging[5] or 0) + (aging[6] or 0))
        disputed = float(aging[7] or 0)

    net_ask = max(overdue - pending, 0)
    held_by_credits = min(overdue, pending)
    currency = dist["currency"]
    fy26 = float(sales[0] or 0)
    fy25 = float(sales[1] or 0)

    lines = []
    for row in credits.to_dict("records"):
        lines.append({
            "credit_id": row["credit_id"],
            "scheme": row["scheme_name"],
            "type": row["scheme_type"],
            "accrued": str(row["accrual_date"])[:10],
            "amount": money(row["amount_local"], currency),
            "amount_local": float(row["amount_local"]),
            "status": "Accrued — credit note not issued",
        })

    return {
        "user": user,
        "distributor": dist,
        "freshness": fresh,
        "metrics_used": [METRICS["pending_credit"], METRICS["M08"], METRICS["M01"]],
        "pending_credits": lines,
        "pending_total": money(pending, currency),
        "pending_total_local": pending,
        "aging_snapshot": snapshot,
        "outstanding": money(outstanding, currency),
        "overdue": money(overdue, currency),
        "overdue_local": overdue,
        "disputed": money(disputed, currency),
        "held_by_unissued_credits": money(held_by_credits, currency),
        "collect_after_credits": money(net_ask, currency),
        "fy26_sales": money(fy26, currency),
        "fy25_sales": money(fy25, currency),
        "fy26_vs_fy25": None if fy25 == 0 else round((fy26 - fy25) / fy25, 3),
        "stock": stock_risk(con, distributor_id, fresh["orders_as_of"]),
        "talking_point": _talking_point(dist["name"], pending, overdue, disputed, currency),
    }


def _talking_point(name, pending, overdue, disputed, currency) -> str:
    if pending <= 0 and overdue <= 0:
        return f"{name} has no pending credits and no overdue. Collect on normal terms."
    if pending > 0 and disputed > 0:
        return (
            f"Do not open with 'why have you not paid'. {name} is holding "
            f"{money(disputed, currency)} as disputed against unissued credits. "
            f"Pending credits total {money(pending, currency)}. "
            f"Ask scheme desk to issue the notes, then collect the rest."
        )
    if pending > 0:
        return (
            f"{name} is waiting on {money(pending, currency)} of accrued credits "
            f"that have not been issued. Raise those before pushing payment."
        )
    return f"{name} is overdue {money(overdue, currency)} with no pending credit offset."



def monday_list(con, user_id: str) -> dict:
    """Distributors to raise on the Monday call, worst credit-hold first."""
    from app.access import AccessDenied

    user = load_user(con, user_id)
    if user["role"] != "Territory Manager" or not user["territory_code"]:
        raise AccessDenied("Monday list is for a territory manager")
    territory = user["territory_code"]
    region = con.execute(
        "select region_code from territories where territory_code = ?",
        [territory],
    ).fetchone()[0]
    rows = con.execute(
        """
        with pending as (
          select distributor_id,
                 sum(amount_local) pending,
                 count(*) n,
                 min(accrual_date) oldest
          from schemes_and_credits
          where status = 'Accrued'
          group by 1
        ),
        aging as (
          select a.*
          from receivables_aging a
          join distributors d on d.distributor_id = a.distributor_id
          where d.territory_code = ?
            and a.snapshot_date = (
              select max(a2.snapshot_date)
              from receivables_aging a2
              join distributors d2 on d2.distributor_id = a2.distributor_id
              where d2.territory_code = ?
            )
        )
        select d.distributor_id, d.distributor_name, d.currency,
               coalesce(p.pending, 0), coalesce(p.n, 0), p.oldest,
               coalesce(a.disputed_local, 0),
               coalesce(a.overdue_1_30_local, 0) + coalesce(a.overdue_31_60_local, 0)
                 + coalesce(a.overdue_61_90_local, 0) + coalesce(a.overdue_90_plus_local, 0)
        from distributors d
        left join pending p on p.distributor_id = d.distributor_id
        left join aging a on a.distributor_id = d.distributor_id
        where d.territory_code = ?
        """,
        [territory, territory, territory],
    ).fetchall()

    items = []
    for row in rows:
        pending, disputed, overdue = float(row[3]), float(row[6]), float(row[7])
        if disputed > 0 and pending > 0:
            action, rank = "Raise credits before collection", 0
        elif pending > 0:
            action, rank = "Credits waiting, not yet a dispute", 1
        elif overdue > 0:
            action, rank = "Collect. No credit offset", 2
        else:
            action, rank = "No Monday action", 3
        items.append({
            "distributor_id": row[0],
            "name": row[1],
            "currency": row[2],
            "pending": money(pending, row[2]),
            "pending_local": pending,
            "credit_count": int(row[4]),
            "oldest_accrual": str(row[5])[:10] if row[5] else None,
            "disputed": money(disputed, row[2]),
            "overdue": money(overdue, row[2]),
            "action": action,
            "rank": rank,
        })
    items.sort(key=lambda i: (i["rank"], -i["pending_local"]))
    return {
        "user": user,
        "territory_code": territory,
        "freshness": freshness(con, region),
        "call_first": [i for i in items if i["rank"] < 3],
        "quiet": [i for i in items if i["rank"] == 3],
    }
