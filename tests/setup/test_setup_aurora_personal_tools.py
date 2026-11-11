from plone import api

import pytest


AURORA_PROFILE = "profile-plone.volto:aurora"


@pytest.fixture
def category(portal):
    def func():
        return api.portal.get_tool("portal_actions")["personal_tools"]

    return func


@pytest.fixture
def install_aurora(portal):
    setup_tool = api.portal.get_tool("portal_setup")
    setup_tool.runAllImportStepsFromProfile(AURORA_PROFILE)


class TestAuroraProfile:
    def test_profile_registered(self, portal):
        setup_tool = api.portal.get_tool("portal_setup")
        profile = setup_tool.getProfileInfo("plone.volto:aurora")
        assert profile["title"] == "Aurora Frontend (plone.volto)"
        assert profile["version"] == "1000"


class TestPersonalToolsWithoutAuroraProfile:
    """Without the aurora profile, the Volto defaults are kept."""

    def test_action_ids(self, category):
        assert list(category().objectIds()) == [
            "profile",
            "preferences",
            "plone_setup",
        ]

    @pytest.mark.parametrize(
        "action_id,expected",
        [
            ["profile", "string:/personal-information"],
            ["preferences", "string:preferences"],
            ["plone_setup", "string:/controlpanel"],
        ],
    )
    def test_url_expr(self, category, action_id: str, expected: str):
        assert category()[action_id].getProperty("url_expr") == expected


class TestPersonalToolsWithAuroraProfile:
    @pytest.fixture(autouse=True)
    def _setup(self, install_aurora, category):
        self.category = category()

    def test_action_ids(self):
        assert list(self.category.objectIds()) == [
            "profile",
            "preferences",
            "plone_setup",
            "logout",
        ]

    @pytest.mark.parametrize(
        "action_id,attr,expected",
        [
            ["profile", "title", "Profile"],
            ["profile", "url_expr", "string:/@@personal-information"],
            ["profile", "link_target", ""],
            ["profile", "available_expr", "python:member is not None"],
            ["profile", "permissions", ("View",)],
            ["preferences", "title", "Preferences"],
            ["preferences", "url_expr", "string:/@@personal-preferences"],
            ["preferences", "link_target", ""],
            ["preferences", "available_expr", "python:member is not None"],
            ["preferences", "permissions", ("View",)],
            ["plone_setup", "title", "Site Setup"],
            ["plone_setup", "url_expr", "string:/controlpanel"],
            ["plone_setup", "link_target", ""],
            ["plone_setup", "available_expr", ""],
            ["plone_setup", "permissions", ("Plone Site Setup: Overview",)],
            ["logout", "title", "Log out"],
            ["logout", "url_expr", "string:/logout"],
            ["logout", "link_target", ""],
            ["logout", "icon_expr", "string:plone-logout"],
            ["logout", "available_expr", "python:member is not None"],
            ["logout", "permissions", ("View",)],
        ],
    )
    def test_action_property(self, action_id: str, attr: str, expected):
        action = self.category[action_id]
        assert action.getProperty(attr) == expected

    @pytest.mark.parametrize(
        "action_id", ["profile", "preferences", "plone_setup", "logout"]
    )
    def test_action_visible(self, action_id: str):
        assert self.category[action_id].visible is True
