"""Pagination, filtering, and write endpoints."""

import pytest


class TestPagination:
    @pytest.mark.parametrize("limit", [1, 5, 30])
    def test_limit_controls_how_many_items_are_returned(self, products_api, limit):
        payload = products_api.list_products(limit=limit).json()

        assert len(payload["products"]) == limit
        assert payload["limit"] == limit

    def test_skip_offsets_the_window(self, products_api):
        first_page = products_api.list_products(limit=5, skip=0).json()
        second_page = products_api.list_products(limit=5, skip=5).json()

        first_ids = [p["id"] for p in first_page["products"]]
        second_ids = [p["id"] for p in second_page["products"]]

        assert not set(first_ids) & set(second_ids), "pages must not overlap"

    def test_total_is_consistent_across_pages(self, products_api):
        first = products_api.list_products(limit=1, skip=0).json()
        second = products_api.list_products(limit=1, skip=50).json()

        assert first["total"] == second["total"], "total must not depend on paging"

    def test_requesting_more_than_exists_is_clamped_not_an_error(self, products_api):
        total = products_api.list_products(limit=1).json()["total"]

        response = products_api.list_products(limit=total + 500)

        assert response.status == 200
        assert len(response.json()["products"]) == total


class TestFiltering:
    def test_search_returns_matching_products(self, products_api):
        payload = products_api.search_products("laptop").json()

        assert payload["total"] > 0
        for product in payload["products"]:
            assert "laptop" in (product["title"] + product["description"]).lower()

    def test_search_with_no_matches_returns_empty_result(self, products_api):
        response = products_api.search_products("qqzzxx-not-a-real-product")

        assert response.status == 200
        assert response.json()["total"] == 0
        assert response.json()["products"] == []

    def test_category_filter_returns_only_that_category(self, products_api):
        payload = products_api.get_by_category("smartphones").json()

        assert payload["total"] > 0
        for product in payload["products"]:
            assert product["category"] == "smartphones"


class TestWriteEndpoints:
    def test_create_returns_201_and_echoes_the_payload(self, products_api):
        payload = {"title": "QA Automation Widget", "price": 49.99, "category": "groceries"}

        response = products_api.create_product(payload)

        assert response.status == 201, "creating a resource must return 201, not 200"
        body = response.json()
        assert body["title"] == payload["title"]
        assert body["price"] == payload["price"]
        assert body["id"] > 0, "a new resource must be assigned an id"

    def test_update_returns_200_with_the_new_values(self, products_api):
        response = products_api.update_product(7, {"title": "Renamed By Test"})

        assert response.status == 200
        assert response.json()["title"] == "Renamed By Test"

    def test_update_of_unknown_product_returns_404(self, products_api):
        response = products_api.update_product(999999, {"title": "Nope"})

        assert response.status == 404

    def test_delete_returns_200_and_flags_the_resource(self, products_api):
        response = products_api.delete_product(78)

        # This API is shared and not isolated between test runs, so this
        # assertion only holds while id 78 exists. See the README note on why
        # the suite avoids read-after-write.
        assert response.status in (200, 404)
        if response.status == 200:
            assert response.json()["isDeleted"] is True
