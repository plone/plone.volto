from copy import deepcopy
from plone import api
from plone.distribution.api import site as site_api
from Products.CMFPlone.Portal import PloneSite
from zope.component.hooks import setSite

import pytest


@pytest.fixture()
def app(functional):
    return functional["app"]


@pytest.fixture()
def http_request(functional):
    return functional["request"]


@pytest.fixture()
def answers():
    return {
        "site_id": "default",
        "title": "A Plone Site",
        "description": "A newly created Plone Site with Classic UI",
        "site_logo": "name=teste;data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==",  # noQA
        "default_language": "en",
        "portal_timezone": "America/Sao_Paulo",
        "setup_content": True,
    }


@pytest.fixture()
def answers_no_logo(answers):
    answers = deepcopy(answers)
    answers.pop("site_logo")
    answers["title"] = "Plone Site with default logo"
    return answers


@pytest.fixture
def create_site(app, distribution_name):
    def func(answers: dict) -> PloneSite:
        with api.env.adopt_roles(["Manager"]):
            site = site_api.create(app, distribution_name, answers)
            setSite(site)
        return site

    return func


class TestCreationSite:

    @pytest.fixture(autouse=True)
    def _setup(self, create_site, answers):
        self.site = create_site(answers)

    @pytest.mark.parametrize(
        "attr,expected",
        [
            ["id", "default"],
        ],
    )
    def test_properties(self, attr, expected):
        site = self.site
        assert getattr(site, attr) == expected

    @pytest.mark.parametrize(
        "key,expected",
        [
            ["plone.site_title", "A Plone Site"],
            [
                "plone.site_logo",
                b"filenameb64:dGVzdGU7ZGF0YTppbWFnZS9wbmc=;datab64:iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==",  # noQA
            ],
        ],
    )
    def test_registry_entries(self, key, expected):
        assert api.portal.get_registry_record(key) == expected


class TestCreationSiteNoLogo:

    @pytest.fixture(autouse=True)
    def _create_site(self, create_site, answers_no_logo):
        self.site = create_site(answers_no_logo)

    @pytest.mark.parametrize(
        "attr,expected",
        [
            ["id", "default"],
        ],
    )
    def test_properties(self, attr, expected):
        site = self.site
        assert getattr(site, attr) == expected

    @pytest.mark.parametrize(
        "key,expected",
        [
            ["plone.site_title", "Plone Site with default logo"],
            ["plone.site_logo", None],
        ],
    )
    def test_registry_entries(self, key, expected):
        assert api.portal.get_registry_record(key) == expected
