# PostgreSQL Internals Demo Application

## Overview
This project demonstrates key PostgreSQL internals using a lightweight content/incident feed application.
The primary focus is on understanding how query planning and indexing behavior map to application-level operations.  
A secondary focus is MVCC, demonstrated through a separate toy phones table to illustrate tuple versioning, isolation levels, and VACUUM behavior.

The application is menu-driven and allows users to run queries in three modes:
- Run query (actual results)
- EXPLAIN (query plan)
- EXPLAIN ANALYZE (execution + performance + buffers)

---

## Project Structure
```
project_root/
│
├── src/
│   ├── main.py
│   ├── actions.py
│   ├── db.py
│   ├── setup_db.py
│   ├── config.py
│   ├── utils.py
│   ├── mvcc.py
│   └── .env
│
├── sql/
│   ├── schema.sql
│   ├── seed.sql
│   └── mvcc.sql
│
├── README.md
└── requirements.txt
```
---

## Requirements

- Python 3.10+
- PostgreSQL installed and running

Install dependencies:

pip install -r requirements.txt

---

## Environment Configuration

Create a `.env` file inside the `src/` directory:
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database
```
---

## How to Run the Application

Step 1: Navigate to project root

`
cd project_root
`

Step 2: Run the application

`
python src/main.py
`

---

## Application Behavior

- On first run, the application automatically initializes:
  - Database schema
  - Seed data

- On subsequent runs:
  - Existing data is preserved
  - Initialization is skipped unless forced

---

## Menu Options

1. Browse latest traffic items
2. Retrieve all crime items
3. Retrieve open items
4. Lookup items by user_id
5. Lookup items by user name
6. MVCC demonstration
7. Exit

For query options, you can choose:
- Run query
- EXPLAIN
- EXPLAIN ANALYZE

---

## Key Concepts Demonstrated

Index Scan  
Efficient retrieval using composite index (category, created_at DESC) with LIMIT.

Bitmap Heap Scan  
Used when many rows match a predicate; reduces random I/O.

Sequential Scan  
Chosen when predicate selectivity is low.

Join Behavior  
Demonstrates planner decisions for joins between users and items.

MVCC  
- Snapshot isolation  
- Non-blocking reads  
- Tuple versioning  
- VACUUM behavior  

---

## Notes

- Dataset is synthetic and intentionally skewed to demonstrate planner behavior.
- EXPLAIN ANALYZE includes buffer usage for deeper insight.
- MVCC demonstrations use two concurrent connections.

---

## Troubleshooting

Database connection issues  
- Verify `.env` file in `src/`  
- Ensure PostgreSQL service is running  

Missing tables  
- Restart the application to trigger initialization  

---

## Author
Rana Shoaaib Mehmood