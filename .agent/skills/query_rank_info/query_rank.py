#!/usr/bin/env python3
"""
query_rank.py

Script to query Amazon ranking SQLite database with SQL queries.
"""

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB_PATH = "lab/database/rank.db"


def find_db(db_path_str: str) -> Path:
  """Locate the database file given a path string."""
  path = Path(db_path_str)
  if path.exists():
    return path.resolve()

  # Search upwards from current file to find the repo root
  current = Path(__file__).resolve().parent
  while current != current.parent:
    candidate = current / db_path_str
    if candidate.exists():
      return candidate.resolve()
    if (current / ".git").exists():
      candidate = current / db_path_str
      return candidate.resolve()
    current = current.parent

  return path.resolve()


def execute_query(db_path: Path, sql: str) -> tuple[list[str], list[tuple]]:
  """Execute a SQL SELECT query and return column names and rows."""
  if not db_path.exists():
    raise FileNotFoundError(f"Database file not found: {db_path}")

  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()
  cursor.execute(sql)
  columns = [desc[0] for desc in cursor.description] if cursor.description else []
  rows = cursor.fetchall()
  conn.close()
  return columns, rows


def print_table(columns: list[str], rows: list[tuple]):
  """Print query results in a clean ASCII table."""
  if not rows:
    print("No records found.")
    return

  col_widths = [len(c) for c in columns]
  for row in rows:
    for i, val in enumerate(row):
      val_str = str(val) if val is not None else "NULL"
      col_widths[i] = max(col_widths[i], len(val_str))

  # Limit max column width for neat display
  max_width = 80
  col_widths = [min(w, max_width) for w in col_widths]

  header = " | ".join(f"{col:<{w}}" for col, w in zip(columns, col_widths))
  separator = "-+-".join("-" * w for w in col_widths)

  print(header)
  print(separator)
  for row in rows:
    row_strs = []
    for val, w in zip(row, col_widths):
      val_str = str(val) if val is not None else "NULL"
      if len(val_str) > w:
        val_str = val_str[: w - 3] + "..."
      row_strs.append(f"{val_str:<{w}}")
    print(" | ".join(row_strs))
  print(f"\n({len(rows)} row{'s' if len(rows) != 1 else ''})")


def main():
  parser = argparse.ArgumentParser(description="Query Amazon rank SQLite database.")
  parser.add_argument(
    "--sql",
    "-s",
    dest="sql",
    help="SQL query to execute",
  )
  parser.add_argument(
    "positional_sql",
    nargs="?",
    help="SQL query to execute (positional)",
  )
  parser.add_argument(
    "--db-path",
    "-d",
    default=DEFAULT_DB_PATH,
    help=f"Path to SQLite database file (default: {DEFAULT_DB_PATH})",
  )
  parser.add_argument(
    "--format",
    "-f",
    choices=["table", "json", "csv"],
    default="table",
    help="Output format (default: table)",
  )
  parser.add_argument(
    "--schema",
    action="store_true",
    help="Display table schema and row count",
  )

  args = parser.parse_args()
  db_file = find_db(args.db_path)

  if args.schema:
    if not db_file.exists():
      print(f"Error: Database file not found at {db_file}", file=sys.stderr)
      sys.exit(1)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(
      "SELECT sql FROM sqlite_master WHERE type='table' AND name='amazon_rank_data';"
    )
    row = cursor.fetchone()
    if row:
      print(row[0])
    cursor.execute("SELECT COUNT(*) FROM amazon_rank_data;")
    count = cursor.fetchone()[0]
    print(f"\nTotal rows in amazon_rank_data: {count}")
    conn.close()
    return

  sql = args.sql or args.positional_sql
  if not sql:
    parser.print_help()
    sys.exit(1)

  try:
    columns, rows = execute_query(db_file, sql)
  except (sqlite3.Error, OSError) as e:
    print(f"Error executing query: {e}", file=sys.stderr)
    sys.exit(1)

  if args.format == "json":
    results = [dict(zip(columns, row)) for row in rows]
    print(json.dumps(results, indent=2, ensure_ascii=False))
  elif args.format == "csv":
    writer = csv.writer(sys.stdout)
    writer.writerow(columns)
    writer.writerows(rows)
  else:
    print_table(columns, rows)


if __name__ == "__main__":
  main()
