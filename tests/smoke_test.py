"""Smoke test: runs every page headlessly and checks dashboard numbers against raw SQL.

Usage (from the project root, with your .env filled in):
    python tests/smoke_test.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest  # noqa: E402

from database import get_connection, run_query  # noqa: E402
from utils import queries as q  # noqa: E402

PAGES = ["1_Dashboard", "2_Customers", "3_Accounts", "4_Transactions", "5_Branches", "6_Reports"]
failures = 0

for name in PAGES:
    at = AppTest.from_file(str(ROOT / "pages" / f"{name}.py"), default_timeout=60).run()
    problems = [str(e.value) for e in at.exception] + [str(e.value) for e in at.error]
    if problems:
        failures += 1
        print(f"FAIL {name}: {problems}")
    else:
        print(f"ok   {name}")

# Cross-check: dashboard metrics must equal independent raw queries.
with get_connection() as conn:
    cur = conn.cursor()
    expected = {}
    for key, sql in {
        "customers": "SELECT COUNT(*) FROM customers",
        "accounts": "SELECT COUNT(*) FROM accounts",
        "transactions": "SELECT COUNT(*) FROM transactions",
        "branches": "SELECT COUNT(*) FROM branches",
        "employees": "SELECT COUNT(*) FROM employees",
        "total_balance": "SELECT SUM(balance) FROM accounts",
    }.items():
        cur.execute(sql)
        expected[key] = float(cur.fetchone()[0])
    cur.close()

m = q.overview_metrics().iloc[0]
for key, value in expected.items():
    if abs(float(m[key]) - value) > 0.001:
        failures += 1
        print(f"FAIL metric {key}: app={m[key]} sql={value}")
    else:
        print(f"ok   metric {key} = {value:,.0f}")

# Write protection: a non-SELECT must be refused before it reaches MySQL.
try:
    run_query("DELETE FROM accounts")
    failures += 1
    print("FAIL read-only guard did not block DELETE")
except ValueError:
    print("ok   read-only guard blocks DELETE")

print("\nAll checks passed." if not failures else f"\n{failures} check(s) failed.")
sys.exit(1 if failures else 0)
