from plone import api

import pytest


@pytest.fixture
def contents(portal) -> dict:
    with api.env.adopt_roles(
        [
            "Manager",
        ]
    ):
        portal.blocks = {}
        portal.blocks_layout = {"items": []}
        portal.reindexObject()
        doc = api.content.create(
            container=portal,
            type="Document",
            id="doc1",
            title="Lorem Ipsum",
            description="Description",
            blocks={
                "1": {"@type": "image", "url": ""},
                "2": {"@type": "teaser", "styles": {"align": "left"}},
            },
        )
    return {
        "doc": doc,
    }


@pytest.fixture
def block_types_index(contents):
    ct = api.portal.get_tool("portal_catalog")
    return ct._catalog.indexes["block_types"]


class TestBlockTypesIndexer:

    @pytest.fixture(autouse=True)
    def _setup(self, http_request, portal, contents):
        self.request = http_request
        self.doc = contents["doc"]

    @pytest.mark.parametrize(
        "block_type,expected",
        [
            ["image", 1],
            ["teaser", 1],
        ],
    )
    def test_block_types_are_indexed(self, block_type, expected):
        brains = api.content.find(block_types=block_type)
        assert len(brains) == expected

    def test_index_has_results(self, block_types_index):
        brains = api.content.find(block_types="teaser")
        assert len(brains) == 1
        assert block_types_index.numObjects() == 1

    def test_mixed_blocks(self, block_types_index):
        """Check that when some blocks have type and others don't, it doesn't fail."""
        doc = self.doc
        blocks = {
            "1": {"url": ""},
            "2": {"@type": "teaser", "styles": {"align": "left"}},
        }
        doc.blocks = blocks
        doc.reindexObject(idxs=["block_types"])
        brains = api.content.find(block_types="teaser")
        assert len(brains) == 1
        assert block_types_index.numObjects() == 1

    def test_removed_blocks(self, block_types_index):
        """Ensure that when blocks are removed, the block_types index is updated."""
        doc = self.doc
        doc.blocks = {}
        doc.reindexObject(idxs=["block_types"])
        brains = api.content.find(block_types="teaser")
        assert len(brains) == 0
        assert block_types_index.numObjects() == 0

    def test_nested_blocks(self):
        """Ensure that nested block types are also included in block_types."""
        doc = self.doc
        blocks = {
            "1": {
                "@type": "gridBlock",
                "blocks": {
                    "2": {"@type": "teaser"},
                },
            },
        }
        doc.blocks = blocks
        doc.reindexObject(idxs=["block_types"])
        brains = api.content.find(block_types="teaser")
        assert len(brains) == 1

    def test_block_types_not_acquired(self):
        """Ensure that block_types is not acquired"""
        doc = self.doc
        api.content.create(container=doc, type="Image", id="image-1")
        brains = api.content.find(block_types="image")
        assert len(brains) == 1
