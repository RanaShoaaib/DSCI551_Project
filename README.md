# PostgreSQL Internals Demo Application

## Overview

This project demonstrates key PostgreSQL internals using a lightweight content/incident feed
application as an experimental testbed. The primary focus is on how PostgreSQL's cost-based
query planner selects access paths (Index Scan, Bitmap Heap Scan, Sequential Scan) and how
B-tree indexes affect query execution. A secondary focus is Multi-Version Concurrency Control
(MVCC), demonstrated through a dedicated `phones` table to illustrate tuple versioning,
isolation levels, and VACUUM behavior.

The application is menu-driven and allows users to run each query in three modes:

- **Run query** — returns actual results
- **EXPLAIN** — shows the query plan with cost estimates
- **EXPLAIN ANALYZE** — shows the actual execution plan with runtime, row counts, and buffer statistics

---

## Project Structure

```
project_root/
│
├── src/
│   ├── main.py          # Entry point; drives the interactive menu
│   ├── actions.py       # Core query functions for all five menu options
│   ├── db.py            # Connection management and query execution
│   ├── setup_db.py      # Idempotent schema and seed data initialization
│   ├── config.py        # Loads and validates database config from .env
│   ├── utils.py         # Menu display and result formatting utilities
│   ├── mvcc.py          # MVCC demonstration logic
│   └── .env             # Not committed — must be created manually (see below)
│
├── sql/
│   ├── schema.sql       # Creates users and items tables and indexes
│   ├── seed.sql         # Generates 100 users and 50,000 skewed items
│   └── mvcc.sql         # Creates the phones table used for MVCC demonstrations
│
├── README.md
└── requirements.txt
```

---

## Requirements

- Python 3.10+
- PostgreSQL installed and running locally

---

## Installation

**Step 1: Clone the repository**

```bash
git clone https://github.com/RanaShoaaib/DSCI551_Project.git
cd DSCI551_Project
```

**Step 2: Install Python dependencies**

```bash
pip install -r requirements.txt
```

---

## Credentials and Environment Configuration

⚠️ **This project requires a PostgreSQL database connection configured via a `.env` file.
This file is not committed — it is listed in `.gitignore`.**

Create a file named `.env` inside the `src/` directory:

```
src/.env
```

The file must contain the following variables:

```
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_NAME=your_database_name
```

**Variable reference:**

| Variable | Description |
|---|---|
| `DB_HOST` | PostgreSQL server host (typically `localhost` for local installs) |
| `DB_PORT` | PostgreSQL port (default is `5432`) |
| `DB_USER` | Your PostgreSQL username |
| `DB_PASSWORD` | Your PostgreSQL password |
| `DB_NAME` | Name of an existing PostgreSQL database to use for this project |

The database (`DB_NAME`) must already exist before running the application.
You can create one using `psql`:

```bash
psql -U your_username -c "CREATE DATABASE your_database_name;"
```

---

## Dataset and Data Generation

This project uses a **synthetic dataset generated automatically** — no separate data file
needs to be downloaded or imported.

On first run, the application automatically executes:

1. **`sql/schema.sql`** — Creates the `users` and `items` tables along with two indexes:
   - `idx_category_created (category, created_at DESC)`
   - `idx_status (status)`

2. **`sql/seed.sql`** — Populates the tables using PostgreSQL's `generate_series`:
   - 100 users with randomized names and timestamps
   - 50,000 items with intentionally skewed distributions:
     - Category: traffic (70%), crime (20%), maintenance (8%), miscellaneous (2%)
     - Status: open (80%), closed (20%)

   This skew is deliberate — it causes the planner to select different access paths for
   different queries, making planner behavior observable and comparable.

3. **`sql/mvcc.sql`** — Creates a small `phones` table (3 rows) used exclusively for
   MVCC demonstrations.

On subsequent runs, initialization is skipped automatically if the tables already exist.
To force re-initialization, set `force_initialize=True` in `setup_db.py`.

---

## Running the Application

From the project root:

```bash
python src/main.py
```

On first run, the application will initialize the schema and seed data before presenting
the menu. This may take a few seconds as 50,000 rows are inserted.

---

## Menu Options

```
1. Browse latest traffic items
2. Retrieve all crime items
3. Retrieve open items
4. Lookup items by user_id
5. Lookup items by user name
6. MVCC demonstration
7. Exit
```

For options 1–5, you will be prompted to select an execution mode:

```
1. Run query
2. Show EXPLAIN
3. Show EXPLAIN ANALYZE
```

---

## Reproducing Results

To reproduce the query plan observations documented in the report, select
**EXPLAIN ANALYZE** (mode 3) for each menu option:

| Menu Option | Query Pattern | Expected Access Path |
|---|---|---|
| 1 — Browse traffic items | `WHERE category = 'traffic' ... LIMIT 20` | Index Scan on `idx_category_created` |
| 2 — Retrieve all crime items | `WHERE category = 'crime' ORDER BY created_at DESC` | Bitmap Heap Scan + Sort |
| 3 — Retrieve open items | `WHERE status = 'open'` | Sequential Scan (index ignored) |
| 4 — Lookup by user ID | `JOIN ... WHERE u.id = ?` | Nested Loop Join |
| 5 — Lookup by user name | `JOIN ... WHERE u.name = ?` | Hash Join |

For the MVCC demonstration (option 6), select from the sub-menu:

```
1. Demonstrate tuple versioning and VACUUM
2. Demonstrate READ COMMITTED isolation
3. Demonstrate REPEATABLE READ isolation
```

Sub-option 1 runs 100 consecutive updates and uses `pgstattuple` to report dead tuple
counts before and after VACUUM. This requires the `pgstattuple` extension, which the
application installs automatically via `CREATE EXTENSION IF NOT EXISTS pgstattuple`.

Sub-options 2 and 3 open two concurrent database connections and demonstrate how each
isolation level responds to uncommitted and committed changes from a concurrent transaction.

---

## Key Concepts Demonstrated

| Concept | Description |
|---|---|
| **Index Scan** | Composite index `(category, created_at DESC)` eliminates sorting and enables early termination with LIMIT |
| **Bitmap Heap Scan** | Batches heap access when many rows match; used for the crime category query |
| **Sequential Scan** | Chosen over an available index when predicate selectivity is too low to justify index lookup overhead |
| **Nested Loop Join** | Used when the outer relation returns a single row (lookup by user ID) |
| **Hash Join** | Used when the join predicate filters on an unindexed column (lookup by user name) |
| **Tuple Versioning** | Each UPDATE creates a new tuple version; dead tuples accumulate until VACUUM reclaims them |
| **Snapshot Isolation** | READ COMMITTED vs REPEATABLE READ differ in when committed changes from concurrent transactions become visible |

---

## Troubleshooting

**Database connection error**
- Verify the `.env` file exists at `src/.env` and all five variables are set
- Ensure the PostgreSQL service is running
- Confirm the database specified in `DB_NAME` exists

**Missing tables on startup**
- Restart the application — initialization runs automatically if tables are absent

**pgstattuple error during MVCC demo**
- Ensure your PostgreSQL user has superuser privileges or the `pg_stat_scan_tables` role,
  as `pgstattuple` requires elevated permissions

---

## Author

Rana Shoaaib Mehmood  
MS Applied Data Science, University of Southern California  
rmehmood@usc.edu
