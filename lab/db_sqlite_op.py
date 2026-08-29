"""Database operations for Amazon rank data using SQLite."""

import logging
import re
import sqlite3
from collections.abc import Sequence
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parent / "database" / "rank_db.sql"


def parse_price(price_str: str | None) -> float | None:
  """Parse price string into a float."""
  if not price_str or price_str == "N/A":
    return None
  match = re.search(r"[\d,]+\.?\d*", price_str)
  if match:
    cleaned = match.group(0).replace(",", "")
    try:
      return float(cleaned)
    except ValueError:
      return None
  return None


def parse_stars(rating_str: str | None) -> float | None:
  """Parse rating string (e.g. '4.8 out of 5 stars') into a float."""
  if not rating_str or rating_str == "N/A":
    return None
  match = re.search(r"\d+\.?\d*", rating_str)
  if match:
    try:
      return float(match.group(0))
    except ValueError:
      return None
  return None


def parse_rating_num(reviews_str: str | None) -> int | None:
  """Parse reviews count string (e.g. '6 ratings') into an integer."""
  if not reviews_str or reviews_str == "N/A":
    return None
  match = re.search(r"[\d,]+", reviews_str)
  if match:
    cleaned = match.group(0).replace(",", "")
    try:
      return int(cleaned)
    except ValueError:
      return None
  return None


def init_db(
  db_path: str | Path,
  schema_path: str | Path | None = None,
) -> sqlite3.Connection:
  """Initialize SQLite database with schema if it does not exist, or load it."""
  db_file = Path(db_path)
  db_exists = db_file.exists()

  if not db_exists and db_file.parent:
    db_file.parent.mkdir(parents=True, exist_ok=True)

  conn = sqlite3.connect(db_file)

  if not db_exists:
    logger.info("Database file %s does not exist. Creating schema...", db_file)
    schema_file = Path(schema_path) if schema_path else DEFAULT_SCHEMA_PATH
    if not schema_file.exists():
      raise FileNotFoundError(f"Schema file not found: {schema_file}")
    with open(schema_file, encoding="utf-8") as f:
      conn.executescript(f.read())
    conn.commit()
    logger.info("Initialized database %s successfully.", db_file)
  else:
    logger.info("Loaded existing database: %s", db_file)

  return conn


def upsert_rank_data(
  db_path: str | Path,
  category: str,
  collect_date: str,
  items: Sequence[dict[str, Any]],
  schema_path: str | Path | None = None,
) -> int:
  """Insert or update rank data in the database for the given category and collect_date."""
  conn = init_db(db_path, schema_path=schema_path)
  cursor = conn.cursor()

  # Ensure table exists in case an empty/existing DB didn't have the table
  schema_file = Path(schema_path) if schema_path else DEFAULT_SCHEMA_PATH
  if schema_file.exists():
    with open(schema_file, encoding="utf-8") as f:
      cursor.executescript(f.read())

  count = 0
  for item in items:
    product_id = item.get("asin") or item.get("product_id") or "N/A"
    product_name = item.get("title") or item.get("product_name") or "N/A"
    price = (
      item["price"]
      if isinstance(item.get("price"), (int, float))
      else parse_price(item.get("price"))
    )
    starts = (
      item["starts"]
      if isinstance(item.get("starts"), (int, float))
      else parse_stars(item.get("rating") or item.get("starts"))
    )
    rating_num = (
      item["rating_num"]
      if isinstance(item.get("rating_num"), int)
      else parse_rating_num(item.get("reviews_count") or item.get("rating_num"))
    )

    cursor.execute(
      """
      SELECT id FROM amazon_rank_data
      WHERE category = ? AND collect_date = ? AND product_id = ?
      """,
      (category, collect_date, product_id),
    )
    row = cursor.fetchone()

    if row:
      record_id = row[0]
      cursor.execute(
        """
        UPDATE amazon_rank_data
        SET product_name = ?, price = ?, starts = ?, rating_num = ?
        WHERE id = ?
        """,
        (product_name, price, starts, rating_num, record_id),
      )
    else:
      cursor.execute(
        """
        INSERT INTO amazon_rank_data
        (category, collect_date, product_name, product_id, price, starts, rating_num)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (category, collect_date, product_name, product_id, price, starts, rating_num),
      )
    count += 1

  conn.commit()
  conn.close()
  logger.info(
    "Upserted %d records for category '%s' on %s into %s",
    count,
    category,
    collect_date,
    db_path,
  )
  return count


__all__ = [
  "DEFAULT_SCHEMA_PATH",
  "init_db",
  "parse_price",
  "parse_rating_num",
  "parse_stars",
  "upsert_rank_data",
]
