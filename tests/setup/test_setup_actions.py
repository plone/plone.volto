from plone import api

import pytest


class TestPersonalToolsActions:
    @pytest.fixture(autouse=True)
    def _setup(self, portal):
        self.portal = portal
        self.category = api.portal.get_tool("portal_actions")["personal_tools"]

    def test_action_ids(self):
        assert list(self.category.objectIds()) == [
            "profile",
            "preferences",
            "plone_setup",
        ]

    @pytest.mark.parametrize(
        "action_id,attr,expected",
        [
            ["profile", "url_expr", "string:/personal-information"],
            ["profile", "link_target", ""],
            ["profile", "available_expr", "python:member is not None"],
            ["profile", "permissions", ("View",)],
            ["preferences", "url_expr", "string:preferences"],
            ["preferences", "link_target", "component"],
            ["preferences", "available_expr", "python:member is not None"],
            ["preferences", "permissions", ("View",)],
            ["plone_setup", "url_expr", "string:/controlpanel"],
            ["plone_setup", "link_target", ""],
            ["plone_setup", "available_expr", ""],
            ["plone_setup", "permissions", ("Plone Site Setup: Overview",)],
        ],
    )
    def test_action_property(self, action_id: str, attr: str, expected):
        action = self.category[action_id]
        assert action.getProperty(attr) == expected

    @pytest.mark.parametrize("action_id", ["profile", "preferences", "plone_setup"])
    def test_action_visible(self, action_id: str):
        assert self.category[action_id].visible is True
