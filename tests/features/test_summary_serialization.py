from plone import api
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import getMultiAdapter

import pytest


@pytest.fixture
def contents(portal) -> dict:
    with api.env.adopt_roles(
        [
            "Manager",
        ]
    ):
        doc = api.content.create(
            container=portal,
            type="Document",
            id="doc1",
            title="Lorem Ipsum",
            description="Description",
        )
    return {
        "doc": doc,
    }


@pytest.fixture
def catalog(portal):
    ct = api.portal.get_tool("portal_catalog")
    column = "image_field"
    column_exists = column in ct.schema()
    if column_exists:
        ct.delColumn(column)
    yield ct
    if column_exists:
        ct.addColumn(column)


class TestSummarySerialization:

    @pytest.fixture(autouse=True)
    def _setup(self, http_request, portal, contents):
        self.request = http_request
        self.doc1 = contents["doc"]

    def test_brain_summary_contains_default_metadata_fields(self):
        brain = api.content.find(UID=self.doc1.UID())[0]
        summary = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
        assert "image_field" in summary
        assert "image_scales" in summary

    def test_brain_summary_does_not_fail_if_column_not_there(self, catalog):
        brain = api.content.find(UID=self.doc1.UID())[0]
        summary = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
        assert "image_field" in summary
