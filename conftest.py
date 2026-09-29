"""Shared fixtures for the API test suite.

The important detail here: Playwright can drive HTTP requests directly with
APIRequestContext. No browser is launched, so API tests run in a fraction of a
second compared with UI tests. That means you can afford far more of them.
"""

import pytest

BASE_URL = "https://dummyjson.com"


@pytest.fixture(scope="session")
def api_context(playwright):
    """One HTTP client for the whole run, torn down automatically.

    Reusing a single context is much faster than creating one per test, and it
    mirrors how a real API client behaves.
    """
    context = playwright.request.new_context(
        base_url=BASE_URL,
        extra_http_headers={"Accept": "application/json"},
    )
    yield context
    context.dispose()


@pytest.fixture
def products_api(api_context):
    from clients.product_api import ProductApi

    return ProductApi(api_context)
