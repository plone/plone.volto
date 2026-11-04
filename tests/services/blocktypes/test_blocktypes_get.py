from plone import api

import pytest
import transaction


@pytest.fixture
def contents(functional_portal):
    with api.env.adopt_roles(["Manager"]):
        doc = api.content.create(functional_portal, type="Document", id="lorem-ipsum")
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
    def _setup(self, contents, functional_portal, manager_request):
        self.path = f"/{functional_portal.getId()}/lorem-ipsum"
        self.api_session = manager_request

    def test_response_type(self):
        response = self.api_session.get("/@blocktypes")
        data = response.json()
        assert isinstance(data, dict)

    def test_response_type_with_id(self):
        response = self.api_session.get("/@blocktypes/title")
        data = response.json()
        assert isinstance(data, list)

    def test_filtered(self):
        response = self.api_session.get(f"/@blocktypes?path={self.path}")
        data = response.json()
        assert len(data) == 3

    def test_filtered_with_id(self):
        response = self.api_session.get(f"/@blocktypes/teaser?path={self.path}")
        data = response.json()
        assert len(data) == 1
