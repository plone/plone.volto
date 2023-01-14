# -*- coding: utf-8 -*-

from plone.dexterity.schema import invalidate_cache
from plone.namedfile.file import NamedBlobImage
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.volto.testing import PLONE_6
from plone.volto.testing import PLONE_VOLTO_CORE_INTEGRATION_TESTING
from z3c.form.interfaces import IDataManager
from zope.component import getMultiAdapter

import unittest


TEST_GIF = (
    b"GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;"
)


@unittest.skipIf(
    not PLONE_6,
    "This test is only intended to run for Plone 6",
)
class TestPreviewLinkBehavior(unittest.TestCase):
    layer = PLONE_VOLTO_CORE_INTEGRATION_TESTING

    def setUp(self):
        from plone.volto.behaviors.preview_link import IPreviewLink

        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.catalog = self.portal.portal_catalog

        fti = self.portal.portal_types.Document
        fti.behaviors += ("volto.preview_image_link",)
        invalidate_cache(fti)

        self.doc = self.portal[self.portal.invokeFactory("Document", id="doc1")]
        self.image = self.portal[
            self.portal.invokeFactory("Image", id="image-1", title="Target image")
        ]
        self.image.image = NamedBlobImage(data=TEST_GIF, filename="test.gif")
        dm = getMultiAdapter(
            (self.doc, IPreviewLink["preview_image_link"]), IDataManager
        )
        dm.set(self.image)
        self.doc.reindexObject()

    def test_image_scales_includes_preview_image_link(self):
        brain = self.catalog(UID=self.doc.UID())[0]
        summary = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
        self.assertIn("preview_image_link", summary["image_scales"])
