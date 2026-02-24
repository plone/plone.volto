from plone import api

import pytest
import transaction


@pytest.fixture(scope="class")
def portal(portal_class):
    yield portal_class


@pytest.fixture(scope="class")
def contents(portal):
    with api.env.adopt_roles(["Manager"]):
        doc = api.content.create(portal, type="Document", id="lorem-ipsum")
        doc.blocks = {
            "1": {"@type": "title"},
            "2": {"@type": "teaser"},
            "3": {
                "@type": "gridBlock",
                "blocks": {
                    "1": {"@type": "teaser"},
                    "2": {"@type": "teaser"},
                    "3": {"@type": "teaser"},
                },
            },
        }
        doc.reindexObject(idxs=["block_types"])
        transaction.commit()


class TestBlockTypesGet:
    @pytest.fixture(autouse=True)
    def _setup(self, contents, portal, api_manager_request):
        self.portal = portal
        self.api_session = api_manager_request

    def test_response_type(self):
        response = self.api_session.get("/@blocktypes")
        data = response.json()
        assert isinstance(data, dict)

    def test_response_type_with_id(self):
        response = self.api_session.get("/@blocktypes/title")
        data = response.json()
        assert isinstance(data, list)

    def test_filtered(self):
        response = self.api_session.get("/@blocktypes?path=/plone/lorem-ipsum")
        data = response.json()
        assert len(data) == 3

    def test_filtered_with_id(self):
        response = self.api_session.get("/@blocktypes/teaser?path=/plone/lorem-ipsum")
        data = response.json()
        assert len(data) == 1
