"""Contract tests: the shape of the response body.

A contract test answers "does the API still return what it promised?". These
catch the most common real-world API defect: a field quietly renamed, made
optional, or changed from a number to a string.
"""

REQUIRED_PRODUCT_FIELDS = {
    "id": int,
    "title": str,
    "description": str,
    "category": str,
    "price": (int, float),
    "discountPercentage": (int, float),
    "rating": (int, float),
    "stock": int,
    "brand": str,
    "sku": str,
    "availabilityStatus": str,
    "tags": list,
    "reviews": list,
    "images": list,
}


class TestProductSchema:
    def test_product_contains_every_documented_field(self, products_api):
        product = products_api.get_product(1).json()

        missing = set(REQUIRED_PRODUCT_FIELDS) - set(product)

        assert not missing, f"response is missing fields: {sorted(missing)}"

    def test_each_field_has_the_documented_type(self, products_api):
        product = products_api.get_product(1).json()

        for field, expected_type in REQUIRED_PRODUCT_FIELDS.items():
            actual_type = type(product[field])
            # isinstance() is used because a bool is a subclass of int, and
            # we want to accept "number OR number", written as a tuple.
            assert isinstance(product[field], expected_type), (
                f"{field} should be {expected_type}, got {actual_type}"
            )

    def test_product_id_matches_the_requested_id(self, products_api):
        product = products_api.get_product(5).json()

        assert product["id"] == 5

    def test_nested_review_objects_are_well_formed(self, products_api):
        product = products_api.get_product(1).json()
        reviews = product["reviews"]

        assert reviews, "product 1 should have at least one review"
        for review in reviews:
            assert set(["rating", "comment", "date", "reviewerName"]) <= set(review)

    def test_images_are_all_urls(self, products_api):
        product = products_api.get_product(1).json()

        for image in product["images"]:
            assert image.startswith("http"), f"{image} is not a URL"


class TestCollectionSchema:
    def test_collection_has_the_envelope_fields(self, products_api):
        payload = products_api.list_products(limit=3).json()

        # A collection is not a bare array: it is wrapped in an envelope with
        # metadata. Clients depend on these keys being present.
        for key in ["products", "total", "skip", "limit"]:
            assert key in payload, f"collection envelope is missing '{key}'"

    def test_defaults_are_applied_when_no_paging_is_requested(self, products_api):
        payload = products_api.list_products().json()

        # Omitting limit/skip is not the same as sending 0. The endpoint applies
        # a default page size, and echoes it back so the client knows the real
        # window size rather than having to guess.
        assert payload["skip"] == 0
        assert payload["limit"] == 30
        assert len(payload["products"]) == payload["limit"]
