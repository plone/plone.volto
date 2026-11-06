from plone import api

import pytest
import transaction


MEMBER_NAME = "member"
MEMBER_PASSWORD = "secret-password"


@pytest.fixture
def member(functional_portal):
    api.user.create(
        email="member@example.org",
        username=MEMBER_NAME,
        password=MEMBER_PASSWORD,
        roles=["Member"],
    )
    transaction.commit()


class TestActionsGetPersonalTools:
    @pytest.fixture(autouse=True)
    def _setup(self, member, request_factory):
        self.sessions = {
            "anonymous": request_factory(),
            "member": request_factory(basic_auth=(MEMBER_NAME, MEMBER_PASSWORD)),
            "manager": request_factory(role="Manager"),
        }

    def get_personal_tools(self, user: str) -> list:
        response = self.sessions[user].get("/@actions")
        assert response.status_code == 200
        return response.json()["personal_tools"]

    @pytest.mark.parametrize(
        "user,expected",
        [
            ["anonymous", []],
            ["member", ["profile", "preferences"]],
            ["manager", ["profile", "preferences", "plone_setup"]],
        ],
    )
    def test_action_ids(self, user: str, expected: list):
        actions = self.get_personal_tools(user)
        assert [action["id"] for action in actions] == expected

    @pytest.mark.parametrize(
        "action_id,title,url,icon",
        [
            ["profile", "Profile", "/personal-information", "plone-user"],
            ["preferences", "Preferences", "preferences", "plone-user"],
            ["plone_setup", "Site Setup", "/controlpanel", "plone-controlpanel"],
        ],
    )
    def test_action_entry(self, action_id: str, title: str, url: str, icon: str):
        actions = {
            action["id"]: action for action in self.get_personal_tools("manager")
        }
        assert actions[action_id] == {
            "id": action_id,
            "title": title,
            "url": url,
            "icon": icon,
        }
