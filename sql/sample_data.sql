-- Sanitized sample data for the Fresh-Start Banking dashboard.
-- Contact details, CNICs, card numbers, IBANs, bill references and passwords are fake placeholders.
-- Run sql/schema.sql first.

INSERT INTO branches (branch_id, branch_name, city, address, phone) VALUES
(1, 'DHA Phase 6 Branch', 'Lahore', 'Main Boulevard, DHA Phase 6', '042-35691111'),
(2, 'I.I. Chundrigar Head Branch', 'Karachi', 'Main I.I. Chundrigar Road', '021-32211111'),
(3, 'F-7 Markaz Branch', 'Islamabad', 'Jinnah Avenue, F-7 Markaz', '051-2277111');

INSERT INTO logins (login_id, username, password, login_type) VALUES
(10, 'user_10', 'REDACTED', 'Customer'),
(20, 'user_20', 'REDACTED', 'Customer'),
(30, 'user_30', 'REDACTED', 'Customer'),
(40, 'user_40', 'REDACTED', 'Customer'),
(50, 'user_50', 'REDACTED', 'Customer'),
(60, 'user_60', 'REDACTED', 'Customer'),
(70, 'user_70', 'REDACTED', 'Customer'),
(80, 'user_80', 'REDACTED', 'Customer'),
(90, 'user_90', 'REDACTED', 'Customer'),
(100, 'user_100', 'REDACTED', 'Customer'),
(901, 'user_901', 'REDACTED', 'Employee'),
(902, 'user_902', 'REDACTED', 'Employee'),
(903, 'user_903', 'REDACTED', 'Employee');

INSERT INTO customers (customer_id, login_id, cnic, name, address, email, phone) VALUES
(1, 10, '00001-0000000-1', 'Kamran Bhatti', 'Gulberg III, Lahore', 'customer1@example.com', '03000000001'),
(2, 20, '00002-0000000-2', 'Ayesha Malik', 'Clifton Block 5, Karachi', 'customer2@example.com', '03000000002'),
(3, 30, '00003-0000000-3', 'Zayan Ahmed', 'G-11, Islamabad', 'customer3@example.com', '03000000003'),
(4, 40, '00004-0000000-4', 'Fiona Shah', 'Model Town, Lahore', 'customer4@example.com', '03000000004'),
(5, 50, '00005-0000000-5', 'Bilal Dar', 'Muzaffarabad Sector C', 'customer5@example.com', '03000000005'),
(6, 60, '00006-0000000-6', 'Zainab Baloch', 'Samungli Road, Quetta', 'customer6@example.com', '03000000006'),
(7, 70, '00007-0000000-7', 'Mustafa Junejo', 'Saddar, Hyderabad', 'customer7@example.com', '03000000007'),
(8, 80, '00008-0000000-8', 'Hina Rabbani', 'Saddar, Rawalpindi', 'customer8@example.com', '03000000008'),
(9, 90, '00009-0000000-9', 'Umar Farooq', 'Model Town, Bahawalpur', 'customer9@example.com', '03000000009'),
(10, 100, '00010-0000000-0', 'Sadia Baig', 'Main Bazar, Abbottabad', 'customer10@example.com', '03000000010');

INSERT INTO account_types (account_type_id, type_name, description) VALUES
(100, 'Savings', 'Standard profit bearing account with variable interest thresholds'),
(200, 'Current', 'Standard business checking account with overdraft facilities'),
(300, 'Islamic PLS', 'Shariah-compliant profit and loss sharing account under Mudarabah rules');

INSERT INTO accounts (account_id, customer_id, account_type_id, balance, open_date, is_islamic) VALUES
(501, 1, 100, 435000.00, '2024-03-15', 0),
(502, 2, 200, 75000.00, '2025-01-10', 0),
(503, 3, 300, 1250000.00, '2025-05-20', 1),
(504, 4, 200, 19500.00, '2025-06-01', 0),
(505, 5, 100, 620000.00, '2025-07-12', 0),
(506, 6, 300, 89000.00, '2025-08-19', 1),
(507, 7, 200, 45000.00, '2025-09-05', 0),
(508, 8, 100, 3100000.00, '2025-10-01', 0),
(509, 9, 300, 15000.00, '2025-11-22', 1),
(510, 10, 200, 550000.00, '2025-12-25', 0),
(511, 1, 200, 12000.00, '2026-01-05', 0),
(512, 2, 100, 950000.00, '2026-02-14', 0);

INSERT INTO savings_account (account_id, interest_rate, minimum_balance) VALUES
(501, 11.50, 5000.00),
(505, 12.00, 5000.00),
(508, 13.25, 10000.00),
(512, 11.00, 5000.00);

INSERT INTO current_account (account_id, overdraft_limit, overdraft_rate) VALUES
(502, 100000.00, 14.50),
(504, 20000.00, 15.00),
(507, 50000.00, 14.00),
(510, 250000.00, 14.00),
(511, 10000.00, 15.00);

INSERT INTO islamic_account (account_id, mudarabah_rate, investment_allocation) VALUES
(503, 9.20, 'Government Sukuk Energy Bonds Pool'),
(506, 8.80, 'Agriculture Development Shariah Fund'),
(509, 9.00, 'Corporate Murabaha Trade Pool');

INSERT INTO employees (employee_id, branch_id, name, designation, phone, email) VALUES
(701, 1, 'Tariq Javed', 'Branch Manager', '03001110701', 'employee701@example.com'),
(702, 1, 'Sajid Raza', 'Main Teller Cashier', '03001110702', 'employee702@example.com'),
(703, 2, 'Amna Farooq', 'Customer Care Advisor', '03001110703', 'employee703@example.com');

INSERT INTO manager (employee_id, manager_level, managed_department) VALUES
(701, 'VP - Senior Executive', 'Branch Administration');

INSERT INTO cashier (employee_id, register_id, till_balance) VALUES
(702, 'LHR-DHA6-CASH01', 345000.00);

INSERT INTO csr (employee_id, csr_specialization, csr_case_load) VALUES
(703, 'Retail Consumer Support', 14);

INSERT INTO atms (atm_id, branch_id, location, status) VALUES
(901, 1, 'DHA Phase 6 Outward Lobby ATM', 'Active'),
(902, 2, 'Chundrigar Ground Floor ATM 1', 'Active');

INSERT INTO transactions (transaction_id, account_id, atm_id, transaction_type, amount, date, description) VALUES
(801, 501, NULL, 'Online Transfer', 35000.00, '2026-03-01 10:00:00', 'Funds sent to sister mobile wallet'),
(802, 502, 901, 'ATM Cash Withdrawal', 20000.00, '2026-03-02 14:30:00', 'ATM cash withdrawal counter transaction'),
(803, 503, NULL, 'Profit Deposit', 8500.00, '2026-03-05 00:00:00', 'Monthly Shariah Profit payout credit'),
(804, 504, 901, 'ATM Cash Withdrawal', 5000.00, '2026-03-06 18:22:00', 'Late night emergency cash out check'),
(805, 505, NULL, 'IBFT Transfer', 15000.00, '2026-03-07 11:15:00', 'Inter-bank fund transfer payment'),
(806, 506, 902, 'ATM Cash Withdrawal', 10000.00, '2026-03-08 09:40:00', 'Karachi branch ATM cash out'),
(807, 507, NULL, 'Online Transfer', 25000.00, '2026-03-09 13:12:00', 'Payment to vendor account'),
(808, 508, NULL, 'Cheque Deposit', 120000.00, '2026-03-10 12:00:00', 'Clearing transaction credit entry'),
(809, 510, NULL, 'Online Transfer', 45000.00, '2026-03-11 16:45:00', 'Rent transaction transfer'),
(810, 512, NULL, 'Cash Deposit', 50000.00, '2026-03-12 11:00:00', 'Over the counter cash deposit asset'),
(811, 501, 901, 'ATM Cash Withdrawal', 5000.00, '2026-05-29 05:24:20', 'Class Demo Live Withdrawal'),
(9100, 501, 901, 'ATM Cash Withdrawal', 5000.00, '2026-06-02 13:16:32', 'Live Demo Withdrawal');

INSERT INTO beneficiary_transactions (beneficiary_id, transaction_id, account_id, beneficiary_name, iban) VALUES
(1, 801, 501, 'Nida Bhatti', 'PK00FAKE0000000000000001'),
(2, 805, 505, 'Zeeshan Ali', 'PK00FAKE0000000000000002'),
(3, 807, 507, 'Aslam Traders', 'PK00FAKE0000000000000003');

INSERT INTO payments (payment_id, account_id, bill_type, bill_reference, amount, status) VALUES
(1, 502, 'Electricity (LESCO)', 'REF000000001', 18500.00, 'Paid'),
(2, 503, 'Gas (SNGPL)', 'REF000000002', 4200.00, 'Paid'),
(3, 504, 'Electricity (K-ELECTRIC)', 'REF000000003', 12300.00, 'Paid'),
(4, 507, 'Water (KWSB)', 'REF000000004', 1450.00, 'Paid'),
(5, 510, 'Electricity (IESCO)', 'REF000000005', 22400.00, 'Paid');

INSERT INTO cards (card_id, account_id, card_number, card_type, issue_date, expiry_date) VALUES
(1, 501, '4000000000000001', 'Visa Gold Debit', '2024-03-16', '2029-03-16'),
(2, 502, '4000000000000002', 'Mastercard Classic', '2025-01-11', '2030-01-11'),
(3, 503, '4000000000000003', 'Visa Platinum', '2025-05-21', '2030-05-21'),
(4, 505, '4000000000000004', 'Mastercard Gold', '2025-07-13', '2030-07-13'),
(5, 508, '4000000000000005', 'Visa Signature', '2025-10-02', '2030-10-02'),
(6, 510, '4000000000000006', 'Visa Platinum Debit', '2025-12-26', '2030-12-26');

INSERT INTO loans (loan_id, customer_id, account_id, loan_type, amount, balance, start_date, end_date, status) VALUES
(1, 1, 501, 'PM Youth Scheme Car Loan', 2500000.00, 2200000.00, '2024-06-01', '2029-06-01', 'Approved'),
(2, 5, 505, 'Personal Construction Loan', 5000000.00, 5000000.00, '2025-08-01', '2035-08-01', 'Approved'),
(3, 8, 508, 'SME Business Loan', 8000000.00, 7500000.00, '2025-10-15', '2030-10-15', 'Approved');

INSERT INTO notifications (notification_id, employee_id, message, date, status) VALUES
(1, 703, 'Dear Customer, your internet banking profile has been successfully modified.', '2026-01-01 09:00:00', 'Sent');
