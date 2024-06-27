from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import RelativeSession

import pytest


@pytest.fixture
def app(coresandbox_functional):
    return coresandbox_functional["app"]


@pytest.fixture
def portal(app):
    return app["plone"]


@pytest.fixture()
def http_request(coresandbox_functional):
    return coresandbox_functional["request"]


@pytest.fixture()
def request_api_factory(portal):
    def factory():
        url = portal.absolute_url()
        api_session = RelativeSession(f"{url}/++api++")
        return api_session

    return factory


@pytest.fixture()
def api_manager_request(request_api_factory):
    request = request_api_factory()
    request.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    yield request
    request.auth = ()
