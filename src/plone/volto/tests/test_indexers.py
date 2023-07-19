# -*- coding: utf-8 -*-
from plone.volto.testing import PLONE_VOLTO_CORE_INTEGRATION_TESTING
from unittest import TestCase


class TestBlockTypesIndexer(TestCase):
    layer = PLONE_VOLTO_CORE_INTEGRATION_TESTING
    maxDiff = None

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.doc1 = self.portal[
            self.portal.invokeFactory(
                "Document", id="doc1", title="Document with Blocks"
            )
        ]
        self.catalog = self.portal.portal_catalog

    def test_block_types_are_indexed(self):
        """Ensure that when blocks are updated, the block_types index is updated."""
        blocks = {
            "1": {"@type": "image", "url": ""},
            "2": {"@type": "teaser", "styles": {"align": "left"}},
        }
        self.portal.doc1.blocks = blocks
        self.portal.doc1.reindexObject(idxs=["block_types"])
        brains = self.catalog(block_types="image")
        self.assertEqual(len(brains), 1)
        brains = self.catalog(block_types="teaser")
        self.assertEqual(len(brains), 1)
        block_types_index = self.catalog._catalog.indexes["block_types"]
        self.assertEqual(block_types_index.numObjects(), 1)

    def test_mixed_blocks(self):
        """Check that when some blocks have type and others don't, it doesn't fail."""
        blocks = {
            "1": {"url": ""},
            "2": {"@type": "teaser", "styles": {"align": "left"}},
        }
        self.portal.doc1.blocks = blocks
        self.portal.doc1.reindexObject(idxs=["block_types"])
        brains = self.catalog(block_types="image")
        self.assertEqual(len(brains), 0)
        brains = self.catalog(block_types="teaser")
        self.assertEqual(len(brains), 1)
        block_types_index = self.catalog._catalog.indexes["block_types"]
        self.assertEqual(block_types_index.numObjects(), 1)

    def test_removed_blocks(self):
        """Ensure that when blocks are removed, the block_types index is updated."""
        blocks = {
            "1": {"@type": "image", "url": ""},
            "2": {"@type": "teaser", "styles": {"align": "left"}},
        }
        self.portal.doc1.blocks = blocks
        self.portal.doc1.reindexObject(idxs=["block_types"])
        self.portal.doc1.blocks = {}
        self.portal.doc1.reindexObject(idxs=["block_types"])
        brains = self.catalog(block_types="teaser")
        self.assertEqual(len(brains), 0)
        block_types_index = self.catalog._catalog.indexes["block_types"]
        self.assertEqual(block_types_index.numObjects(), 0)

    def test_nested_blocks(self):
        """Ensure that nested block types are also included in block_types."""
        blocks = {
            "1": {
                "@type": "gridBlock",
                "blocks": {
                    "2": {"@type": "teaser"},
                },
            },
        }
        self.portal.doc1.blocks = blocks
        self.portal.doc1.reindexObject(idxs=["block_types"])
        brains = self.catalog(block_types="teaser")
        self.assertEqual(len(brains), 1)
