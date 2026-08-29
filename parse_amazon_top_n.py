#!/usr/bin/env python3
"""
parse_amazon_top_n.py

Fetch and parse top N items from Amazon Hot New Releases category,
save the results to a CSV file, and print a formatted table to the terminal.
"""

import argparse
import csv
import re
import sys
import requests
from bs4 import BeautifulSoup


def parse_amazon_new_releases(url: str, top_n: int = 10, lang: str = "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": lang,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }

    print(f"[*] Fetching: {url} ...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"[!] Error: Failed to fetch page. HTTP Status: {response.status_code}", file=sys.stderr)
        return []

    soup = BeautifulSoup(response.text, "lxml")
    items = soup.select('div[id*="gridItemRoot"]')
    
    if not items:
        # Fallback selector for alternative layout
        items = soup.select(".p13n-grid-content, .zg-grid-general-faceout")

    results = []
    for i, item in enumerate(items[:top_n]):
        # 1. Rank
        rank_elem = item.select_one(".zg-bdg-text, .zg-badge-text, span.zg-badge-text")
        rank = rank_elem.get_text(strip=True) if rank_elem else f"#{i+1}"

        # 2. Title & ASIN & Link
        title_elem = item.select_one(
            'div[class*="p13n-sc-css-line-clamp"], '
            'span.a-size-small, '
            '.p13n-sc-truncate, '
            'div.p13n-sc-truncate-desktop-type2'
        )
        title = title_elem.get_text(strip=True) if title_elem else "N/A"

        # ASIN and Link
        asin = "N/A"
        clean_url = "N/A"
        
        # Check parent container data-asin
        asin_elem = item.select_one("[data-asin]")
        if asin_elem and asin_elem.get("data-asin"):
            asin = asin_elem["data-asin"]
            clean_url = f"https://www.amazon.com/dp/{asin}"
        else:
            dp_links = item.select('a[href*="/dp/"]')
            if dp_links:
                url_path = dp_links[0].get("href", "")
                match = re.search(r"/dp/([A-Z0-9]{10})", url_path)
                if match:
                    asin = match.group(1)
                    clean_url = f"https://www.amazon.com/dp/{asin}"
                else:
                    clean_url = "https://www.amazon.com" + url_path.split("/ref=")[0]

        # 3. Price
        price_elem = item.select_one(
            "span._cDEzb_p13n-sc-price_3mJ9Z, "
            "span.p13n-sc-price, "
            "span.a-price span.a-offscreen, "
            "span.a-color-price"
        )
        price = price_elem.get_text(strip=True) if price_elem else "N/A"

        # 4. Rating & Reviews
        review_link = item.select_one('a[href*="/product-reviews/"]')
        rating = "N/A"
        reviews_count = "N/A"
        
        if review_link:
            aria = review_link.get("aria-label", "")
            if aria:
                parts = [p.strip() for p in aria.split(",")]
                if len(parts) >= 1:
                    rating = parts[0]
                if len(parts) >= 2:
                    reviews_count = parts[1]
            else:
                rating_elem = review_link.select_one("span.a-icon-alt")
                cnt_elem = review_link.select_one("span.a-size-small")
                if rating_elem:
                    rating = rating_elem.get_text(strip=True)
                if cnt_elem:
                    reviews_count = cnt_elem.get_text(strip=True)

        results.append({
            "rank": rank,
            "asin": asin,
            "title": title,
            "price": price,
            "rating": rating,
            "reviews_count": reviews_count,
            "url": clean_url
        })

    return results


def save_to_csv(results: list, filename: str):
    fieldnames = ["rank", "asin", "title", "price", "rating", "reviews_count", "url"]
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"[+] Saved {len(results)} items to CSV: {filename}")


def print_table(results: list):
    print("\n" + "=" * 120)
    print(f"{'排名':^6} | {'ASIN':^12} | {'價格':^10} | {'評分 / 評論數':^22} | {'商品名稱'}")
    print("-" * 120)
    for r in results:
        rating_info = f"{r['rating']} ({r['reviews_count']})" if r['reviews_count'] != "N/A" else r['rating']
        print(f"{r['rank']:^6} | {r['asin']:^12} | {r['price']:^10} | {rating_info:^22} | {r['title']}")
        print(f"{'':^6} | {'':^12} | {'':^10} | {'':^22} | 🔗 {r['url']}")
        print("-" * 120)
    print("=" * 120 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Scrape Amazon Hot New Releases Top N items.")
    parser.add_argument(
        "--url", "-u",
        default="https://www.amazon.com/gp/new-releases/fashion/",
        help="Amazon New Releases category URL (default: fashion/clothing)"
    )
    parser.add_argument(
        "--top-n", "-n",
        type=int,
        default=10,
        help="Number of items to collect (default: 10)"
    )
    parser.add_argument(
        "--output", "-o",
        default="amazon_top_releases.csv",
        help="Output CSV file path (default: amazon_top_releases.csv)"
    )

    args = parser.parse_args()

    results = parse_amazon_new_releases(url=args.url, top_n=args.top_n)
    if not results:
        print("[!] No items found.")
        return

    # Print table to console
    print_table(results)

    # Save to CSV
    save_to_csv(results, args.output)


if __name__ == "__main__":
    main()
