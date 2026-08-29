---
name: query_rank_info
description: Accept a natural language query for Amazon product ranking data, translate it to SQL, execute it against the SQLite database, and return the response.
---

# Query Amazon Rank Info

Use this skill when the user asks natural language questions or queries about Amazon product ranking, price, stars, ratings, or categories stored in the SQLite database.

## Database Schema Reference

The SQLite database default location is `lab/database/rank.db` with schema defined in `lab/database/rank_db.sql`:

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
```

### Column Descriptions:
- **`category`** (`TEXT`): Product category (e.g. `'coins'`, `'fashion'`, `'kitchen'`, `'lawn-garden'`).
- **`collect_date`** (`TEXT`): The collection date in UTC formatted as `'YYYY/MM/DD'` (e.g. `'2026/08/29'`).
- **`product_name`** (`TEXT`): Product title/name.
- **`product_id`** (`TEXT`): Amazon Standard Identification Number (ASIN).
- **`price`** (`REAL`): Product price in USD (e.g. `39.95`).
- **`starts`** (`REAL`): Average rating stars (e.g. `4.8` for "4.8 out of 5 stars").
- **`rating_num`** (`INTEGER`): Total number of customer ratings/reviews (e.g. `12`).

## Execution Workflow

1. **Understand Natural Language Intent**: Determine what the user is asking (e.g., filtering by category, date, price thresholds, top ratings, aggregations, etc.).
2. **Translate to SQL**: Formulate a standard SQLite query targeting `amazon_rank_data`.
3. **Execute the Query**:
   Run the helper script `query_rank.py` using `run_command`:
   ```bash
   python3 .agents/skills/query_rank_info/query_rank.py --sql "<SQL_QUERY>"
   ```
   If a custom DB path is requested, provide `--db-path <PATH>`.
   To output JSON format, add `--format json`.
4. **Format Results**: Present the query results clearly to the user in clean Markdown tables and summarize the key findings.

## Example Queries

- **Top products by rating in a category**:
  ```sql
  SELECT product_name, starts, rating_num, price
  FROM amazon_rank_data
  WHERE category = 'coins' AND starts IS NOT NULL
  ORDER BY starts DESC, rating_num DESC
  LIMIT 5;
  ```

- **Cheapest products under a specific price**:
  ```sql
  SELECT product_name, price, starts, rating_num
  FROM amazon_rank_data
  WHERE price IS NOT NULL AND price < 20.0
  ORDER BY price ASC;
  ```

- **Summary count and average price by category**:
  ```sql
  SELECT category, COUNT(*) AS count, AVG(price) AS avg_price, AVG(starts) AS avg_stars
  FROM amazon_rank_data
  GROUP BY category;
  ```
