from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.volto.testing import PLONE_VOLTO_CORE_INTEGRATION_TESTING  # noqa
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

import unittest


class TestSummarySerialization(unittest.TestCase):

    layer = PLONE_VOLTO_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.catalog = getToolByName(self.portal, "portal_catalog")
        self.doc1 = createContentInContainer(
            self.portal,
            "Document",
            id="doc1",
            title="Lorem Ipsum",
            description="Description",
        )

    def test_brain_summary_contains_default_metadata_fields(self):
        brain = self.catalog(UID=self.doc1.UID())[0]
        summary = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
        self.assertIn("image_field", summary)
        self.assertIn("image_scales", summary)

    def test_brain_summary_does_not_fail_if_column_not_there(self):
        # First remove the image_field column, if it exists
        column = "image_field"
        column_exists = column in self.catalog.schema()
        if column_exists:
            self.catalog.delColumn(column)
        try:
            brain = self.catalog(UID=self.doc1.UID())[0]
            summary = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
            self.assertIn("image_field", summary)
        finally:
            if column_exists:
                self.catalog.addColumn(column)
