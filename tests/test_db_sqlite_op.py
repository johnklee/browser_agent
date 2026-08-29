import sqlite3
import sys
from pathlib import Path

# Ensure lab directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lab"))

from db_sqlite_op import (
  init_db,
  parse_price,
  parse_rating_num,
  parse_stars,
  upsert_rank_data,
)


def test_parsers():
  assert parse_price("$39.95") == 39.95
  assert parse_price("$1,234.56") == 1234.56
  assert parse_price("N/A") is None
  assert parse_price(None) is None

  assert parse_stars("4.8 out of 5 stars") == 4.8
  assert parse_stars("5.0") == 5.0
  assert parse_stars("N/A") is None
  assert parse_stars(None) is None

  assert parse_rating_num("6 ratings") == 6
  assert parse_rating_num("1,234 ratings") == 1234
  assert parse_rating_num("N/A") is None
  assert parse_rating_num(None) is None


def test_init_and_upsert_rank_data(tmp_path):
  db_path = tmp_path / "test_rank.db"
  schema_path = (
    Path(__file__).resolve().parent.parent / "lab" / "database" / "rank_db.sql"
  )

  conn = init_db(db_path, schema_path=schema_path)
  conn.close()
  assert db_path.exists()

  sample_items = [
    {
      "rank": "#1",
      "asin": "B001",
      "title": "Item 1",
      "price": "$10.00",
      "rating": "4.5 out of 5 stars",
      "reviews_count": "100 ratings",
      "url": "https://example.com/1",
    },
    {
      "rank": "#2",
      "asin": "B002",
      "title": "Item 2",
      "price": "N/A",
      "rating": "N/A",
      "reviews_count": "N/A",
      "url": "https://example.com/2",
    },
  ]

  count = upsert_rank_data(
    db_path=db_path,
    category="test_cat",
    collect_date="2026/08/29",
    items=sample_items,
    schema_path=schema_path,
  )
  assert count == 2

  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()
  cursor.execute(
    "SELECT category, collect_date, product_name, product_id, price, starts, rating_num FROM amazon_rank_data"
  )
  rows = cursor.fetchall()
  conn.close()

  assert len(rows) == 2
  assert rows[0] == (
    "test_cat",
    "2026/08/29",
    "Item 1",
    "B001",
    10.0,
    4.5,
    100,
  )
  assert rows[1] == (
    "test_cat",
    "2026/08/29",
    "Item 2",
    "B002",
    None,
    None,
    None,
  )

  # Test update on existing (category, collect_date, product_id)
  updated_items = [
    {
      "rank": "#1",
      "asin": "B001",
      "title": "Item 1 Updated",
      "price": "$15.50",
      "rating": "4.9 out of 5 stars",
      "reviews_count": "200 ratings",
      "url": "https://example.com/1",
    }
  ]

  upsert_rank_data(
    db_path=db_path,
    category="test_cat",
    collect_date="2026/08/29",
    items=updated_items,
    schema_path=schema_path,
  )

  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()
  cursor.execute(
    "SELECT product_name, price, starts, rating_num FROM amazon_rank_data WHERE product_id = 'B001'"
  )
  row = cursor.fetchone()
  conn.close()

  assert row == ("Item 1 Updated", 15.5, 4.9, 200)
