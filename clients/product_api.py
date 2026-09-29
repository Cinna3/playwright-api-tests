"""Thin client wrapping the product endpoints.

The value of a client layer: your tests say products_api.get_product(1) instead
of scattering raw paths and status assertions everywhere. If the base URL or the
endpoint path changes, you change it in one place.
"""


class ApiResponse:
    """Small wrapper so tests can read response.status / .json / .headers."""

    def __init__(self, raw):
        self.raw = raw

    @property
    def status(self):
        return self.raw.status

    @property
    def headers(self):
        return self.raw.headers

    def json(self):
        return self.raw.json()

    def text(self):
        return self.raw.text()


class ProductApi:
    def __init__(self, context):
        self.context = context

    # ---------- reads ----------

    def list_products(self, **params):
        return ApiResponse(self.context.get("/products", params=params))

    def get_product(self, product_id):
        return ApiResponse(self.context.get(f"/products/{product_id}"))

    def search_products(self, query):
        return ApiResponse(self.context.get("/products/search", params={"q": query}))

    def get_by_category(self, category):
        return ApiResponse(
            self.context.get(f"/products/category/{category}", params={"limit": 0})
        )

    # ---------- writes ----------

    def create_product(self, payload):
        return ApiResponse(self.context.post("/products/add", data=payload))

    def update_product(self, product_id, payload):
        return ApiResponse(self.context.put(f"/products/{product_id}", data=payload))

    def delete_product(self, product_id):
        return ApiResponse(self.context.delete(f"/products/{product_id}"))
