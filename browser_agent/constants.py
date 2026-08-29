"""Keep constant variables used in browser agent."""

import dataclasses
from collections.abc import Mapping, Sequence
from typing import Final


@dataclasses.dataclass(frozen=True)
class ProductCategory:
  """Product category information."""

  name: str
  url: str


AmazonProductCategories: Sequence[ProductCategory] = (
  ProductCategory(
    name="fashion",
    url="https://www.amazon.com/gp/new-releases/fashion/",
  ),
  ProductCategory(
    name="coins",
    url="https://www.amazon.com/gp/new-releases/coins/",
  ),
  ProductCategory(
    name="kitchen",
    url="https://www.amazon.com/gp/new-releases/kitchen/",
  ),
  ProductCategory(
    name="lawn-garden",
    url="https://www.amazon.com/gp/new-releases/lawn-garden/",
  ),
)

AmazonProductCategoryByName: Mapping[str, ProductCategory] = {
  product_category.name: product_category
  for product_category in AmazonProductCategories
}

DEFAULT_USER_AGENT: Final[str] = (
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
  "AppleWebKit/537.36 (KHTML, like Gecko) "
  "Chrome/124.0.0.0 Safari/537.36"
)

__all__ = [
  "DEFAULT_USER_AGENT",
  "AmazonProductCategories",
  "AmazonProductCategoryByName",
  "ProductCategory",
]
