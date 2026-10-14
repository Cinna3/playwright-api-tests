"""Shared fixtures for the API test suite.

All the real wiring lives in the installed qa_framework package: settings, the
API client, logging and the session fixture that builds it. This file only maps
the fixture name the tests expect onto the one the framework provides.

The base URL is not hardcoded here. API_BASE_URL comes from the environment
(see qa_framework's settings.py), defaulting to https://dummyjson.com.
"""

import pytest


@pytest.fixture
def products_api(api_client):
    """The product endpoints, as a test-facing alias for the framework client."""
    return api_client
