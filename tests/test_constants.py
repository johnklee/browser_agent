from browser_agent.constants import (
  DEFAULT_USER_AGENT,
  AmazonProductCategories,
  AmazonProductCategoryByName,
  ProductCategory,
)


def test_product_category():
  category = ProductCategory(name="test", url="https://example.com")
  assert category.name == "test"
  assert category.url == "https://example.com"


def test_amazon_product_categories():
  assert len(AmazonProductCategories) == 4
  expected_names = {"fashion", "coins", "kitchen", "lawn-garden"}
  assert {c.name for c in AmazonProductCategories} == expected_names


def test_amazon_product_category_by_name():
  assert len(AmazonProductCategoryByName) == 4
  assert "fashion" in AmazonProductCategoryByName
  assert (
    AmazonProductCategoryByName["fashion"].url
    == "https://www.amazon.com/gp/new-releases/fashion/"
  )


def test_default_user_agent():
  assert "Mozilla/5.0" in DEFAULT_USER_AGENT
