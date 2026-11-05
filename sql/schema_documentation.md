# Schema documentation

19 tables in MySQL, using primary keys, foreign keys, CHECK constraints and class-table inheritance.

## Entity overview

| Group | Tables | Notes |
|---|---|---|
| People | `customers`, `logins` | `customers.login_id` is a unique FK to `logins`. |
| Accounts | `account_types`, `accounts` | `accounts` is the parent table. FK to `customers` and `account_types`. `balance >= 0` (CHECK). |
| Account subtypes | `savings_account`, `current_account`, `islamic_account` | Same PK as `accounts` (`account_id`). One row per account, in exactly one subtype table. |
| Staff | `branches`, `employees` | `employees.branch_id` FK to `branches`. |
| Staff subtypes | `manager`, `cashier`, `csr` | Same PK as `employees` (`employee_id`). |
| Channels | `atms` | FK to `branches`. |
| Money movement | `transactions`, `beneficiary_transactions`, `payments` | `transactions.amount > 0` (CHECK). |
| Products | `cards`, `loans` | Cards belong to an account. Loans link a customer and an account. |
| Admin | `notifications` | FK to `employees`. |

## Relationships used by the app

```
customers 1 --- * accounts * --- 1 account_types
accounts  1 --- 0..1 savings_account | current_account | islamic_account
accounts  1 --- * transactions * --- 0..1 atms * --- 1 branches 1 --- * employees
transactions 1 --- 0..1 beneficiary_transactions
accounts  1 --- * cards, payments, loans
employees 1 --- 0..1 manager | cashier | csr
```

Class-table inheritance is read with `LEFT JOIN` on each subtype table (see `ACCOUNT_DETAIL_SQL`
and `employees()` in `utils/queries.py`).

## Limitations that shape the app

1. **Accounts and customers have no branch.** Only employees and ATMs reference `branches`, so
   the Branches page reports staff, ATMs and ATM transactions, not customers per branch.
2. **Transactions have no status and no debit/credit flag.** The app shows no status. Direction is
   derived from `transaction_type`: Cash Deposit, Cheque Deposit and Profit Deposit are credits;
   ATM Cash Withdrawal, Online Transfer and IBFT Transfer are debits. This is an assumption.
3. **Balances are not derived from transactions.** `accounts.balance` is stored, not computed
   from the ledger, so the two can disagree (the sample data includes two demo withdrawals).
4. **`accounts.is_islamic` duplicates** the `Islamic PLS` account type.
5. **Employee logins are not linked to employees.** `logins` rows of type Employee have no FK to `employees`.
6. **`logins.password` holds plaintext in the original data.** The app never reads the `logins`
   table. A real system would store salted hashes.
7. **Table names are lowercase** so the schema works on case-sensitive (Linux) servers.
