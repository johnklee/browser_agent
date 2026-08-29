-- Schema for storing Amazon product ranking data
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
