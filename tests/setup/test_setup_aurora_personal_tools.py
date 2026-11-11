from plone import api

import pytest


VOLTO_PERSONAL_TOOLS = ["profile", "preferences", "plone_setup"]


class TestAuroraPersonalTools:
    @pytest.fixture(autouse=True)
    def _setup(self, portal):
        self.portal = portal
        self.setup_tool = api.portal.get_tool("portal_setup")

    @property
    def category(self):
        return api.portal.get_tool("portal_actions")["personal_tools"]

    def install_aurora_profile(self):
        self.setup_tool.runAllImportStepsFromProfile("profile-plone.volto:aurora")

    def test_profile_registered(self):
        profile = self.setup_tool.getProfileInfo("plone.volto:aurora")
        assert profile["title"] == "Aurora Frontend (plone.volto)"
        assert profile["version"] == "1000"

    @pytest.mark.parametrize("action_id", VOLTO_PERSONAL_TOOLS)
    def test_actions_present_without_aurora_profile(self, action_id: str):
        assert action_id in self.category.objectIds()

    @pytest.mark.parametrize("action_id", VOLTO_PERSONAL_TOOLS)
    def test_actions_removed_by_aurora_profile(self, action_id: str):
        self.install_aurora_profile()
        assert action_id not in self.category.objectIds()

    def test_category_empty_after_aurora_profile(self):
        self.install_aurora_profile()
        assert list(self.category.objectIds()) == []
