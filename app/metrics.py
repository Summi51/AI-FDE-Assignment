"""Named metrics. Never sum raw amounts across currencies."""

METRICS = {
    "M01": {
        "name": "Sales",
        "owner": "Sales Operations",
        "plain": "Gross sell-in after on-invoice discount. Returns are not deducted.",
        "currency": "Territory billing currency. No conversion.",
        "date_basis": "order_date",
    },
    "M08": {
        "name": "Overdue",
        "owner": "Finance",
        "plain": "Open invoice value past its due date, from the latest aging snapshot.",
        "currency": "Billing currency of the distributor.",
        "date_basis": "snapshot_date",
    },
    "pending_credit": {
        "name": "Pending scheme credit",
        "owner": "Finance (status = Accrued, not yet issued)",
        "plain": "Scheme credits accrued but not issued. Cancelled credits are excluded.",
        "currency": "Billing currency of the distributor.",
        "date_basis": "accrual_date",
    },
}
