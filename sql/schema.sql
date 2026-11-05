-- Fresh-Start Retail & Islamic Banking: SCHEMA ONLY (no data, no credentials).
-- Table names are lowercase so the app also works on case-sensitive (Linux) MySQL servers.
-- Create a database first, e.g.:  CREATE DATABASE DB_Final_Group_Project_Working;  USE DB_Final_Group_Project_Working;

-- ====================================================================
-- PHASE 1: CORE TABLE CREATION (BASE ARCHITECTURE)
-- ====================================================================

-- 1. Branches Table
CREATE TABLE branches (
    branch_id INT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL
);

-- 2. Logins Table (Security Isolation layer)
CREATE TABLE logins (
    login_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    login_type ENUM('Customer', 'Employee') NOT NULL
);

-- 3. Customers Table
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    login_id INT UNIQUE,
    cnic VARCHAR(15) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    FOREIGN KEY (login_id) REFERENCES logins(login_id) ON DELETE CASCADE
);

-- 4. Account Types Lookup Table
CREATE TABLE account_types (
    account_type_id INT PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL,
    description VARCHAR(255)
);

-- 5. Accounts Superclass Table
CREATE TABLE accounts (
    account_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    account_type_id INT NOT NULL,
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    open_date DATE NOT NULL,
    is_islamic BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT chk_positive_balance CHECK (balance >= 0.00),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (account_type_id) REFERENCES account_types(account_type_id)
);

-- ====================================================================
-- PHASE 2: CLASS TABLE INHERITANCE (ACCOUNT SUBCLASSES)
-- ====================================================================

-- 6. Savings Account Subclass (Conventional)
CREATE TABLE savings_account (
    account_id INT PRIMARY KEY,
    interest_rate DECIMAL(5,2) NOT NULL,
    minimum_balance DECIMAL(10,2) NOT NULL DEFAULT 5000.00,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- 7. Current Account Subclass (Conventional with Overdraft)
CREATE TABLE current_account (
    account_id INT PRIMARY KEY,
    overdraft_limit DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    overdraft_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- 8. Islamic Account Subclass (Shariah Compliant / Mudarabah)
CREATE TABLE islamic_account (
    account_id INT PRIMARY KEY,
    mudarabah_rate DECIMAL(5,2) NOT NULL,
    investment_allocation VARCHAR(150) NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- ====================================================================
-- PHASE 3: STAFF HIERARCHY & INHERITANCE
-- ====================================================================

-- 9. Base Employees Table
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    branch_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    designation VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

-- 10. Manager Subclass
CREATE TABLE manager (
    employee_id INT PRIMARY KEY,
    manager_level VARCHAR(50) NOT NULL,
    managed_department VARCHAR(50) NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- 11. Cashier Subclass
CREATE TABLE cashier (
    employee_id INT PRIMARY KEY,
    register_id VARCHAR(50) UNIQUE NOT NULL,
    till_balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- 12. CSR Subclass
CREATE TABLE csr (
    employee_id INT PRIMARY KEY,
    csr_specialization VARCHAR(50) NOT NULL,
    csr_case_load INT NOT NULL DEFAULT 0,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- ====================================================================
-- PHASE 4: TRANSACTIONS, CHANNELS, & UTILITIES
-- ====================================================================

-- 13. ATMs Infrastructure Table
CREATE TABLE atms (
    atm_id INT PRIMARY KEY,
    branch_id INT NOT NULL,
    location VARCHAR(150) NOT NULL,
    status ENUM('Active', 'Maintenance', 'Out of Cash') NOT NULL DEFAULT 'Active',
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

-- 14. Master Ledger Transactions Table
CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY,
    account_id INT NOT NULL,
    atm_id INT DEFAULT NULL,
    transaction_type ENUM('ATM Cash Withdrawal', 'Cash Deposit', 'Online Transfer', 'IBFT Transfer', 'Profit Deposit', 'Cheque Deposit') NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255),
    CONSTRAINT chk_positive_tx CHECK (amount > 0.00),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE RESTRICT,
    FOREIGN KEY (atm_id) REFERENCES atms(atm_id)
);

-- 15. Beneficiary Third-Party Bridge Table (Audit Trail)
CREATE TABLE beneficiary_transactions (
    beneficiary_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_id INT NOT NULL,
    account_id INT NOT NULL,
    beneficiary_name VARCHAR(100) NOT NULL,
    iban VARCHAR(34) NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

-- 16. Ecosystem Consumer Payments (Utility Bills Integration)
CREATE TABLE payments (
    payment_id INT PRIMARY KEY,
    account_id INT NOT NULL,
    bill_type VARCHAR(50) NOT NULL,
    bill_reference VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('Pending', 'Paid', 'Failed') NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE RESTRICT
);

-- ====================================================================
-- PHASE 5: CARDS, LIABILITIES, & NOTIFICATIONS
-- ====================================================================

-- 17. Cards Management Table
CREATE TABLE cards (
    card_id INT PRIMARY KEY,
    account_id INT NOT NULL,
    card_number VARCHAR(16) UNIQUE NOT NULL,
    card_type VARCHAR(50) NOT NULL,
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- 18. Commercial Loans Table
CREATE TABLE loans (
    loan_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    account_id INT NOT NULL,
    loan_type VARCHAR(100) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    balance DECIMAL(15,2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected', 'Closed') NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

-- 19. Administrative Logs / System Notifications
CREATE TABLE notifications (
    notification_id INT PRIMARY KEY,
    employee_id INT NOT NULL,
    message TEXT NOT NULL,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Sent', 'Failed') NOT NULL DEFAULT 'Sent',
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);
