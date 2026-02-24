from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import RelativeSession
from zope.component.hooks import site

import pytest


@pytest.fixture()
def portal(functional):
    """Provide the Plone portal instance for functional tests."""
    yield functional["portal"]


@pytest.fixture(scope="class")
def portal_class(functional_class):
    """Provide the Plone portal instance for class-scoped functional tests."""
    if hasattr(functional_class, "testSetUp"):
        functional_class.testSetUp()
    portal = functional_class["portal"]
    with site(portal):
        yield portal
    if hasattr(functional_class, "testTearDown"):
        functional_class.testTearDown()


@pytest.fixture()
def request_api_factory(portal):
    """Provide a factory function for creating Plone REST API session objects."""

    def factory():
        url = portal.absolute_url()
        api_session = RelativeSession(f"{url}/++api++")
        return api_session

    return factory


@pytest.fixture()
def api_anon_request(request_api_factory):
    """Provide an unauthenticated REST API session for anonymous requests."""
    request = request_api_factory()
    yield request


@pytest.fixture()
def api_manager_request(request_api_factory):
    """Provide an authenticated REST API session with manager privileges."""
    request = request_api_factory()
    request.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    yield request
    request.auth = ()
