import json
import sqlite3
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = (
  Path(__file__).resolve().parent.parent
  / ".agents"
  / "skills"
  / "query_rank_info"
  / "query_rank.py"
)


def test_query_rank_cli(tmp_path):
  db_file = tmp_path / "test.db"
  schema_file = (
    Path(__file__).resolve().parent.parent / "lab" / "database" / "rank_db.sql"
  )

  conn = sqlite3.connect(db_file)
  with open(schema_file, encoding="utf-8") as f:
    conn.executescript(f.read())

  conn.execute(
    """
    INSERT INTO amazon_rank_data (category, collect_date, product_name, product_id, price, starts, rating_num)
    VALUES ('coins', '2026/08/29', 'Test Coin', 'B001', 19.99, 4.5, 50);
    """
  )
  conn.commit()
  conn.close()

  # Test Table Output
  res = subprocess.run(
    [
      sys.executable,
      str(SCRIPT_PATH),
      "--db-path",
      str(db_file),
      "--sql",
      "SELECT category, product_id, price FROM amazon_rank_data;",
    ],
    capture_output=True,
    text=True,
    check=True,
  )
  assert "coins" in res.stdout
  assert "B001" in res.stdout
  assert "19.99" in res.stdout

  # Test JSON Output
  res_json = subprocess.run(
    [
      sys.executable,
      str(SCRIPT_PATH),
      "--db-path",
      str(db_file),
      "--sql",
      "SELECT product_id, price FROM amazon_rank_data;",
      "--format",
      "json",
    ],
    capture_output=True,
    text=True,
    check=True,
  )
  data = json.loads(res_json.stdout)
  assert len(data) == 1
  assert data[0]["product_id"] == "B001"
  assert data[0]["price"] == 19.99

  # Test Schema Output
  res_schema = subprocess.run(
    [sys.executable, str(SCRIPT_PATH), "--db-path", str(db_file), "--schema"],
    capture_output=True,
    text=True,
    check=True,
  )
  assert "CREATE TABLE amazon_rank_data" in res_schema.stdout
  assert "Total rows in amazon_rank_data: 1" in res_schema.stdout
