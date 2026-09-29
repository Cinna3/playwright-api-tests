"""Negative and boundary tests.

Good API testing is not only "does the happy path work". It is "does the
endpoint fail properly when given bad input?".

Two kinds of test live here:

1. Tests of behaviour the API already implements correctly (400 on a bad limit).
2. Tests of behaviour the API SHOULD implement but does not, marked `xfail`.
   An xfail test documents a real requirement and proves you found the gap
   without turning the build red. Flip it to a normal assertion once the API is
   fixed.
"""

import pytest

NEW_PRODUCT = {"title": "QA Widget", "price": 19.99, "category": "groceries"}


class TestParameterValidation:
    @pytest.mark.parametrize("limit", ["abc", "not-a-number", "-5"], ids=["text", "words", "negative"])
    def test_non_numeric_limit_is_rejected(self, products_api, limit):
        response = products_api.list_products(limit=limit)

        assert response.status == 400
        assert "message" in response.json(), "error responses must explain the problem"

    def test_limit_beyond_the_cap_is_clamped_to_what_exists(self, products_api):
        total = products_api.list_products(limit=1).json()["total"]
        response = products_api.list_products(limit=10_000)
        payload = response.json()

        # The API clamps rather than rejecting: ask for 10 000 items and you
        # quietly get everything. The reported "limit" reflects what was really
        # applied, so a client can tell the difference.
        assert response.status == 200
        assert payload["limit"] == total
        assert len(payload["products"]) == total


class TestSearchEdgeCases:
    def test_search_with_an_injection_style_string_is_handled_safely(self, products_api):
        # The payload that would break a naive string-concatenated SQL query.
        # The correct outcome is a normal empty result, NOT a 500.
        response = products_api.search_products("' OR 1=1 --")

        assert response.status == 200
        assert response.json()["total"] == 0

    def test_search_tolerates_unicode(self, products_api):
        response = products_api.search_products("café")

        assert response.status == 200


class TestMissingServerSideValidation:
    """Documented gaps in the API under test.

    Each test below states the behaviour a well-built API should have. They are
    marked xfail because the API currently does not enforce it, which is the
    finding. Remove the marker once the endpoint is fixed.
    """

    @pytest.mark.xfail(reason="DEFECT: endpoint accepts an empty body with no required fields")
    def test_create_with_empty_body_should_be_rejected(self, products_api):
        response = products_api.create_product({})

        assert response.status == 400, "a product needs at least a title and a price"

    @pytest.mark.xfail(reason="DEFECT: create succeeds with no title")
    def test_create_without_title_should_be_rejected(self, products_api):
        response = products_api.create_product({"price": 10})

        assert response.status == 400

    @pytest.mark.xfail(reason="DEFECT: price is stored as the string 'abc', unvalidated")
    def test_create_with_non_numeric_price_should_be_rejected(self, products_api):
        response = products_api.create_product({"title": "Bad price", "price": "abc"})

        assert response.status == 400

    @pytest.mark.xfail(reason="DEFECT: negative price is accepted")
    def test_create_with_negative_price_should_be_rejected(self, products_api):
        response = products_api.create_product({"title": "Negative", "price": -50})

        assert response.status == 400
