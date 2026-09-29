"""Status code and header checks.

This is the most basic and most valuable layer of API testing: does each
endpoint answer with the code it promises?
"""

import pytest


class TestReadEndpoints:
    def test_get_existing_product_returns_200(self, products_api):
        response = products_api.get_product(1)

        assert response.status == 200

    def test_list_products_returns_200(self, products_api):
        response = products_api.list_products(limit=5)

        assert response.status == 200
        assert len(response.json()["products"]) == 5

    def test_response_declares_json_content_type(self, products_api):
        response = products_api.get_product(1)

        # Header names are case-insensitive in HTTP, so "Content-Type" is safe
        # to look up regardless of how the server spelled it.
        assert "application/json" in response.headers["content-type"]


class TestMissingResources:
    @pytest.mark.parametrize(
        "product_id",
        [999999, 0, -1],
        ids=["id-too-large", "id-zero", "negative-id"],
    )
    def test_unknown_product_returns_404(self, products_api, product_id):
        response = products_api.get_product(product_id)

        assert response.status == 404, f"expected 404 for id {product_id}"

    def test_non_numeric_id_returns_404(self, products_api):
        # The contract question: does bad input fail cleanly with 404, or does
        # it crash with a 500? A 500 here would be a real defect.
        response = products_api.get_product("not-a-number")

        assert response.status == 404

    def test_404_body_still_parses_as_json(self, products_api):
        # Even error responses should honour the documented content type, so
        # that clients can always parse the body the same way.
        response = products_api.get_product(999999)

        assert "application/json" in response.headers["content-type"]
        assert isinstance(response.json(), dict)
