import pytest


@pytest.fixture
def app(migration_functional):
    return migration_functional["app"]


@pytest.fixture
def portal(app):
    return app["plone"]


@pytest.fixture()
def http_request(migration_functional):
    return migration_functional["request"]
