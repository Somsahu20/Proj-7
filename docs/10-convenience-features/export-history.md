# Export History

## Overview

Users can export their transaction history in various formats.

---

## Export Formats

| Format | Use Case |
|--------|----------|
| CSV | Spreadsheet analysis |
| PDF | Printable reports |
| JSON | Developer/integration |

---

## Export Options

### My Transactions

**Request**
```
GET /api/v1/users/me/export
Authorization: Bearer <access_token>
Query Parameters:
  - format: csv | pdf | json
  - type: all | expenses | payments
  - start_date: date
  - end_date: date
```

### Group Transactions

**Request**
```
GET /api/v1/groups/{group_id}/export
Authorization: Bearer <access_token>
Query Parameters:
  - format: csv | pdf | json
  - start_date: date
  - end_date: date
```

---

## CSV Format

```csv
Date,Type,Description,Amount,Payer,Your Share,Category,Group
2026-01-11,Expense,Dinner at restaurant,120.00,John Doe,30.00,Food,Trip to Paris
2026-01-10,Payment,Settlement,50.00,Me→Jane,50.00,,Trip to Paris
```

---

## PDF Report

```
┌─────────────────────────────────────────┐
│           EXPENSE REPORT                │
│        Trip to Paris                    │
│    January 1 - January 31, 2026         │
├─────────────────────────────────────────┤
│                                         │
│ Summary                                 │
│ ─────────                               │
│ Total Expenses: $1,250.50               │
│ Your Share: $312.50                     │
│ Payments Made: $300.00                  │
│ Outstanding: $12.50                     │
│                                         │
│ Expenses by Category                    │
│ ─────────────────────                   │
│ Food & Drinks: $450.00 (36%)            │
│ Transport: $300.00 (24%)                │
│ ...                                     │
│                                         │
│ Detailed Transactions                   │
│ ─────────────────────                   │
│ [Table of all transactions]             │
│                                         │
└─────────────────────────────────────────┘
```

---

## Response

**CSV/JSON**
```
HTTP 200 OK
Content-Type: text/csv (or application/json)
Content-Disposition: attachment; filename="expenses_2026-01.csv"

[file content]
```

**PDF**
```
HTTP 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="report_2026-01.pdf"

[binary PDF content]
```

---

## Acceptance Criteria

- [ ] CSV export works
- [ ] PDF export works
- [ ] JSON export works
- [ ] Date filtering works
- [ ] Group export works
- [ ] File downloads correctly
