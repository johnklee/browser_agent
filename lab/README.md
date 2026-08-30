# Amazon Hot New Releases Scraper (`parse_amazon_top_n.py`)

`parse_amazon_top_n.py` is a Python script designed to scrape and parse the Top $N$ products from Amazon's **Hot New Releases** section across supported product categories.

It displays formatted tabular results in the terminal, exports them to a timestamped CSV file, and optionally persists the ranking data into an SQLite database.

---

## Directory Structure

```
lab/
├── database/
│   ├── rank.db                 # SQLite database storing historical ranking records
│   └── rank_db.sql             # Database schema initialization script
├── constants.py                # Category configurations and request constants
├── db_sqlite_op.py             # SQLite helper functions (upsert, data parsing)
├── parse_amazon_top_n.py       # Main scraper script
└── README.md                   # This documentation
```

---

## Features

- **Multi-Category Support**: Scrapes various Amazon categories (e.g., Fashion, Kitchen, Coins, Lawn & Garden).
- **Data Extraction**: Extracts product rank, ASIN, title, price, rating, reviews count, and canonical product URL (`https://www.amazon.com/dp/{asin}`).
- **Console Table Output**: Formats and prints results directly to the terminal.
- **CSV Export**: Automatically exports scraped items to a CSV file (encoded in UTF-8 with BOM for spreadsheet compatibility).
- **SQLite Database Persistence**: Upserts rank data into an SQLite database with schema validation and duplicate handling.
- **Configurable Options**: Command-line arguments for category selection, item count limit, custom output paths, database integration, and logging verbosity.

---

## Supported Categories

Category mappings are defined in [`constants.py`](constants.py):

| Category Key (`--category`) | Amazon New Releases URL |
|---|---|
| `fashion` *(default)* | `https://www.amazon.com/gp/new-releases/fashion/` |
| `coins` | `https://www.amazon.com/gp/new-releases/coins/` |
| `kitchen` | `https://www.amazon.com/gp/new-releases/kitchen/` |
| `lawn-garden` | `https://www.amazon.com/gp/new-releases/lawn-garden/` |
| `all` | Process all supported product categories with a `tqdm` progress bar |

---

## Command-Line Arguments

| Argument | Short Flag | Type | Default | Description |
|---|---|---|---|---|
| `--category` | `-c` | `str` | `fashion` | Amazon Hot New Releases category (`fashion`, `coins`, `kitchen`, `lawn-garden`, or `all`). |
| `--top-n` | `-n` | `int` | `10` | Number of top items to collect. |
| `--output` | `-o` | `str` | `None` | Custom output CSV file path. Defaults to `amazon_top_releases_{category}_{YYYYMMDD}.csv`. |
| `--sqlite-file` | `-s` | `str` | `None` | Path to SQLite DB file to persist ranking data (e.g. `database/rank.db`). |
| `--log-level` | | `str` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| `--help` | `-h` | | | Show help message and exit. |

---

## Prerequisites & Environment Setup

To ensure the runtime environment has all necessary dependencies (e.g., `requests`, `beautifulsoup4`, `lxml`, `tqdm`), create and activate a virtual environment using `uv`:

### 1. Create and Activate Virtual Environment

From the project root:

```bash
# Create a virtual environment with uv
uv venv

# Activate the virtual environment
# On Linux / macOS:
source .venv/bin/activate

# On Windows:
# .venv\Scripts\activate
```

### 2. Install Project Dependencies

Synchronize all required dependencies into the virtual environment:

```bash
# Sync dependencies from pyproject.toml / uv.lock
uv sync

# Or install from requirements.txt
uv pip install -r requirements.txt
```

> [!TIP]
> **Direct Execution via `uv run`**: You can also run the script directly without manually activating the virtual environment by prefixing the command with `uv run`:
> ```bash
> uv run python lab/parse_amazon_top_n.py --category kitchen --top-n 10
> ```

---

## Usage Examples

Make sure your working directory is `lab/` (or adjust relative paths accordingly):

```bash
cd lab
```

### 1. Basic Run (Default Settings)
Fetches the top 10 items in the `fashion` category and saves them to `amazon_top_releases_fashion_YYYYMMDD.csv`:

```bash
python parse_amazon_top_n.py
```

### 2. Specify Category and Item Count
Fetch the top 20 items from the `kitchen` category:

```bash
python parse_amazon_top_n.py --category kitchen --top-n 20
```

Short flags:
```bash
python parse_amazon_top_n.py -c kitchen -n 20
```

### 3. Custom CSV Output Path
Save the results to a specific file:

```bash
python parse_amazon_top_n.py -c coins -n 15 -o output/coins_top15.csv
```

### 4. Persist to SQLite Database
Collect top 10 items from `fashion` and insert/update the records in `database/rank.db`:

```bash
python parse_amazon_top_n.py -c fashion -n 10 -s database/rank.db
```

### 5. Enable Debug Logging
Show detailed HTTP request and parsing logs:

```bash
python parse_amazon_top_n.py -c lawn-garden --log-level DEBUG
```

### 6. Process All Categories
Fetch top items from all supported categories and show a progress bar with `tqdm`:

```bash
python parse_amazon_top_n.py --category all
```

---

## Output Formats

### 1. Terminal Table

```text
========================================================================================================================
 排名   |     ASIN     |    價格    |     評分 / 評論數      | 商品名稱
------------------------------------------------------------------------------------------------------------------------
  #1   |  B0XXXXXX1   |   $19.99   | 4.6 out of 5 stars (120) | Example Product Name
       |              |            |                        | 🔗 https://www.amazon.com/dp/B0XXXXXX1
------------------------------------------------------------------------------------------------------------------------
```

### 2. CSV File

Output fields:
- `rank`: Rank badge number (e.g., `#1`)
- `asin`: Amazon Standard Identification Number
- `title`: Product title
- `price`: Product price string
- `rating`: Rating description (e.g., `4.5 out of 5 stars`)
- `reviews_count`: Total review/rating count string
- `url`: Canonical product URL

### 3. SQLite Database (`amazon_rank_data`)

When `--sqlite-file` (`-s`) is provided, records are upserted into the `amazon_rank_data` table defined in [`database/rank_db.sql`](database/rank_db.sql):

```sql
CREATE TABLE IF NOT EXISTS amazon_rank_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    collect_date TEXT NOT NULL,
    product_name TEXT NOT NULL,
    product_id TEXT NOT NULL,
    price REAL,
    starts REAL,
    rating_num INTEGER
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_amazon_rank_category_date_product
ON amazon_rank_data (category, collect_date, product_id);
```
