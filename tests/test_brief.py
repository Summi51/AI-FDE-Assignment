import unittest
from app.access import AccessDenied
from app.brief import monday_list, visit_brief
from app.warehouse import connect


class VisitBriefTests(unittest.TestCase):
    def setUp(self):
        self.con = connect()

    def tearDown(self):
        self.con.close()

    def test_vidarbha_manager_sees_malana_credits(self):
        brief = visit_brief(self.con, "U042", "D1101")
        self.assertEqual(brief["distributor"]["territory_code"], "IN-W01")
        self.assertGreater(brief["pending_total_local"], 9_000_000)
        self.assertIn("INR", brief["pending_total"])
        self.assertIn("Do not open with", brief["talking_point"])
        self.assertTrue(all("USD" not in c["amount"] for c in brief["pending_credits"]))
        names = [m["name"] for m in brief["metrics_used"]]
        self.assertIn("Sales", names)
        self.assertIn("Pending scheme credit", names)

    def test_territory_manager_cannot_see_another_territory(self):
        other = self.con.execute(
            """
            select distributor_id from distributors
            where territory_code <> 'IN-W01'
            limit 1
            """
        ).fetchone()[0]
        with self.assertRaises(AccessDenied):
            visit_brief(self.con, "U042", other)

    def test_sales_is_local_currency_not_a_global_sum(self):
        brief = visit_brief(self.con, "U042", "D1098")
        self.assertIn("INR", brief["fy26_sales"])
        self.assertNotIn("USD", brief["fy26_sales"])
        self.assertGreater(brief["fy26_vs_fy25"], -1)

    def test_cancelled_credits_are_excluded(self):
        brief = visit_brief(self.con, "U042", "D1102")
        self.assertEqual(brief["pending_total_local"], 0)
        self.assertEqual(brief["pending_credits"], [])

    def test_monday_list_puts_disputed_credits_first(self):
        monday = monday_list(self.con, "U042")
        first = [i["distributor_id"] for i in monday["call_first"]]
        self.assertEqual(first[0], "D1101")
        self.assertEqual(first[1], "D1098")
        self.assertEqual(monday["quiet"][0]["distributor_id"], "D1102")
        self.assertEqual([i["rank"] for i in monday["call_first"][:3]], [0, 0, 0])

    def test_malana_scan_drop_blocks_another_truck(self):
        brief = visit_brief(self.con, "U042", "D1101")
        self.assertEqual(brief["stock"]["flag"], "Do not push")
        self.assertLess(brief["stock"]["scan_change"], -0.25)
        self.assertIn("2 of 8", brief["stock"]["coverage"])

    def test_no_coverage_is_not_called_a_slowdown(self):
        brief = visit_brief(self.con, "U042", "D1102")
        self.assertEqual(brief["stock"]["flag"], "No scan coverage")
        self.assertIsNone(brief["stock"]["scan_change"])

    def test_regional_manager_cannot_open_another_sub_region(self):
        with self.assertRaises(AccessDenied):
            visit_brief(self.con, "U008", "D1101")

    def test_unknown_user_is_denied(self):
        with self.assertRaises(AccessDenied):
            visit_brief(self.con, "U999", "D1101")

    def test_stock_sell_in_uses_deduped_orders(self):
        brief = visit_brief(self.con, "U042", "D1101")
        as_of = brief["freshness"]["orders_as_of"]
        from app.warehouse import CLEAN_ORDERS
        clean = self.con.execute(
            f"""
            select sum(quantity)
            from ({CLEAN_ORDERS}) o
            where distributor_id = 'D1101'
              and order_date > cast(? as date) - 56
              and order_date <= cast(? as date)
            """,
            [as_of, as_of],
        ).fetchone()[0]
        self.assertEqual(brief["stock"]["recent_sell_in_packs"], float(clean or 0))

    def test_fy26_does_not_include_the_next_year(self):
        brief = visit_brief(self.con, "U042", "D1101")
        self.assertIn("INR", brief["fy26_sales"])
        self.assertNotIn("USD", brief["fy26_sales"])


if __name__ == "__main__":
    unittest.main()
