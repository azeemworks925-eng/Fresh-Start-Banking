"""All SQL used by the app, in one place.

Notes on the schema (see sql/schema_documentation.md):
  * `transactions` has no status column and no debit/credit flag, so direction is derived
    from `transaction_type`.
  * Accounts and customers are NOT linked to a branch, so branch statistics only use
    what the schema really supports: employees, ATMs and ATM withdrawals.
"""
from database import run_query

# Direction is inferred from the transaction type (documented assumption).
CREDIT_TYPES = ("Cash Deposit", "Cheque Deposit", "Profit Deposit")
DIRECTION_SQL = (
    "CASE WHEN t.transaction_type IN ('Cash Deposit','Cheque Deposit','Profit Deposit') "
    "THEN 'Credit' ELSE 'Debit' END"
)


def _in_clause(values) -> str:
    """Build '%s,%s,%s' placeholders for a parameterised IN (...) list."""
    return ",".join(["%s"] * len(values))


# ------------------------------------------------------------------ Dashboard
def overview_metrics():
    return run_query(
        """
        SELECT
          (SELECT COUNT(*)               FROM customers)    AS customers,
          (SELECT COUNT(*)               FROM accounts)     AS accounts,
          (SELECT COALESCE(SUM(balance),0) FROM accounts)   AS total_balance,
          (SELECT COUNT(*)               FROM transactions) AS transactions,
          (SELECT COUNT(*)               FROM branches)     AS branches,
          (SELECT COUNT(*)               FROM employees)    AS employees
        """
    )


def accounts_by_type():
    return run_query(
        """
        SELECT at.type_name AS account_type,
               COUNT(a.account_id)          AS accounts,
               COALESCE(SUM(a.balance), 0)  AS total_balance,
               COALESCE(AVG(a.balance), 0)  AS avg_balance
        FROM account_types at
        LEFT JOIN accounts a ON a.account_type_id = at.account_type_id
        GROUP BY at.account_type_id, at.type_name
        ORDER BY at.account_type_id
        """
    )


def monthly_activity():
    return run_query(
        """
        SELECT DATE_FORMAT(t.date, '%Y-%m') AS month,
               COUNT(*)      AS transactions,
               SUM(t.amount) AS volume
        FROM transactions t
        GROUP BY DATE_FORMAT(t.date, '%Y-%m')
        ORDER BY month
        """
    )


def recent_transactions(limit: int = 8):
    return run_query(
        f"""
        SELECT t.transaction_id, t.date, c.name AS customer, t.account_id,
               t.transaction_type, {DIRECTION_SQL} AS direction, t.amount
        FROM transactions t
        JOIN accounts  a ON a.account_id  = t.account_id
        JOIN customers c ON c.customer_id = a.customer_id
        ORDER BY t.date DESC, t.transaction_id DESC
        LIMIT %s
        """,
        (limit,),
    )


def customers_by_account_count():
    return run_query(
        """
        SELECT n_accounts, COUNT(*) AS customers FROM (
            SELECT c.customer_id, COUNT(a.account_id) AS n_accounts
            FROM customers c LEFT JOIN accounts a ON a.customer_id = c.customer_id
            GROUP BY c.customer_id
        ) x
        GROUP BY n_accounts ORDER BY n_accounts
        """
    )


# ------------------------------------------------------------------ Customers
def customers(search: str = ""):
    """Search by name (partial, case-insensitive) or by exact customer ID."""
    like = f"%{search.strip()}%"
    cid = int(search) if search.strip().isdigit() else -1
    return run_query(
        """
        SELECT c.customer_id, c.name, c.cnic, c.phone, c.email, c.address,
               COUNT(a.account_id)         AS accounts,
               COALESCE(SUM(a.balance), 0) AS total_balance
        FROM customers c
        LEFT JOIN accounts a ON a.customer_id = c.customer_id
        WHERE (%s = '' OR c.name LIKE %s OR c.customer_id = %s)
        GROUP BY c.customer_id, c.cnic, c.name, c.phone, c.email, c.address
        ORDER BY c.customer_id
        """,
        (search.strip(), like, cid),
    )


def customer_accounts(customer_id: int):
    return run_query(ACCOUNT_DETAIL_SQL + " WHERE a.customer_id = %s ORDER BY a.account_id", (customer_id,))


def customer_loans(customer_id: int):
    return run_query(
        """
        SELECT loan_id, loan_type, account_id, amount, balance, start_date, end_date, status
        FROM loans WHERE customer_id = %s ORDER BY loan_id
        """,
        (customer_id,),
    )


def customer_cards(customer_id: int):
    # card_number is selected only so the UI can mask it; it is never displayed in full.
    return run_query(
        """
        SELECT k.card_id, k.account_id, k.card_type, k.card_number, k.issue_date, k.expiry_date
        FROM cards k JOIN accounts a ON a.account_id = k.account_id
        WHERE a.customer_id = %s ORDER BY k.card_id
        """,
        (customer_id,),
    )


# ------------------------------------------------------------------ Accounts
# One row per account, joined to whichever subtype table applies (class-table inheritance).
ACCOUNT_DETAIL_SQL = """
    SELECT a.account_id, a.customer_id, c.name AS holder, at.type_name AS account_type,
           a.balance, a.open_date,
           s.interest_rate, s.minimum_balance,
           ca.overdraft_limit, ca.overdraft_rate,
           i.mudarabah_rate, i.investment_allocation
    FROM accounts a
    JOIN customers     c  ON c.customer_id      = a.customer_id
    JOIN account_types at ON at.account_type_id = a.account_type_id
    LEFT JOIN savings_account s  ON s.account_id  = a.account_id
    LEFT JOIN current_account ca ON ca.account_id = a.account_id
    LEFT JOIN islamic_account i  ON i.account_id  = a.account_id
"""


def account_types():
    return run_query("SELECT account_type_id, type_name, description FROM account_types ORDER BY account_type_id")


def accounts(search: str = "", type_names=()):
    like = f"%{search.strip()}%"
    aid = int(search) if search.strip().isdigit() else -1
    sql = ACCOUNT_DETAIL_SQL + " WHERE (%s = '' OR c.name LIKE %s OR a.account_id = %s OR a.customer_id = %s)"
    params = [search.strip(), like, aid, aid]
    if type_names:
        sql += f" AND at.type_name IN ({_in_clause(type_names)})"
        params += list(type_names)
    sql += " ORDER BY a.account_id"
    return run_query(sql, tuple(params))


# ------------------------------------------------------------------ Transactions
def transaction_types():
    return run_query("SELECT DISTINCT transaction_type FROM transactions ORDER BY transaction_type")["transaction_type"].tolist()


def transaction_date_range():
    return run_query("SELECT MIN(DATE(date)) AS first_day, MAX(DATE(date)) AS last_day FROM transactions")


def transactions(search="", types=(), account_id=None, start=None, end=None):
    sql = f"""
        SELECT t.transaction_id, t.date, t.account_id, c.name AS customer,
               t.transaction_type, {DIRECTION_SQL} AS direction, t.amount,
               t.description, t.atm_id, atm.location AS atm_location, b.branch_name AS atm_branch,
               bt.beneficiary_name
        FROM transactions t
        JOIN accounts  a ON a.account_id  = t.account_id
        JOIN customers c ON c.customer_id = a.customer_id
        LEFT JOIN atms atm     ON atm.atm_id    = t.atm_id
        LEFT JOIN branches b   ON b.branch_id   = atm.branch_id
        LEFT JOIN beneficiary_transactions bt ON bt.transaction_id = t.transaction_id
        WHERE 1 = 1
    """
    params: list = []
    if str(search).strip().isdigit():
        sql += " AND t.transaction_id = %s"
        params.append(int(search))
    elif str(search).strip():
        sql += " AND (t.description LIKE %s OR c.name LIKE %s)"
        params += [f"%{search.strip()}%"] * 2
    if types:
        sql += f" AND t.transaction_type IN ({_in_clause(types)})"
        params += list(types)
    if account_id:
        sql += " AND t.account_id = %s"
        params.append(int(account_id))
    if start:
        sql += " AND DATE(t.date) >= %s"
        params.append(start)
    if end:
        sql += " AND DATE(t.date) <= %s"
        params.append(end)
    sql += " ORDER BY t.date DESC, t.transaction_id DESC"
    return run_query(sql, tuple(params))


# ------------------------------------------------------------------ Branches
def branch_summary():
    return run_query(
        """
        SELECT b.branch_id, b.branch_name, b.city, b.address, b.phone,
               (SELECT COUNT(*) FROM employees e WHERE e.branch_id = b.branch_id) AS employees,
               (SELECT COUNT(*) FROM atms m      WHERE m.branch_id = b.branch_id) AS atms,
               (SELECT COUNT(*) FROM transactions t JOIN atms m ON m.atm_id = t.atm_id
                 WHERE m.branch_id = b.branch_id) AS atm_transactions,
               (SELECT COALESCE(SUM(t.amount),0) FROM transactions t JOIN atms m ON m.atm_id = t.atm_id
                 WHERE m.branch_id = b.branch_id) AS atm_volume
        FROM branches b ORDER BY b.branch_id
        """
    )


def employees():
    return run_query(
        """
        SELECT e.employee_id, e.name, e.designation, b.branch_name,
               CASE WHEN m.employee_id  IS NOT NULL THEN 'Manager'
                    WHEN ca.employee_id IS NOT NULL THEN 'Cashier'
                    WHEN r.employee_id  IS NOT NULL THEN 'CSR'
                    ELSE 'Unassigned' END AS role_type,
               COALESCE(m.managed_department, ca.register_id, r.csr_specialization) AS role_detail
        FROM employees e
        JOIN branches b ON b.branch_id = e.branch_id
        LEFT JOIN manager m ON m.employee_id  = e.employee_id
        LEFT JOIN cashier ca ON ca.employee_id = e.employee_id
        LEFT JOIN csr r      ON r.employee_id  = e.employee_id
        ORDER BY e.branch_id, e.employee_id
        """
    )


def atms():
    return run_query(
        """
        SELECT m.atm_id, m.location, b.branch_name, m.status,
               COUNT(t.transaction_id) AS transactions
        FROM atms m JOIN branches b ON b.branch_id = m.branch_id
        LEFT JOIN transactions t ON t.atm_id = m.atm_id
        GROUP BY m.atm_id, m.location, b.branch_name, m.status
        ORDER BY m.atm_id
        """
    )


# ------------------------------------------------------------------ Reports
def balance_bands():
    return run_query(
        """
        SELECT band, COUNT(*) AS accounts, SUM(balance) AS total_balance FROM (
            SELECT balance,
                   CASE WHEN balance <   50000 THEN '1. Under 50K'
                        WHEN balance <  250000 THEN '2. 50K - 250K'
                        WHEN balance < 1000000 THEN '3. 250K - 1M'
                        ELSE '4. Over 1M' END AS band
            FROM accounts) x
        GROUP BY band ORDER BY band
        """
    )


def top_accounts(limit: int = 5):
    return run_query(
        """
        SELECT a.account_id, c.name AS holder, at.type_name AS account_type, a.balance
        FROM accounts a
        JOIN customers c ON c.customer_id = a.customer_id
        JOIN account_types at ON at.account_type_id = a.account_type_id
        ORDER BY a.balance DESC LIMIT %s
        """,
        (limit,),
    )


def multi_account_customers():
    return run_query(
        """
        SELECT c.customer_id, c.name, COUNT(a.account_id) AS accounts,
               SUM(a.balance) AS total_balance,
               GROUP_CONCAT(at.type_name ORDER BY a.account_id SEPARATOR ', ') AS account_types
        FROM customers c
        JOIN accounts a ON a.customer_id = c.customer_id
        JOIN account_types at ON at.account_type_id = a.account_type_id
        GROUP BY c.customer_id, c.name
        HAVING COUNT(a.account_id) > 1
        ORDER BY total_balance DESC
        """
    )


def transaction_summary():
    return run_query(
        f"""
        SELECT t.transaction_type, {DIRECTION_SQL} AS direction,
               COUNT(*) AS transactions, SUM(t.amount) AS volume, ROUND(AVG(t.amount), 0) AS avg_amount
        FROM transactions t
        GROUP BY t.transaction_type, {DIRECTION_SQL}
        ORDER BY volume DESC
        """
    )


def type_comparison():
    return run_query(
        """
        SELECT at.type_name AS account_type, COUNT(a.account_id) AS accounts,
               SUM(a.balance) AS total_balance, ROUND(AVG(a.balance), 0) AS avg_balance,
               MIN(a.balance) AS min_balance, MAX(a.balance) AS max_balance,
               COUNT(DISTINCT a.customer_id) AS customers
        FROM account_types at LEFT JOIN accounts a ON a.account_type_id = at.account_type_id
        GROUP BY at.account_type_id, at.type_name ORDER BY at.account_type_id
        """
    )


def loan_overview():
    return run_query(
        """
        SELECT l.loan_id, c.name AS customer, l.loan_type, l.amount, l.balance,
               ROUND(100 * (l.amount - l.balance) / l.amount, 1) AS repaid_pct,
               l.end_date, l.status
        FROM loans l JOIN customers c ON c.customer_id = l.customer_id
        ORDER BY l.loan_id
        """
    )


def payment_status():
    return run_query(
        """
        SELECT status, COUNT(*) AS payments, SUM(amount) AS total
        FROM payments GROUP BY status ORDER BY status
        """
    )
