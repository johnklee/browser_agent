import csv
import sqlite3
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure lab directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lab"))

from constants import (
  AmazonProductCategories,
  ProductCategory,
)
from parse_amazon_top_n import (
  main,
  parse_amazon_new_releases,
  print_table,
  process_category,
  save_to_csv,
)

SAMPLE_HTML = """
<html>
  <body>
    <div id="gridItemRoot_1" class="zg-grid-general-faceout" data-asin="B001TEST10">
      <span class="zg-bdg-text">#1</span>
      <div class="p13n-sc-css-line-clamp-2">Test Product Title 1</div>
      <span class="_cDEzb_p13n-sc-price_3mJ9Z">$29.99</span>
      <a href="/product-reviews/B001TEST10" aria-label="4.6 out of 5 stars, 150 ratings"></a>
    </div>
    <div id="gridItemRoot_2" class="zg-grid-general-faceout">
      <a href="/dp/B002TEST20/ref=zg_bs_tab">
        <span class="a-size-small">Test Product Title 2</span>
      </a>
      <span class="a-price"><span class="a-offscreen">$15.00</span></span>
      <a href="/product-reviews/B002TEST20">
        <span class="a-icon-alt">4.2 out of 5 stars</span>
        <span class="a-size-small">80</span>
      </a>
    </div>
  </body>
</html>
"""


def test_parse_amazon_new_releases_success():
  with patch("requests.get") as mock_get:
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = SAMPLE_HTML
    mock_get.return_value = mock_resp

    results = parse_amazon_new_releases("https://example.com", top_n=2)
    assert len(results) == 2
    assert results[0]["rank"] == "#1"
    assert results[0]["asin"] == "B001TEST10"
    assert results[0]["title"] == "Test Product Title 1"
    assert results[0]["price"] == "$29.99"
    assert results[0]["rating"] == "4.6 out of 5 stars"
    assert results[0]["reviews_count"] == "150 ratings"
    assert results[0]["url"] == "https://www.amazon.com/dp/B001TEST10"

    assert results[1]["rank"] == "#2"
    assert results[1]["asin"] == "B002TEST20"
    assert results[1]["title"] == "Test Product Title 2"
    assert results[1]["price"] == "$15.00"
    assert results[1]["rating"] == "4.2 out of 5 stars"
    assert results[1]["reviews_count"] == "80"
    assert results[1]["url"] == "https://www.amazon.com/dp/B002TEST20"


def test_parse_amazon_new_releases_error():
  with patch("requests.get") as mock_get:
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_get.return_value = mock_resp

    results = parse_amazon_new_releases("https://example.com")
    assert results == []


def test_save_to_csv(tmp_path):
  csv_file = tmp_path / "test_out.csv"
  results = [
    {
      "rank": "#1",
      "asin": "B001",
      "title": "Title 1",
      "price": "$10",
      "rating": "5.0",
      "reviews_count": "10",
      "url": "https://example.com/1",
    }
  ]
  save_to_csv(results, str(csv_file))

  assert csv_file.exists()
  with open(csv_file, encoding="utf-8-sig") as f:
    reader = list(csv.DictReader(f))
    assert len(reader) == 1
    assert reader[0]["asin"] == "B001"


def test_print_table(capsys):
  results = [
    {
      "rank": "#1",
      "asin": "B001",
      "title": "Sample Item",
      "price": "$9.99",
      "rating": "4.5 out of 5 stars",
      "reviews_count": "100",
      "url": "https://example.com/item1",
    }
  ]
  print_table(results)
  captured = capsys.readouterr().out
  assert "#1" in captured
  assert "B001" in captured
  assert "$9.99" in captured
  assert "Sample Item" in captured


def test_process_category(tmp_path):
  csv_file = tmp_path / "fashion.csv"
  db_file = tmp_path / "rank.db"
  schema_file = (
    Path(__file__).resolve().parent.parent / "lab" / "database" / "rank_db.sql"
  )

  # Init DB schema
  conn = sqlite3.connect(db_file)
  with open(schema_file, encoding="utf-8") as f:
    conn.executescript(f.read())
  conn.close()

  category = ProductCategory(name="fashion", url="https://example.com/fashion")
  sample_results = [
    {
      "rank": "#1",
      "asin": "B001FASH10",
      "title": "Fashion Item",
      "price": "$19.99",
      "rating": "4.0 out of 5 stars",
      "reviews_count": "50",
      "url": "https://example.com/fashion1",
    }
  ]

  with patch(
    "parse_amazon_top_n.parse_amazon_new_releases", return_value=sample_results
  ):
    res = process_category(
      category=category,
      top_n=5,
      output=str(csv_file),
      sqlite_file=str(db_file),
    )
    assert len(res) == 1
    assert csv_file.exists()

    # Check sqlite data
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT category, product_id, price FROM amazon_rank_data")
    row = cur.fetchone()
    conn.close()
    assert row == ("fashion", "B001FASH10", 19.99)


def test_main_single_category(tmp_path):
  out_file = tmp_path / "coins.csv"
  test_args = [
    "parse_amazon_top_n.py",
    "--category",
    "coins",
    "--top-n",
    "5",
    "--output",
    str(out_file),
  ]

  with (
    patch("sys.argv", test_args),
    patch(
      "parse_amazon_top_n.parse_amazon_new_releases",
      return_value=[
        {
          "rank": "#1",
          "asin": "B001COIN10",
          "title": "Coin Item",
          "price": "$5.00",
          "rating": "5.0",
          "reviews_count": "1",
          "url": "https://example.com/coin",
        }
      ],
    ) as mock_parse,
  ):
    main()
    assert mock_parse.call_count == 1
    assert out_file.exists()


def test_main_all_categories(tmp_path):
  out_prefix = tmp_path / "custom_out.csv"
  test_args = [
    "parse_amazon_top_n.py",
    "--category",
    "all",
    "--top-n",
    "5",
    "--output",
    str(out_prefix),
  ]

  mock_item = {
    "rank": "#1",
    "asin": "B001ALL010",
    "title": "All Item",
    "price": "$12.00",
    "rating": "4.0",
    "reviews_count": "20",
    "url": "https://example.com/item",
  }

  with (
    patch("sys.argv", test_args),
    patch(
      "parse_amazon_top_n.parse_amazon_new_releases", return_value=[mock_item]
    ) as mock_parse,
    patch("parse_amazon_top_n.tqdm", side_effect=lambda x, **kwargs: x) as mock_tqdm,
  ):
    main()
    # All categories in AmazonProductCategories should be processed
    assert mock_parse.call_count == len(AmazonProductCategories)
    assert mock_tqdm.call_count == 1

    # Verify separate CSV files generated for all categories
    for cat in AmazonProductCategories:
      expected_file = tmp_path / f"custom_out_{cat.name}.csv"
      assert expected_file.exists()
