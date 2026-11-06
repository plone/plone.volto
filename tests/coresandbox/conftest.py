import pytest


@pytest.fixture
def functional_portal(coresandbox_functional):
    """Point pytest-plone's request fixtures at the coresandbox portal."""
    return coresandbox_functional["portal"]
