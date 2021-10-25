# -*- coding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityFTI
from plone.volto.scripts.listingaddsummary import migrate_listing_block_to_summary
from plone.volto.scripts.searchscalesinimageblocks import remove_image_scales
from plone.volto.testing import PLONE_VOLTO_CORE_INTEGRATION_TESTING  # noqa
from zope.component import queryUtility

import unittest


class TestBlocksTransforms(unittest.TestCase):

    layer = PLONE_VOLTO_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append("volto.blocks")
        fti.behaviors = tuple(behavior_list)

        self.portal.invokeFactory("Document", id=u"doc1")
        self.doc1 = self.portal["doc1"]
        self.image = self.portal[
            self.portal.invokeFactory("Image", id="image1", title="Target image")
        ]

    def test_migrate_listing_block_to_summary(self):
        blocks = {"@type": "listing"}

        result = migrate_listing_block_to_summary(blocks)

        self.assertEqual(result["template"], "summary")

    def test_remove_image_scales(self):
        blocks = {
            "b53feefa-e6f7-42f0-8f04-534655c6c594": {
                "@type": "image",
                "url": "/foo/bar/@@images/image/large",
            }
        }

        result = remove_image_scales(blocks)

        self.assertEqual(
            result["b53feefa-e6f7-42f0-8f04-534655c6c594"]["url"], "/foo/bar"
        )
        self.assertEqual(result["b53feefa-e6f7-42f0-8f04-534655c6c594"]["size"], "l")

    def test_remove_image_scales_no_large(self):
        blocks = {
            "b53feefa-e6f7-42f0-8f04-534655c6c594": {
                "@type": "image",
                "url": "/foo/bar/@@images/image/teaser",
            }
        }

        result = remove_image_scales(blocks)

        self.assertEqual(
            result["b53feefa-e6f7-42f0-8f04-534655c6c594"]["url"], "/foo/bar"
        )
