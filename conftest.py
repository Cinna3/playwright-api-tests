"""Shared fixtures for the API test suite.

All the real wiring lives in the installed qa_framework package: settings, the
API client, logging and the session fixture that builds it. This file only maps
the fixture name the tests expect onto the one the framework provides.

The base URL is not hardcoded here. API_BASE_URL comes from the environment
(see qa_framework's settings.py), defaulting to https://dummyjson.com.
"""

import pytest


@pytest.fixture(scope="session")
def base_url():
    """Disable the UI base URL: this suite only talks to the API.

    pytest-base-url's autouse verifier asks for ``base_url`` for every test.
    The framework's ``base_url`` starts the demo app server, which this repo
    does not ship. Returning None tells the verifier there is no UI target.
    """
    return None


@pytest.fixture
def products_api(api_client):
    """The product endpoints, as a test-facing alias for the framework client."""
    return api_client
